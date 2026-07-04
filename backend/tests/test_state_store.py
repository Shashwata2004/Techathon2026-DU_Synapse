from dataclasses import replace
from datetime import datetime, time, timedelta

from app.config import settings
from app.state_store import StateStore


def test_initializes_exactly_15_devices() -> None:
    store = StateStore(replace(settings, simulation_enabled=False))
    state = store.get_state()

    assert state.total_device_count == 15
    assert len(state.rooms) == 3
    for room in state.rooms:
      assert len(room.devices) == 5
      assert sum(1 for device in room.devices if device.type == "fan") == 2
      assert sum(1 for device in room.devices if device.type == "light") == 3


def test_power_usage_matches_device_states() -> None:
    store = StateStore(replace(settings, simulation_enabled=False))
    store.set_device("drawing-room-fan-1", "ON")
    state = store.set_device("drawing-room-light-1", "ON")

    assert state.total_current_watts == 75
    assert state.room_wise_power["Drawing Room"] == 75
    assert state.active_device_count == 2


def test_on_since_and_last_changed_follow_status_changes() -> None:
    store = StateStore(replace(settings, simulation_enabled=False))
    initial = next(device for device in store.get_devices() if device.id == "drawing-room-fan-1")
    initial_changed = initial.last_changed

    turned_on = store.set_device("drawing-room-fan-1", "ON")
    device = next(device for device in turned_on.devices if device.id == "drawing-room-fan-1")
    assert device.on_since is not None
    assert device.current_power == 60
    assert device.last_changed >= initial_changed

    unchanged = store.set_device("drawing-room-fan-1", "ON")
    same_device = next(device for device in unchanged.devices if device.id == "drawing-room-fan-1")
    assert same_device.last_changed == device.last_changed

    turned_off = store.set_device("drawing-room-fan-1", "OFF")
    off_device = next(device for device in turned_off.devices if device.id == "drawing-room-fan-1")
    assert off_device.on_since is None
    assert off_device.current_power == 0


def test_noop_device_set_does_not_advance_revision() -> None:
    store = StateStore(replace(settings, simulation_enabled=False))
    initial_revision = store.revision

    store.set_device("drawing-room-fan-1", "OFF")
    assert store.revision == initial_revision

    store.set_device("drawing-room-fan-1", "ON")
    assert store.revision == initial_revision + 1


def test_room_aliases_work() -> None:
    store = StateStore(replace(settings, simulation_enabled=False))

    assert store.get_room("drawing").id == "drawing-room"
    assert store.get_room("work1").id == "work-room-1"
    assert store.get_room("work2").id == "work-room-2"


def test_usage_reports_all_highest_rooms_on_tie() -> None:
    store = StateStore(replace(settings, simulation_enabled=False))
    store.set_device("drawing-room-fan-1", "ON")
    store.set_device("work-room-1-fan-1", "ON")

    usage = store.get_usage()

    assert usage.highest_room == "Drawing Room"
    assert usage.highest_rooms == ["Drawing Room", "Work Room 1"]


def test_usage_has_no_highest_room_when_all_rooms_are_zero() -> None:
    store = StateStore(replace(settings, simulation_enabled=False))

    usage = store.get_usage()

    assert usage.highest_room is None
    assert usage.highest_rooms == []


def test_state_includes_simulator_metadata() -> None:
    store = StateStore(replace(settings, simulation_enabled=True, simulation_interval_seconds=25))
    state = store.get_state()

    assert state.simulator_status.enabled is True
    assert state.simulator_status.interval_seconds == 25


def test_device_changes_are_recorded_in_event_log() -> None:
    store = StateStore(replace(settings, simulation_enabled=False))
    state = store.set_device("drawing-room-fan-1", "ON", source="manual")

    assert len(state.events) == 1
    assert state.events[0].type == "device_change"
    assert state.events[0].device_id == "drawing-room-fan-1"
    assert state.events[0].status == "ON"


def test_simulator_status_can_change_at_runtime() -> None:
    store = StateStore(replace(settings, simulation_enabled=True, simulation_interval_seconds=25))
    state = store.set_simulator_enabled(False, source="manual")

    assert state.simulator_status.enabled is False
    assert state.events[0].type == "simulator"
    assert "OFF" in state.events[0].message


def test_after_hours_alert_is_duplicate_safe() -> None:
    always_after_hours = replace(
        settings,
        simulation_enabled=False,
        office_hours_start=time(0, 0),
        office_hours_end=time(0, 0),
    )
    store = StateStore(always_after_hours)

    first = store.set_device("work-room-2-fan-1", "ON")
    second = store.set_device("work-room-2-light-1", "ON")

    assert len(first.active_alerts) == 1
    assert len(second.active_alerts) == 1
    assert second.active_alerts[0].id == "alert-work-room-2-after-hours"


def test_room_all_on_over_two_hours_alert() -> None:
    office_hours_all_day = replace(
        settings,
        simulation_enabled=False,
        office_hours_start=time(0, 0),
        office_hours_end=time(23, 59),
    )
    store = StateStore(office_hours_all_day)
    store.set_room_status("drawing-room", "ON")

    now = datetime.now().astimezone()
    for device in store._devices.values():
        if device.room_id == "drawing-room":
            device.on_since = now - timedelta(hours=3)

    store._evaluate_alerts(now)
    state = store.get_state()

    assert any(alert.id == "alert-drawing-room-all-on-2h" for alert in state.active_alerts)
