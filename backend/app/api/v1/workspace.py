from fastapi import APIRouter, Depends # pyrefly: ignore [missing-import]
from app.api.deps.auth import get_current_user
from app.api.deps import get_ticket_service
from app.models.user import User
from app.services.ticket_service import TicketService
from app.schemas.ticket import WorkspaceResponse

router = APIRouter()

@router.get("", response_model=WorkspaceResponse)
def get_workspace(
    current_user: User = Depends(get_current_user),
    service: TicketService = Depends(get_ticket_service),
) -> WorkspaceResponse:
    return WorkspaceResponse(**service.get_workspace(current_user))
