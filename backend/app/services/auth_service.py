from sqlalchemy.orm import Session  # pyright: ignore[reportMissingImports]

from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest
from app.core.security import hash_password, verify_password
from app.repositories.user_repository import UserRepository
from app.exceptions.auth import EmailAlreadyRegisteredError, InvalidCredentialsError


class AuthService:
    """Phase 6.1 service contract.
    Implementation deferred to Phase 6.3/6.4.
    """

    def register_user(self, db: Session, data: RegisterRequest) -> User:
        user_repo = UserRepository(db)
        if user_repo.get_by_email(data.email):
            raise EmailAlreadyRegisteredError()
            
        new_user = User(
            email=data.email,
            full_name=data.full_name,
            hashed_password=hash_password(data.password)
        )
        created_user = user_repo.create(new_user)
        db.commit()
        return created_user

    def authenticate_user(self, db: Session, data: LoginRequest) -> User:
        user_repo = UserRepository(db)
        user = user_repo.get_by_email(data.email)
        if not user:
            raise InvalidCredentialsError()
            
        if not verify_password(data.password, user.hashed_password):
            raise InvalidCredentialsError()
            
        return user
