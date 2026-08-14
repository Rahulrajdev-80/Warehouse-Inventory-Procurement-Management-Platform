from typing import List, Dict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # topic -> List of active WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {
            "inventory": [],
            "alerts": [],
            "transfers": [],
        }

    async def connect(self, topic: str, websocket: WebSocket):
        await websocket.accept()
        if topic in self.active_connections:
            self.active_connections[topic].append(websocket)

    def disconnect(self, topic: str, websocket: WebSocket):
        if topic in self.active_connections and websocket in self.active_connections[topic]:
            self.active_connections[topic].remove(websocket)

    async def broadcast(self, topic: str, message: dict):
        if topic in self.active_connections:
            disconnected = []
            for connection in self.active_connections[topic]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(connection)
            for conn in disconnected:
                self.disconnect(topic, conn)

ws_manager = ConnectionManager()
