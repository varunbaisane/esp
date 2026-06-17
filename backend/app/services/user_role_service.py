from sqlalchemy.orm import Session  # pyrefly: ignore [missing-import]

from app.models import UserRole, Role, User
from app.repositories import UserRoleRepository, UserRepository, RoleRepository


class UserRoleService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._repository = UserRoleRepository(session)
        self._user_repository = UserRepository(session)
        self._role_repository = RoleRepository(session)

    def assign_role(self, user_id: int, role_id: int) -> UserRole:
        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        role = self._role_repository.get_by_id(role_id)
        if not role:
            raise ValueError("Role not found")

        existing = self._repository.get_assignment(user_id, role_id)
        if existing:
            raise ValueError("Role already assigned to user")

        user_role = UserRole(user_id=user_id, role_id=role_id)

        try:
            user_role = self._repository.assign(user_role)
            self._session.commit()
            return user_role
        except Exception:
            self._session.rollback()
            raise

    def get_user_roles(self, user_id: int) -> list[Role]:
        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        return self._repository.list_roles_for_user(user_id)

    def get_role_users(self, role_id: int) -> list[User]:
        role = self._role_repository.get_by_id(role_id)
        if not role:
            raise ValueError("Role not found")
            
        return self._repository.list_users_for_role(role_id)

