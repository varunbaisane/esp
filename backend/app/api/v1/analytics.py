from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.deps.rbac import require_roles
from app.models.user import User
from app.repositories.ticket_repository import TicketRepository
from app.schemas.ticket import AnalyticsResponse, TicketDistributionStats, SLAAnalytics, ResolutionAnalytics, EscalationAnalytics, WorkloadAnalytics

router = APIRouter()

@router.get("", response_model=AnalyticsResponse)
def get_analytics(
    current_user: User = Depends(require_roles(["ADMIN", "ENGINEERING_MANAGER"])),
    db: Session = Depends(get_db)
):
    repo = TicketRepository(db)
    
    distribution = repo.get_ticket_distribution_stats()
    sla = repo.get_sla_analytics()
    resolution = repo.get_resolution_analytics()
    escalation = repo.get_escalation_analytics()
    workload = repo.get_workload_analytics()
    open_vs_closed_ratio = repo.get_open_vs_closed_ratio()
    
    return AnalyticsResponse(
        distribution=TicketDistributionStats(**distribution),
        sla=SLAAnalytics(**sla),
        resolution=ResolutionAnalytics(**resolution),
        escalation=EscalationAnalytics(**escalation),
        workload=WorkloadAnalytics(**workload),
        open_vs_closed_ratio=open_vs_closed_ratio
    )
