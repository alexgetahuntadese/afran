import asyncio
from collections import defaultdict
from uuid import UUID

from fastapi import WebSocket


class WebSocketManager:
    def __init__(self) -> None:
        self._connections: dict[UUID, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, organization_id: UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections[organization_id].add(websocket)

    async def disconnect(self, organization_id: UUID, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections[organization_id].discard(websocket)

    async def broadcast(self, organization_id: UUID, event: str, payload: dict) -> None:
        dead: list[WebSocket] = []
        async with self._lock:
            sockets = list(self._connections[organization_id])
        for websocket in sockets:
            try:
                await websocket.send_json({"event": event, "payload": payload})
            except RuntimeError:
                dead.append(websocket)
        if dead:
            async with self._lock:
                for websocket in dead:
                    self._connections[organization_id].discard(websocket)


websocket_manager = WebSocketManager()
