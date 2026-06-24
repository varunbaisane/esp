from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr  # pyright: ignore[reportMissingImports]


class UserCreate(BaseModel):
    email: str
    full_name: str


from app.schemas.role import RoleRead

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    roles: list[RoleRead] = []
