from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr  # pyright: ignore[reportMissingImports]


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
