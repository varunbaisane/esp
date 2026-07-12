import logging
import asyncio
from app.infrastructure.realtime.redis_client import redis_client

logger = logging.getLogger(__name__)

class RealtimePublisher:
    """
    Publishes WebSocket payloads to Redis channels for distributed delivery.
    """
    def __init__(self):
        self.loop = None

    def _ensure_loop(self):
        if self.loop is None or not self.loop.is_running():
            try:
                self.loop = asyncio.get_running_loop()
            except RuntimeError:
                pass

    async def publish_broadcast(self, event_json: str) -> None:
        """
        Publishes a message to all connected users across all backend instances.
        """
        if not redis_client.is_connected:
            from app.websocket.connection_manager import connection_manager
            connection_manager.publish_fire_and_forget(event_json)
            return

        channel = "esp:realtime:broadcast"
        try:
            await redis_client.client.publish(channel, event_json)
            logger.debug(f"Published broadcast event to {channel}")
        except Exception as e:
            logger.error(f"Failed to publish to {channel}: {e}")

    async def publish_to_user(self, user_id: int, event_json: str) -> None:
        """
        Publishes a message to a specific user across all backend instances.
        """
        if not redis_client.is_connected:
            from app.websocket.connection_manager import connection_manager
            connection_manager.dispatch_fire_and_forget(user_id, event_json)
            return

        channel = f"esp:realtime:user:{user_id}"
        try:
            await redis_client.client.publish(channel, event_json)
            logger.debug(f"Published user event to {channel}")
        except Exception as e:
            logger.error(f"Failed to publish to {channel}: {e}")

    def publish_broadcast_fire_and_forget(self, event_json: str) -> None:
        self._ensure_loop()
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self.publish_broadcast(event_json), self.loop)

    def publish_to_user_fire_and_forget(self, user_id: int, event_json: str) -> None:
        self._ensure_loop()
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self.publish_to_user(user_id, event_json), self.loop)

realtime_publisher = RealtimePublisher()
