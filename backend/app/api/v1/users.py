
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


from typing import Optional
from app.api.deps import get_user_service, get_user_management_service, get_role_provisioning_service
from app.services.user_management_service import UserManagementService
from app.services.role_provisioning_service import RoleProvisioningService
from app.schemas.user_management import UserSummaryResponse, RoleOperationRequest
from app.core.roles import RoleOperation

@router.get(
    "",
    response_model=list[UserSummaryResponse],
)
def list_users(
    search: Optional[str] = None,
    status: Optional[str] = None,
    role: Optional[str] = None,
    service: UserManagementService = Depends(get_user_management_service),
    current_user: User = Depends(require_roles(["admin", "engineering_manager"])),
) -> list[UserSummaryResponse]:
    return service.list_users(requester=current_user, search=search, status=status, role=role)

@router.patch(
    "/{user_id}/roles",
    status_code=status.HTTP_200_OK,
)
def operate_role_on_user(
    user_id: int,
    request: RoleOperationRequest,
    service: RoleProvisioningService = Depends(get_role_provisioning_service),
    current_user: User = Depends(require_roles(["admin", "engineering_manager"])),
):
    try:
        if request.operation == RoleOperation.ASSIGN:
            service.assign_role(user_id, request.role_code, current_user)
        elif request.operation == RoleOperation.REMOVE:
            service.remove_role(user_id, request.role_code, current_user)
        return {"status": "success"}
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
