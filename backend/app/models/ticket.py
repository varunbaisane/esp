from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Integer, String, DateTime, ForeignKey, Enum as SQLAlchemyEnum  # pyrefly: ignore [missing-import]
from sqlalchemy.orm import Mapped, mapped_column, relationship  # pyrefly: ignore [missing-import]

from app.db.base import Base


class TicketStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class TicketPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[TicketStatus] = mapped_column(
        SQLAlchemyEnum(TicketStatus),
        nullable=False,
        default=TicketStatus.OPEN,
    )
    priority: Mapped[TicketPriority] = mapped_column(
        SQLAlchemyEnum(TicketPriority),
        nullable=False,
        default=TicketPriority.MEDIUM,
    )
    
    created_by_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )
    assigned_to_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    creator: Mapped["User"] = relationship(  # noqa: F821
        "User",
        foreign_keys=[created_by_id],
        back_populates="created_tickets",
    )
    assigned_to: Mapped["User"] = relationship(  # noqa: F821
        "User",
        foreign_keys=[assigned_to_id],
        back_populates="assigned_tickets",
    )

    @property
    def created_by_name(self) -> str:
        return self.creator.full_name if self.creator else ""

    @property
    def assigned_to_name(self) -> str | None:
        return self.assigned_to.full_name if self.assigned_to else None
