import json
from typing import Optional
import requests
from device.base_device import BaseDevice
from datetime import datetime
from paho.mqtt import client as mqtt


from device.config import DeviceConfig
from dataio.data_reader import IntelLabDataReader

import json
from typing import Optional
from paho.mqtt import client as mqtt

class MqttDevice(BaseDevice):
    """MQTT device that publishes readings to a topic (paho-mqtt)."""

    def __init__(
        self,
        reader: IntelLabDataReader,
        config: DeviceConfig,
        broker: str,
        port: int = 1883,
        topic: str = "sensors/readings",
        keepalive: int = 60,
        client_id: Optional[str] = None,
        qos: int = 0,
        retain: bool = False,
    ):
        super().__init__(reader, config)
        self.topic = topic
        self.qos = qos
        self.retain = retain
        # Use composite id by default for the MQTT client id
        self.client = mqtt.Client(client_id or self.unique_id)
        self.client.connect(broker, port, keepalive)

    def run(self) -> None:
        self.client.loop_start()
        try:
            while not self.stopped():
                reading = self.build_reading(protocol="mqtt")
                try:
                    self.client.publish(self.topic, json.dumps(reading), qos=self.qos, retain=self.retain)
                except Exception as e:
                    print(f"[MQTT DEVICE {self.unique_id}] Error: {e}")
                if self._stop_evt.wait(self.config.period_s):
                    break
        finally:
            try:
                self.client.loop_stop()
                self.client.disconnect()
            except Exception:
                pass
