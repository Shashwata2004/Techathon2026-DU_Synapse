# Smart Office Monitor

Smart Office Monitor is a Techathon preliminary-round MVP for monitoring simulated office lights and fans from both a live web dashboard and a Discord bot.

## Device Count Note

The v1.2 problem statement defines the fixed office setup as 3 rooms, each with 2 fans and 3 lights. That equals 5 devices per room and 15 total devices. Some later references still mention 18 devices, which appears to be leftover text from an earlier version. This implementation follows the corrected fixed office setup: 15 devices total.

## Features

- FastAPI backend as the single source of truth
- 15 simulated devices across 3 rooms
- Live wattage, room-wise usage, and estimated kWh
- WebSocket dashboard updates without refresh
- Polling fallback if WebSocket disconnects
- Alert rules for after-hours usage and rooms left fully ON
- Discord commands for status, room checks, and usage
- Clickable floorplan controls backed by local demo endpoints
- Optional OpenAI rewrite for friendlier Discord responses

## Architecture

Simulated Device Layer -> FastAPI State Store -> REST API -> Discord Bot -> Discord User

Simulated Device Layer -> FastAPI State Store -> WebSocket -> React Dashboard -> Web User

The frontend and bot never maintain independent device state.

## Tech Stack

- Backend: Python, FastAPI, Pydantic
- Frontend: React, Vite, lucide-react
- Realtime: FastAPI WebSocket
- Discord: discord.py, aiohttp
- Optional LLM: OpenAI API only when `OPENAI_API_KEY` is configured

## Repository Structure

```text
backend/     FastAPI app, simulator, tests
frontend/    React dashboard
bot/         Discord bot
docs/        diagrams, wiring guide, demo script
```

## Environment

Copy `.env.example` to `.env` where needed and fill only real secrets.

```env
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
SIMULATION_ENABLED=false
SIMULATION_INTERVAL_SECONDS=15
OFFICE_HOURS_START=09:00
OFFICE_HOURS_END=17:00

VITE_BACKEND_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws

DISCORD_BOT_TOKEN=
BACKEND_BASE_URL=http://localhost:8000
DISCORD_ALERT_CHANNEL_ID=
OPENAI_API_KEY=
```

## Run Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Windows activation:

```bash
venv\Scripts\activate
```

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal, usually `http://localhost:5173`.

## Run Discord Bot

```bash
cd bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python bot.py
```

Set `DISCORD_BOT_TOKEN` before running. `OPENAI_API_KEY` and `DISCORD_ALERT_CHANNEL_ID` are optional.

## API Endpoints

- `GET /api/state`: full state
- `GET /api/devices`: all 15 devices
- `GET /api/rooms`: all room summaries
- `GET /api/rooms/{roomId}`: one room, with aliases such as `drawing`, `work1`, `work2`
- `GET /api/usage`: total watts, room-wise watts, estimated kWh, active count
- `GET /api/alerts`: active and recent alerts
- `WS /ws`: full-state live updates

Local demo endpoints:

- `POST /api/demo/toggle/{deviceId}`
- `POST /api/demo/set-device/{deviceId}`
- `POST /api/demo/set-room-all-on/{roomId}`
- `POST /api/demo/set-room-all-off/{roomId}`
- `POST /api/demo/trigger-after-hours-alert`
- `POST /api/demo/reset`

The dashboard uses `POST /api/demo/toggle/{deviceId}` when a user clicks a fan or light directly on the floorplan. These endpoints are kept for local demo control and are not production-facing features.

## Discord Commands

- `!status`
- `!room drawing`
- `!room work1`
- `!room work2`
- `!usage`

## Alert Rules

- After-hours alert: any device ON outside `09:00` to `17:00`.
- Room all-on alert: all 5 devices in one room ON continuously for more than 2 hours.
- Alert IDs are stable so the backend avoids duplicate alert spam.

## Simulation Logic

For the final demo, keep `SIMULATION_ENABLED=false` and click fans/lights directly on the floorplan to change device states manually. This keeps the dashboard and Discord responses stable and predictable.

If `SIMULATION_ENABLED=true`, the backend simulator runs every `SIMULATION_INTERVAL_SECONDS`, toggles exactly one device, updates timestamps and `onSince`, recalculates watts and kWh, evaluates alerts, and broadcasts only when state actually changes. The default interval is `15` seconds.

Energy estimate:

```text
estimatedKwhToday += currentTotalWatts * elapsedHours / 1000
```

## Hardware Schematic

Use `docs/hardware-wiring.md` to build a representative one-room Wokwi schematic with ESP32 inputs for 2 fans and 3 lights. Save the screenshot as `docs/diagrams/hardware-schematic.png`.

The ESP32/Wokwi schematic is a hardware concept deliverable only. The running software demo does not read live ESP32 data; live device state comes from the FastAPI in-memory simulator and the local toggle endpoints. A real ESP32 integration is listed as a future improvement.

## Diagrams

- System diagram: `docs/diagrams/system-diagram.png`
- Hardware schematic screenshot: `docs/diagrams/hardware-schematic.png`

The diagrams are not Mermaid-based.

## Demo

Use `docs/demo-script.md` for a concise under-3-minute demo flow.

Recommended demo settings:

```env
SIMULATION_ENABLED=false
SIMULATION_INTERVAL_SECONDS=15
```

Then click fans and lights directly on the dashboard floorplan to toggle devices at predictable moments. The dashboard calls the backend toggle endpoint, so Discord bot responses stay in sync with the same backend state.

## Team Member Contributions

Add team names and contributions before submission.

## Future Improvements

- Persist state and usage history in SQLite or Postgres
- Add authentication for demo/admin endpoints
- Add charts for historical energy usage
- Add real ESP32 telemetry ingestion
- Deploy dashboard and backend for remote judging
