# Backend

FastAPI is the single source of truth for all simulated device state, usage totals, alerts, REST APIs, and WebSocket updates.

For stable demos, run with:

```env
SIMULATION_ENABLED=false
SIMULATION_INTERVAL_SECONDS=15
```

Demo endpoints still work when simulation is disabled, and WebSocket broadcasts still happen after demo controls change device state.

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
- `WS /ws`

Demo-only local endpoints:

- `POST /api/demo/toggle/{deviceId}`
- `POST /api/demo/set-device/{deviceId}`
- `POST /api/demo/set-room-all-on/{roomId}`
- `POST /api/demo/set-room-all-off/{roomId}`
- `POST /api/demo/trigger-after-hours-alert`
- `POST /api/demo/reset`
