import asyncio
import random
from collections.abc import Awaitable, Callable

from .state_store import StateStore


StatePublisher = Callable[[], Awaitable[None]]


class DeviceSimulator:
    def __init__(self, store: StateStore, interval_seconds: int, publish_state: StatePublisher) -> None:
        self.store = store
        self.interval_seconds = interval_seconds
        self.publish_state = publish_state
        self._running = False

    async def run(self) -> None:
        self._running = True
        while self._running:
            await asyncio.sleep(self.interval_seconds)
            devices = self.store.get_devices()
            if not devices:
                continue

            sample_size = 1 if random.random() < 0.8 else 2
            for device in random.sample(devices, k=min(sample_size, len(devices))):
                self.store.toggle_device(device.id)
            await self.publish_state()

    def stop(self) -> None:
        self._running = False
