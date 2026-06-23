from datetime import datetime, timedelta
from app.models.ticket import TicketPriority

SLA_HOURS = {
    TicketPriority.LOW: 72,
    TicketPriority.MEDIUM: 48,
    TicketPriority.HIGH: 24,
    TicketPriority.CRITICAL: 4,
}

def calculate_sla_due(priority: TicketPriority, created_at: datetime) -> datetime:
    hours = SLA_HOURS.get(priority, 48)  # default to MEDIUM if somehow missing
    return created_at + timedelta(hours=hours)
