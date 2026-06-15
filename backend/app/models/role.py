from datetime import datetime, timezone

from sqlalchemy import Integer, String, DateTime  # pyrefly: ignore [missing-import]
from sqlalchemy.orm import Mapped, mapped_column, relationship  # pyrefly: ignore [missing-import]

from app.db.base import Base
from app.models.user_role import user_roles


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
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

    users: Mapped[list["User"]] = relationship(  # noqa: F821
        "User",
        secondary=user_roles,
        back_populates="roles",
    )
