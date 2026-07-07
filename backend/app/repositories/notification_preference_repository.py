from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.notification_preference import NotificationPreference, NotificationType, NotificationChannel

class NotificationPreferenceRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_preferences(self, user_id: int) -> List[NotificationPreference]:
        return self.session.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id
        ).all()

    def get_preference(self, preference_id: int) -> Optional[NotificationPreference]:
        return self.session.query(NotificationPreference).filter(
            NotificationPreference.id == preference_id
        ).first()

    def get_specific_preference(self, user_id: int, notification_type: NotificationType, channel: NotificationChannel) -> Optional[NotificationPreference]:
        return self.session.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id,
            NotificationPreference.notification_type == notification_type.value,
            NotificationPreference.channel == channel.value
        ).first()

    def create(self, preference: NotificationPreference) -> NotificationPreference:
        self.session.add(preference)
        return preference

    def delete_for_user(self, user_id: int) -> None:
        self.session.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id
        ).delete(synchronize_session=False)
