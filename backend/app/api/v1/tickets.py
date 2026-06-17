from fastapi import APIRouter, Depends, HTTPException, status # pyrefly: ignore [missing-import]

from app.api.deps import get_ticket_service
from app.schemas.ticket import TicketCreate, TicketRead, TicketSummary, TicketAssign, TicketStatusUpdate
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


@router.post(
    "/{ticket_id}/assign",
    response_model=TicketRead,
)
def assign_ticket(
    ticket_id: int,
    assignment_data: TicketAssign,
    service: TicketService = Depends(get_ticket_service),
) -> TicketRead:
    try:
        return service.assign_user(ticket_id, assignment_data.user_id)
    except ValueError as e:
        if str(e) == "Ticket not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )


@router.post(
    "/{ticket_id}/status",
    response_model=TicketRead,
)
def update_ticket_status(
    ticket_id: int,
    status_data: TicketStatusUpdate,
    service: TicketService = Depends(get_ticket_service),
) -> TicketRead:
    try:
        return service.update_status(ticket_id, status_data.status)
    except ValueError as e:
        if str(e) == "Ticket not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )


