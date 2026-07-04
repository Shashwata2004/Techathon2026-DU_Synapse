# Backend

FastAPI is the single source of truth for all simulated device state, usage totals, alerts, REST APIs, and WebSocket updates.

By default, automatic dummy data simulation is enabled:

```env
SIMULATION_ENABLED=true
SIMULATION_INTERVAL_SECONDS=25
```

The simulator toggles exactly one of the 15 devices every 25 seconds, recalculates usage and alerts, and broadcasts the updated state through WebSocket.

For stable controlled demos, run with `SIMULATION_ENABLED=false`. Demo endpoints still work when simulation is disabled, and WebSocket broadcasts still happen after a floorplan click or direct demo endpoint call changes device state.

## Run

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

On Windows:

```bash
venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Test

```bash
cd backend
pytest
```

## API

- `GET /api/state`
- `GET /api/devices`
- `GET /api/rooms`
- `GET /api/rooms/{roomId}`
- `GET /api/usage`
- `GET /api/alerts`
- `GET /api/events`
- `WS /ws`

Demo-only local endpoints:

- `POST /api/demo/toggle/{deviceId}`
- `POST /api/demo/set-device/{deviceId}`
- `POST /api/demo/set-room-all-on/{roomId}`
- `POST /api/demo/set-room-all-off/{roomId}`
- `POST /api/demo/trigger-after-hours-alert`
- `POST /api/demo/reset`
- `POST /api/demo/simulator/toggle`
