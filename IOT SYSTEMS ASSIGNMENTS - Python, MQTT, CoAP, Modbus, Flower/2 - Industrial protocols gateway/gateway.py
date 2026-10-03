# gateway.py
import asyncio
import json
import csv
import os
import time
import threading
from pathlib import Path
from typing import Dict, Tuple
from datetime import datetime, timezone

import pika
from pymodbus.datastore import (
    ModbusDeviceContext,
    ModbusServerContext,
    ModbusSequentialDataBlock,
)
from pymodbus.server import StartTcpServer  # sync server
from aiocoap import Context as CoapContext, Message as CoapMessage, resource as coap_resource, CHANGED


class UnifiedGateway:
    """
    Unified gateway:
      - RabbitMQ consumer for "MQTT" devices (JSON messages)
      - Modbus TCP server + polling for Modbus devices
      - CoAP server for CoAP devices
      - Persists everything into one CSV.

    CSV schema:
        device_id, protocol, produced_timestamp, delivered_timestamp, sensor, value
    """

    def __init__(
        self,
        sink_csv_path: str = "gateway_output.csv",
        # RabbitMQ
        host: str = "localhost",
        port: int = 5672,
        username: str = "guest",
        password: str = "guest",
        exchange: str = "iot",
        queue_name: str = "gateway",
        bind_key: str = "iot.#",
        # Modbus
        modbus_port: int = 5020,
        modbus_unit_id: int = 1,
        # map: register_address -> (device_id, sensor_name)
        modbus_register_map: Dict[int, Tuple[str, str]] | None = None,
        modbus_poll_interval: float = 1.0,
    ):
        self.csv_path = Path(sink_csv_path)
        self.csv_lock = threading.Lock()

        # overwrite CSV on startup
        if self.csv_path.exists():
            os.remove(self.csv_path)
        self._write_header()

        # RabbitMQ setup
        self.exchange = exchange
        self.queue_name = queue_name
        self.bind_key = bind_key

        creds = pika.PlainCredentials(username, password)
        params = pika.ConnectionParameters(host=host, port=port, credentials=creds)
        self.rm_connection = pika.BlockingConnection(params)
        self.rm_channel = self.rm_connection.channel()

        self.rm_channel.exchange_declare(
            exchange=self.exchange,
            exchange_type="topic",
            durable=False,
        )
        self.rm_channel.queue_declare(queue=self.queue_name, durable=False)
        self.rm_channel.queue_bind(
            exchange=self.exchange,
            queue=self.queue_name,
            routing_key=self.bind_key,
        )

        # Modbus setup
        self.modbus_port = modbus_port
        self.modbus_unit_id = modbus_unit_id
        self.modbus_register_map = modbus_register_map or {}  # {addr: (device_id, sensor)}
        self.modbus_poll_interval = modbus_poll_interval

        # Simple holding register block with enough space
        max_reg = max(self.modbus_register_map.keys(), default=10)

        device_ctx = ModbusDeviceContext(
            di=None,
            co=None,
            ir=None,
            hr=ModbusSequentialDataBlock(0, [0] * (max_reg + 10)),
        )

        # single=True → every device_id uses the same context instance
        self.modbus_context = ModbusServerContext(devices=device_ctx, single=True)

        self._stop_evt = threading.Event()

    # ---------------- CSV helpers ----------------
    def _write_header(self):
        # produced_timestamp = timestamp from device
        # delivered_timestamp = when gateway actually persists it
        headers = [
            "device_id",
            "protocol",
            "produced_timestamp",
            "delivered_timestamp",
            "sensor",
            "value",
        ]
        with open(self.csv_path, "w", newline="") as f:
            csv.writer(f).writerow(headers)

    def _write_row(
        self,
        device_id: str,
        protocol: str,
        timestamp: str,
        sensor: str,
        value,
    ):
        """
        timestamp = produced_timestamp (from device or poll time)
        delivered_timestamp = gateway time when we persist (with sub-second precision)
        """
        delivered_timestamp = datetime.now(timezone.utc).isoformat()

        with self.csv_lock:
            with open(self.csv_path, "a", newline="") as f:
                csv.writer(f).writerow(
                    [device_id, protocol, timestamp, delivered_timestamp, sensor, value]
                )

    # ---------------- RabbitMQ consumer ----------------
    def _on_rabbit_message(self, ch, method, properties, body):
        try:
            payload = body.decode("utf-8", errors="replace")
            data = json.loads(payload)
            if not isinstance(data, dict):
                raise ValueError("Payload must be a JSON object")
        except Exception as e:
            print(f"[Gateway/RabbitMQ] Bad message on {method.routing_key}: {e}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        device_id = str(data.get("device_id", ""))

        self._write_row(
            device_id=device_id,
            protocol=str(data.get("protocol", "")),
            timestamp=str(data.get("timestamp", "")),
            sensor=str(data.get("sensor", "")),
            value=data.get("value", ""),
        )

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def _run_rabbitmq(self):
        print("[Gateway/RabbitMQ] Starting consume loop...")
        self.rm_channel.basic_qos(prefetch_count=50)
        self.rm_channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self._on_rabbit_message,
            auto_ack=False,
        )
        try:
            self.rm_channel.start_consuming()
        except Exception as e:
            print("[Gateway/RabbitMQ] Exception:", e)
        finally:
            try:
                self.rm_connection.close()
            except Exception:
                pass
            print("[Gateway/RabbitMQ] Stopped.")

    # ---------------- Modbus server + poller ----------------
    def _run_modbus_server(self):
        print(f"[Gateway/Modbus] Starting Modbus TCP server on 0.0.0.0:{self.modbus_port}")
        # Blocking call, run in its own thread
        StartTcpServer(
            context=self.modbus_context,
            address=("0.0.0.0", self.modbus_port),
        )
        # When server stops, we get here
        print("[Gateway/Modbus] Modbus server stopped.")

    def _run_modbus_poll(self):
        print("[Gateway/Modbus] Starting Modbus polling loop...")
        last_values: Dict[int, int] = {}

        while not self._stop_evt.is_set():
            try:
                device_id_modbus = 1  # default device id in pymodbus 3.x
                for addr, (device_id, sensor) in self.modbus_register_map.items():
                    regs = self.modbus_context[device_id_modbus].getValues(3, addr, count=1)
                    if not regs:
                        continue
                    value = regs[0]
                    prev = last_values.get(addr)
                    if prev != value:
                        last_values[addr] = value

                        # For Modbus, we treat poll time as produced_timestamp
                        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                        self._write_row(
                            device_id=device_id,
                            protocol="modbus",
                            timestamp=ts,
                            sensor=sensor,
                            value=value,
                        )
                        # print(f"[Gateway/Modbus] HR[{addr}] = {value} (device={device_id}, sensor={sensor})")
            except Exception as e:
                print("[Gateway/Modbus] Poll error:", e)

            if self._stop_evt.wait(self.modbus_poll_interval):
                break

        print("[Gateway/Modbus] Polling loop stopped.")

    # ---------------- CoAP server ----------------
    async def _coap_server_async(self):
        root = coap_resource.Site()
        root.add_resource(["sensor"], CoapSensorResource(self))
        print("[Gateway/CoAP] Starting CoAP server on udp/5683 (localhost)")
        await CoapContext.create_server_context(root, bind=("localhost", 5683))
        # Keep running forever
        await asyncio.get_running_loop().create_future()

    def _run_coap_server(self):
        try:
            asyncio.run(self._coap_server_async())
        except Exception as e:
            print("[Gateway/CoAP] Server stopped with exception:", e)
        finally:
            print("[Gateway/CoAP] Server stopped.")

    # ---------------- lifecycle ----------------
    def start(self):
        # RabbitMQ consumer thread
        t_rm = threading.Thread(target=self._run_rabbitmq, daemon=True)
        t_rm.start()

        # Modbus server thread
        t_modbus_srv = threading.Thread(target=self._run_modbus_server, daemon=True)
        t_modbus_srv.start()

        # Modbus poller thread
        t_modbus_poll = threading.Thread(target=self._run_modbus_poll, daemon=True)
        t_modbus_poll.start()

        # CoAP server thread
        t_coap = threading.Thread(target=self._run_coap_server, daemon=True)
        t_coap.start()

        print("[Gateway] RabbitMQ + Modbus + CoAP started.")

    def stop(self):
        self._stop_evt.set()
        print("[Gateway] Stop signal sent.")


class CoapSensorResource(coap_resource.Resource):
    """
    CoAP resource bound at /sensor.
    On POST, expects JSON payload matching our unified message schema.
    """

    def __init__(self, gateway: "UnifiedGateway"):
        super().__init__()
        self.gateway = gateway

    async def render_post(self, request):
        try:
            payload = request.payload.decode("utf-8", errors="replace")
            data = json.loads(payload)

            device_id = str(data.get("device_id", ""))
            protocol = str(data.get("protocol", "coap"))
            timestamp = str(data.get("timestamp", ""))
            sensor = str(data.get("sensor", ""))
            value = data.get("value", "")

            self.gateway._write_row(
                device_id=device_id,
                protocol=protocol,
                timestamp=timestamp,
                sensor=sensor,
                value=value,
            )

            return CoapMessage(code=CHANGED, payload=b"ACK")
        except Exception as e:
            print(f"[Gateway/CoAP] Bad CoAP payload: {e}")
            return CoapMessage(code=CHANGED, payload=b"ERR")
