from datetime import datetime
from pydantic import BaseModel, ConfigDict  # pyrefly: ignore [missing-import]

from app.models.ticket import TicketStatus, TicketPriority, TicketLevel

class TicketCreate(BaseModel):
    title: str
    description: str
    priority: TicketPriority

class TicketUpdate(BaseModel):
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    assigned_to_id: int | None = None


class TicketAssign(BaseModel):
    user_id: int


class TicketStatusUpdate(BaseModel):
    status: TicketStatus


class TicketStats(BaseModel):
    open: int
    in_progress: int
    resolved: int
    closed: int
    total: int

    model_config = ConfigDict(from_attributes=True)



class TicketSummary(BaseModel):
    id: int
    title: str
    status: TicketStatus
    priority: TicketPriority
    support_level: TicketLevel
    created_by_id: int
    assigned_to_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketRead(BaseModel):
    id: int
    title: str
    description: str
    status: TicketStatus
    priority: TicketPriority
    support_level: TicketLevel
    created_by_id: int
    created_by_name: str
    assigned_to_id: int | None
    assigned_to_name: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
