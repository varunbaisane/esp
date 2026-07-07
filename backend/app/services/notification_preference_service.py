from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.notification_preference import NotificationPreference, NotificationType, NotificationChannel
from app.repositories.notification_preference_repository import NotificationPreferenceRepository

DEFAULT_PREFERENCES_MATRIX = {
    NotificationType.TICKET_ASSIGNED: {
        NotificationChannel.IN_APP: True,
        NotificationChannel.EMAIL: True,
        NotificationChannel.BROWSER: False,
    },
    NotificationType.TICKET_REASSIGNED: {
        NotificationChannel.IN_APP: True,
        NotificationChannel.EMAIL: True,
        NotificationChannel.BROWSER: False,
    },
    NotificationType.TICKET_STATUS_CHANGED: {
        NotificationChannel.IN_APP: True,
        NotificationChannel.EMAIL: False,
        NotificationChannel.BROWSER: False,
    },
    NotificationType.TICKET_PRIORITY_CHANGED: {
        NotificationChannel.IN_APP: True,
        NotificationChannel.EMAIL: False,
        NotificationChannel.BROWSER: False,
    },
    NotificationType.ROLE_ASSIGNED: {
        NotificationChannel.IN_APP: True,
        NotificationChannel.EMAIL: True,
        NotificationChannel.BROWSER: False,
    },
    NotificationType.ROLE_REMOVED: {
        NotificationChannel.IN_APP: True,
        NotificationChannel.EMAIL: True,
        NotificationChannel.BROWSER: False,
    },
}

class NotificationPreferenceService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = NotificationPreferenceRepository(session)

    def create_defaults(self, user_id: int) -> None:
        """Create the default matrix of preferences for a new user."""
        existing = self.repo.get_preferences(user_id)
        if existing:
            return  # Safety guard

        for notif_type, channels in DEFAULT_PREFERENCES_MATRIX.items():
            for channel, enabled in channels.items():
                pref = NotificationPreference(
                    user_id=user_id,
                    notification_type=notif_type.value,
                    channel=channel.value,
                    enabled=enabled
                )
                self.repo.create(pref)
                
        self.session.commit()

    def get_preferences(self, user_id: int) -> List[NotificationPreference]:
        prefs = self.repo.get_preferences(user_id)
        if not prefs:
            # Option B: Automatically generate default preferences on first access for legacy users
            self.create_defaults(user_id)
            prefs = self.repo.get_preferences(user_id)
        return prefs

    def update_preference(self, user_id: int, preference_id: int, enabled: bool) -> NotificationPreference:
        pref = self.repo.get_preference(preference_id)
        if not pref or pref.user_id != user_id:
            raise ValueError("Preference not found or access denied")
            
        pref.enabled = enabled
        self.session.commit()
        return pref

    def is_channel_enabled(self, user_id: int, notification_type: NotificationType, channel: NotificationChannel) -> bool:
        pref = self.repo.get_specific_preference(user_id, notification_type, channel)
        if pref:
            return pref.enabled
            
        # Option B: Generate on first access if legacy user
        existing = self.repo.get_preferences(user_id)
        if not existing:
            from sqlalchemy.exc import IntegrityError
            try:
                self.create_defaults(user_id)
                pref = self.repo.get_specific_preference(user_id, notification_type, channel)
                if pref:
                    return pref.enabled
            except IntegrityError:
                self.session.rollback()
            
        # Fallback to default if not found
        defaults = DEFAULT_PREFERENCES_MATRIX.get(notification_type)
        if defaults:
            return defaults.get(channel, False)
            
        return False
