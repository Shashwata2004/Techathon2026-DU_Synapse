from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from threading import RLock

from .alerts import evaluate_alerts
from .config import Settings, settings
from .models import Alert, Device, DeviceStatus, Room, SystemState, UsageResponse
from .usage import calculate_incremental_kwh


ROOMS = [
    ("drawing-room", "Drawing Room", "Waiting area"),
    ("work-room-1", "Work Room 1", "Employee workspace"),
    ("work-room-2", "Work Room 2", "Employee workspace"),
]

ROOM_ALIASES = {
    "drawing": "drawing-room",
    "drawing-room": "drawing-room",
    "drawing room": "drawing-room",
    "work1": "work-room-1",
    "work-room-1": "work-room-1",
    "work room 1": "work-room-1",
    "work2": "work-room-2",
    "work-room-2": "work-room-2",
    "work room 2": "work-room-2",
}


class StateStore:
    def __init__(self, app_settings: Settings = settings) -> None:
        self.settings = app_settings
        self._lock = RLock()
        self._devices: dict[str, Device] = {}
        self._active_alerts: dict[str, Alert] = {}
        self._recent_alerts: list[Alert] = []
        self._estimated_kwh_today = 0.0
        self._last_energy_update = self._now()
        self._last_updated = self._last_energy_update
        self._force_after_hours_alert = False
        self._revision = 0
        self.reset()

    def reset(self) -> SystemState:
        with self._lock:
            now = self._now()
            self._devices = {}
            self._active_alerts = {}
            self._recent_alerts = []
            self._estimated_kwh_today = 0.0
            self._last_energy_update = now
            self._last_updated = now
            self._force_after_hours_alert = False
            self._revision = 0

            for room_id, room_name, _purpose in ROOMS:
                for index in range(1, 3):
                    self._create_device(room_id, room_name, "fan", index, 60, now)
                for index in range(1, 4):
                    self._create_device(room_id, room_name, "light", index, 15, now)

            self._evaluate_alerts(now)
            self._revision += 1
            return self.get_state()

    @property
    def revision(self) -> int:
        with self._lock:
            return self._revision

    def get_state(self) -> SystemState:
        with self._lock:
            devices = list(self._devices.values())
            rooms = self._build_rooms()
            total_current_watts = sum(device.current_power for device in devices)
            room_wise_power = {room.name: room.current_power for room in rooms}
            active_device_count = sum(1 for device in devices if device.status == "ON")
            return SystemState(
                rooms=rooms,
                devices=devices,
                totalCurrentWatts=total_current_watts,
                roomWisePower=room_wise_power,
                estimatedKwhToday=round(self._estimated_kwh_today, 3),
                activeAlerts=list(self._active_alerts.values()),
                recentAlerts=self._recent_alerts,
                activeDeviceCount=active_device_count,
                totalDeviceCount=len(devices),
                lastUpdated=self._last_updated,
            )

    def get_devices(self) -> list[Device]:
        return self.get_state().devices

    def get_rooms(self) -> list[Room]:
        return self.get_state().rooms

    def get_room(self, room_alias: str) -> Room:
        room_id = self.resolve_room_id(room_alias)
        for room in self.get_rooms():
            if room.id == room_id:
                return room
        raise KeyError(room_alias)

    def get_usage(self) -> UsageResponse:
        state = self.get_state()
        highest_room = None
        if state.room_wise_power:
            highest_room = max(state.room_wise_power, key=state.room_wise_power.get)
        return UsageResponse(
            totalCurrentWatts=state.total_current_watts,
            roomWisePower=state.room_wise_power,
            estimatedKwhToday=state.estimated_kwh_today,
            activeDeviceCount=state.active_device_count,
            totalDeviceCount=state.total_device_count,
            highestRoom=highest_room,
        )

    def get_alerts(self) -> dict[str, list[Alert]]:
        state = self.get_state()
        return {"activeAlerts": state.active_alerts, "recentAlerts": state.recent_alerts}

    def toggle_device(self, device_id: str) -> SystemState:
        with self._lock:
            device = self._get_device(device_id)
            next_status: DeviceStatus = "OFF" if device.status == "ON" else "ON"
            return self.set_device(device_id, next_status)

    def set_device(self, device_id: str, status: DeviceStatus) -> SystemState:
        with self._lock:
            device = self._get_device(device_id)
            if device.status == status:
                return self.get_state()

            now = self._prepare_update()
            device.status = status
            device.current_power = device.wattage if status == "ON" else 0
            device.last_changed = now
            device.on_since = now if status == "ON" else None
            return self._finish_update(now, changed=True)

    def set_room_status(self, room_alias: str, status: DeviceStatus) -> SystemState:
        with self._lock:
            room_id = self.resolve_room_id(room_alias)
            changed = any(device.room_id == room_id and device.status != status for device in self._devices.values())
            if not changed:
                return self.get_state()

            now = self._prepare_update()
            for device in self._devices.values():
                if device.room_id == room_id and device.status != status:
                    device.status = status
                    device.current_power = device.wattage if status == "ON" else 0
                    device.last_changed = now
                    device.on_since = now if status == "ON" else None
            return self._finish_update(now, changed=True)

    def trigger_after_hours_alert(self) -> SystemState:
        with self._lock:
            changed = not self._force_after_hours_alert
            self._force_after_hours_alert = True
            before_revision = self._revision
            state = self.set_room_status("work-room-2", "ON")
            if self._revision == before_revision and changed:
                now = self._prepare_update()
                return self._finish_update(now, changed=True)
            return state

    def resolve_room_id(self, room_alias: str) -> str:
        normalized = room_alias.strip().lower()
        if normalized in ROOM_ALIASES:
            return ROOM_ALIASES[normalized]
        raise KeyError(room_alias)

    def _create_device(
        self,
        room_id: str,
        room_name: str,
        device_type: str,
        index: int,
        wattage: int,
        now: datetime,
    ) -> None:
        name = f"{device_type.capitalize()} {index}"
        device_id = f"{room_id}-{device_type}-{index}"
        self._devices[device_id] = Device(
            id=device_id,
            name=name,
            roomId=room_id,
            roomName=room_name,
            type=device_type,
            status="OFF",
            wattage=wattage,
            currentPower=0,
            lastChanged=now,
            onSince=None,
        )

    def _build_rooms(self) -> list[Room]:
        devices_by_room: dict[str, list[Device]] = defaultdict(list)
        for device in self._devices.values():
            devices_by_room[device.room_id].append(device)

        rooms = []
        for room_id, room_name, purpose in ROOMS:
            room_devices = sorted(devices_by_room[room_id], key=lambda device: (device.type, device.name))
            room_alerts = [alert for alert in self._active_alerts.values() if alert.room_id == room_id]
            rooms.append(
                Room(
                    id=room_id,
                    name=room_name,
                    purpose=purpose,
                    devices=room_devices,
                    fansOn=sum(1 for device in room_devices if device.type == "fan" and device.status == "ON"),
                    lightsOn=sum(1 for device in room_devices if device.type == "light" and device.status == "ON"),
                    currentPower=sum(device.current_power for device in room_devices),
                    activeAlerts=room_alerts,
                )
            )
        return rooms

    def _prepare_update(self) -> datetime:
        now = self._now()
        current_total = sum(device.current_power for device in self._devices.values())
        self._estimated_kwh_today += calculate_incremental_kwh(current_total, self._last_energy_update, now)
        self._last_energy_update = now
        return now

    def _finish_update(self, now: datetime, changed: bool) -> SystemState:
        before_alerts = self._alert_signature()
        self._evaluate_alerts(now)
        alerts_changed = before_alerts != self._alert_signature()
        if changed or alerts_changed:
            self._last_updated = now
            self._revision += 1
        return self.get_state()

    def _evaluate_alerts(self, now: datetime) -> None:
        devices_by_room: dict[str, list[Device]] = defaultdict(list)
        for device in self._devices.values():
            devices_by_room[device.room_id].append(device)
        evaluate_alerts(
            dict(devices_by_room),
            self._active_alerts,
            self._recent_alerts,
            now,
            self.settings,
            force_after_hours_alert=self._force_after_hours_alert,
        )

    def _get_device(self, device_id: str) -> Device:
        if device_id not in self._devices:
            raise KeyError(device_id)
        return self._devices[device_id]

    def _alert_signature(self) -> tuple[tuple[str, str, tuple[str, ...]], ...]:
        return tuple(
            sorted(
                (alert.id, alert.message, tuple(alert.affected_devices))
                for alert in self._active_alerts.values()
            )
        )

    @staticmethod
    def _now() -> datetime:
        return datetime.now().astimezone()
