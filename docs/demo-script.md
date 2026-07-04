# Demo Video Script

Target length: under 3 minutes.

## 0:00-0:20 Problem

People leave office lights and fans on after work. This project monitors the office through a live dashboard and a Discord bot.

## 0:20-0:45 Architecture

Show `docs/diagrams/system-architecture.png`. Explain that simulated devices feed one FastAPI backend. The dashboard uses WebSocket updates, and the Discord bot reads the same backend through REST.

For the final recording, use:

```env
SIMULATION_ENABLED=false
SIMULATION_INTERVAL_SECONDS=25
```

This keeps the state stable while you click fans and lights directly on the floorplan.

To show automatic dummy data simulation instead, start the backend with `SIMULATION_ENABLED=true`, wait about 25 seconds, and point out that one device changes automatically while the dashboard updates without refresh.

## 0:45-1:35 Dashboard

Show the office layout, simulator ON/OFF control, live device status, total watts, room-wise watts, estimated kWh, energy recommendation, recent activity, and alert panel. Click one fan and one light on the floorplan, then point out the glowing light, spinning fan, updated power values, updated recommendation, and new activity feed entries.

## 1:35-2:15 Discord Bot

Run:

```text
!help
!summary
!status
!room work1
!usage
!top
!recommend
```

Mention that every answer comes from the backend.

## 2:15-2:35 Alert

Click several devices on the floorplan after office hours, or call:

```bash
curl -X POST http://localhost:8000/api/demo/trigger-after-hours-alert
```

Show the alert appearing on the dashboard. If `DISCORD_ALERT_CHANNEL_ID` is configured, show the proactive Discord alert too.

For the bonus proactive alert demo:

1. Enable Discord Developer Mode.
2. Copy the target channel ID.
3. Set `DISCORD_ALERT_CHANNEL_ID`.
4. Start the bot.
5. Trigger an alert.
6. Show that the bot posts the alert once in the configured channel.

Optional control commands to demonstrate:

```text
!toggle work1 fan1
!roomon work2
!roomoff work2
!resetdemo
```

## 2:35-3:00 Hardware And Close

Show the Wokwi schematic screenshot and mention the one-room representative ESP32 design. Close with the shared backend, real-time updates, and clickable floorplan controls.
