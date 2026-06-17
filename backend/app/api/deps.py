from typing import Generator

from fastapi import Depends # pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session  # pyrefly: ignore [missing-import]

from app.db.session import get_db
from app.services import UserService, RoleService


def get_user_service(
    db: Session = Depends(get_db),
) -> UserService:
    return UserService(db)


def get_role_service(
    db: Session = Depends(get_db),
) -> RoleService:
    return RoleService(db)
