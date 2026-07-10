from typing import List, Optional
from app.repositories.notification_repository import NotificationRepository
from app.models.notification import Notification
from app.core.notifications import NotificationType
from app.models.user import User
from app.models.ticket import Ticket
from app.core.notification_templates import (
    NotificationContent,
    build_ticket_created,
    build_ticket_assigned,
    build_ticket_reassigned,
    build_ticket_status_changed,
    build_ticket_priority_changed,
    build_ticket_escalated,
    build_role_assigned,
    build_role_removed,
    build_first_role_assigned,
)
from enum import Enum

from app.services.notification_delivery_dispatcher import NotificationDeliveryDispatcher

class NotificationService:
    def __init__(self, notification_repo: NotificationRepository, dispatcher: NotificationDeliveryDispatcher):
        self.notification_repo = notification_repo
        self.dispatcher = dispatcher

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
        return created_notification

    def _notify(
        self,
        recipient_id: int,
        actor_id: Optional[int],
        type: NotificationType,
        content: NotificationContent,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
    ) -> Optional[Notification]:
        # Skip self-notifications
        if actor_id == recipient_id:
            return None

        notification = self.create_notification(
            recipient_id=recipient_id,
            actor_id=actor_id,
            type=type,
            title=content.title,
            message=content.message,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        
        # Fan-out to secondary channels
        self.dispatcher.dispatch(notification, content)
        
        return notification

    def notify_ticket_created(self, ticket: Ticket, actor: User, assignee_id: int) -> Optional[Notification]:
        content = build_ticket_created(actor_name=str(actor.full_name), ticket=ticket)
        return self._notify(
            recipient_id=assignee_id,
            actor_id=actor.id,
            type=NotificationType.TICKET_ASSIGNED,
            content=content,
            entity_type="TICKET",
            entity_id=ticket.id,
        )

    def notify_ticket_assigned(self, ticket: Ticket, actor: User, assignee_id: int, assignee_name: str) -> Optional[Notification]:
        content = build_ticket_assigned(actor_name=str(actor.full_name), ticket=ticket, assignee_name=assignee_name)
        return self._notify(
            recipient_id=assignee_id,
            actor_id=actor.id,
            type=NotificationType.TICKET_ASSIGNED,
            content=content,
            entity_type="TICKET",
            entity_id=ticket.id,
        )

    def notify_ticket_reassigned(self, ticket: Ticket, actor: User, recipient_id: int, old_assignee_name: str, new_assignee_name: str) -> Optional[Notification]:
        content = build_ticket_reassigned(actor_name=str(actor.full_name), ticket=ticket, old_assignee_name=old_assignee_name, new_assignee_name=new_assignee_name)
        return self._notify(
            recipient_id=recipient_id,
            actor_id=actor.id,
            type=NotificationType.TICKET_REASSIGNED,
            content=content,
            entity_type="TICKET",
            entity_id=ticket.id,
        )

    def notify_ticket_status_changed(self, ticket: Ticket, actor: User, old_status: str) -> Optional[Notification]:
        assignee_id = ticket.assigned_to_id
        if not assignee_id:
            return None
        
        status_str = (
            ticket.status.value
            if isinstance(ticket.status, Enum)
            else str(ticket.status)
        )
        content = build_ticket_status_changed(actor_name=str(actor.full_name), ticket=ticket, old_status=old_status, new_status=status_str)
        return self._notify(
            recipient_id=assignee_id,
            actor_id=actor.id,
            type=NotificationType.TICKET_STATUS_CHANGED,
            content=content,
            entity_type="TICKET",
            entity_id=ticket.id,
        )

    def notify_ticket_priority_changed(self, ticket: Ticket, actor: User, old_priority: str) -> Optional[Notification]:
        assignee_id = ticket.assigned_to_id
        if not assignee_id:
            return None
            
        priority_str = (
            ticket.priority.value 
            if isinstance(ticket.priority, Enum) 
            else str(ticket.priority)
        )
        content = build_ticket_priority_changed(actor_name=str(actor.full_name), ticket=ticket, old_priority=old_priority, new_priority=priority_str)
        return self._notify(
            recipient_id=assignee_id,
            actor_id=actor.id,
            type=NotificationType.TICKET_PRIORITY_CHANGED,
            content=content,
            entity_type="TICKET",
            entity_id=ticket.id,
        )
        
    def notify_ticket_escalated(self, ticket: Ticket, actor: User, recipient_id: int, old_level: str, new_level: str) -> Optional[Notification]:
        content = build_ticket_escalated(actor_name=str(actor.full_name), ticket=ticket, old_level=old_level, new_level=new_level)
        return self._notify(
            recipient_id=recipient_id,
            actor_id=actor.id,
            type=NotificationType.TICKET_ESCALATED,  # Assume we need to handle this type, or map to TICKET_ASSIGNED
            content=content,
            entity_type="TICKET",
            entity_id=ticket.id,
        )

    def notify_role_assigned(self, target_user: User, role_name: str, actor: User) -> Optional[Notification]:
        content = build_role_assigned(actor_name=actor.full_name, role_name=role_name)
        return self._notify(
            recipient_id=target_user.id,
            actor_id=actor.id,
            type=NotificationType.ROLE_ASSIGNED,
            content=content,
            entity_type="USER",
            entity_id=target_user.id,
        )

    def notify_role_removed(self, target_user: User, role_name: str, actor: User) -> Optional[Notification]:
        content = build_role_removed(actor_name=actor.full_name, role_name=role_name)
        return self._notify(
            recipient_id=target_user.id,
            actor_id=actor.id,
            type=NotificationType.ROLE_REMOVED,
            content=content,
            entity_type="USER",
            entity_id=target_user.id,
        )

    def notify_first_role_assigned(self, target_user: User, role_name: str, actor: User) -> Optional[Notification]:
        content = build_first_role_assigned(actor_name=actor.full_name, role_name=role_name)
        return self._notify(
            recipient_id=target_user.id,
            actor_id=actor.id,
            type=NotificationType.ROLE_ASSIGNED,
            content=content,
            entity_type="USER",
            entity_id=target_user.id,
        )

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
