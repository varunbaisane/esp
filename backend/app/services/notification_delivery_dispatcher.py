from app.models.notification import Notification
from app.core.notification_templates import NotificationContent
from app.services.email_service import EmailService

class NotificationDeliveryDispatcher:
    """
    Orchestrates the delivery of notifications to secondary channels
    like Email and Browser Hooks. Database persistence is handled upstream.
    """
    def __init__(self, email_service: EmailService):
        self.email_service = email_service

    def dispatch(self, notification: Notification, content: NotificationContent) -> None:
        """
        Dispatches the notification event to secondary channels.
        
        Business logic for whether to send an email (e.g. checking user preferences)
        will be added here in future phases.
        """
        # 1. Email delivery
        # We assume EmailService is configured correctly.
        # In a later phase, this will check User Notification Preferences
        # and we might fetch the User from the database using notification.recipient_id.
        pass
        
        # 2. Browser delivery (placeholder)
        # WebSockets or Server-Sent Events will integrate here.
        pass
