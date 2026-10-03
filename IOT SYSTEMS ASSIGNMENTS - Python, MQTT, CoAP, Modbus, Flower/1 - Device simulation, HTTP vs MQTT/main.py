# main.py
"""
Main orchestrator (single mode):
- mode: 'http' OR 'mqtt' (run only one type at a time)
- num_devices: how many devices of that type
- period_s: per-device reading frequency
- offset_step: start offset = device_id * offset_step
- Hardcoded infra: paths, ports, URLs, topics
- Exposes Prometheus metrics on :9090 (/metrics and /actuator/prometheus)
"""

import random
import threading
import time
from dataclasses import dataclass
from typing import Literal

from device.base_device import BaseDevice
from device.config import DeviceConfig
from device.http_device import HttpDevice
from device.mqtt_device import MqttDevice
from dataio.data_reader import IntelLabDataReader

from consumer import (
    make_http_app,
    MqttConsumer,
    Sink,
    make_metrics_app,   # <— add this import
)

# === Hardcoded infrastructure (no CLI/flags) ===
DATA_PATH = "data.txt"                 # path to Intel Berkeley Lab dataset
HTTP_HOST = "0.0.0.0"
HTTP_PORT = 8000
HTTP_INGEST_URL = f"http://localhost:{HTTP_PORT}/ingest"
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "sensors/readings"

HTTP_CSV = "readings_http.csv"
MQTT_CSV = "readings_mqtt.csv"

# Prometheus metrics endpoint
METRICS_HOST = "0.0.0.0"
METRICS_PORT = 9090

# Round-robin across sensor types when we create devices
SENSORS = ["temperature", "humidity", "light", "voltage"]


@dataclass
class AppConfig:
    mode: Literal["http", "mqtt"] = "http"  # run only one type at a time
    num_devices: int = 4
    period_s: float = 2.0                   # reading frequency per device
    offset_step: int = 200                  # per-device start offset = device_id * step


class SimulationApp:
    def __init__(self, cfg: AppConfig):
        self.cfg = cfg
        self.reader = IntelLabDataReader(DATA_PATH, sensors=SENSORS)
        self.sink = Sink(http_csv=HTTP_CSV, mqtt_csv=MQTT_CSV)

        # Only one of these is used depending on mode
        self._http_thread: threading.Thread | None = None
        self._mqtt_consumer: MqttConsumer | None = None

        # Metrics thread
        self._metrics_thread: threading.Thread | None = None

        # Device threads
        self._devices: list[BaseDevice] = []

        # For shutdown
        self._stop_evt = threading.Event()

    # ---------- metrics ----------
    def start_metrics(self):
        mapp = make_metrics_app()

        def _run_metrics():
            # expose /metrics and /actuator/prometheus
            mapp.run(host=METRICS_HOST, port=METRICS_PORT, threaded=True)

        self._metrics_thread = threading.Thread(target=_run_metrics, daemon=True)
        self._metrics_thread.start()
        print(f"[METRICS] Exposed on http://{METRICS_HOST}:{METRICS_PORT}/metrics (and /actuator/prometheus)")

    # ---------- consumer ----------
    def start_consumer(self):
        if self.cfg.mode == "http":
            app = make_http_app(self.sink)

            def _run_http():
                # threaded=True lets Flask handle multiple posts concurrently
                app.run(host=HTTP_HOST, port=HTTP_PORT, threaded=True)

            self._http_thread = threading.Thread(target=_run_http, daemon=True)
            self._http_thread.start()
            print(f"[HTTP] Listening on http://{HTTP_HOST}:{HTTP_PORT}/ingest  → {HTTP_CSV}")

        elif self.cfg.mode == "mqtt":
            try:
                self._mqtt_consumer = MqttConsumer(
                    sink=self.sink,
                    broker=MQTT_BROKER,
                    port=MQTT_PORT,
                    topic=MQTT_TOPIC,
                    client_id=None,
                    keepalive=60,
                    qos=0,
                )
                self._mqtt_consumer.start()
                print(f"[MQTT] Subscribed to {MQTT_BROKER}:{MQTT_PORT} topic '{MQTT_TOPIC}' → {MQTT_CSV}")
            except Exception as e:
                print(f"[MQTT] Could not connect to broker at {MQTT_BROKER}:{MQTT_PORT}: {e}")
                raise SystemExit(1)

    # ---------- devices ----------
    def build_devices(self):
        self._devices = []
        if self.cfg.mode == "http":
            for i in range(self.cfg.num_devices):
                sensor = SENSORS[i % len(SENSORS)]
                dcfg = DeviceConfig(
                    device_id=i,
                    sensor=sensor,
                    period_s=self.cfg.period_s,
                    offset_step=self.cfg.offset_step,
                )
                dev = HttpDevice(self.reader, dcfg, collector_url=HTTP_INGEST_URL)
                self._devices.append(dev)
        else:  # mqtt
            for i in range(self.cfg.num_devices):
                sensor = SENSORS[i % len(SENSORS)]
                dcfg = DeviceConfig(
                    device_id=i,
                    sensor=sensor,
                    period_s=self.cfg.period_s,
                    offset_step=self.cfg.offset_step,
                )
                dev = MqttDevice(
                    self.reader,
                    dcfg,
                    broker=MQTT_BROKER,
                    port=MQTT_PORT,
                    topic=MQTT_TOPIC,
                )
                self._devices.append(dev)

    def start_devices(self):
        for dev in self._devices:
            dev.start()
            print(f"[DEVICE] started {dev.__class__.__name__} id={getattr(dev, 'unique_id', '?')}")
            time.sleep(random.uniform(0.5, 1.5))  # staggered start

    # ---------- lifecycle ----------
    def run(self):
        print(f"[MAIN] Starting in '{self.cfg.mode}' mode with {self.cfg.num_devices} device(s).")
        self.start_metrics()     # <— start Prometheus endpoint
        self.start_consumer()
        self.build_devices()
        self.start_devices()
        print("[MAIN] All devices started. Press Ctrl+C to stop.")
        try:
            while not self._stop_evt.is_set():
                time.sleep(1.0)
        except KeyboardInterrupt:
            print("\n[MAIN] Shutdown requested.")
            self.stop()

    def stop(self):
        self._stop_evt.set()
        # stop devices
        for dev in self._devices:
            if hasattr(dev, "stop"):
                dev.stop()
        for dev in self._devices:
            try:
                dev.join(timeout=3.0)
            except Exception:
                pass
        # stop consumers
        if self.cfg.mode == "mqtt" and self._mqtt_consumer:
            try:
                self._mqtt_consumer.stop()
            except Exception:
                pass
        # Sink/CSV
        try:
            self.sink.close()
        except Exception:
            pass
        print("[MAIN] Stopped cleanly.")


if __name__ == "__main__":
    # Switch 'mode' between 'http' and 'mqtt' to run one type at a time.
    cfg = AppConfig(
        mode="http",       # 'http' or 'mqtt'
        num_devices=4,
        period_s=2.0,
        offset_step=200,   # increase if you want less cross-device overlap
    )
    app = SimulationApp(cfg)
    app.run()
