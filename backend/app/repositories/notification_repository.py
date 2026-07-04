from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.notification import Notification

class NotificationRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, notification: Notification) -> Notification:
        self.session.add(notification)
        self.session.commit()
        self.session.refresh(notification)
        return notification

    def get(self, notification_id: int) -> Optional[Notification]:
        return self.session.query(Notification).filter(Notification.id == notification_id).first()

    def list_for_user(self, user_id: int, skip: int = 0, limit: int = 50, unread_only: bool = False) -> List[Notification]:
        query = self.session.query(Notification).filter(Notification.recipient_id == user_id)
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

    def unread_count(self, user_id: int) -> int:
        return self.session.query(Notification).filter(
            Notification.recipient_id == user_id,
            Notification.is_read == False
        ).count()

    def mark_read(self, notification_id: int) -> Optional[Notification]:
        notification = self.get(notification_id)
        if notification and not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.now(timezone.utc)
            self.session.add(notification)
            self.session.commit()
            self.session.refresh(notification)
        return notification

    def mark_all_read(self, user_id: int) -> int:
        notifications = self.session.query(Notification).filter(
            Notification.recipient_id == user_id,
            Notification.is_read == False
        ).all()
        
        count = 0
        now = datetime.now(timezone.utc)
        for notif in notifications:
            notif.is_read = True
            notif.read_at = now
            self.session.add(notif)
            count += 1
            
        if count > 0:
            self.session.commit()
            
        return count
