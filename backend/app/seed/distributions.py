"""
Distributions — Hardcoded distribution constants for the enterprise demo dataset.

These define the exact counts for statuses, priorities, support levels,
and per-engineer workloads. The seed script enforces these before writing
to the database.
"""

from app.models.ticket import TicketStatus, TicketPriority, TicketLevel

# ──────────────────────────────────────────────
# Total tickets
# ──────────────────────────────────────────────
TOTAL_TICKETS = 55

# ──────────────────────────────────────────────
# Status distribution
# ──────────────────────────────────────────────
STATUS_DISTRIBUTION: dict[TicketStatus, int] = {
    TicketStatus.OPEN: 18,
    TicketStatus.IN_PROGRESS: 14,
    TicketStatus.RESOLVED: 12,
    TicketStatus.CLOSED: 11,
}

# ──────────────────────────────────────────────
# Priority distribution
# ──────────────────────────────────────────────
PRIORITY_DISTRIBUTION: dict[TicketPriority, int] = {
    TicketPriority.CRITICAL: 6,
    TicketPriority.HIGH: 14,
    TicketPriority.MEDIUM: 21,
    TicketPriority.LOW: 14,
}

# ──────────────────────────────────────────────
# Support level distribution
# ──────────────────────────────────────────────
LEVEL_DISTRIBUTION: dict[TicketLevel, int] = {
    TicketLevel.L1: 30,
    TicketLevel.L2: 18,
    TicketLevel.L3: 7,
}

# ──────────────────────────────────────────────
# Engineer workload distribution
#
# Keys are user emails. Values are number of
# tickets to assign. None = unassigned.
# ──────────────────────────────────────────────
WORKLOAD_DISTRIBUTION: dict[str | None, int] = {
    "sarah.l1@esp.com": 8,       # busiest L1
    "john.l1@esp.com": 7,
    "alice.l1@esp.com": 6,
    "mike.l2@esp.com": 8,        # busiest L2
    "bob.l2@esp.com": 6,
    "charlie.l3@esp.com": 5,     # busiest L3
    "david.l3@esp.com": 3,       # least busy
    None: 0,  # Placeholder — calculated dynamically
}

# Unassigned is the remainder
UNASSIGNED_COUNT = TOTAL_TICKETS - sum(
    v for k, v in WORKLOAD_DISTRIBUTION.items() if k is not None
)
# Replace placeholder
WORKLOAD_DISTRIBUTION[None] = UNASSIGNED_COUNT


# ──────────────────────────────────────────────
# Time buckets for deterministic timestamp spread
# Values are (days_ago, number_of_tickets)
# ──────────────────────────────────────────────
TIME_BUCKETS: list[tuple[int, int]] = [
    (0, 5),      # today
    (1, 5),      # yesterday
    (2, 4),      # 2 days ago
    (4, 5),      # 4 days ago
    (7, 7),      # 1 week ago
    (14, 8),     # 2 weeks ago
    (21, 6),     # 3 weeks ago
    (30, 8),     # 1 month ago
    (38, 4),     # ~5 weeks ago
    (45, 3),     # 45 days ago
]

# ──────────────────────────────────────────────
# SLA targets (approximate)
# ──────────────────────────────────────────────
SLA_HEALTHY_TARGET = 37
SLA_NEAR_BREACH_TARGET = 10
SLA_BREACHED_TARGET = 8

# ──────────────────────────────────────────────
# Categories
# ──────────────────────────────────────────────
CATEGORIES = [
    "Authentication",
    "Backend API",
    "Frontend",
    "Database",
    "Infrastructure",
    "DevOps",
    "Performance",
    "Security",
    "Integrations",
]

# ──────────────────────────────────────────────
# User definitions (lookup/create, never duplicate)
# ──────────────────────────────────────────────
DEMO_USERS = [
    {"email": "admin@esp.com",     "full_name": "Alex Morgan",    "role": "ADMIN"},
    {"email": "manager@esp.com",   "full_name": "Emma Davis",     "role": "ENGINEERING_MANAGER"},
    {"email": "sarah.l1@esp.com",  "full_name": "Sarah Connor",   "role": "SUPPORT_L1"},
    {"email": "alice.l1@esp.com",  "full_name": "Alice Johnson",  "role": "SUPPORT_L1"},
    {"email": "john.l1@esp.com",   "full_name": "John Doe",       "role": "SUPPORT_L1"},
    {"email": "bob.l2@esp.com",    "full_name": "Bob Smith",      "role": "SUPPORT_L2"},
    {"email": "mike.l2@esp.com",   "full_name": "Mike Wazowski",  "role": "SUPPORT_L2"},
    {"email": "charlie.l3@esp.com","full_name": "Charlie Brown",  "role": "SUPPORT_L3"},
    {"email": "david.l3@esp.com",  "full_name": "David Wallace",  "role": "SUPPORT_L3"},
]
