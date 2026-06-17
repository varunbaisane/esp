from fastapi import APIRouter, Depends, HTTPException, status # pyrefly: ignore [missing-import]

from app.api.deps import get_user_service
from app.schemas import UserCreate, UserRead
from app.services import UserService


router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    try:
        return service.create(user_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/{user_id}",
    response_model=UserRead,
)
def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    user = service.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.get(
    "",
    response_model=list[UserRead],
)
def list_users(
    service: UserService = Depends(get_user_service),
) -> list[UserRead]:
    return service.list()
