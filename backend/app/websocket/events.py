from enum import Enum
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
from typing import Dict, Any

class WebSocketEventType(str, Enum):
    NOTIFICATION = "notification"
    # Future phases:
    # TICKET_UPDATED = "ticket_updated"
    # DASHBOARD_UPDATED = "dashboard_updated"
    # WORKSPACE_UPDATED = "workspace_updated"
    # PRESENCE_UPDATED = "presence_updated"

class WebSocketEvent(BaseModel):
    type: WebSocketEventType
    payload: Dict[str, Any]
