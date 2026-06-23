from app.models.ticket import TicketLevel

ESCALATION_PATH = {
    TicketLevel.L1: TicketLevel.L2,
    TicketLevel.L2: TicketLevel.L3,
    TicketLevel.L3: None,
}

def get_next_level(level: TicketLevel) -> TicketLevel | None:
    return ESCALATION_PATH.get(level)
