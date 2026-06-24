
from fastapi import APIRouter, Depends, HTTPException, status   # pyrefly: ignore [missing-import]

from app.api.deps import get_user_service, get_user_role_service
from app.api.deps.auth import get_current_user
from app.api.deps.rbac import require_roles
from app.models import User
from app.schemas import UserCreate, UserRead, UserRoleAssign, UserRoleRead, RoleSummary
from app.services import UserService, UserRoleService


router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service),
    _: User = Depends(require_roles(["admin"])),
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
    _: User = Depends(get_current_user),
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
    _: User = Depends(get_current_user),
) -> list[UserRead]:
    return service.list()

@router.post(
    "/{user_id}/roles",
    response_model=UserRoleRead,
    status_code=status.HTTP_201_CREATED,
)
def assign_role_to_user(
    user_id: int,
    assignment: UserRoleAssign,
    service: UserRoleService = Depends(get_user_role_service),
    _: User = Depends(require_roles(["admin"])),
) -> UserRoleRead:
    try:
        return service.assign_role(user_id, assignment.role_id)
    except ValueError as e:
        if str(e) in ("User not found", "Role not found"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/{user_id}/roles",
    response_model=list[RoleSummary],
)
def get_user_roles(
    user_id: int,
    service: UserRoleService = Depends(get_user_role_service),
    _: User = Depends(require_roles(["admin"])),
) -> list[RoleSummary]:
    try:
        return service.get_user_roles(user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
