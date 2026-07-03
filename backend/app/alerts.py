from datetime import datetime, timedelta

from .config import Settings
from .models import Alert, Device


def _outside_office_hours(now: datetime, settings: Settings) -> bool:
    current = now.time()
    return current < settings.office_hours_start or current >= settings.office_hours_end


def _room_on_summary(devices: list[Device]) -> tuple[int, int]:
    fans_on = sum(1 for device in devices if device.type == "fan" and device.status == "ON")
    lights_on = sum(1 for device in devices if device.type == "light" and device.status == "ON")
    return fans_on, lights_on


def evaluate_alerts(
    rooms: dict[str, list[Device]],
    active_alerts: dict[str, Alert],
    recent_alerts: list[Alert],
    now: datetime,
    settings: Settings,
    force_after_hours_alert: bool = False,
) -> None:
    next_active_ids: set[str] = set()
    after_hours = _outside_office_hours(now, settings) or force_after_hours_alert

    for room_id, devices in rooms.items():
        room_name = devices[0].room_name
        on_devices = [device for device in devices if device.status == "ON"]

        if after_hours and on_devices:
            alert_id = f"alert-{room_id}-after-hours"
            next_active_ids.add(alert_id)
            fans_on, lights_on = _room_on_summary(on_devices)
            message = f"{room_name} has {fans_on} fans and {lights_on} lights ON after office hours."
            _upsert_alert(
                active_alerts,
                recent_alerts,
                Alert(
                    id=alert_id,
                    type="after_hours",
                    roomId=room_id,
                    message=message,
                    severity="warning",
                    createdAt=now,
                    affectedDevices=[device.id for device in on_devices],
                ),
            )

        room_all_on_since = [device.on_since for device in devices if device.status == "ON" and device.on_since]
        if len(room_all_on_since) == len(devices) and min(room_all_on_since) <= now - timedelta(hours=2):
            alert_id = f"alert-{room_id}-all-on-2h"
            next_active_ids.add(alert_id)
            _upsert_alert(
                active_alerts,
                recent_alerts,
                Alert(
                    id=alert_id,
                    type="room_all_on_2h",
                    roomId=room_id,
                    message=f"{room_name} has all devices ON for more than 2 hours.",
                    severity="warning",
                    createdAt=now,
                    affectedDevices=[device.id for device in devices],
                ),
            )

    for alert_id in list(active_alerts.keys()):
        if alert_id not in next_active_ids:
            alert = active_alerts.pop(alert_id)
            alert.active = False


def _upsert_alert(active_alerts: dict[str, Alert], recent_alerts: list[Alert], alert: Alert) -> None:
    existing = active_alerts.get(alert.id)
    if existing:
        existing.message = alert.message
        existing.affected_devices = alert.affected_devices
        return

    active_alerts[alert.id] = alert
    recent_alerts.insert(0, alert)
    del recent_alerts[20:]
