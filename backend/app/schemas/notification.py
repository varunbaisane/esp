from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from app.core.notifications import NotificationType
from app.schemas.user_management import UserSummaryResponse

class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recipient_id: int
    actor_id: Optional[int]
    type: NotificationType
    title: str
    message: str
    entity_type: Optional[str]
    entity_id: Optional[int]
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime

    # The relationships can be included if eager loaded
    # actor: Optional[UserSummaryResponse] = None
    
class NotificationListResponse(BaseModel):
    notifications: List[NotificationResponse]
    total_unread: int
    page: int
    page_size: int

class UnreadCountResponse(BaseModel):
    unread_count: int
