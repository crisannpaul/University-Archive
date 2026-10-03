import requests
from device.base_device import BaseDevice
from datetime import datetime
import threading

from device.config import DeviceConfig
from dataio.data_reader import IntelLabDataReader

import requests

class HttpDevice(BaseDevice):
    """HTTP device that sends readings via POST to a collector URL."""

    def __init__(self, reader: IntelLabDataReader, config: DeviceConfig, collector_url: str, timeout_s: float = 5.0):
        super().__init__(reader, config)
        self.collector_url = collector_url
        self.timeout_s = timeout_s

    def emit(self, reading: dict) -> None:
        try:
            requests.post(self.collector_url, json=reading, timeout=self.timeout_s)
        except Exception as e:
            print(f"[HTTP DEVICE {self.unique_id}] Error: {e}")

    def run(self) -> None:
        while not self.stopped():
            reading = self.build_reading(protocol="http")
            self.emit(reading)
            if self._stop_evt.wait(self.config.period_s):
                break
