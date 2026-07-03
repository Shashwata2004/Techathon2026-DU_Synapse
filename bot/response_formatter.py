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
    highest_room = usage.get("highestRoom") or "No room"
    highest_watts = usage["roomWisePower"].get(highest_room, 0)
    return (
        f"Right now, the office is using {usage['totalCurrentWatts']}W.\n"
        f"Estimated usage today: {usage['estimatedKwhToday']:.3f} kWh.\n"
        f"Highest room right now: {highest_room} at {highest_watts}W.\n"
        f"Active devices: {usage['activeDeviceCount']} / {usage['totalDeviceCount']}."
    )


def format_alert(alert: dict) -> str:
    return f"Warning: {alert['message']} ({len(alert['affectedDevices'])} affected devices)"
