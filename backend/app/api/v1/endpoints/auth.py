from fastapi import APIRouter, Depends, HTTPException, status # pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session # pyrefly: ignore [missing-import] 

from app.api.deps import get_db
from app.api.deps.auth import get_current_user
from app.models import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, CurrentUserResponse
from app.schemas.user import UserRead
from app.repositories import UserRoleRepository
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

@router.get("/me", response_model=CurrentUserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get current user profile including roles.
    """
    roles = UserRoleRepository(db).list_roles_for_user(current_user.id)
    role_names = [role.name for role in roles]
    
    return CurrentUserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        roles=role_names
    )
