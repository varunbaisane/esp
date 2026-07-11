# pyrefly: ignore [missing-import]
from fastapi import WebSocket
from typing import Dict, Set
import logging
import json

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Maps user_id -> set of active WebSockets
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        self.loop = None

    async def connect(self, user_id: int, websocket: WebSocket):
        if self.loop is None:
            import asyncio
            self.loop = asyncio.get_running_loop()
            
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(f"User {user_id} connected. Total active tabs: {len(self.active_connections[user_id])}")

    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            logger.info(f"User {user_id} disconnected.")

    async def send_to_user(self, user_id: int, message: str):
        if user_id in self.active_connections:
            # We copy the set to safely iterate while items might disconnect
            websockets = list(self.active_connections[user_id])
            for ws in websockets:
                try:
                    await ws.send_text(message)
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")
                    self.disconnect(user_id, ws)

    def dispatch_fire_and_forget(self, user_id: int, message: str):
        """
        Safely dispatches a WebSocket event from a synchronous worker thread
        to the main asyncio event loop without blocking the HTTP request.
        """
        if self.loop and self.loop.is_running():
            import asyncio
            asyncio.run_coroutine_threadsafe(self.send_to_user(user_id, message), self.loop)

    async def publish(self, message: str):
        """
        Publishes a message to relevant connections.
        Currently iterates all users (Phase 9.2).
        In Phase 9.5 (Multi-workspace), this will only target applicable users.
        """
        for user_id in list(self.active_connections.keys()):
            await self.send_to_user(user_id, message)

    def publish_fire_and_forget(self, message: str):
        """
        Safely dispatches a global/workspace WebSocket event from a synchronous worker thread.
        """
        if self.loop and self.loop.is_running():
            import asyncio
            asyncio.run_coroutine_threadsafe(self.publish(message), self.loop)
# Global singleton
connection_manager = ConnectionManager()
