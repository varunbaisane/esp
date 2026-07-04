from fastapi import APIRouter, Depends, Query, status, HTTPException
from typing import Optional

from app.api.deps import get_notification_service
from app.api.deps.auth import get_current_user
from app.models import User
from app.schemas.notification import NotificationResponse, NotificationListResponse, UnreadCountResponse
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get(
    "",
    response_model=NotificationListResponse,
)
def list_notifications(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    unread_only: bool = Query(False, description="Filter by unread notifications only"),
    service: NotificationService = Depends(get_notification_service),
    current_user: User = Depends(get_current_user),
) -> NotificationListResponse:
    skip = (page - 1) * page_size
    notifications = service.list_notifications(
        user_id=current_user.id,
        skip=skip,
        limit=page_size,
        unread_only=unread_only
    )
    
    # We could also fetch total count if we wanted precise pagination,
    # but returning what we have is fine for now based on the spec.
    # A complete pagination would return `total` elements. Let's return total_unread as requested by schemas.
    total_unread = service.get_unread_count(user_id=current_user.id)
    
    return NotificationListResponse(
        notifications=notifications,
        total_unread=total_unread,
        page=page,
        page_size=page_size
    )


@router.get(
    "/unread-count",
    response_model=UnreadCountResponse,
)
def get_unread_count(
    service: NotificationService = Depends(get_notification_service),
    current_user: User = Depends(get_current_user),
) -> UnreadCountResponse:
    count = service.get_unread_count(user_id=current_user.id)
    return UnreadCountResponse(unread_count=count)


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
def mark_as_read(
    notification_id: int,
    service: NotificationService = Depends(get_notification_service),
    current_user: User = Depends(get_current_user),
) -> NotificationResponse:
    try:
        notification = service.mark_as_read(notification_id=notification_id, user_id=current_user.id)
        if not notification:
            # Should be handled by ValueError inside service, but just in case
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        return notification
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.patch(
    "/read-all",
    response_model=dict,
)
def mark_all_as_read(
    service: NotificationService = Depends(get_notification_service),
    current_user: User = Depends(get_current_user),
) -> dict:
    count = service.mark_all_as_read(user_id=current_user.id)
    return {"marked_read_count": count, "status": "success"}
