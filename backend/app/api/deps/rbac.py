from typing import Callable
from fastapi import Depends, HTTPException, status # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import Session # pyright: ignore[reportMissingImports]

from app.api.deps import get_db
from app.api.deps.auth import get_current_user
from app.models import User
from app.repositories import UserRoleRepository

def require_roles(allowed_roles: list[str]) -> Callable:
    def role_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        roles = UserRoleRepository(db).list_roles_for_user(current_user.id)
        role_names = [role.name for role in roles]
        
        if not any(role in allowed_roles for role in role_names):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
            
        return current_user
        
    return role_checker
