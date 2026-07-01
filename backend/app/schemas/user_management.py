from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from app.core.roles import RoleOperation

class RoleData(BaseModel):
    code: str
    display_name: str

class UserSummaryResponse(BaseModel):
    id: int
    name: str
    email: str
    account_status: str
    current_role: Optional[RoleData]
    joined_at: datetime
    last_login_at: Optional[datetime] = None
    assignable_roles: List[str] = []

    class Config:
        from_attributes = True

class RoleOperationRequest(BaseModel):
    operation: RoleOperation
    role_code: str
