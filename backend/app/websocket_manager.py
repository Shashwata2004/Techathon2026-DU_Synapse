import json
from typing import Any

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect


class WebSocketManager:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections.discard(websocket)

    async def keep_alive(self, websocket: WebSocket) -> None:
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            self.disconnect(websocket)

    async def broadcast(self, payload: dict[str, Any]) -> None:
        if not self._connections:
            return

        encoded = json.dumps(payload)
        disconnected: list[WebSocket] = []
        for websocket in self._connections:
            try:
                await websocket.send_text(encoded)
            except RuntimeError:
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(websocket)
