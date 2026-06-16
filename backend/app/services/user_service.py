from sqlalchemy.orm import Session  # pyrefly: ignore [missing-import]

from app.models import User
from app.repositories import UserRepository
from app.schemas import UserCreate


class UserService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._repository = UserRepository(session)

    def create(self, user_data: UserCreate) -> User:
        if self._repository.get_by_email(user_data.email):
            raise ValueError("User with this email already exists")

        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
        )

        try:
            user = self._repository.create(user)
            self._session.commit()
            return user
        except Exception:
            self._session.rollback()
            raise

    def get_by_id(self, user_id: int) -> User | None:
        return self._repository.get_by_id(user_id)

    def get_by_email(self, email: str) -> User | None:
        return self._repository.get_by_email(email)

    def list(self) -> list[User]:
        return self._repository.list()
