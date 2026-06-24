from sqlalchemy import select  # pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session  # pyrefly: ignore [missing-import]

from app.models.audit_log import AuditLog
from app.schemas.audit import AuditLogCreate

class AuditRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, audit_in: AuditLogCreate) -> AuditLog:
        audit_log = AuditLog(**audit_in.model_dump())
        self._session.add(audit_log)
        self._session.flush()
        return audit_log

    def list_for_ticket(self, ticket_id: int) -> list[AuditLog]:
        stmt = select(AuditLog).where(AuditLog.ticket_id == ticket_id).order_by(AuditLog.created_at.desc())
        return list(self._session.execute(stmt).scalars().all())

    def list_recent(self, limit: int = 50) -> list[AuditLog]:
        stmt = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
        return list(self._session.execute(stmt).scalars().all())

    def list_for_actor(self, actor_id: int, limit: int = 50) -> list[AuditLog]:
        stmt = select(AuditLog).where(AuditLog.actor_id == actor_id).order_by(AuditLog.created_at.desc()).limit(limit)
        return list(self._session.execute(stmt).scalars().all())

    def list_all(self, limit: int = 100, offset: int = 0) -> tuple[list[AuditLog], int]:
        from sqlalchemy import func
        # Get total count
        count_stmt = select(func.count()).select_from(AuditLog)
        total = self._session.execute(count_stmt).scalar() or 0
        
        # Get paginated items
        stmt = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
        items = list(self._session.execute(stmt).scalars().all())
        
        return items, total
