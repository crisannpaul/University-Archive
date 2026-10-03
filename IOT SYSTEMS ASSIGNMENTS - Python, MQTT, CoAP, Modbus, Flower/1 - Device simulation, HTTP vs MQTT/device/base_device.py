from datetime import datetime
import threading

from dataio.data_reader import IntelLabDataReader
from device.config import DeviceConfig

class BaseDevice(threading.Thread):
    """Common base for simulated IoT devices.

    Each device pulls its next value from the shared IntelLabDataReader and emits a
    reading dict. Subclasses implement the actual transport in `emit(reading)`.
    """

    def __init__(self, reader: IntelLabDataReader, config: DeviceConfig):
        super().__init__(daemon=True)
        self.reader = reader
        self.config = config
        self._stop_evt = threading.Event()
        self._k = 0  # per-device local cursor

    # ---- identity ----
    @property
    def unique_id(self) -> str:
        # Composite "type_deviceid", e.g., "humidity_3"
        return f"{self.config.sensor}_{self.config.device_id}"

    # ---- life cycle ----
    def stop(self) -> None:
        self._stop_evt.set()

    def stopped(self) -> bool:
        return self._stop_evt.is_set()

    # ---- reading with per-device offset ----
    def _next_value(self) -> float:
        n = self.reader.get_length(self.config.sensor)
        start = (self.config.device_id * self.config.offset_step) % n
        idx = (start + self._k) % n
        self._k += 1
        return self.reader.get_by_index(self.config.sensor, idx)

    def build_reading(self, protocol: str) -> dict:
        return {
            "device_id": self.unique_id,  # composite id
            "protocol": protocol,
            "timestamp": datetime.utcnow().isoformat(),
            "sensor": self.config.sensor,
            "value": self._next_value(),
        }

    # ---- transport hook ----
    def emit(self, reading: dict) -> None:  # pragma: no cover
        raise NotImplementedError

    def run(self) -> None:  # pragma: no cover - overridden in subclasses for clarity
        while not self.stopped():
            reading = self.build_reading(protocol="base")
            self.emit(reading)
            if self._stop_evt.wait(self.config.period_s):
                break
