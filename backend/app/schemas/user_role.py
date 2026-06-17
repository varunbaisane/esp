from datetime import datetime
from pydantic import BaseModel, ConfigDict  # pyrefly: ignore [missing-import]


class UserRoleAssign(BaseModel):
    role_id: int


class RoleSummary(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserRoleRead(BaseModel):
    user_id: int
    role_id: int

    model_config = ConfigDict(from_attributes=True)


class UserSummary(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


