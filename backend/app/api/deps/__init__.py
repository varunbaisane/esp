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

from app.services.notification_service import NotificationService
from app.repositories.notification_repository import NotificationRepository
from app.services.email_service import EmailService
from app.services.notification_delivery_dispatcher import NotificationDeliveryDispatcher
from app.email.factory import get_email_provider
from app.email.base import BaseEmailProvider

def get_email_service() -> EmailService:
    provider = get_email_provider()
    return EmailService(provider)

def get_notification_delivery_dispatcher(
    email_service: EmailService = Depends(get_email_service)
) -> NotificationDeliveryDispatcher:
    return NotificationDeliveryDispatcher(email_service)

def get_notification_service(
    db: Session = Depends(get_db),
    dispatcher: NotificationDeliveryDispatcher = Depends(get_notification_delivery_dispatcher)
) -> NotificationService:
    return NotificationService(NotificationRepository(db), dispatcher)

