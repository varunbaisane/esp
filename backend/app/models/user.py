from datetime import datetime, timezone

from sqlalchemy import Integer, String, Boolean, DateTime  # pyrefly: ignore [missing-import]
from sqlalchemy.orm import Mapped, mapped_column, relationship  # pyrefly: ignore [missing-import]

from app.db.base import Base
from app.models.user_role import user_roles


class User(Base):
    """
    User model representing an account in the system.
    
    The `is_system_account` field is used for:
    * cleanup exemption (prevents unverified system accounts from being deleted)
    * demo users
    * future demo reset
    * analytics exclusion
    * protected accounts
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_system_account: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
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

    roles: Mapped[list["Role"]] = relationship(  # noqa: F821
        "Role",
        secondary=user_roles,
        back_populates="users",
    )

    created_tickets: Mapped[list["Ticket"]] = relationship(  # noqa: F821
        "Ticket",
        foreign_keys="Ticket.created_by_id",
        back_populates="creator",
    )

    assigned_tickets: Mapped[list["Ticket"]] = relationship(  # noqa: F821
        "Ticket",
        foreign_keys="Ticket.assigned_to_id",
        back_populates="assigned_to",
    )

    notification_preferences: Mapped[list["NotificationPreference"]] = relationship( # noqa: F821
        "NotificationPreference",
        back_populates="user",
        cascade="all, delete-orphan",
    )

