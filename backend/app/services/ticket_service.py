from sqlalchemy.orm import Session  # pyrefly: ignore [missing-import]

from app.models.ticket import Ticket, TicketStatus
from app.repositories.ticket_repository import TicketRepository
from app.repositories.user_repository import UserRepository
from app.schemas.ticket import TicketCreate


class TicketService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._repository = TicketRepository(session)
        self._user_repository = UserRepository(session)

    def create(self, ticket_data: TicketCreate) -> Ticket:
        user = self._user_repository.get_by_id(ticket_data.created_by_id)
        if not user:
            raise ValueError("User not found")

        ticket = Ticket(
            title=ticket_data.title,
            description=ticket_data.description,
            created_by_id=ticket_data.created_by_id,
            status=TicketStatus.OPEN,
        )

        try:
            ticket = self._repository.create(ticket)
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
        return self._repository.list_by_creator(user_id)
