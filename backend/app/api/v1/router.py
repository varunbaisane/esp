from fastapi import APIRouter # pyrefly: ignore [missing-import]    
from app.api.v1.endpoints import auth, notification_preferences
from app.api.v1 import users, roles, tickets, audit, workspace, team_operations, analytics, notifications

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router)
api_router.include_router(roles.router)
api_router.include_router(tickets.router)
api_router.include_router(audit.router)
api_router.include_router(workspace.router, prefix="/workspace", tags=["workspace"])
api_router.include_router(team_operations.router, prefix="/team-operations", tags=["team_operations"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(notifications.router)
api_router.include_router(notification_preferences.router, prefix="/notification-preferences", tags=["notification_preferences"])
