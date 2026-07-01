from typing import Generator

from fastapi import Depends # pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session  # pyrefly: ignore [missing-import]

from app.db.session import get_db
from app.services import UserService, RoleService, UserRoleService, TicketService
from app.services.ticket_permission_service import TicketPermissionService


def get_user_service(
    db: Session = Depends(get_db),
) -> UserService:
    return UserService(db)


def get_role_service(
    db: Session = Depends(get_db),
) -> RoleService:
    return RoleService(db)


def get_user_role_service(
    db: Session = Depends(get_db),
) -> UserRoleService:
    return UserRoleService(db)


def get_ticket_service(
    db: Session = Depends(get_db),
) -> TicketService:
    return TicketService(db)

def get_ticket_permission_service() -> TicketPermissionService:
    return TicketPermissionService()

from app.services.user_management_service import UserManagementService
from app.services.role_provisioning_service import RoleProvisioningService

def get_user_management_service(db: Session = Depends(get_db)) -> UserManagementService:
    return UserManagementService(db)

def get_role_provisioning_service(db: Session = Depends(get_db)) -> RoleProvisioningService:
    return RoleProvisioningService(db)
