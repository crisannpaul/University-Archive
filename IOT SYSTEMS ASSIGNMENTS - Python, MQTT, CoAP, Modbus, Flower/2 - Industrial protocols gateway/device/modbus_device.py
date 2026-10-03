# device/modbus_device.py
import random
import time
from typing import Optional

from pymodbus.client import ModbusTcpClient  # pymodbus >=3.x
from device.base_device import BaseDevice


class ModbusDevice(BaseDevice):
    """
    Real Modbus TCP device simulator.
    - Uses IndustrialDatasetReader as data source.
    - Connects as Modbus TCP client to a central Modbus server (the gateway).
    - Writes its current sensor value into a dedicated holding register.
    """

    def __init__(
        self,
        device_id: str,
        sensor_name: str,
        reader,
        register_address: int,
        shard_len: int = 300,
        period_s: float = 1.0,
        host: str = "127.0.0.1",
        port: int = 5020,
        unit_id: int = 1,
    ):
        super().__init__(
            device_id=device_id,
            protocol_name="modbus",
            sensor_name=sensor_name,
            reader=reader,
            shard_len=shard_len,
            sampling_interval=period_s,
        )

        self.period_s = period_s
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self.register_address = register_address

        self.client = ModbusTcpClient(host=self.host, port=self.port)

    def run(self):
        try:
            if not self.client.connect():
                print(f"[ModbusDevice {self.device_id}] Could not connect to Modbus server at {self.host}:{self.port}")
                return

            print(f"[ModbusDevice {self.device_id}] Connected to Modbus server at {self.host}:{self.port}, reg={self.register_address}")

            while True:
                value = self._next_value()          # still has device failure logic
                reg_value = int(value)

                # ---- packet loss for Modbus: reuse BaseDevice settings ----
                if random.random() < self._loss_rate:
                    reg_value = int(self._loss_sentinel)  # -100

                # ---- latency for Modbus: reuse BaseDevice settings ----
                if self._latency_range_ms is not None:
                    lo, hi = self._latency_range_ms
                    if hi > 0:
                        delay_ms = random.uniform(lo, hi)
                        time.sleep(delay_ms / 1000.0)

                try:
                    result = self.client.write_register(
                        address=self.register_address,
                        value=reg_value,
                        device_id=self.unit_id,
                    )
                    if result.isError():
                        print(f"[ModbusDevice {self.device_id}] Write error: {result}")
                except Exception as e:
                    print(f"[ModbusDevice {self.device_id}] Exception during write: {e}")
                    break

                time.sleep(self.period_s)
        finally:
            try:
                self.client.close()
            except Exception:
                pass
