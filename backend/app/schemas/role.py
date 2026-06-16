from datetime import datetime

from pydantic import BaseModel # pyrefly: ignore [missing-import]
from pydantic import ConfigDict # pyrefly: ignore [missing-import]

class RoleCreate(BaseModel):
    name: str
    description: str | None = None


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
