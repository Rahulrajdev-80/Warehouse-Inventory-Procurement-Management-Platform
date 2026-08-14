from typing import Dict, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

ws_router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.connections: Dict[str, Set[WebSocket]] = {
            "inventory": set(),
            "alerts": set(),
            "transfers": set(),
        }

    async def connect(self, websocket: WebSocket, channel: str):
        await websocket.accept()

        if channel not in self.connections:
            self.connections[channel] = set()

        self.connections[channel].add(websocket)

        await websocket.send_json(
            {
                "type": "connection",
                "channel": channel,
                "message": f"Connected to {channel} websocket",
            }
        )

    def disconnect(self, websocket: WebSocket, channel: str):
        if channel in self.connections:
            self.connections[channel].discard(websocket)

    async def broadcast(self, channel: str, message: dict):
        if channel not in self.connections:
            return

        disconnected = set()

        for websocket in self.connections[channel]:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.add(websocket)

        for websocket in disconnected:
            self.connections[channel].discard(websocket)


manager = ConnectionManager()


# ============================================================
# WEBSOCKET ENDPOINTS
# ============================================================

@ws_router.websocket("/ws/inventory")
async def inventory_websocket(websocket: WebSocket):
    await manager.connect(websocket, "inventory")

    try:
        while True:
            data = await websocket.receive_json()

            await manager.broadcast(
                "inventory",
                {
                    "type": "inventory_message",
                    "data": data,
                },
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket, "inventory")


@ws_router.websocket("/ws/alerts")
async def alerts_websocket(websocket: WebSocket):
    await manager.connect(websocket, "alerts")

    try:
        while True:
            data = await websocket.receive_json()

            await manager.broadcast(
                "alerts",
                {
                    "type": "alert_message",
                    "data": data,
                },
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket, "alerts")


@ws_router.websocket("/ws/transfers")
async def transfers_websocket(websocket: WebSocket):
    await manager.connect(websocket, "transfers")

    try:
        while True:
            data = await websocket.receive_json()

            await manager.broadcast(
                "transfers",
                {
                    "type": "transfer_message",
                    "data": data,
                },
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket, "transfers")


# ============================================================
# SWAGGER DOCUMENTATION ENDPOINTS
# ============================================================
#
# These GET routes are ONLY for displaying the WebSocket
# endpoints inside Swagger UI.
#
# The actual WebSocket routes are the @ws_router.websocket()
# routes above.
# ============================================================

@ws_router.get(
    "/ws/inventory",
    tags=["WebSocket"],
    summary="WebSocket - Inventory",
    description=(
        "WebSocket endpoint for real-time inventory updates. "
        "Connect using: ws://localhost:8000/ws/inventory"
    ),
)
async def inventory_websocket_docs():
    return {
        "type": "websocket",
        "endpoint": "/ws/inventory",
        "url": "ws://localhost:8000/ws/inventory",
        "description": "Real-time inventory WebSocket connection",
    }


@ws_router.get(
    "/ws/alerts",
    tags=["WebSocket"],
    summary="WebSocket - Alerts",
    description=(
        "WebSocket endpoint for real-time alerts. "
        "Connect using: ws://localhost:8000/ws/alerts"
    ),
)
async def alerts_websocket_docs():
    return {
        "type": "websocket",
        "endpoint": "/ws/alerts",
        "url": "ws://localhost:8000/ws/alerts",
        "description": "Real-time alerts WebSocket connection",
    }


@ws_router.get(
    "/ws/transfers",
    tags=["WebSocket"],
    summary="WebSocket - Transfers",
    description=(
        "WebSocket endpoint for real-time stock transfers. "
        "Connect using: ws://localhost:8000/ws/transfers"
    ),
)
async def transfers_websocket_docs():
    return {
        "type": "websocket",
        "endpoint": "/ws/transfers",
        "url": "ws://localhost:8000/ws/transfers",
        "description": "Real-time stock transfers WebSocket connection",
    }