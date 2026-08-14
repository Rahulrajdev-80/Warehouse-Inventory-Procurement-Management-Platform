from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect


router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.connections: Dict[str, Set[WebSocket]] = {
            "inventory": set(),
            "alerts": set(),
            "transfers": set(),
        }

    async def connect(self, websocket: WebSocket, channel: str):
        await websocket.accept()
        self.connections[channel].add(websocket)

        await websocket.send_json({
            "type": "connection",
            "channel": channel,
            "message": f"Connected to {channel} websocket"
        })

    def disconnect(self, websocket: WebSocket, channel: str):
        self.connections[channel].discard(websocket)

    async def broadcast(self, channel: str, message: dict):
        disconnected = set()

        for websocket in self.connections[channel]:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.add(websocket)

        for websocket in disconnected:
            self.connections[channel].discard(websocket)


manager = ConnectionManager()


@router.websocket("/ws/inventory")
async def inventory_websocket(websocket: WebSocket):
    await manager.connect(websocket, "inventory")

    try:
        while True:
            data = await websocket.receive_json()

            await manager.broadcast(
                "inventory",
                {
                    "type": "inventory_message",
                    "data": data
                }
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket, "inventory")


@router.websocket("/ws/alerts")
async def alerts_websocket(websocket: WebSocket):
    await manager.connect(websocket, "alerts")

    try:
        while True:
            data = await websocket.receive_json()

            await manager.broadcast(
                "alerts",
                {
                    "type": "alert_message",
                    "data": data
                }
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket, "alerts")


@router.websocket("/ws/transfers")
async def transfers_websocket(websocket: WebSocket):
    await manager.connect(websocket, "transfers")

    try:
        while True:
            data = await websocket.receive_json()

            await manager.broadcast(
                "transfers",
                {
                    "type": "transfer_message",
                    "data": data
                }
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket, "transfers")