from sqlalchemy import select  # pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session  # pyrefly: ignore [missing-import]

from app.models.ticket import Ticket


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
        stmt = select(Ticket)
        return list(self._session.execute(stmt).scalars().all())

    def list_by_creator(self, user_id: int) -> list[Ticket]:
        stmt = select(Ticket).where(Ticket.created_by_id == user_id)
        return list(self._session.execute(stmt).scalars().all())
