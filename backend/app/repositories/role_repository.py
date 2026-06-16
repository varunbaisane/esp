from sqlalchemy import select  # pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session  # pyrefly: ignore [missing-import]

from app.models import Role


class RoleRepository:
    """Foundational persistence query methods for the Role entity."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, role: Role) -> Role:
        self._session.add(role)
        self._session.flush()
        self._session.refresh(role)
        return role

    def get_by_id(self, role_id: int) -> Role | None:
        stmt = select(Role).where(Role.id == role_id)
        return self._session.execute(stmt).scalar_one_or_none()

    def get_by_name(self, name: str) -> Role | None:
        stmt = select(Role).where(Role.name == name)
        return self._session.execute(stmt).scalar_one_or_none()

    def list(self) -> list[Role]:
        stmt = select(Role)
        return list(self._session.execute(stmt).scalars().all())
