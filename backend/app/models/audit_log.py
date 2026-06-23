from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import Integer, String, DateTime, Enum, JSON, ForeignKey  # pyrefly: ignore [missing-import]
from sqlalchemy.orm import Mapped, mapped_column  # pyrefly: ignore [missing-import]

from app.db.base import Base


class EntityType(str, PyEnum):
    TICKET = "ticket"
    USER = "user"
    ROLE = "role"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ticket_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("tickets.id", ondelete="SET NULL"), nullable=True, index=True)
    actor_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    actor_name: Mapped[str] = mapped_column(String, nullable=False)
    actor_email: Mapped[str] = mapped_column(String, nullable=False)
    
    action: Mapped[str] = mapped_column(String, nullable=False, index=True)
    entity_type: Mapped[EntityType] = mapped_column(Enum(EntityType), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    
    old_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    event_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )
