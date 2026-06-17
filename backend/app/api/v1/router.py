from fastapi import APIRouter # pyrefly: ignore [missing-import]    
from app.api.v1.endpoints import health
from app.api.v1 import users, roles, tickets

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(users.router)
api_router.include_router(roles.router)
api_router.include_router(tickets.router)


