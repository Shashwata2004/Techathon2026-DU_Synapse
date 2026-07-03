# Demo Video Script

Target length: under 3 minutes.

## 0:00-0:20 Problem

People leave office lights and fans on after work. This project monitors the office through a live dashboard and a Discord bot.

## 0:20-0:45 Architecture

Show `docs/diagrams/system-diagram.png`. Explain that simulated devices feed one FastAPI backend. The dashboard uses WebSocket updates, and the Discord bot reads the same backend through REST.

For the final recording, use:

```env
SIMULATION_ENABLED=false
SIMULATION_INTERVAL_SECONDS=15
```

This keeps the state stable while you click fans and lights directly on the floorplan.

## 0:45-1:35 Dashboard

Show the office layout, live device status, total watts, room-wise watts, estimated kWh, and alert panel. Click one fan and one light on the floorplan, then point out the glowing light, spinning fan, and updated power values.

## 1:35-2:15 Discord Bot

Run:

```text
!status
!room work1
!usage
```

Mention that every answer comes from the backend.

## 2:15-2:35 Alert

Click several devices on the floorplan after office hours, or call:

```bash
curl -X POST http://localhost:8000/api/demo/trigger-after-hours-alert
```

Show the alert appearing on the dashboard. If `DISCORD_ALERT_CHANNEL_ID` is configured, show the proactive Discord alert too.

## 2:35-3:00 Hardware And Close

Show the Wokwi schematic screenshot and mention the one-room representative ESP32 design. Close with the shared backend, real-time updates, and clickable floorplan controls.
