from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.api.deps.auth import get_current_user
from app.api.deps import get_notification_preference_service
from app.models.user import User
from app.services.notification_preference_service import NotificationPreferenceService
from app.models.notification_preference import NotificationChannel, NotificationType

router = APIRouter()

class NotificationPreferenceResponse(BaseModel):
    id: int
    notification_type: NotificationType
    channel: NotificationChannel
    enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class NotificationPreferenceUpdateRequest(BaseModel):
    enabled: bool

@router.get("/", response_model=List[NotificationPreferenceResponse])
def get_notification_preferences(
    current_user: User = Depends(get_current_user),
    preference_service: NotificationPreferenceService = Depends(get_notification_preference_service)
):
    """
    Retrieve all notification preferences for the current user.
    """
    prefs = preference_service.get_preferences(current_user.id)
    return [
        p for p in prefs 
        if p.notification_type not in (NotificationType.WELCOME.value, NotificationType.FIRST_ROLE_ASSIGNED.value)
    ]

@router.patch("/{preference_id}", response_model=NotificationPreferenceResponse)
def update_notification_preference(
    preference_id: int,
    data: NotificationPreferenceUpdateRequest,
    current_user: User = Depends(get_current_user),
    preference_service: NotificationPreferenceService = Depends(get_notification_preference_service)
):
    """
    Update a notification preference for the current user.
    """
    try:
        return preference_service.update_preference(current_user.id, preference_id, data.enabled)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preference not found"
        )
