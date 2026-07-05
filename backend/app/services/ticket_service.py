from app.schemas import TicketSummary
from sqlalchemy.orm import Session  # pyrefly: ignore [missing-import]

from app.models.ticket import Ticket, TicketStatus, TicketPriority
from app.repositories.ticket_repository import TicketRepository
from app.repositories.user_repository import UserRepository
from app.repositories.notification_repository import NotificationRepository
from app.models.user import User
from app.schemas.ticket import TicketCreate, TicketUpdate
from app.domain.ticket_workflow import can_transition
from app.exceptions.ticket import InvalidTicketTransitionError, InvalidEscalationError
from app.domain.ticket_escalation import get_next_level
from app.domain.ticket_sla import calculate_sla_due
from app.services.audit_service import AuditService
from app.services.notification_service import NotificationService


class TicketService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._repository = TicketRepository(session)
        self._user_repository = UserRepository(session)
        self._audit_service = AuditService(session)
        self._notification_service = NotificationService(NotificationRepository(session))

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

    def list_filtered(
        self,
        current_user: "User",
        status: str | None = None,
        priority: str | None = None,
        level: str | None = None,
        assigned_to: str | None = None,
        sla_status: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        limit: int = 25,
        offset: int = 0
    ) -> tuple[list["TicketSummary"], int]:
        assigned_to_id = None
        if assigned_to:
            if assigned_to.lower() == "mine":
                assigned_to_id = current_user.id
            elif assigned_to.lower() == "unassigned":
                assigned_to_id = -1
            elif assigned_to.lower() == "assigned":
                assigned_to_id = -2
            else:
                try:
                    assigned_to_id = int(assigned_to)
                except ValueError:
                    pass

        items, total = self._repository.list_filtered(
            status=status,
            priority=priority,
            support_level=level,
            assigned_to_id=assigned_to_id,
            sla_status=sla_status,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset
        )
        from app.schemas.ticket import TicketSummary
        return [TicketSummary.model_validate(t) for t in items], total

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

    def get_stats(self, user_id: int) -> dict[str, int]:
        return self._repository.get_stats(user_id)

    def get_workspace(self, user: User) -> dict:
        from datetime import datetime, timezone
        from app.models.ticket import TicketPriority
        
        stats = self._repository.get_user_ticket_stats(user.id)
        
        tickets, total = self.list_filtered(
            current_user=user,
            assigned_to="mine",
            status="ACTIVE",
            limit=1000
        )
        
        now = datetime.now(timezone.utc)
        def urgency_key(ticket):
            is_breached = ticket.sla_due_at < now
            is_critical = ticket.priority == TicketPriority.CRITICAL
            is_high = ticket.priority == TicketPriority.HIGH
            return (not is_breached, not is_critical, not is_high, ticket.sla_due_at)
            
        sorted_tickets = sorted(tickets, key=urgency_key)
        
        return {
            "stats": stats,
            "total_assigned_tickets": total,
            "tickets": sorted_tickets[:10]
        }

    def get_team_operations(self) -> dict:
        stats = self._repository.get_team_operations_stats()
        workloads = self._repository.get_engineer_workloads()
        workloads = sorted(workloads, key=lambda w: w["assigned_tickets"], reverse=True)
        return {
            "stats": stats,
            "workloads": workloads
        }


    def update(self, ticket_or_id: int | Ticket, update_data: TicketUpdate, actor: User) -> Ticket:
        if isinstance(ticket_or_id, int):
            ticket = self._repository.get_by_id(ticket_or_id)
        else:
            ticket = ticket_or_id
            
        if not ticket:
            raise ValueError("Ticket not found")

        old_status = ticket.status.value
        if update_data.status is not None and update_data.status != ticket.status:
            if not can_transition(ticket.status, update_data.status):
                raise InvalidTicketTransitionError(f"Cannot transition from {ticket.status.value} to {update_data.status.value}")
            ticket.status = update_data.status
            
            if update_data.status in (TicketStatus.RESOLVED, TicketStatus.CLOSED):
                from datetime import datetime, timezone
                if not ticket.closed_at:
                    ticket.closed_at = datetime.now(timezone.utc)
            else:
                ticket.closed_at = None

            self._audit_service.log_ticket_status_changed(actor, ticket, old_status, update_data.status.value)
            self._notification_service.notify_ticket_status_changed(ticket, actor)
            
        if update_data.priority is not None and update_data.priority != ticket.priority:
            ticket.priority = update_data.priority
            self._notification_service.notify_ticket_priority_changed(ticket, actor)
            
        old_assignee_id = ticket.assigned_to_id
        if update_data.assigned_to_id is not None and update_data.assigned_to_id != old_assignee_id:
            assigned_user = self._user_repository.get_by_id(update_data.assigned_to_id)
            if not assigned_user:
                raise ValueError("Assignee not found")
            ticket.assigned_to_id = update_data.assigned_to_id
            self._audit_service.log_ticket_assigned(actor, ticket, old_assignee_id, update_data.assigned_to_id)
            
            if old_assignee_id is None:
                self._notification_service.notify_ticket_assigned(ticket, actor, update_data.assigned_to_id)
            else:
                self._notification_service.notify_ticket_reassigned(ticket, actor, update_data.assigned_to_id)

        try:
            self._session.commit()
            return ticket
        except Exception:
            self._session.rollback()
            raise

    def claim_ticket(self, ticket_id: int, actor: User) -> Ticket:
        from app.exceptions.ticket import TicketAlreadyAssignedError
        from app.domain.permissions import can_claim_ticket
        from app.exceptions.auth import InsufficientPermissionsError

        ticket = self._repository.get_by_id(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        if ticket.assigned_to_id is not None:
            raise TicketAlreadyAssignedError("Ticket is already assigned")
            
        if not can_claim_ticket(actor, ticket):
            raise InsufficientPermissionsError("User does not have permission to claim this ticket")
            
        ticket.assigned_to_id = actor.id
        self._audit_service.log_ticket_claimed(actor, ticket)
        self._notification_service.notify_ticket_assigned(ticket, actor, actor.id)
        
        try:
            self._session.commit()
            return ticket
        except Exception:
            self._session.rollback()
            raise

    def assign_ticket(self, ticket_or_id: int | Ticket, assignee_id: int, actor: User) -> Ticket:
        from app.domain.permissions import can_assign_ticket
        from app.exceptions.ticket import InvalidAssignmentError
        from app.exceptions.auth import InsufficientPermissionsError

        if isinstance(ticket_or_id, int):
            ticket = self._repository.get_by_id(ticket_or_id)
        else:
            ticket = ticket_or_id
            
        if not ticket:
            raise ValueError("Ticket not found")
            
        target_user = self._user_repository.get_by_id(assignee_id)
        if not target_user:
            raise ValueError("Assignee not found")
            
        if not can_assign_ticket(actor, ticket, target_user):
            raise InsufficientPermissionsError("User does not have permission to assign this ticket to this user")
            
        old_assignee_id = ticket.assigned_to_id
        old_assignee_name = ticket.assigned_to_name
        
        if old_assignee_id == assignee_id:
            return ticket # No-op
            
        ticket.assigned_to_id = assignee_id
        self._audit_service.log_ticket_reassigned(actor, ticket, old_assignee_name, target_user.full_name)
        
        if old_assignee_id is None:
            self._notification_service.notify_ticket_assigned(ticket, actor, assignee_id)
        else:
            self._notification_service.notify_ticket_reassigned(ticket, actor, assignee_id)
        
        try:
            self._session.commit()
            return ticket
        except Exception:
            self._session.rollback()
            raise

    def escalate(self, ticket_id: int, actor: User) -> Ticket:
        from app.domain.permissions import can_escalate
        from app.exceptions.auth import InsufficientPermissionsError

        ticket = self._repository.get_by_id(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
            
        if not can_escalate(actor, ticket.support_level):
            raise InsufficientPermissionsError("User does not have permission to escalate this ticket")

        next_level = get_next_level(ticket.support_level)
        if not next_level:
            raise InvalidEscalationError("Ticket cannot be escalated further")

        old_level = ticket.support_level.value
        ticket.support_level = next_level
        ticket.assigned_to_id = None
        self._audit_service.log_ticket_escalated(actor, ticket, old_level, next_level.value)

        try:
            self._session.commit()
            return ticket
        except Exception:
            self._session.rollback()
            raise
