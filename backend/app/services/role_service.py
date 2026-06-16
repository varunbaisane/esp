from sqlalchemy.orm import Session  # pyrefly: ignore [missing-import]

from app.models import Role
from app.repositories import RoleRepository
from app.schemas import RoleCreate


class RoleService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._repository = RoleRepository(session)

    def create(self, role_data: RoleCreate) -> Role:
        if self._repository.get_by_name(role_data.name):
            raise ValueError("Role with this name already exists")

        role = Role(
            name=role_data.name,
            description=role_data.description,
        )

        try:
            role = self._repository.create(role)
            self._session.commit()
            return role
        except Exception:
            self._session.rollback()
            raise

    def get_by_id(self, role_id: int) -> Role | None:
        return self._repository.get_by_id(role_id)

    def get_by_name(self, name: str) -> Role | None:
        return self._repository.get_by_name(name)

    def list(self) -> list[Role]:
        return self._repository.list()
