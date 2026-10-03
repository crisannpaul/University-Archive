import json
import time
from typing import Optional

import pika

from device.base_device import BaseDevice


class MqttDevice(BaseDevice):
    """
    Device that publishes readings to RabbitMQ using AMQP.
    We keep the JSON schema identical to the previous MQTT version.
    """

    def __init__(
        self,
        device_id: str,
        sensor_name: str,
        reader,
        shard_len: int = 300,
        period_s: float = 1.0,
        host: str = "localhost",
        port: int = 5672,
        username: str = "guest",
        password: str = "guest",
        exchange: str = "iot",
        routing_key: Optional[str] = None,
    ):
        super().__init__(
            device_id=device_id,
            protocol_name="mqtt",   # logically still "mqtt" if you want; change to "amqp" if you prefer
            sensor_name=sensor_name,
            reader=reader,
            shard_len=shard_len,
            sampling_interval=period_s,
        )

        self.period_s = period_s
        self.exchange = exchange
        self.routing_key = routing_key or f"iot.{device_id}"

        creds = pika.PlainCredentials(username, password)
        params = pika.ConnectionParameters(host=host, port=port, credentials=creds)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()

        # topic-style exchange: iot.<device_id>
        self.channel.exchange_declare(exchange=self.exchange, exchange_type="topic", durable=False)

    def run(self):
        """
        Loop that periodically generates readings and publishes to RabbitMQ.
        """
        try:
            while True:
                value = self._next_value()
                message = self._make_message(value)
                payload = json.dumps(message)

                try:
                    self.channel.basic_publish(
                        exchange=self.exchange,
                        routing_key=self.routing_key,
                        body=payload.encode("utf-8"),
                    )
                    # print(f"[RabbitMQ] {self.device_id} → {self.routing_key}: {payload}")
                except Exception as e:
                    print(f"[RabbitMQ DEVICE {self.device_id}] Error: {e}")

                time.sleep(self.period_s)
        finally:
            try:
                self.connection.close()
            except Exception:
                pass
