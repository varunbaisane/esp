from sqlalchemy.orm import Session # pyright: ignore[reportMissingImports]
from app.models.user import User
from app.repositories import UserRoleRepository

class UserStateService:
    def __init__(self, db: Session):
        self.db = db
        self.user_role_repo = UserRoleRepository(db)

    def has_engineering_role(self, user: User) -> bool:
        """Checks if the user has at least one role assigned."""
        roles = self.user_role_repo.list_roles_for_user(user.id)
        return len(roles) > 0

    def is_email_verified(self, user: User) -> bool:
        """Checks if the user's email has been verified."""
        return user.email_verified

    def is_pending_approval(self, user: User) -> bool:
        """A user is pending if they are verified but have no roles assigned."""
        return self.is_email_verified(user) and not self.has_engineering_role(user)

    def can_access_application(self, user: User) -> bool:
        """Definitive check for access: active account, verified email, and not pending approval."""
        if not user.is_active:
            return False
            
        if not self.is_email_verified(user):
            return False
            
        if self.is_pending_approval(user):
            return False
            
        return True
