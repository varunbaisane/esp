from fastapi import APIRouter, Depends, HTTPException, status # pyrefly: ignore [missing-import]

from app.api.deps import get_role_service, get_user_role_service
from app.api.deps.rbac import require_roles
from app.models import User
from app.schemas import RoleCreate, RoleRead, UserSummary
from app.services import RoleService, UserRoleService


router = APIRouter(prefix="/roles", tags=["Roles"])


@router.post(
    "",
    response_model=RoleRead,
    status_code=status.HTTP_201_CREATED,
)
def create_role(
    role_data: RoleCreate,
    service: RoleService = Depends(get_role_service),
    _: User = Depends(require_roles(["admin"])),
) -> RoleRead:
    try:
        return service.create(role_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/{role_id}",
    response_model=RoleRead,
)
def get_role(
    role_id: int,
    service: RoleService = Depends(get_role_service),
    _: User = Depends(require_roles(["admin"])),
) -> RoleRead:
    role = service.get_by_id(role_id)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    return role


@router.get(
    "",
    response_model=list[RoleRead],
)
def list_roles(
    service: RoleService = Depends(get_role_service),
    _: User = Depends(require_roles(["admin"])),
) -> list[RoleRead]:
    return service.list()


@router.get(
    "/{role_id}/users",
    response_model=list[UserSummary],
)
def get_role_users(
    role_id: int,
    service: UserRoleService = Depends(get_user_role_service),
    _: User = Depends(require_roles(["admin"])),
) -> list[UserSummary]:
    try:
        return service.get_role_users(role_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

