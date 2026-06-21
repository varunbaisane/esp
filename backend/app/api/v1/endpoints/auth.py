from fastapi import APIRouter, Depends, HTTPException, status # pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session # pyrefly: ignore [missing-import] 

from app.api.deps import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import UserRead
from app.services.auth_service import AuthService
from app.exceptions.auth import EmailAlreadyRegisteredError, InvalidCredentialsError
from app.core.jwt import create_access_token

router = APIRouter()
auth_service = AuthService()

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    """
    try:
        return auth_service.register_user(db, data)
    except EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return an access token.
    """
    try:
        user = auth_service.authenticate_user(db, data)
        token = create_access_token(subject=str(user.id))
        return TokenResponse(access_token=token)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
