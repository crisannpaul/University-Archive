# main.py
import threading
import time

from gateway import UnifiedGateway
from data_reader.aq_reader import AirQualityDatasetReader
from data_reader.industrial_reader import IndustrialDatasetReader
from device.mqtt_device import MqttDevice
from device.modbus_device import ModbusDevice
from device.coap_device import CoapDevice


def main():
    print("=== IoT System Startup (RabbitMQ + Modbus + CoAP) ===")

    # 1. Dataset readers
    aq_reader = AirQualityDatasetReader("datasets/AirQuality.csv")
    ind_reader = IndustrialDatasetReader("datasets/chicago.csv")

    # 2. Gateway with Modbus mapping
    modbus_register_map = {
        0: ("modbus_motor_01", "pressure"),
        1: ("modbus_pump_01", "vibration"),
    }

    gateway = UnifiedGateway(
        sink_csv_path="gateway_output.csv",
        # RabbitMQ
        host="localhost",
        port=5672,
        username="guest",
        password="guest",
        exchange="iot",
        queue_name="gateway",
        bind_key="iot.#",
        # Modbus
        modbus_port=5020,
        modbus_unit_id=1,
        modbus_register_map=modbus_register_map,
        modbus_poll_interval=1.0,
        # 🔥 Network simulation params
    )

    gateway.start()

    # 3. "MQTT" devices over RabbitMQ
    mqtt_dev1 = MqttDevice(
        device_id="mqtt_sensor_01",
        sensor_name="T",
        reader=aq_reader,
        shard_len=1000,
        period_s=1.0,
        host="localhost",
        port=5672,
        username="guest",
        password="guest",
        exchange="iot",
        routing_key="iot.mqtt.mqtt_sensor_01",
    )

    mqtt_dev2 = MqttDevice(
        device_id="mqtt_sensor_02",
        sensor_name="CO(GT)",
        reader=aq_reader,
        shard_len=1000,
        period_s=1.3,
        host="localhost",
        port=5672,
        username="guest",
        password="guest",
        exchange="iot",
        routing_key="iot.mqtt.mqtt_sensor_02",
    )

    # 4. Modbus devices (real Modbus)
    modbus_dev1 = ModbusDevice(
        device_id="modbus_motor_01",
        sensor_name="pressure",
        reader=ind_reader,
        register_address=0,
        shard_len=1000,
        period_s=1.0,
        host="127.0.0.1",
        port=5020,
        unit_id=1,
    )

    modbus_dev2 = ModbusDevice(
        device_id="modbus_pump_01",
        sensor_name="vibration",
        reader=ind_reader,
        register_address=1,
        shard_len=1000,
        period_s=1.2,
        host="127.0.0.1",
        port=5020,
        unit_id=1,
    )

    # 5. CoAP devices (using AirQuality reader, for example)
    coap_dev1 = CoapDevice(
        device_id="coap_wearable_01",
        sensor_name="T",   # reuse temp for demo
        reader=aq_reader,
        shard_len=1000,
        period_s=2.0,
        uri="coap://localhost/sensor",
    )

    coap_dev2 = CoapDevice(
        device_id="coap_wearable_02",
        sensor_name="CO(GT)",
        reader=aq_reader,
        shard_len=1000,
        period_s=2.5,
        uri="coap://localhost/sensor",
    )

    # Start all device threads
    threads = [
        threading.Thread(target=mqtt_dev1.run, daemon=True),
        threading.Thread(target=mqtt_dev2.run, daemon=True),
        threading.Thread(target=modbus_dev1.run, daemon=True),
        threading.Thread(target=modbus_dev2.run, daemon=True),
        threading.Thread(target=coap_dev1.run, daemon=True),
        threading.Thread(target=coap_dev2.run, daemon=True),
    ]
    for t in threads:
        t.start()

    print("[Main] Devices and gateway started. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Main] Shutting down...")
        gateway.stop()


if __name__ == "__main__":
    main()
