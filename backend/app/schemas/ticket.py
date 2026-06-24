from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, computed_field  # pyrefly: ignore [missing-import]

from app.models.ticket import TicketStatus, TicketPriority, TicketLevel

class SLAStatus(str, Enum):
    HEALTHY = "HEALTHY"
    AT_RISK = "AT_RISK"
    BREACHED = "BREACHED"

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
    open_tickets: int
    breached_tickets: int
    high_priority_tickets: int
    critical_tickets: int
    my_assigned_tickets: int
    unassigned_tickets: int

    model_config = ConfigDict(from_attributes=True)



class TicketSummary(BaseModel):
    id: int
    title: str
    status: TicketStatus
    priority: TicketPriority
    support_level: TicketLevel
    created_by_id: int
    assigned_to_id: int | None
    assigned_to_name: str | None
    created_at: datetime
    sla_due_at: datetime
    closed_at: datetime | None = None

    @computed_field
    @property
    def is_sla_breached(self) -> bool:
        if self.status in [TicketStatus.RESOLVED, TicketStatus.CLOSED]:
            return False
        return datetime.now(timezone.utc) > self.sla_due_at

    @computed_field
    @property
    def sla_status(self) -> SLAStatus:
        if self.status in [TicketStatus.RESOLVED, TicketStatus.CLOSED]:
            return SLAStatus.HEALTHY
            
        now = datetime.now(timezone.utc)
        if now > self.sla_due_at:
            return SLAStatus.BREACHED
            
        remaining = self.sla_due_at - now
        duration = self.sla_due_at - self.created_at
        
        if duration.total_seconds() > 0:
            if (remaining.total_seconds() / duration.total_seconds()) <= 0.25:
                return SLAStatus.AT_RISK
                
        return SLAStatus.HEALTHY

    model_config = ConfigDict(from_attributes=True)


class TicketPaginated(BaseModel):
    items: list[TicketSummary]
    total: int
    limit: int
    offset: int

    model_config = ConfigDict(from_attributes=True)

class WorkspaceStats(BaseModel):
    assigned_tickets: int
    critical_tickets: int
    high_priority_tickets: int
    breached_tickets: int

    model_config = ConfigDict(from_attributes=True)

class WorkspaceResponse(BaseModel):
    stats: WorkspaceStats
    total_assigned_tickets: int
    tickets: list[TicketSummary]

    model_config = ConfigDict(from_attributes=True)

class EngineerWorkload(BaseModel):
    user_id: int
    full_name: str
    role: str
    assigned_tickets: int
    critical_tickets: int
    breached_tickets: int

class TeamOperationsStats(BaseModel):
    l1_active: int
    l2_active: int
    l3_active: int

    l1_unassigned: int
    l2_unassigned: int
    l3_unassigned: int

    l1_breached: int
    l2_breached: int
    l3_breached: int

class TeamOperationsResponse(BaseModel):
    stats: TeamOperationsStats
    workloads: list[EngineerWorkload]


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
    sla_due_at: datetime
    closed_at: datetime | None = None

    @computed_field
    @property
    def is_sla_breached(self) -> bool:
        if self.status in [TicketStatus.RESOLVED, TicketStatus.CLOSED]:
            return False
        return datetime.now(timezone.utc) > self.sla_due_at

    @computed_field
    @property
    def sla_status(self) -> SLAStatus:
        if self.status in [TicketStatus.RESOLVED, TicketStatus.CLOSED]:
            return SLAStatus.HEALTHY
            
        now = datetime.now(timezone.utc)
        if now > self.sla_due_at:
            return SLAStatus.BREACHED
            
        remaining = self.sla_due_at - now
        duration = self.sla_due_at - self.created_at
        if duration.total_seconds() > 0:
            if (remaining.total_seconds() / duration.total_seconds()) <= 0.25:
                return SLAStatus.AT_RISK
                
        return SLAStatus.HEALTHY

    model_config = ConfigDict(from_attributes=True)

class TicketDistributionStats(BaseModel):
    by_status: dict[str, int]
    by_priority: dict[str, int]
    by_level: dict[str, int]

class SLAAnalytics(BaseModel):
    total_active: int
    breached: int
    healthy: int
    at_risk: int
    sla_compliance_percent: float

class ResolutionAnalytics(BaseModel):
    average_resolution_hours: float | None

class EscalationAnalytics(BaseModel):
    total_escalations: int
    l1_to_l2: int
    l2_to_l3: int
    avg_escalations_per_ticket: float

class WorkloadAnalytics(BaseModel):
    max_assigned: int
    avg_assigned: float
    unassigned: int
    workload_distribution: dict[str, int]

class AnalyticsResponse(BaseModel):
    distribution: TicketDistributionStats
    sla: SLAAnalytics
    resolution: ResolutionAnalytics
    escalation: EscalationAnalytics
    workload: WorkloadAnalytics
    open_vs_closed_ratio: float
