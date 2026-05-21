from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.api.websocket_manager import websocket_manager

router = APIRouter(tags=["realtime"])


@router.websocket("/ws/{organization_id}")
async def websocket_endpoint(websocket: WebSocket, organization_id: UUID) -> None:
    await websocket_manager.connect(organization_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await websocket_manager.disconnect(organization_id, websocket)
