# consumer.py
"""
Unified consumer for IoT readings + Prometheus metrics:
- HTTP mode: exposes /ingest (POST) and appends to readings_http.csv
- MQTT mode: subscribes to a topic and appends to readings_mqtt.csv
- Prometheus metrics on :9090 at /metrics and /actuator/prometheus

Install:
  pip install flask paho-mqtt prometheus-client

Run (HTTP):
  python consumer.py --mode http --http-port 8000 --http-csv readings_http.csv

Run (MQTT):
  python consumer.py --mode mqtt --mqtt-broker localhost --mqtt-topic sensors/readings --mqtt-csv readings_mqtt.csv

Run (both):
  python consumer.py --mode both --http-port 8000 --mqtt-broker localhost
"""

import argparse
import csv
import json
import os
import queue
import signal
import sys
import threading
import time
from datetime import datetime

from flask import Flask, request, jsonify, Response
from paho.mqtt import client as mqtt

# ---- Prometheus
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    CONTENT_TYPE_LATEST,
    generate_latest,
)

# -----------------------------
# Prometheus metrics
# -----------------------------
INGEST_TOTAL = Counter(
    "consumer_ingest_total",
    "Total ingested messages",
    ["protocol", "sensor"],
)

INGEST_LATENCY = Histogram(
    "consumer_ingest_latency_seconds",
    "Ingest path latency seconds",
    ["protocol"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5),
)

LAST_VALUE = Gauge(
    "consumer_last_value",
    "Last observed sensor value",
    ["protocol", "sensor", "device_id"],
)

LAST_TS = Gauge(
    "consumer_last_timestamp_seconds",
    "Last observed sensor timestamp (epoch seconds)",
    ["protocol", "sensor"],
)

QUEUE_SIZE = Gauge(
    "consumer_inflight_queue_size",
    "Message queue size",
    ["protocol"],
)


def _to_epoch(ts: str | None) -> float:
    if not ts:
        return time.time()
    try:
        return datetime.fromisoformat(ts).timestamp()
    except Exception:
        return time.time()


# -----------------------------
# CSV writer (background-drained)
# -----------------------------
CSV_FIELDS = ["device_id", "protocol", "timestamp", "sensor", "value"]


class CsvWriter:
    def __init__(self, path: str):
        self.path = path
        self._lock = threading.Lock()
        # Create parent dirs if needed
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self._file = open(self.path, "a", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._file, fieldnames=CSV_FIELDS)
        # Write header only if file is new/empty
        if os.stat(self.path).st_size == 0:
            self._writer.writeheader()
            self._file.flush()

    def write(self, row: dict):
        with self._lock:
            self._writer.writerow({k: row.get(k, "") for k in CSV_FIELDS})
            self._file.flush()

    def close(self):
        try:
            self._file.close()
        except Exception:
            pass


class Sink:
    """Two queues (http/mqtt) + background drainers → separate CSVs."""

    def __init__(self, http_csv: str, mqtt_csv: str):
        self._stop = threading.Event()
        self._queues = {"http": queue.Queue(maxsize=10000), "mqtt": queue.Queue(maxsize=10000)}
        self._writers = {
            "http": CsvWriter(http_csv),
            "mqtt": CsvWriter(mqtt_csv),
        }
        self._threads = []
        for proto in ("http", "mqtt"):
            t = threading.Thread(target=self._drain, args=(proto,), daemon=True)
            t.start()
            self._threads.append(t)

    def submit(self, proto: str, reading: dict):
        # normalize protocol field to the channel we're writing to
        reading = dict(reading)
        reading["protocol"] = proto
        try:
            self._queues[proto].put(reading, timeout=2.0)
        except queue.Full:
            # Backpressure handling – drop oldest to make room
            try:
                self._queues[proto].get_nowait()
                self._queues[proto].put_nowait(reading)
            except Exception:
                # If we still can't enqueue, log & drop
                print(f"[SINK] Dropped reading due to full queue ({proto}).", file=sys.stderr)
        finally:
            # Update queue size metric
            try:
                QUEUE_SIZE.labels(protocol=proto).set(self._queues[proto].qsize())
            except Exception:
                pass

    def _drain(self, proto: str):
        q = self._queues[proto]
        w = self._writers[proto]
        while not self._stop.is_set():
            try:
                row = q.get(timeout=0.5)
            except queue.Empty:
                continue
            try:
                w.write(row)
            except Exception as e:
                print(f"[SINK] Failed to write {proto} row: {e}", file=sys.stderr)

    def close(self):
        self._stop.set()
        for t in self._threads:
            t.join(timeout=2.0)
        for w in self._writers.values():
            w.close()


# -----------------------------
# HTTP mode (Flask)
# -----------------------------
def make_http_app(sink: Sink):
    app = Flask("consumer-http")

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"ok": True, "time": datetime.utcnow().isoformat()}), 200

    @app.route("/ingest", methods=["POST"])
    def ingest():
        start = time.perf_counter()
        try:
            reading = request.get_json(force=True, silent=False)
            if not isinstance(reading, dict):
                raise ValueError("Body must be a JSON object.")
            # Minimal validation
            for key in ("device_id", "timestamp", "sensor", "value"):
                if key not in reading:
                    raise ValueError(f"Missing field: {key}")

            # Metrics
            sensor = str(reading["sensor"])
            device_id = str(reading["device_id"])
            value = float(reading["value"])
            ts_epoch = _to_epoch(reading.get("timestamp"))

            INGEST_TOTAL.labels(protocol="http", sensor=sensor).inc()
            LAST_VALUE.labels(protocol="http", sensor=sensor, device_id=device_id).set(value)
            LAST_TS.labels(protocol="http", sensor=sensor).set(ts_epoch)

            sink.submit("http", reading)
            return "", 204
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        finally:
            try:
                INGEST_LATENCY.labels(protocol="http").observe(time.perf_counter() - start)
            except Exception:
                pass

    return app


# -----------------------------
# MQTT mode (paho-mqtt)
# -----------------------------
class MqttConsumer:
    def __init__(self, sink: Sink, broker: str, port: int, topic: str, client_id: str | None = None, keepalive: int = 60, qos: int = 0):
        self.sink = sink
        self.topic = topic
        self.qos = qos
        self.client = mqtt.Client(client_id or f"consumer_{int(time.time())}")
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.connect(broker, port, keepalive)

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"[MQTT] Connected. Subscribing to '{self.topic}' (qos={self.qos})")
            client.subscribe(self.topic, qos=self.qos)
        else:
            print(f"[MQTT] Connect failed with rc={rc}", file=sys.stderr)

    def _on_message(self, client, userdata, msg):
        start = time.perf_counter()
        try:
            payload = msg.payload.decode("utf-8", errors="replace")
            reading = json.loads(payload)
            if not isinstance(reading, dict):
                raise ValueError("Payload must be a JSON object.")
            # Minimal validation (same schema as HTTP)
            for key in ("device_id", "timestamp", "sensor", "value"):
                if key not in reading:
                    raise ValueError(f"Missing field: {key}")

            # Metrics
            sensor = str(reading["sensor"])
            device_id = str(reading["device_id"])
            value = float(reading["value"])
            ts_epoch = _to_epoch(reading.get("timestamp"))

            INGEST_TOTAL.labels(protocol="mqtt", sensor=sensor).inc()
            LAST_VALUE.labels(protocol="mqtt", sensor=sensor, device_id=device_id).set(value)
            LAST_TS.labels(protocol="mqtt", sensor=sensor).set(ts_epoch)

            self.sink.submit("mqtt", reading)
        except Exception as e:
            print(f"[MQTT] Bad message on {msg.topic}: {e}", file=sys.stderr)
        finally:
            try:
                INGEST_LATENCY.labels(protocol="mqtt").observe(time.perf_counter() - start)
            except Exception:
                pass

    def start(self):
        self.client.loop_start()

    def stop(self):
        try:
            self.client.loop_stop()
            self.client.disconnect()
        except Exception:
            pass


# -----------------------------
# Metrics server (Flask on 9090)
# -----------------------------
def make_metrics_app():
    app = Flask("consumer-metrics")

    @app.route("/metrics", methods=["GET"])
    @app.route("/actuator/prometheus", methods=["GET"])  # compat with your previous config
    def metrics():
        data = generate_latest()
        return Response(data, mimetype=CONTENT_TYPE_LATEST)

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"ok": True, "time": datetime.utcnow().isoformat()}), 200

    return app
