from fastapi import APIRouter, Depends, HTTPException, status # pyrefly: ignore [missing-import]

from app.api.deps import get_ticket_service
from app.api.deps.auth import get_current_user
from app.models.ticket import TicketStatus
from app.models.user import User
from app.schemas.ticket import TicketCreate, TicketRead, TicketSummary, TicketUpdate, TicketStats
from app.services.ticket_service import TicketService
from app.exceptions.ticket import InvalidTicketTransitionError, InvalidEscalationError


router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post(
    "",
    response_model=TicketRead,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(
    ticket_data: TicketCreate,
    service: TicketService = Depends(get_ticket_service),
    current_user: User = Depends(get_current_user),
) -> TicketRead:
    try:
        return service.create(ticket_data, current_user.id)
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
    _: User = Depends(get_current_user),
) -> list[TicketSummary]:
    return service.list()





@router.patch(
    "/{ticket_id}",
    response_model=TicketRead,
)
def update_ticket(
    ticket_id: int,
    update_data: TicketUpdate,
    service: TicketService = Depends(get_ticket_service),
    _: User = Depends(get_current_user),
) -> TicketRead:
    try:
        return service.update(ticket_id, update_data)
    except InvalidTicketTransitionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
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
    "/{ticket_id}/escalate",
    response_model=TicketRead,
)
def escalate_ticket(
    ticket_id: int,
    service: TicketService = Depends(get_ticket_service),
    _: User = Depends(get_current_user),
) -> TicketRead:
    try:
        return service.escalate(ticket_id)
    except InvalidEscalationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/stats",
    response_model=TicketStats,
)
def get_stats(
    service: TicketService = Depends(get_ticket_service),
    _: User = Depends(get_current_user),
) -> TicketStats:
    return TicketStats(**service.get_stats())


@router.get(
    "/status/{status}",
    response_model=list[TicketSummary],
)
def list_by_status(
    status: TicketStatus,
    service: TicketService = Depends(get_ticket_service),
    _: User = Depends(get_current_user),
) -> list[TicketSummary]:
    return service.list_by_status(status)


@router.get(
    "/assigned/{user_id}",
    response_model=list[TicketSummary],
)
def list_by_assignee(
    user_id: int,
    service: TicketService = Depends(get_ticket_service),
    _: User = Depends(get_current_user),
) -> list[TicketSummary]:
    try:
        return service.list_by_assignee(user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/created/{user_id}",
    response_model=list[TicketSummary],
)
def list_by_creator(
    user_id: int,
    service: TicketService = Depends(get_ticket_service),
    _: User = Depends(get_current_user),
) -> list[TicketSummary]:
    try:
        return service.list_by_creator(user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/{ticket_id}",
    response_model=TicketRead,
)
def get_ticket(
    ticket_id: int,
    service: TicketService = Depends(get_ticket_service),
    _: User = Depends(get_current_user),
) -> TicketRead:
    ticket = service.get_by_id(ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    return ticket
