from sqlalchemy.orm import Session  # pyrefly: ignore [missing-import]

from app.models.ticket import Ticket, TicketStatus, TicketPriority
from app.repositories.ticket_repository import TicketRepository
from app.repositories.user_repository import UserRepository
from app.schemas.ticket import TicketCreate, TicketUpdate
from app.domain.ticket_workflow import can_transition
from app.exceptions.ticket import InvalidTicketTransitionError, InvalidEscalationError
from app.domain.ticket_escalation import get_next_level
from app.domain.ticket_sla import calculate_sla_due
from app.services.audit_service import AuditService


class TicketService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._repository = TicketRepository(session)
        self._user_repository = UserRepository(session)
        self._audit_service = AuditService(session)

    def create(self, ticket_data: TicketCreate, user_id: int) -> Ticket:
        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        
        ticket = Ticket(
            title=ticket_data.title,
            description=ticket_data.description,
            priority=ticket_data.priority,
            created_by_id=user_id,
            status=TicketStatus.OPEN,
            created_at=now,
            sla_due_at=calculate_sla_due(ticket_data.priority, now)
        )

        try:
            ticket = self._repository.create(ticket)
            self._audit_service.log_ticket_created(user, ticket)
            self._session.commit()
            return ticket
        except Exception:
            self._session.rollback()
            raise

    def get_by_id(self, ticket_id: int) -> Ticket | None:
        return self._repository.get_by_id(ticket_id)

    def list(self) -> list[Ticket]:
        return self._repository.list()

    def list_by_creator(self, user_id: int) -> list[Ticket]:
        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return self._repository.list_by_creator(user_id)

    def list_by_assignee(self, user_id: int) -> list[Ticket]:
        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return self._repository.list_by_assignee(user_id)

    def list_by_status(self, status: TicketStatus) -> list[Ticket]:
        return self._repository.list_by_status(status)

    def get_stats(self) -> dict[str, int]:
        return self._repository.get_stats()


    def update(self, ticket_id: int, update_data: TicketUpdate, actor_id: int) -> Ticket:
        ticket = self._repository.get_by_id(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
            
        actor = self._user_repository.get_by_id(actor_id)
        if not actor:
            raise ValueError("Actor not found")

        old_status = ticket.status.value
        if update_data.status is not None and update_data.status != ticket.status:
            if not can_transition(ticket.status, update_data.status):
                raise InvalidTicketTransitionError(f"Cannot transition from {ticket.status.value} to {update_data.status.value}")
            ticket.status = update_data.status
            self._audit_service.log_ticket_status_changed(actor, ticket, old_status, update_data.status.value)
            
        if update_data.priority is not None:
            # We don't have an audit log explicitly for priority in the specs, but we could add one if desired.
            # Leaving this alone per requirements.
            ticket.priority = update_data.priority
            
        old_assignee_id = ticket.assigned_to_id
        if update_data.assigned_to_id is not None and update_data.assigned_to_id != old_assignee_id:
            assigned_user = self._user_repository.get_by_id(update_data.assigned_to_id)
            if not assigned_user:
                raise ValueError("Assignee not found")
            ticket.assigned_to_id = update_data.assigned_to_id
            self._audit_service.log_ticket_assigned(actor, ticket, old_assignee_id, update_data.assigned_to_id)

        try:
            self._session.commit()
            return ticket
        except Exception:
            self._session.rollback()
            raise

    def escalate(self, ticket_id: int, actor_id: int) -> Ticket:
        ticket = self._repository.get_by_id(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
            
        actor = self._user_repository.get_by_id(actor_id)
        if not actor:
            raise ValueError("Actor not found")

        next_level = get_next_level(ticket.support_level)
        if not next_level:
            raise InvalidEscalationError("Ticket cannot be escalated further")

        old_level = ticket.support_level.value
        ticket.support_level = next_level
        self._audit_service.log_ticket_escalated(actor, ticket, old_level, next_level.value)

        try:
            self._session.commit()
            return ticket
        except Exception:
            self._session.rollback()
            raise
