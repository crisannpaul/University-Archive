"""
IoT Device Simulation — shared Data Reader + HTTP & MQTT device classes

Usage
-----
1) Install deps:
   pip install pandas paho-mqtt requests

2) Download the Intel Berkeley Lab dataset text file (e.g., labdata.txt) from:
   https://db.csail.mit.edu/labdata/labdata.html

3) Run a collector (HTTP endpoint and/or MQTT broker), then start devices:
   python iot_devices_and_data_reader.py --data labdata.txt \
          --http COLLECTOR_URL --mqtt-broker localhost --mqtt-port 1883

This module provides:
- IntelLabDataReader: a thread-safe, middleman reader over the large dataset.
- BaseDevice: a common base for simulated devices with .start()/.stop()/.run().
- HttpDevice: posts readings to an HTTP collector.
- MqttDevice: publishes readings to an MQTT broker.

Design Highlights
-----------------
- Single dataset reader instance (shared by many devices) to avoid N devices each
  opening the 150MB file. The reader keeps an index per sensor type and returns
  the next value in a circular fashion (wrap-around when reaching the end).
- Thread-safe per-sensor locks ensure correctness under concurrency.
- Devices are threads (daemon) and can be started/stopped cleanly.
"""
from __future__ import annotations

import argparse
import json
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Optional

import pandas as pd
import requests
try:
    import paho.mqtt.client as mqtt
except Exception:  # pragma: no cover
    mqtt = None  # Allow running without MQTT installed


# -----------------------------
# Dataset Middleman / DataReader
# -----------------------------
class IntelLabDataReader:
    """Read-only intermediary to the Intel Berkeley Lab Sensor Data.

    The original text file is whitespace-delimited with columns commonly ordered as:
    date, time, epoch, moteid, temperature, humidity, light, voltage

    This reader exposes random-access by index for each sensor stream and does **not**
    keep shared cursors/locks. Concurrent reads are safe because the data is immutable.
    """

    COLUMN_NAMES = [
        "date", "time", "epoch", "moteid", "temperature", "humidity", "light", "voltage"
    ]

    SENSOR_COLUMNS = ("temperature", "humidity", "light", "voltage")

    def __init__(self, path: str, sensors: Iterable[str] = SENSOR_COLUMNS):
        self.path = path
        # Normalize sensor names (aliases)
        self._aliases = {
            "temp": "temperature",
            "temperature": "temperature",
            "humid": "humidity",
            "humidity": "humidity",
            "light": "light",
            "volt": "voltage",
            "voltage": "voltage",
        }
        self._data: Dict[str, pd.Series] = {}
        self._load(sensors)

    def _load(self, sensors: Iterable[str]) -> None:
        sensors = [self._aliases.get(s, s) for s in sensors]
        sensors = [s for s in dict.fromkeys(sensors) if s in self.SENSOR_COLUMNS]
        if not sensors:
            raise ValueError("No valid sensors requested.")

        # Map sensors to column indices for faster read_csv usecols
        col_indices = [self.COLUMN_NAMES.index(s) for s in sensors]

        # Read only the requested sensor columns, using regex separator for whitespace
        df = pd.read_csv(
            self.path,
            sep=r"\s+",
            header=None,
            names=self.COLUMN_NAMES,
            usecols=col_indices,
            engine="python",
            comment="#",
        )

        for s in sensors:
            series = pd.to_numeric(df[s], errors="coerce").dropna()
            if series.empty:
                raise ValueError(f"No data loaded for sensor '{s}'.")
            self._data[s] = series.reset_index(drop=True)

    def _norm_sensor(self, sensor: str) -> str:
        try:
            return self._aliases[sensor]
        except KeyError:
            if sensor in self.SENSOR_COLUMNS:
                return sensor
            raise KeyError(f"Unknown sensor '{sensor}'. Valid: {self.SENSOR_COLUMNS}")

    def get_by_index(self, sensor: str, idx: int) -> float:
        """Return value at absolute index (wrap-around)."""
        s = self._norm_sensor(sensor)
        series = self._data[s]
        return round(float(series.iat[idx % len(series)]), 2)

    def get_length(self, sensor: str) -> int:
        s = self._norm_sensor(sensor)
        return len(self._data[s])
