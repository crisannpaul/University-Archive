from dataclasses import dataclass

@dataclass
class DeviceConfig:
    device_id: int                 # integer id: 0,1,2,...
    sensor: str                    # 'temperature' | 'humidity' | 'light' | 'voltage'
    period_s: float = 2.0
    offset_step: int = 200         # starting offset per device: device_id * offset_step
