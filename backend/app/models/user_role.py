from sqlalchemy import Column, Integer, ForeignKey, Table  # pyrefly: ignore [missing-import]

from app.db.base import Base

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)

class UserRole(Base):
    __table__ = user_roles
