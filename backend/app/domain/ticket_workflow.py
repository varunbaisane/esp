from app.models.ticket import TicketStatus

ALLOWED_TRANSITIONS = {
    TicketStatus.OPEN: [TicketStatus.IN_PROGRESS],
    TicketStatus.IN_PROGRESS: [TicketStatus.RESOLVED],
    TicketStatus.RESOLVED: [
        TicketStatus.CLOSED,
        TicketStatus.IN_PROGRESS,
    ],
    TicketStatus.CLOSED: [
        TicketStatus.IN_PROGRESS,
    ],
}

def can_transition(
    current: TicketStatus,
    target: TicketStatus,
) -> bool:
    return target in ALLOWED_TRANSITIONS.get(current, [])
