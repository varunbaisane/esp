from fastapi import APIRouter, Depends, HTTPException, status # pyrefly: ignore [missing-import]
from app.api.deps.auth import get_current_user
from app.api.deps import get_ticket_service
from app.models.user import User
from app.services.ticket_service import TicketService
from app.schemas.ticket import TeamOperationsResponse

router = APIRouter()

@router.get("", response_model=TeamOperationsResponse)
def get_team_operations(
    current_user: User = Depends(get_current_user),
    service: TicketService = Depends(get_ticket_service),
) -> TeamOperationsResponse:
    # Check if user has required roles
    has_access = False
    for role in current_user.roles:
        if role.name in ["ADMIN", "ENGINEERING_MANAGER"]:
            has_access = True
            break
            
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view team operations."
        )

    return TeamOperationsResponse(**service.get_team_operations())
