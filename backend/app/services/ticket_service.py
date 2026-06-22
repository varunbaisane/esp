from sqlalchemy.orm import Session  # pyrefly: ignore [missing-import]

from app.models.ticket import Ticket, TicketStatus, TicketPriority
from app.repositories.ticket_repository import TicketRepository
from app.repositories.user_repository import UserRepository
from app.schemas.ticket import TicketCreate, TicketUpdate
from app.domain.ticket_workflow import can_transition
from app.exceptions.ticket import InvalidTicketTransitionError


class TicketService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._repository = TicketRepository(session)
        self._user_repository = UserRepository(session)

    def create(self, ticket_data: TicketCreate, user_id: int) -> Ticket:
        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        ticket = Ticket(
            title=ticket_data.title,
            description=ticket_data.description,
            priority=ticket_data.priority,
            created_by_id=user_id,
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
        return self._repository.get_status_counts()


    def update(self, ticket_id: int, update_data: TicketUpdate) -> Ticket:
        ticket = self._repository.get_by_id(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")

        if update_data.status is not None and update_data.status != ticket.status:
            if not can_transition(ticket.status, update_data.status):
                raise InvalidTicketTransitionError(f"Cannot transition from {ticket.status.value} to {update_data.status.value}")
            ticket.status = update_data.status
            
        if update_data.priority is not None:
            ticket.priority = update_data.priority
            
        if update_data.assigned_to_id is not None:
            user = self._user_repository.get_by_id(update_data.assigned_to_id)
            if not user:
                raise ValueError("Assignee not found")
            ticket.assigned_to_id = update_data.assigned_to_id

        try:
            self._session.commit()
            return ticket
        except Exception:
            self._session.rollback()
            raise
