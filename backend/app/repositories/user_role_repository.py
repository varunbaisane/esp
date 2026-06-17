from sqlalchemy import select  # pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session  # pyrefly: ignore [missing-import]

from app.models import UserRole, Role, User


class UserRoleRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def assign(self, user_role: UserRole) -> UserRole:
        self._session.add(user_role)
        self._session.flush()
        self._session.refresh(user_role)
        return user_role

    def get_assignment(self, user_id: int, role_id: int) -> UserRole | None:
        stmt = select(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id,
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def list_roles_for_user(self, user_id: int) -> list[Role]:
        stmt = select(Role).join(UserRole).where(UserRole.user_id == user_id)
        return list(self._session.execute(stmt).scalars().all())

    def list_users_for_role(self, role_id: int) -> list[User]:
        stmt = select(User).join(UserRole).where(UserRole.role_id == role_id)
        return list(self._session.execute(stmt).scalars().all())
