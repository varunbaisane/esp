from sqlalchemy.orm import Session  # pyright: ignore[reportMissingImports]

from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest
from app.core.security import hash_password, verify_password


class AuthService:
    """Phase 6.1 service contract.
    Implementation deferred to Phase 6.3/6.4.
    """

    def register_user(self, db: Session, data: RegisterRequest) -> User:
        raise NotImplementedError("Registration implementation deferred to Phase 6.3")

    def authenticate_user(self, db: Session, data: LoginRequest) -> User | None:
        raise NotImplementedError("Authentication implementation deferred to Phase 6.4")
