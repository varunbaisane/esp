import asyncio
import logging
from app.infrastructure.realtime.redis_client import redis_client
from app.websocket.connection_manager import connection_manager
from redis.exceptions import ConnectionError, TimeoutError # pyrefly: ignore [missing-import]

logger = logging.getLogger(__name__)

class RealtimeSubscriber:
    """
    Subscribes to Redis channels and forwards payloads to the ConnectionManager.
    """
    def __init__(self):
        self._task = None
        self._stop_event = asyncio.Event()

    async def _listen(self) -> None:
        pubsub = redis_client.client.pubsub()
        await pubsub.psubscribe("esp:realtime:*")
        
        logger.info("Subscribed to esp:realtime:* channels")

        async for message in pubsub.listen():
            if self._stop_event.is_set():
                break

            if message["type"] == "pmessage":
                channel = message.get("channel")
                data = message.get("data")
                
                try:
                    if channel == "esp:realtime:broadcast":
                        connection_manager.publish_fire_and_forget(data)
                    elif channel.startswith("esp:realtime:user:"):
                        user_id = int(channel.split(":")[-1])
                        connection_manager.dispatch_fire_and_forget(user_id, data)
                except Exception as e:
                    logger.error(f"Error forwarding redis message from {channel}: {e}")
                    
        await pubsub.punsubscribe("esp:realtime:*")

    async def _run(self) -> None:
        retry_delay = 1.0
        max_delay = 30.0

        while not self._stop_event.is_set():
            try:
                # Wait for redis client to be initialized
                if getattr(redis_client, 'client', None) is None:
                    await asyncio.sleep(1)
                    continue

                await self._listen()
                
            except (ConnectionError, TimeoutError) as e:
                logger.error(f"Redis subscriber disconnected: {e}. Reconnecting in {retry_delay}s...")
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_delay)
            except Exception as e:
                logger.error(f"Unexpected error in Redis subscriber: {e}")
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_delay)
            else:
                # If listen exited normally without an exception, reset retry delay
                retry_delay = 1.0

    def start(self) -> None:
        if self._task is None:
            self._stop_event.clear()
            self._task = asyncio.create_task(self._run())
            logger.info("Realtime subscriber started.")

    async def stop(self) -> None:
        if self._task is not None:
            self._stop_event.set()
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
            logger.info("Realtime subscriber stopped.")

realtime_subscriber = RealtimeSubscriber()
