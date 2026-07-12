from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router
from app.api.v1.endpoints import health, version

from contextlib import asynccontextmanager
from app.infrastructure.realtime.redis_client import redis_client
from app.infrastructure.realtime.subscriber import realtime_subscriber

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await redis_client.connect()
    if redis_client.is_connected:
        realtime_subscriber.start()
    yield
    # Shutdown
    await realtime_subscriber.stop()
    await redis_client.disconnect()

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "name": "Engineering Support Escalation Platform",
        "status": "running",
        "version": "1.0.0"
    }

app.include_router(health.router)
app.include_router(version.router)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
