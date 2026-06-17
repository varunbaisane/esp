from datetime import datetime
from pydantic import BaseModel, ConfigDict  # pyrefly: ignore [missing-import]

from app.models.ticket import TicketStatus


class TicketCreate(BaseModel):
    title: str
    description: str
    created_by_id: int


class TicketAssign(BaseModel):
    user_id: int


class TicketStatusUpdate(BaseModel):
    status: TicketStatus



class TicketSummary(BaseModel):
    id: int
    title: str
    status: TicketStatus
    created_by_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketRead(BaseModel):
    id: int
    title: str
    description: str
    status: TicketStatus
    created_by_id: int
    assigned_to_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
