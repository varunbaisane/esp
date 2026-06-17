from fastapi import APIRouter, Depends, HTTPException, status # pyrefly: ignore [missing-import]

from app.api.deps import get_ticket_service
from app.schemas.ticket import TicketCreate, TicketRead, TicketSummary
from app.services.ticket_service import TicketService


router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post(
    "",
    response_model=TicketRead,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(
    ticket_data: TicketCreate,
    service: TicketService = Depends(get_ticket_service),
) -> TicketRead:
    try:
        return service.create(ticket_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "",
    response_model=list[TicketSummary],
)
def list_tickets(
    service: TicketService = Depends(get_ticket_service),
) -> list[TicketSummary]:
    return service.list()


@router.get(
    "/{ticket_id}",
    response_model=TicketRead,
)
def get_ticket(
    ticket_id: int,
    service: TicketService = Depends(get_ticket_service),
) -> TicketRead:
    ticket = service.get_by_id(ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    return ticket
