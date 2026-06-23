from fastapi import Depends, HTTPException, status # pyrefly: ignore [missing-import]
from app.models.user import User
from app.api.deps.auth import get_current_user
from app.domain.permissions import get_user_highest_rank

def require_role_rank(minimum_rank: int):
    """
    FastAPI Dependency that asserts the current user has at least the provided role rank.
    """
    def _require_role_rank(user: User = Depends(get_current_user)) -> User:
        user_rank = get_user_highest_rank(user)
        if user_rank < minimum_rank:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return user
    return _require_role_rank
