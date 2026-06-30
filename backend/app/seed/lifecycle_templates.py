"""
Lifecycle Templates — Pre-defined sequences of audit events for tickets.

Each template is a list of audit action strings. The seed script walks
these sequences to generate realistic audit histories. Templates are
matched to tickets based on their final status.

Actions reference the constants in app.domain.audit_actions.
"""

from app.models.ticket import TicketStatus

# ──────────────────────────────────────────────
# Audit action strings (mirroring audit_actions.py)
# ──────────────────────────────────────────────
CREATED     = "TICKET_CREATED"
ASSIGNED    = "TICKET_ASSIGNED"
CLAIMED     = "TICKET_CLAIMED"
REASSIGNED  = "TICKET_REASSIGNED"
STARTED     = "STATUS_CHANGED"       # OPEN → IN_PROGRESS
ESCALATED  = "TICKET_ESCALATED"
PRIORITY    = "TICKET_UPDATED"       # priority change
RESOLVED    = "TICKET_RESOLVED"
CLOSED      = "TICKET_CLOSED"
REOPENED    = "STATUS_CHANGED"       # special: CLOSED/RESOLVED → OPEN


# ──────────────────────────────────────────────
# Templates for OPEN tickets (2-5 events)
# ──────────────────────────────────────────────
OPEN_TEMPLATES = [
    # A: Just created
    [CREATED],

    # B: Created → Assigned
    [CREATED, ASSIGNED],

    # C: Created → Claimed
    [CREATED, CLAIMED],

    # D: Created → Assigned → Priority Changed
    [CREATED, ASSIGNED, PRIORITY],

    # E: Created → Assigned → Reassigned
    [CREATED, ASSIGNED, REASSIGNED],
]

# ──────────────────────────────────────────────
# Templates for IN_PROGRESS tickets (3-8 events)
# ──────────────────────────────────────────────
IN_PROGRESS_TEMPLATES = [
    # A: Simple start
    [CREATED, ASSIGNED, STARTED],

    # B: Claimed and started
    [CREATED, CLAIMED, STARTED],

    # C: Assigned → Priority Changed → Started
    [CREATED, ASSIGNED, PRIORITY, STARTED],

    # D: Assigned → Reassigned → Started
    [CREATED, ASSIGNED, REASSIGNED, STARTED],

    # E: Assigned → Started → Escalated
    [CREATED, ASSIGNED, STARTED, ESCALATED],

    # F: Assigned → Escalated → Started → Priority Changed
    [CREATED, ASSIGNED, ESCALATED, STARTED, PRIORITY],

    # G: Claimed → Started → Reassigned → Escalated
    [CREATED, CLAIMED, STARTED, REASSIGNED, ESCALATED],
]

# ──────────────────────────────────────────────
# Templates for RESOLVED tickets (4-10 events)
# ──────────────────────────────────────────────
RESOLVED_TEMPLATES = [
    # A: Clean resolution
    [CREATED, ASSIGNED, STARTED, RESOLVED],

    # B: Claimed and resolved
    [CREATED, CLAIMED, STARTED, RESOLVED],

    # C: Priority changed before resolution
    [CREATED, ASSIGNED, PRIORITY, STARTED, RESOLVED],

    # D: Escalated before resolution
    [CREATED, ASSIGNED, STARTED, ESCALATED, RESOLVED],

    # E: Reassigned then resolved
    [CREATED, ASSIGNED, REASSIGNED, STARTED, RESOLVED],

    # F: Complex — reassigned, escalated, priority changed
    [CREATED, ASSIGNED, STARTED, REASSIGNED, ESCALATED, PRIORITY, RESOLVED],

    # G: Full lifecycle — claimed, escalated, priority, resolved
    [CREATED, CLAIMED, STARTED, ESCALATED, PRIORITY, RESOLVED],
]

# ──────────────────────────────────────────────
# Templates for CLOSED tickets (5-15 events)
# ──────────────────────────────────────────────
CLOSED_TEMPLATES = [
    # A: Clean lifecycle
    [CREATED, ASSIGNED, STARTED, RESOLVED, CLOSED],

    # B: Claimed → resolved → closed
    [CREATED, CLAIMED, STARTED, RESOLVED, CLOSED],

    # C: Priority change in the middle
    [CREATED, ASSIGNED, PRIORITY, STARTED, RESOLVED, CLOSED],

    # D: Escalated before close
    [CREATED, ASSIGNED, STARTED, ESCALATED, RESOLVED, CLOSED],

    # E: Reopened then closed again
    [CREATED, ASSIGNED, STARTED, RESOLVED, REOPENED, ASSIGNED, STARTED, RESOLVED, CLOSED],

    # F: Complex — reassigned multiple times
    [CREATED, ASSIGNED, REASSIGNED, STARTED, PRIORITY, ESCALATED, RESOLVED, CLOSED],

    # G: Very complex — escalated twice, priority changed
    [CREATED, ASSIGNED, STARTED, ESCALATED, PRIORITY, REASSIGNED, ESCALATED, RESOLVED, CLOSED],

    # H: Full enterprise lifecycle
    [CREATED, ASSIGNED, STARTED, PRIORITY, REASSIGNED, STARTED, ESCALATED, PRIORITY, RESOLVED, CLOSED],
]


# ──────────────────────────────────────────────
# Template lookup by status
# ──────────────────────────────────────────────
LIFECYCLE_TEMPLATES: dict[TicketStatus, list[list[str]]] = {
    TicketStatus.OPEN: OPEN_TEMPLATES,
    TicketStatus.IN_PROGRESS: IN_PROGRESS_TEMPLATES,
    TicketStatus.RESOLVED: RESOLVED_TEMPLATES,
    TicketStatus.CLOSED: CLOSED_TEMPLATES,
}
