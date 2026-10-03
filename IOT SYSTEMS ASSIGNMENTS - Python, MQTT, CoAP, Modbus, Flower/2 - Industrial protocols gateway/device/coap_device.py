# device/coap_device.py
import asyncio
import json

from aiocoap import Context, Message, POST

from device.base_device import BaseDevice


class CoapDevice(BaseDevice):
    """
    CoAP device simulator.
    - Uses a DatasetReader (same as other devices).
    - Sends JSON readings via CoAP POST to /sensor.
    """

    def __init__(
        self,
        device_id: str,
        sensor_name: str,
        reader,
        shard_len: int = 300,
        period_s: float = 2.0,
        uri: str = "coap://localhost/sensor",
    ):
        super().__init__(
            device_id=device_id,
            protocol_name="coap",
            sensor_name=sensor_name,
            reader=reader,
            shard_len=shard_len,
            sampling_interval=period_s,
        )
        self.period_s = period_s
        self.uri = uri

    async def _run_async(self):
        protocol = await Context.create_client_context()
        await asyncio.sleep(1)  # give server time

        while True:
            value = self._next_value()
            message = self._make_message(value)  # includes device_id, protocol, timestamp, sensor, value

            payload = json.dumps(message).encode("utf-8")
            request = Message(code=POST, uri=self.uri, payload=payload)

            try:
                response = await protocol.request(request).response
                # print(f"[CoAP Device {self.device_id}] Response: {response.payload.decode('utf-8', errors='replace')}")
            except Exception as e:
                print(f"[CoAP Device {self.device_id}] Send failed: {e}")

            await asyncio.sleep(self.period_s)

    def run(self):
        """
        Entry point for running in a thread.
        """
        asyncio.run(self._run_async())
