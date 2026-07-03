# Frontend

React + Vite dashboard for the Smart Office Monitor.

## Run

```bash
cd frontend
npm install
npm run dev
```

The dashboard connects to:

```env
VITE_BACKEND_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

It loads initial state from `GET /api/state`, then uses `WS /ws` for live updates. If WebSocket disconnects, it polls the backend every 5 seconds until live updates return.
