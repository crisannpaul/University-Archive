from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Any
import random
import time


class BaseDevice:
    """
    Base class for all simulated devices.
    Handles:
        - IDs
        - sensor names
        - shard loading
        - message creation
        - basic fault injection (failure, latency, packet "loss")
    """

    def __init__(
        self,
        device_id,
        protocol_name,
        sensor_name,
        reader,
        shard_len: int = 500,
        sampling_interval: float = 1.0,
    ):

        self.device_id = device_id
        self.protocol_name = protocol_name
        self.sensor_name = sensor_name

        self.reader = reader
        self.shard_len = shard_len
        self.sampling_interval = sampling_interval

        self.shard: Optional[Any] = None
        self.index: int = 0

        # ---- Fault simulation parameters ----
        # Device failure
        self._failure_prob = 0.05        # 5% chance per reading to trigger a failure episode
        self._failure_sleep_s = 10.0     # device "offline" for 10 seconds

        # Latency (applied per message in _make_message)
        # Example spec: LATENCY_RANGE = (10, 500) ms
        self._latency_range_ms = (10.0, 500.0)

        # Packet "loss" (we annotate the value instead of dropping the row)
        self._loss_rate = 0.10           # 10% of messages marked as lost
        self._loss_sentinel = 65534

    # ---------------------------------------------------------
    # Shard handling
    # ---------------------------------------------------------
    def _ensure_shard(self):
        """
        Fetches a new shard if:
            - no shard loaded
            - the shard has been fully consumed
        """
        if self.shard is None or self.index >= len(self.shard):
            self.shard = self.reader.get_shard(self.shard_len)
            self.index = 0

    def _next_value(self):
        """
        Gets the next sensor value from the shard.

        Also simulates temporary device failure:
          - with small probability, device "dies" for 10s
          - during that time, we skip ahead in the shard:
                skip_steps = failure_seconds / sampling_interval
        """
        self._ensure_shard()
        if self.shard is None:
            raise RuntimeError("Reader.get_shard(...) returned None; cannot fetch next value.")

        # --- simulate temporary failure BEFORE picking the next sample ---
        if random.random() < self._failure_prob:
            # device offline for a fixed duration
            sleep_s = self._failure_sleep_s
            time.sleep(sleep_s)

            # how many samples would we have missed?
            if self.sampling_interval > 0:
                skip_steps = int(sleep_s / self.sampling_interval)
            else:
                skip_steps = 0

            if skip_steps > 0:
                self.index += skip_steps
                # if we ran past the current shard, roll into a new shard and
                # carry over any extra offset
                if self.index >= len(self.shard):
                    extra = self.index - len(self.shard)
                    self.shard = self.reader.get_shard(self.shard_len)
                    # clamp extra inside new shard bounds
                    if extra >= len(self.shard):
                        extra = len(self.shard) - 1
                    self.index = max(0, extra)

        # ensure we still have a valid shard/index after possible skip
        self._ensure_shard()
        if self.shard is None:
            raise RuntimeError("Reader.get_shard(...) returned None after failure simulation.")

        # now actually take the next value
        row = self.shard.iloc[self.index]
        self.index += 1
        return float(row[self.sensor_name])

    # ---------------------------------------------------------
    # Message formatting + latency + packet "loss"
    # ---------------------------------------------------------
    def _make_message(self, value):
        """
        Builds the standardized message format AND simulates:
          - Random latency: sleep between LATENCY_RANGE ms
          - Random packet loss: mark value as sentinel with probability LOSS_RATE

        The gateway will add delivered_timestamp; here we only set produced timestamp.
        """
        # produced timestamp (when the device "creates" the reading)
        produced_ts = datetime.now(timezone.utc).isoformat()

        # ---- packet "loss" simulation ----
        # Instead of dropping the row entirely, we annotate the value with a sentinel.
        if random.random() < self._loss_rate:
            value_to_send = self._loss_sentinel
        else:
            value_to_send = value

        # ---- latency simulation ----
        # Sleep for a random time in the configured range (ms → s)
        if self._latency_range_ms is not None:
            lo, hi = self._latency_range_ms
            if hi > 0:
                delay_ms = random.uniform(lo, hi)
                time.sleep(delay_ms / 1000.0)

        return {
            "device_id": self.device_id,
            "protocol": self.protocol_name,
            "timestamp": produced_ts,      # produced_timestamp
            "sensor": self.sensor_name,
            "value": value_to_send,
        }

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------
    def generate(self):
        """
        Reads a value, forms message, and publishes.
        Overridden by child classes because each protocol
        has its own publishing mechanism.
        """
        raise NotImplementedError("Child class must implement generate().")
