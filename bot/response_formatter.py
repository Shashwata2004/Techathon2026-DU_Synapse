from datetime import datetime


ROOM_ALIASES = {
    "drawing": "drawing-room",
    "drawing-room": "drawing-room",
    "work1": "work-room-1",
    "work-room-1": "work-room-1",
    "work2": "work-room-2",
    "work-room-2": "work-room-2",
}

DEVICE_ALIASES = {
    "fan1": "fan-1",
    "fan-1": "fan-1",
    "fan2": "fan-2",
    "fan-2": "fan-2",
    "light1": "light-1",
    "light-1": "light-1",
    "light2": "light-2",
    "light-2": "light-2",
    "light3": "light-3",
    "light-3": "light-3",
}


def resolve_room_id(room_alias: str) -> str:
    normalized = room_alias.strip().lower()
    if normalized not in ROOM_ALIASES:
        raise ValueError("invalid_room")
    return ROOM_ALIASES[normalized]


def resolve_device_id(room_alias: str, device_alias: str) -> str:
    room_id = resolve_room_id(room_alias)
    normalized_device = device_alias.strip().lower()
    if normalized_device not in DEVICE_ALIASES:
        raise ValueError("invalid_device")
    return f"{room_id}-{DEVICE_ALIASES[normalized_device]}"


def format_help_text() -> str:
    return "\n".join(
        [
            "Smart Office Bot Commands:",
            "!status - Full office status",
            "!room <room> - Check one room",
            "!usage - Current power usage",
            "!alerts - Show active alerts",
            "!summary - Boss-friendly quick summary",
            "!waste <hours> - Estimate waste for a time period",
            "!recommend - Energy-saving recommendation",
            "!top - Highest consuming room(s)",
            "!toggle <room> <device> - Toggle one device",
            "!roomon <room> - Turn all devices in a room ON",
            "!roomoff <room> - Turn all devices in a room OFF",
            "!resetdemo - Reset demo state",
        ]
    )


def format_status(state: dict) -> str:
    lines = ["Here's the office status right now:"]
    for room in state["rooms"]:
        fans_on = room["fansOn"]
        lights_on = room["lightsOn"]
        if fans_on == 0 and lights_on == 0:
            summary = "all devices are OFF"
        else:
            summary = f"{fans_on} fan{'s' if fans_on != 1 else ''} ON, {lights_on} light{'s' if lights_on != 1 else ''} ON"
        lines.append(f"{room['name']}: {summary}.")
    lines.append(f"Current total usage: {state['totalCurrentWatts']}W.")
    return "\n".join(lines)


def format_room(room: dict) -> str:
    lines = [f"{room['name']} is currently using {room['currentPower']}W."]
    for device in room["devices"]:
        lines.append(f"{device['name']}: {device['status']} ({device['currentPower']}W)")
    if room["activeAlerts"]:
        lines.append("Active alert: " + room["activeAlerts"][0]["message"])
    return "\n".join(lines)


def format_usage(usage: dict) -> str:
    highest_text = _highest_usage_text(usage)
    return (
        f"Right now, the office is using {usage['totalCurrentWatts']}W.\n"
        f"Estimated usage today: {usage['estimatedKwhToday']:.3f} kWh.\n"
        f"{highest_text}\n"
        f"Active devices: {usage['activeDeviceCount']} / {usage['totalDeviceCount']}."
    )


def format_alerts(alerts_payload: dict) -> str:
    active_alerts = alerts_payload.get("activeAlerts", [])
    if not active_alerts:
        return "✅ No active alerts right now."

    lines = ["Active alerts:"]
    for alert in active_alerts:
        affected = alert.get("affectedDevices", [])
        affected_text = ", ".join(affected) if affected else "No devices listed"
        lines.append(
            f"- {room_name_from_id(alert.get('roomId'))}: {alert['message']}\n"
            f"  Devices: {affected_text}\n"
            f"  Time: {_format_time(alert.get('createdAt'))}"
        )
    return "\n".join(lines)


def format_alert(alert: dict) -> str:
    return format_proactive_alert(alert)


def format_proactive_alert(alert: dict) -> str:
    affected = alert.get("affectedDevices", [])
    affected_text = f" Affected: {', '.join(affected)}." if affected else ""
    return (
        f"⚠️ Hey! {alert['message']} Did someone forget to turn them off?"
        f"{affected_text} Time: {_format_time(alert.get('createdAt'))}."
    )


def format_summary(state: dict) -> str:
    highest_room_names, _highest_watts = _highest_rooms_from_state(state)
    highest_label = _join_names(highest_room_names) if highest_room_names else "None"
    return (
        "Office Summary:\n"
        f"{state['activeDeviceCount']} / {state['totalDeviceCount']} devices are ON.\n"
        f"Current usage: {state['totalCurrentWatts']}W.\n"
        f"Highest room{'s' if len(highest_room_names) > 1 else ''}: {highest_label}.\n"
        f"Alerts: {len(state['activeAlerts'])} active.\n"
        f"Estimated today: {state['estimatedKwhToday']:.3f} kWh."
    )


def format_waste(usage: dict, hours: float) -> str:
    total_watts = usage["totalCurrentWatts"]
    wasted_kwh = total_watts * hours / 1000
    hours_text = _format_number(hours)
    return (
        f"At the current {total_watts}W usage, if devices stay ON for "
        f"{hours_text} hour{'s' if hours != 1 else ''}, estimated waste is {wasted_kwh:.3f} kWh."
    )


def format_recommendation(state: dict) -> str:
    if state["activeDeviceCount"] == 0:
        return "The office is already efficient right now. All devices are OFF."

    if state["activeAlerts"]:
        rooms = sorted({room_name_from_id(alert.get("roomId")) for alert in state["activeAlerts"]})
        return "Fix alert rooms first: " + ", ".join(rooms) + "."

    highest_room_names, highest_watts = _highest_rooms_from_state(state)
    lights_on = sum(room["lightsOn"] for room in state["rooms"])
    lines = []
    if highest_room_names and highest_watts > 0:
        room_label = _join_names(highest_room_names)
        verb = "are" if len(highest_room_names) > 1 else "is"
        lines.append(f"Start with {room_label}; {verb} using {highest_watts}W.")
    if lights_on >= 4:
        lines.append(f"{lights_on} lights are ON, so turn off unused lights first.")
    if not lines:
        lines.append("Usage looks moderate. Turn off unused fans or lights before leaving.")
    return " ".join(lines)


def format_top(usage: dict) -> str:
    highest_rooms, watts = _highest_rooms_from_usage(usage)
    if not highest_rooms:
        return "No room is using power right now."
    room_label = _join_names(highest_rooms)
    verb = "are" if len(highest_rooms) > 1 else "is"
    return f"{room_label} {verb} using the most power right now: {watts}W."


def format_toggle_result(room: dict, device_id: str) -> str:
    device = next((item for item in room["devices"] if item["id"] == device_id), None)
    if not device:
        return f"{room['name']} updated. Current room usage: {room['currentPower']}W."
    return f"{room['name']} {device['name']} is now {device['status']}. Current room usage: {room['currentPower']}W."


def format_room_power_result(room: dict, status: str) -> str:
    return f"{room['name']} is now {status}. Current room usage: {room['currentPower']}W."


def format_reset_result(state: dict) -> str:
    return f"Demo state reset. All devices are OFF. Current usage: {state['totalCurrentWatts']}W."


def room_name_from_id(room_id: str | None) -> str:
    room_names = {
        "drawing-room": "Drawing Room",
        "work-room-1": "Work Room 1",
        "work-room-2": "Work Room 2",
    }
    return room_names.get(room_id or "", "Unknown room")


def _highest_rooms_from_state(state: dict) -> tuple[list[str], int]:
    rooms = state.get("rooms", [])
    if not rooms:
        return [], 0
    max_watts = max(room["currentPower"] for room in rooms)
    if max_watts <= 0:
        return [], 0
    return [room["name"] for room in rooms if room["currentPower"] == max_watts], max_watts


def _highest_rooms_from_usage(usage: dict) -> tuple[list[str], int]:
    room_wise_power = usage.get("roomWisePower", {})
    if not room_wise_power:
        return [], 0

    highest_rooms = usage.get("highestRooms")
    if highest_rooms:
        watts = room_wise_power.get(highest_rooms[0], 0)
        return highest_rooms, watts

    max_watts = max(room_wise_power.values())
    if max_watts <= 0:
        return [], 0
    return [room for room, watts in room_wise_power.items() if watts == max_watts], max_watts


def _highest_usage_text(usage: dict) -> str:
    highest_rooms, watts = _highest_rooms_from_usage(usage)
    if not highest_rooms:
        return "No room is using power right now."
    room_label = _join_names(highest_rooms)
    label = "Highest rooms" if len(highest_rooms) > 1 else "Highest room"
    return f"{label} right now: {room_label} at {watts}W."


def _join_names(names: list[str]) -> str:
    if len(names) <= 2:
        return " and ".join(names)
    return ", ".join(names[:-1]) + f", and {names[-1]}"


def _format_time(value: str | None) -> str:
    if not value:
        return "unknown"
    try:
        return datetime.fromisoformat(value).strftime("%I:%M %p").lstrip("0")
    except ValueError:
        return value


def _format_number(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return f"{value:.2f}".rstrip("0").rstrip(".")
