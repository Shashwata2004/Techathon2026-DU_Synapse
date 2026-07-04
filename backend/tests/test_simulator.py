import asyncio
from dataclasses import replace

from app.config import settings
from app.simulator import DeviceSimulator
from app.state_store import StateStore


def test_simulator_toggles_exactly_one_device_and_publishes(monkeypatch) -> None:
    store = StateStore(replace(settings, simulation_enabled=True, simulation_interval_seconds=30))
    published = 0

    async def publish_state() -> None:
        nonlocal published
        published += 1

    first_device = store.get_devices()[0]
    first_device_last_changed = first_device.last_changed
    monkeypatch.setattr("app.simulator.random.choice", lambda devices: first_device)
    simulator = DeviceSimulator(store, interval_seconds=30, publish_state=publish_state)

    before = {device.id: device.status for device in store.get_devices()}
    changed = asyncio.run(simulator.simulate_once())
    after = {device.id: device.status for device in store.get_devices()}

    changed_devices = [device_id for device_id, status in before.items() if after[device_id] != status]
    updated_device = next(device for device in store.get_devices() if device.id == first_device.id)

    assert changed is True
    assert published == 1
    assert changed_devices == [first_device.id]
    assert updated_device.last_changed > first_device_last_changed
    assert updated_device.current_power == updated_device.wattage
