from datetime import datetime
from pydantic import BaseModel, ConfigDict # pyrefly: ignore [missing-import]
from app.models.audit_log import EntityType

class AuditLogBase(BaseModel):
    ticket_id: int | None
    actor_id: int
    actor_name: str
    actor_email: str
    action: str
    entity_type: EntityType
    entity_id: str
    old_value: dict | None = None
    new_value: dict | None = None
    event_metadata: dict | None = None

class AuditLogCreate(AuditLogBase):
    pass

class AuditLogRead(AuditLogBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime

class AuditLogSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ticket_id: int | None
    actor_name: str
    action: str
    entity_type: EntityType
    entity_id: str
    event_metadata: dict | None = None
    created_at: datetime
