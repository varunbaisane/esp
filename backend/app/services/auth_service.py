from sqlalchemy.orm import Session  # pyright: ignore[reportMissingImports]

from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest
from app.core.security import hash_password, verify_password
from app.repositories.user_repository import UserRepository
from app.exceptions.auth import EmailAlreadyRegisteredError, InvalidCredentialsError, UnverifiedEmailError


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
            
        if not user.email_verified:
            raise UnverifiedEmailError()
            
        return user

    def authenticate_google_user(self, db: Session, id_token: str) -> User:
        from app.services.google_auth_service import GoogleAuthService
        from app.services.notification_preference_service import NotificationPreferenceService
        
        token_info = GoogleAuthService.verify_token(id_token)
        google_sub = token_info["sub"]
        email = token_info["email"]
        name = token_info["name"]
        picture = token_info.get("picture")
        
        user_repo = UserRepository(db)
        
        # Case B: Existing Google account
        user = user_repo.get_by_google_sub(google_sub)
        if user:
            if user.google_picture != picture:
                user.google_picture = picture
                db.commit()
            return user
            
        # Case C: Existing LOCAL account with same email
        user = user_repo.get_by_email(email)
        if user:
            user.google_sub = google_sub
            if not user.google_picture:
                user.google_picture = picture
            user.email_verified = True
            db.commit()
            return user
            
        # Case A: User does not exist, create account
        new_user = User(
            email=email,
            full_name=name,
            google_sub=google_sub,
            google_picture=picture,
            email_verified=True,
            hashed_password="!GOOGLE_AUTH_ONLY!"
        )
        created_user = user_repo.create(new_user)
        NotificationPreferenceService(db).create_defaults(created_user.id)
        db.commit()
        
        return created_user
