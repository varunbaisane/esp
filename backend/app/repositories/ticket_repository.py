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

    def get_status_counts(self) -> dict[str, int]:
        stmt = select(Ticket.status, func.count(Ticket.id)).group_by(Ticket.status)
        counts = self._session.execute(stmt).all()
        res = {
            "open": 0,
            "in_progress": 0,
            "resolved": 0,
            "closed": 0,
            "total": 0,
        }
        for status, count in counts:
            res[status.value.lower()] = count
            res["total"] += count
        return res
