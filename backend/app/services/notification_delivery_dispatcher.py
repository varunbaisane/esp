from app.models.notification import Notification
from app.core.notification_templates import NotificationContent
from app.services.email_service import EmailService
from app.services.notification_preference_service import NotificationPreferenceService
from app.models.notification_preference import NotificationChannel, NotificationType

class NotificationDeliveryDispatcher:
    """
    Orchestrates the delivery of notifications to secondary channels
    like Email and Browser Hooks. Database persistence is handled upstream.
    """
    def __init__(self, email_service: EmailService, preference_service: NotificationPreferenceService):
        self.email_service = email_service
        self.preference_service = preference_service

    def _dispatch_email(self, notification: Notification, content: NotificationContent) -> None:
        from app.email.models import EmailMessage
        from app.email.template_renderer import render_email
        
        if not notification.recipient or not notification.recipient.email:
            return
            
        html_body = f"<p>{content.message}</p>"
        if content.template_name:
            context = dict(content.template_context)
            if content.ticket_summary:
                context["ticket_summary"] = content.ticket_summary
            if content.summary_rows:
                context["summary_rows"] = content.summary_rows
                
            html_body = render_email(content.template_name, context)
        message = EmailMessage(
            subject=content.title,
            to=[notification.recipient.email],
            text=content.message,
            html=html_body
        )
        self.email_service.send(message)

    def _dispatch_websocket(self, notification: Notification, content: NotificationContent) -> None:
        import logging
        import json
        from app.schemas.notification import NotificationResponse
        from app.websocket.connection_manager import connection_manager
        from app.websocket.events import WebSocketEvent, WebSocketEventType
        import asyncio
        
        logger = logging.getLogger(__name__)
        logger.debug("WebSocket delivery queued for notification %d: %s", notification.id, content.title)
        
        try:
            # Serialize the notification exactly as the REST API does
            payload = NotificationResponse.model_validate(notification).model_dump(mode="json")
            
            # Wrap in WebSocketEvent
            event = WebSocketEvent(
                type=WebSocketEventType.NOTIFICATION,
                payload=payload
            )
            
            # Dispatch asynchronously using the thread-safe fire-and-forget mechanism
            event_json = event.model_dump_json()
            from app.infrastructure.realtime.publisher import realtime_publisher
            
            realtime_publisher.publish_to_user_fire_and_forget(notification.recipient_id, event_json)
        except Exception as e:
            logger.error(f"Failed to dispatch WebSocket event for notification {notification.id}: {e}")

    def dispatch(self, notification: Notification, content: NotificationContent) -> None:
        """
        Dispatches the notification event to secondary channels.
        """
        try:
            notification_type = NotificationType(notification.type)
        except ValueError:
            # If the notification type isn't recognized in preferences, default to In-App only.
            return

        # Mandatory onboarding notifications bypass preferences
        if notification_type in (NotificationType.WELCOME, NotificationType.FIRST_ROLE_ASSIGNED):
            self._dispatch_email(notification, content)
            self._dispatch_websocket(notification, content)
            return

        # Check user preferences
        if self.preference_service.is_channel_enabled(
            notification.recipient_id,
            notification_type,
            NotificationChannel.EMAIL
        ):
            self._dispatch_email(notification, content)

        if self.preference_service.is_channel_enabled(
            notification.recipient_id,
            notification_type,
            NotificationChannel.BROWSER
        ):
            self._dispatch_websocket(notification, content)
