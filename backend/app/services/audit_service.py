from sqlalchemy.orm import Session  # pyrefly: ignore [missing-import]

from app.models.user import User
from app.models.ticket import Ticket
from app.models.audit_log import EntityType
from app.schemas.audit import AuditLogCreate
from app.repositories.audit_repository import AuditRepository
from app.domain import audit_actions

class AuditService:
    def __init__(self, session: Session) -> None:
        self._repository = AuditRepository(session)

    def _create_log(
        self,
        actor: User,
        action: str,
        entity_type: EntityType,
        entity_id: str,
        ticket_id: int | None = None,
        old_value: dict | None = None,
        new_value: dict | None = None,
        event_metadata: dict | None = None,
    ) -> None:
        audit_in = AuditLogCreate(
            ticket_id=ticket_id,
            actor_id=actor.id,
            actor_name=actor.full_name,
            actor_email=actor.email,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
            event_metadata=event_metadata
        )
        self._repository.create(audit_in)

    def log_ticket_created(self, actor: User, ticket: Ticket) -> None:
        self._create_log(
            actor=actor,
            action=audit_actions.TICKET_CREATED,
            entity_type=EntityType.TICKET,
            entity_id=str(ticket.id),
            ticket_id=ticket.id,
            new_value={"title": ticket.title, "priority": ticket.priority.value, "support_level": ticket.support_level.value}
        )

    def log_ticket_status_changed(self, actor: User, ticket: Ticket, old_status: str, new_status: str) -> None:
        action = audit_actions.STATUS_CHANGED
        if new_status == "RESOLVED":
            action = audit_actions.TICKET_RESOLVED
        elif new_status == "CLOSED":
            action = audit_actions.TICKET_CLOSED

        self._create_log(
            actor=actor,
            action=action,
            entity_type=EntityType.TICKET,
            entity_id=str(ticket.id),
            ticket_id=ticket.id,
            event_metadata={
                "from_status": old_status,
                "to_status": new_status
            }
        )

    def log_ticket_assigned(self, actor: User, ticket: Ticket, old_assignee_id: int | None, new_assignee_id: int | None) -> None:
        action = audit_actions.TICKET_REASSIGNED if old_assignee_id else audit_actions.TICKET_ASSIGNED
        self._create_log(
            actor=actor,
            action=action,
            entity_type=EntityType.TICKET,
            entity_id=str(ticket.id),
            ticket_id=ticket.id,
            event_metadata={
                "from_user": old_assignee_id,
                "to_user": new_assignee_id
            }
        )

    def log_ticket_escalated(self, actor: User, ticket: Ticket, old_level: str, new_level: str) -> None:
        self._create_log(
            actor=actor,
            action=audit_actions.TICKET_ESCALATED,
            entity_type=EntityType.TICKET,
            entity_id=str(ticket.id),
            ticket_id=ticket.id,
            event_metadata={
                "from_level": old_level,
                "to_level": new_level
            }
        )
