from sqlalchemy import select, func  # pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session  # pyrefly: ignore [missing-import]

from app.models.ticket import Ticket, TicketStatus


class TicketRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, ticket: Ticket) -> Ticket:
        self._session.add(ticket)
        self._session.flush()
        self._session.refresh(ticket)
        return ticket

    def get_by_id(self, ticket_id: int) -> Ticket | None:
        stmt = select(Ticket).where(Ticket.id == ticket_id)
        return self._session.execute(stmt).scalar_one_or_none()

    def list(self) -> list[Ticket]:
        stmt = select(Ticket).order_by(Ticket.id.desc())
        return list(self._session.execute(stmt).scalars().all())

    def list_by_creator(self, user_id: int) -> list[Ticket]:
        stmt = select(Ticket).where(Ticket.created_by_id == user_id).order_by(Ticket.id.desc())
        return list(self._session.execute(stmt).scalars().all())

    def list_by_status(self, status: TicketStatus) -> list[Ticket]:
        stmt = select(Ticket).where(Ticket.status == status).order_by(Ticket.id.desc())
        return list(self._session.execute(stmt).scalars().all())

    def list_by_assignee(self, user_id: int) -> list[Ticket]:
        stmt = select(Ticket).where(Ticket.assigned_to_id == user_id).order_by(Ticket.id.desc())
        return list(self._session.execute(stmt).scalars().all())

    def get_stats(self) -> dict[str, int]:
        from datetime import datetime, timezone
        from app.models.ticket import TicketPriority
        
        now = datetime.now(timezone.utc)
        
        open_count = self._session.execute(
            select(func.count(Ticket.id))
            .where(Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]))
        ).scalar() or 0
        
        breached_count = self._session.execute(
            select(func.count(Ticket.id))
            .where(Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]))
            .where(Ticket.sla_due_at < now)
        ).scalar() or 0
        
        high_count = self._session.execute(
            select(func.count(Ticket.id))
            .where(Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]))
            .where(Ticket.priority == TicketPriority.HIGH)
        ).scalar() or 0
        
        critical_count = self._session.execute(
            select(func.count(Ticket.id))
            .where(Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]))
            .where(Ticket.priority == TicketPriority.CRITICAL)
        ).scalar() or 0

        return {
            "open_tickets": open_count,
            "breached_tickets": breached_count,
            "high_priority_tickets": high_count,
            "critical_tickets": critical_count,
        }
