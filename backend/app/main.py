import asyncio

from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .models import SetDeviceRequest
from .simulator import DeviceSimulator
from .state_store import StateStore
from .websocket_manager import WebSocketManager


app = FastAPI(title="Smart Office Monitor API", version="1.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_allow_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = StateStore(settings)
websockets = WebSocketManager()
simulator: DeviceSimulator | None = None
simulator_task: asyncio.Task | None = None


async def publish_state() -> None:
    await websockets.broadcast(store.get_state().model_dump(mode="json", by_alias=True))


async def publish_if_changed(previous_revision: int) -> None:
    if store.revision != previous_revision:
        await publish_state()


def require_local_demo_request(request: Request) -> None:
    host = request.client.host if request.client else ""
    if host not in {"127.0.0.1", "::1", "localhost"}:
        raise HTTPException(status_code=403, detail="Demo endpoints are available only from localhost.")


@app.on_event("startup")
async def startup() -> None:
    global simulator, simulator_task
    if settings.simulation_enabled:
        simulator = DeviceSimulator(store, settings.simulation_interval_seconds, publish_state)
        simulator_task = asyncio.create_task(simulator.run())


@app.on_event("shutdown")
async def shutdown() -> None:
    if simulator:
        simulator.stop()
    if simulator_task:
        simulator_task.cancel()


@app.get("/api/state")
async def get_state():
    return store.get_state()


@app.get("/api/devices")
async def get_devices():
    return store.get_devices()


@app.get("/api/rooms")
async def get_rooms():
    return store.get_rooms()


@app.get("/api/rooms/{room_id}")
async def get_room(room_id: str):
    try:
        return store.get_room(room_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Unknown room. Try: drawing, work1, or work2.") from exc


@app.get("/api/usage")
async def get_usage():
    return store.get_usage()


@app.get("/api/alerts")
async def get_alerts():
    return store.get_alerts()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websockets.connect(websocket)
    await websocket.send_json(store.get_state().model_dump(mode="json", by_alias=True))
    await websockets.keep_alive(websocket)


@app.post("/api/demo/toggle/{device_id}", dependencies=[Depends(require_local_demo_request)])
async def demo_toggle(device_id: str):
    previous_revision = store.revision
    try:
        state = store.toggle_device(device_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Unknown device.") from exc
    await publish_if_changed(previous_revision)
    return state


@app.post("/api/demo/set-device/{device_id}", dependencies=[Depends(require_local_demo_request)])
async def demo_set_device(device_id: str, body: SetDeviceRequest):
    previous_revision = store.revision
    try:
        state = store.set_device(device_id, body.status)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Unknown device.") from exc
    await publish_if_changed(previous_revision)
    return state


@app.post("/api/demo/set-room-all-on/{room_id}", dependencies=[Depends(require_local_demo_request)])
async def demo_set_room_all_on(room_id: str):
    previous_revision = store.revision
    try:
        state = store.set_room_status(room_id, "ON")
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Unknown room. Try: drawing, work1, or work2.") from exc
    await publish_if_changed(previous_revision)
    return state


@app.post("/api/demo/set-room-all-off/{room_id}", dependencies=[Depends(require_local_demo_request)])
async def demo_set_room_all_off(room_id: str):
    previous_revision = store.revision
    try:
        state = store.set_room_status(room_id, "OFF")
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Unknown room. Try: drawing, work1, or work2.") from exc
    await publish_if_changed(previous_revision)
    return state


@app.post("/api/demo/trigger-after-hours-alert", dependencies=[Depends(require_local_demo_request)])
async def demo_trigger_after_hours_alert():
    previous_revision = store.revision
    state = store.trigger_after_hours_alert()
    await publish_if_changed(previous_revision)
    return state


@app.post("/api/demo/reset", dependencies=[Depends(require_local_demo_request)])
async def demo_reset():
    previous_revision = store.revision
    state = store.reset()
    await publish_if_changed(previous_revision)
    return state
