from fastapi import Depends, HTTPException, status # pyright: ignore [missing-import]
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials # pyright: ignore [missing-import]
from sqlalchemy.orm import Session  # pyright: ignore[reportMissingImports]
from app.api.deps import get_db
from app.core.jwt import decode_access_token
from app.exceptions.auth import InvalidTokenError, TokenExpiredError
from app.repositories.user_repository import UserRepository
from app.models import User

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    try:
        payload = decode_access_token(credentials.credentials)
    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(int(payload.sub))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return user
