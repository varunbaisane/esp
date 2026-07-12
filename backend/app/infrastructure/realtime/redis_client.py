import logging
from redis import asyncio as aioredis  # pyrefly: ignore [missing-import]
from app.core.config import settings
from typing import Optional

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self._client: Optional[aioredis.Redis] = None
        self.is_connected = False

    async def connect(self) -> None:
        if self._client is None:
            logger.info(f"Connecting to Redis at {settings.REDIS_URL}")
            self._client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
            try:
                # Test connection
                await self._client.ping()
                self.is_connected = True
                logger.info("Successfully connected to Redis.")
            except Exception as e:
                self._client = None
                self.is_connected = False
                if settings.ENVIRONMENT == "production":
                    logger.error("Redis connection failed and ENVIRONMENT is production. Aborting startup.")
                    raise e
                else:
                    logger.warning("Redis unavailable.")
                    logger.warning("Running in standalone realtime mode.")
                    logger.warning("Distributed Pub/Sub disabled.")

    async def disconnect(self) -> None:
        if self._client is not None:
            logger.info("Disconnecting from Redis.")
            try:
                await self._client.aclose()
            except AttributeError:
                # Fallback for older redis-py versions
                await self._client.close()
            self._client = None
            self.is_connected = False

    @property
    def client(self) -> aioredis.Redis:
        if self._client is None:
            raise RuntimeError("Redis client is not connected.")
        return self._client

redis_client = RedisClient()
