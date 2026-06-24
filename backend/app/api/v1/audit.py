from fastapi import APIRouter, Depends, HTTPException, status # pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session # pyrefly: ignore [missing-import]

from app.api.deps import get_db
from app.api.deps.auth import get_current_user
from app.models.user import User
from app.models.ticket import Ticket
from app.schemas.audit import AuditLogRead, AuditLogSummary, AuditLogPaginated
from app.repositories.audit_repository import AuditRepository
from app.repositories.ticket_repository import TicketRepository

router = APIRouter(prefix="/audit", tags=["Audit Logs"])

@router.get("", response_model=AuditLogPaginated)
def get_all_audit_logs(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
) -> AuditLogPaginated:
    repo = AuditRepository(db)
    items, total = repo.list_all(limit, offset)
    return AuditLogPaginated(
        items=items,
        total=total,
        limit=limit,
        offset=offset
    )

@router.get("/recent", response_model=list[AuditLogSummary])
def get_recent_audit_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
) -> list[AuditLogSummary]:
    repo = AuditRepository(db)
    return repo.list_recent(limit)

@router.get("/tickets/{ticket_id}", response_model=list[AuditLogRead])
def get_ticket_audit_logs(
    ticket_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
) -> list[AuditLogRead]:
    # Ensure ticket exists
    ticket_repo = TicketRepository(db)
    if not ticket_repo.get_by_id(ticket_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    repo = AuditRepository(db)
    return repo.list_for_ticket(ticket_id)
