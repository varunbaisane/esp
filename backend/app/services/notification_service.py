from typing import List, Optional
from app.repositories.notification_repository import NotificationRepository
from app.models.notification import Notification
from app.core.notifications import NotificationType

class NotificationService:
    def __init__(self, notification_repo: NotificationRepository):
        self.notification_repo = notification_repo

    def create_notification(
        self,
        recipient_id: int,
        type: NotificationType,
        title: str,
        message: str,
        actor_id: Optional[int] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
    ) -> Notification:
        notification = Notification(
            recipient_id=recipient_id,
            actor_id=actor_id,
            type=type,
            title=title,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        created_notification = self.notification_repo.create(notification)
        
        # TODO:
        # Fan-out to additional delivery channels
        # (email, browser, websocket)
        
        return created_notification

    def list_notifications(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 50, 
        unread_only: bool = False
    ) -> List[Notification]:
        return self.notification_repo.list_for_user(user_id, skip, limit, unread_only)

    def mark_as_read(self, notification_id: int, user_id: int) -> Optional[Notification]:
        # Optional check to ensure user_id owns the notification before marking read
        notification = self.notification_repo.get(notification_id)
        if not notification or notification.recipient_id != user_id:
            raise ValueError("Notification not found or access denied")
        
        return self.notification_repo.mark_read(notification_id)

    def mark_all_as_read(self, user_id: int) -> int:
        return self.notification_repo.mark_all_read(user_id)

    def get_unread_count(self, user_id: int) -> int:
        return self.notification_repo.unread_count(user_id)
