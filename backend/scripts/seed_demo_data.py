"""
Phase 8.6 — Enterprise Demo Dataset & Seed Infrastructure

A deterministic, production-quality seed script that generates 55 realistic
engineering support tickets with audit histories spanning 45 days.

Architecture:
    ensure_users()         → Lookup or create demo users (never duplicate)
    clear_demo_data()      → Delete AuditLog → Ticket (dependency order)
    build_ticket_specs()   → Assemble 55 TicketSpec objects deterministically
    validate_specs()       → Verify all distributions before writing
    seed_tickets()         → Persist tickets to the database
    seed_audit_logs()      → Generate lifecycle audit events per ticket
    print_summary()        → Rich verification output

Usage:
    cd backend
    python scripts/seed_demo_data.py
"""

import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta

# Add the backend root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session  # pyrefly: ignore [missing-import]
from app.db.session import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.ticket import Ticket, TicketPriority, TicketStatus, TicketLevel
from app.models.audit_log import AuditLog, EntityType
from app.domain.ticket_sla import calculate_sla_due
from app.core.security import hash_password

from app.seed.distributions import (
    TOTAL_TICKETS,
    STATUS_DISTRIBUTION,
    PRIORITY_DISTRIBUTION,
    LEVEL_DISTRIBUTION,
    WORKLOAD_DISTRIBUTION,
    UNASSIGNED_COUNT,
    TIME_BUCKETS,
    CATEGORIES,
    DEMO_USERS,
)
from app.seed.ticket_catalog import TICKET_CATALOG
from app.seed.ticket_descriptions import generate_description
from app.seed.lifecycle_templates import LIFECYCLE_TEMPLATES


# ──────────────────────────────────────────────
# Data classes
# ──────────────────────────────────────────────

@dataclass
class TicketSpec:
    """Intermediate representation of a ticket before DB persistence."""
    index: int
    title: str
    description: str
    category: str
    status: TicketStatus
    priority: TicketPriority
    support_level: TicketLevel
    assignee_email: str | None
    creator_email: str
    created_at: datetime
    lifecycle_template: list[str] = field(default_factory=list)


# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────

ROLES = [
    "ADMIN",
    "ENGINEERING_MANAGER",
    "SUPPORT_L1",
    "SUPPORT_L2",
    "SUPPORT_L3",
]

# Creators: all tickets are created by support engineers or managers
CREATOR_POOL = [
    "sarah.l1@esp.com",
    "alice.l1@esp.com",
    "john.l1@esp.com",
    "mike.l2@esp.com",
    "bob.l2@esp.com",
    "charlie.l3@esp.com",
    "manager@esp.com",
]


# ──────────────────────────────────────────────
# 1. ensure_users()
# ──────────────────────────────────────────────

def ensure_users(db: Session) -> dict[str, User]:
    """Lookup or create all demo users. Returns email→User mapping."""
    print("═" * 50)
    print("Ensuring Users")
    print("═" * 50)

    # Ensure roles exist
    role_map: dict[str, Role] = {}
    for role_name in ROLES:
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            role = Role(name=role_name)
            db.add(role)
            db.flush()
            print(f"  ✓ Created role: {role_name}")
        role_map[role_name] = role

    # Ensure users exist
    hashed_password = hash_password("Password123!")
    user_map: dict[str, User] = {}

    for u in DEMO_USERS:
        user = db.query(User).filter(User.email == u["email"]).first()
        if not user:
            user = User(
                email=u["email"],
                full_name=u["full_name"],
                hashed_password=hashed_password,
                email_verified=True,
                email_verified_at=datetime.now(timezone.utc),
                is_system_account=True,
            )
            db.add(user)
            db.flush()
            print(f"  ✓ Created user: {u['full_name']} ({u['email']})")
        else:
            # Ensure system account flag and verification
            user.is_system_account = True
            user.email_verified = True
            if not user.email_verified_at:
                user.email_verified_at = datetime.now(timezone.utc)
            db.flush()
            print(f"  • Reusing user: {u['full_name']} ({u['email']})")

        # Assign role if missing
        role = role_map.get(u["role"])
        if role and role not in user.roles:
            user.roles.append(role)
            db.flush()
            print(f"    → Assigned role: {u['role']}")

        user_map[u["email"]] = user

    print(f"\n  Total users: {len(user_map)}\n")
    return user_map


# ──────────────────────────────────────────────
# 2. clear_demo_data()
# ──────────────────────────────────────────────

def clear_demo_data(db: Session) -> None:
    """Delete all tickets and audit logs in dependency order."""
    print("═" * 50)
    print("Clearing Demo Data")
    print("═" * 50)

    # 1. AuditLog (depends on Ticket via FK)
    audit_count = db.query(AuditLog).delete()
    print(f"  ✓ Deleted {audit_count} audit logs")

    # 2. Tickets
    ticket_count = db.query(Ticket).delete()
    print(f"  ✓ Deleted {ticket_count} tickets")

    db.flush()
    print()


# ──────────────────────────────────────────────
# 3. build_ticket_specs()
# ──────────────────────────────────────────────

def build_ticket_specs() -> list[TicketSpec]:
    """Build 55 deterministic TicketSpec objects from the catalog."""
    print("═" * 50)
    print("Building Ticket Specifications")
    print("═" * 50)

    now = datetime.now(timezone.utc)

    # ── Step 1: Build flat arrays for each dimension ──
    statuses: list[TicketStatus] = []
    for status, count in STATUS_DISTRIBUTION.items():
        statuses.extend([status] * count)

    priorities: list[TicketPriority] = []
    for priority, count in PRIORITY_DISTRIBUTION.items():
        priorities.extend([priority] * count)

    levels: list[TicketLevel] = []
    for level, count in LEVEL_DISTRIBUTION.items():
        levels.extend([level] * count)

    # ── Step 2: Build assignment pool ──
    # Put assigned engineers first, unassigned (None) last.
    # This way unassigned slots align with OPEN tickets at the end of the OPEN block.
    assigned_pool: list[str | None] = []
    for email, count in WORKLOAD_DISTRIBUTION.items():
        if email is not None:
            assigned_pool.extend([email] * count)
    unassigned_pool: list[None] = [None] * UNASSIGNED_COUNT

    # Interleave: non-OPEN tickets get assigned engineers,
    # OPEN tickets get a mix of assigned + unassigned.
    # Strategy: assigned pool covers IN_PROGRESS/RESOLVED/CLOSED first,
    # then fills remaining OPEN slots. Unassigned fills the rest of OPEN.
    non_open_count = TOTAL_TICKETS - STATUS_DISTRIBUTION[TicketStatus.OPEN]
    assigned_for_non_open = assigned_pool[:non_open_count]
    assigned_for_open = assigned_pool[non_open_count:]
    open_assignments: list[str | None] = assigned_for_open + unassigned_pool

    # Final assignment array: first non-open statuses, then open
    # But statuses array is: [OPEN x18, IN_PROGRESS x14, RESOLVED x12, CLOSED x11]
    # We need to reorder so OPEN is last for assignment alignment.
    # Better: build specs status-by-status.

    # ── Step 3: Build timestamps from time buckets ──
    timestamps: list[datetime] = []
    for days_ago, count in TIME_BUCKETS:
        for i in range(count):
            jitter_hours = (i + 1) * 2.5
            jitter_minutes = (i * 17) % 60
            ts = now - timedelta(days=days_ago, hours=jitter_hours, minutes=jitter_minutes)
            timestamps.append(ts)

    # ── Step 4: Select 55 catalog entries ──
    catalog_entries = TICKET_CATALOG[:TOTAL_TICKETS]

    # ── Step 5: Build specs by status group to align assignments ──
    # Order: IN_PROGRESS, RESOLVED, CLOSED (all assigned), then OPEN (mix)
    status_groups = [
        (TicketStatus.IN_PROGRESS, STATUS_DISTRIBUTION[TicketStatus.IN_PROGRESS]),
        (TicketStatus.RESOLVED, STATUS_DISTRIBUTION[TicketStatus.RESOLVED]),
        (TicketStatus.CLOSED, STATUS_DISTRIBUTION[TicketStatus.CLOSED]),
        (TicketStatus.OPEN, STATUS_DISTRIBUTION[TicketStatus.OPEN]),
    ]

    ordered_statuses: list[TicketStatus] = []
    for status, count in status_groups:
        ordered_statuses.extend([status] * count)

    # Re-allocate timestamps to fix SLA:
    # We want OPEN and IN_PROGRESS to get the newest timestamps,
    # and RESOLVED/CLOSED to get the oldest.
    # Timestamps are currently sorted newest to oldest.
    active_count = STATUS_DISTRIBUTION[TicketStatus.OPEN] + STATUS_DISTRIBUTION[TicketStatus.IN_PROGRESS]
    resolved_count = STATUS_DISTRIBUTION[TicketStatus.RESOLVED] + STATUS_DISTRIBUTION[TicketStatus.CLOSED]
    
    newest_ts = timestamps[:active_count]
    oldest_ts = timestamps[active_count:]
    
    # We need to map these to our ordered_statuses:
    # ordered_statuses = IN_PROGRESS (from newest), RESOLVED (from oldest), CLOSED (from oldest), OPEN (from newest)
    in_prog_ts = newest_ts[:STATUS_DISTRIBUTION[TicketStatus.IN_PROGRESS]]
    open_ts = newest_ts[STATUS_DISTRIBUTION[TicketStatus.IN_PROGRESS]:]
    
    res_ts = oldest_ts[:STATUS_DISTRIBUTION[TicketStatus.RESOLVED]]
    clos_ts = oldest_ts[STATUS_DISTRIBUTION[TicketStatus.RESOLVED]:]
    
    ordered_timestamps = in_prog_ts + res_ts + clos_ts + open_ts

    # Assignments in order: assigned for non-open, then open_assignments
    ordered_assignments: list[str | None] = assigned_for_non_open + open_assignments

    # Lifecycle templates
    template_counters: dict[TicketStatus, int] = {s: 0 for s in TicketStatus}
    template_assignments: list[list[str]] = []
    for status in ordered_statuses:
        templates = LIFECYCLE_TEMPLATES[status]
        idx = template_counters[status] % len(templates)
        template_assignments.append(templates[idx])
        template_counters[status] += 1

    # ── Step 6: Assemble TicketSpecs ──
    specs: list[TicketSpec] = []
    for i in range(TOTAL_TICKETS):
        catalog = catalog_entries[i]
        creator = CREATOR_POOL[i % len(CREATOR_POOL)]

        spec = TicketSpec(
            index=i,
            title=catalog["title"],
            description=generate_description(catalog["title"], catalog["category"]),
            category=catalog["category"],
            status=ordered_statuses[i],
            priority=priorities[i],
            support_level=levels[i],
            assignee_email=ordered_assignments[i],
            creator_email=creator,
            created_at=ordered_timestamps[i],
            lifecycle_template=template_assignments[i],
        )
        specs.append(spec)

    print(f"  ✓ Built {len(specs)} ticket specifications\n")
    return specs


# ──────────────────────────────────────────────
# 4. validate_specs()
# ──────────────────────────────────────────────

def validate_specs(specs: list[TicketSpec]) -> None:
    """Validate all distributions before writing to the database."""
    print("═" * 50)
    print("Validating Distributions")
    print("═" * 50)

    errors: list[str] = []

    # Total count
    if len(specs) != TOTAL_TICKETS:
        errors.append(f"Expected {TOTAL_TICKETS} tickets, got {len(specs)}")

    # Status distribution
    status_counts: dict[TicketStatus, int] = {}
    for spec in specs:
        status_counts[spec.status] = status_counts.get(spec.status, 0) + 1
    for status, expected in STATUS_DISTRIBUTION.items():
        actual = status_counts.get(status, 0)
        if actual != expected:
            errors.append(f"Status {status.value}: expected {expected}, got {actual}")

    # Priority distribution
    priority_counts: dict[TicketPriority, int] = {}
    for spec in specs:
        priority_counts[spec.priority] = priority_counts.get(spec.priority, 0) + 1
    for priority, expected in PRIORITY_DISTRIBUTION.items():
        actual = priority_counts.get(priority, 0)
        if actual != expected:
            errors.append(f"Priority {priority.value}: expected {expected}, got {actual}")

    # Level distribution
    level_counts: dict[TicketLevel, int] = {}
    for spec in specs:
        level_counts[spec.support_level] = level_counts.get(spec.support_level, 0) + 1
    for level, expected in LEVEL_DISTRIBUTION.items():
        actual = level_counts.get(level, 0)
        if actual != expected:
            errors.append(f"Level {level.value}: expected {expected}, got {actual}")

    # Assignment distribution
    assignment_counts: dict[str | None, int] = {}
    for spec in specs:
        assignment_counts[spec.assignee_email] = assignment_counts.get(spec.assignee_email, 0) + 1
    for email, expected in WORKLOAD_DISTRIBUTION.items():
        actual = assignment_counts.get(email, 0)
        if actual != expected:
            errors.append(f"Assignment {email}: expected {expected}, got {actual}")

    # Unique titles
    titles = [spec.title for spec in specs]
    if len(titles) != len(set(titles)):
        errors.append("Duplicate ticket titles detected")

    if errors:
        print("\n  ✗ VALIDATION FAILED:")
        for e in errors:
            print(f"    - {e}")
        raise RuntimeError(f"Dataset validation failed with {len(errors)} errors: {'; '.join(errors)}")

    print("  ✓ Total tickets: OK")
    print("  ✓ Status distribution: OK")
    print("  ✓ Priority distribution: OK")
    print("  ✓ Level distribution: OK")
    print("  ✓ Assignment distribution: OK")
    print("  ✓ Unique titles: OK")
    print()


# ──────────────────────────────────────────────
# 5. seed_tickets()
# ──────────────────────────────────────────────

def seed_tickets(
    db: Session,
    specs: list[TicketSpec],
    user_map: dict[str, User],
) -> list[Ticket]:
    """Persist TicketSpec objects to the database. Returns created Ticket objects."""
    print("═" * 50)
    print("Seeding Tickets")
    print("═" * 50)

    now = datetime.now(timezone.utc)
    tickets: list[Ticket] = []

    # Keep track of how many we've assigned to each SLA bucket to match targets exactly
    sla_bucket_counts = {"HEALTHY": 0, "NEAR": 0, "BREACHED": 0}

    for spec in specs:
        creator = user_map[spec.creator_email]
        assignee = user_map.get(spec.assignee_email) if spec.assignee_email else None
        
        # Get SLA limit for this priority
        sla_hours = 48
        if spec.priority == TicketPriority.CRITICAL:
            sla_hours = 4
        elif spec.priority == TicketPriority.HIGH:
            sla_hours = 24
        elif spec.priority == TicketPriority.LOW:
            sla_hours = 72

        # Assign a target bucket to hit exact numbers: 37 Healthy, 10 Near Breach, 8 Breached
        target_bucket = "HEALTHY"
        if spec.status in (TicketStatus.OPEN, TicketStatus.IN_PROGRESS):
            if sla_bucket_counts["NEAR"] < 10:
                target_bucket = "NEAR"
                sla_bucket_counts["NEAR"] += 1
            elif sla_bucket_counts["BREACHED"] < 3:
                target_bucket = "BREACHED"
                sla_bucket_counts["BREACHED"] += 1
            else:
                sla_bucket_counts["HEALTHY"] += 1
        else:
            if sla_bucket_counts["BREACHED"] < 8:
                target_bucket = "BREACHED"
                sla_bucket_counts["BREACHED"] += 1
            else:
                sla_bucket_counts["HEALTHY"] += 1

        # Adjust created_at / closed_at to fit the bucket
        closed_at = None
        
        if spec.status in (TicketStatus.RESOLVED, TicketStatus.CLOSED):
            # For closed tickets, we keep created_at as is, and modify closed_at
            if target_bucket == "HEALTHY":
                # Close it halfway through its SLA window
                closed_at = spec.created_at + timedelta(hours=sla_hours / 2)
            else:
                # BREACHED: Close it 2 hours after SLA
                closed_at = spec.created_at + timedelta(hours=sla_hours + 2)
                
            if closed_at > now:
                # If it pushes into the future, pull created_at backward
                diff = closed_at - now
                spec.created_at = spec.created_at - diff - timedelta(hours=1)
                closed_at = now - timedelta(hours=1)
        else:
            # For open tickets, we modify created_at relative to now
            if target_bucket == "HEALTHY":
                # Created recently
                spec.created_at = now - timedelta(hours=sla_hours / 4)
            elif target_bucket == "NEAR":
                # Created close to SLA limit
                spec.created_at = now - timedelta(hours=sla_hours - 2)
            else:
                # BREACHED
                spec.created_at = now - timedelta(hours=sla_hours + 2)

        sla_due = calculate_sla_due(spec.priority, spec.created_at)

        ticket = Ticket(
            title=spec.title,
            description=spec.description,
            status=spec.status,
            priority=spec.priority,
            support_level=spec.support_level,
            created_by_id=creator.id,
            assigned_to_id=assignee.id if assignee else None,
            created_at=spec.created_at,
            sla_due_at=sla_due,
            updated_at=spec.created_at + timedelta(hours=1),
            closed_at=closed_at,
        )
        db.add(ticket)
        tickets.append(ticket)

    db.flush()  # Get IDs assigned
    print(f"  ✓ Created {len(tickets)} tickets\n")
    return tickets


# ──────────────────────────────────────────────
# 6. seed_audit_logs()
# ──────────────────────────────────────────────

def seed_audit_logs(
    db: Session,
    specs: list[TicketSpec],
    tickets: list[Ticket],
    user_map: dict[str, User],
) -> int:
    """Generate audit log entries from lifecycle templates. Returns total count."""
    print("═" * 50)
    print("Seeding Audit Logs")
    print("═" * 50)

    total_logs = 0

    for spec, ticket in zip(specs, tickets):
        template = spec.lifecycle_template
        base_time = spec.created_at
        creator = user_map[spec.creator_email]
        assignee = user_map.get(spec.assignee_email) if spec.assignee_email else None

        for step_idx, action in enumerate(template):
            # Progress timestamps by 30-120 minutes per step
            event_time = base_time + timedelta(
                minutes=(step_idx + 1) * 45 + (spec.index % 30)
            )

            # Determine actor based on action type
            actor = creator
            if action in ("TICKET_ASSIGNED", "TICKET_REASSIGNED"):
                # Manager or admin assigns
                actor = user_map.get("manager@esp.com", creator)
            elif action in ("TICKET_CLAIMED",):
                actor = assignee if assignee else creator
            elif action in ("TICKET_ESCALATED",):
                actor = assignee if assignee else creator
            elif action in ("TICKET_RESOLVED", "TICKET_CLOSED"):
                actor = assignee if assignee else creator
            elif action == "STATUS_CHANGED":
                actor = assignee if assignee else creator

            # Build metadata
            old_value = None
            new_value = None
            event_metadata = None

            if action == "TICKET_CREATED":
                event_time = spec.created_at  # First event = creation time
                new_value = {
                    "title": ticket.title,
                    "priority": ticket.priority.value,
                    "support_level": ticket.support_level.value,
                }
            elif action == "TICKET_ASSIGNED":
                event_metadata = {
                    "previous_owner": None,
                    "new_owner": assignee.full_name if assignee else "Unassigned",
                }
            elif action == "TICKET_CLAIMED":
                event_metadata = {
                    "previous_owner": None,
                    "new_owner": actor.full_name,
                }
            elif action == "TICKET_REASSIGNED":
                # Simulate reassignment from one engineer to another
                prev_owner = CREATOR_POOL[(spec.index + 1) % len(CREATOR_POOL)]
                event_metadata = {
                    "previous_owner": user_map.get(prev_owner, creator).full_name,
                    "new_owner": assignee.full_name if assignee else "Unassigned",
                }
            elif action == "STATUS_CHANGED":
                # Determine from/to based on position in template
                if step_idx < len(template) - 1:
                    event_metadata = {
                        "from_status": "OPEN",
                        "to_status": "IN_PROGRESS",
                    }
                else:
                    event_metadata = {
                        "from_status": "RESOLVED",
                        "to_status": "OPEN",
                    }
            elif action == "TICKET_UPDATED":
                # Priority change
                old_priorities = ["LOW", "MEDIUM", "HIGH"]
                old_p = old_priorities[spec.index % len(old_priorities)]
                event_metadata = {
                    "field": "priority",
                    "old_value": old_p,
                    "new_value": ticket.priority.value,
                }
            elif action == "TICKET_ESCALATED":
                levels = ["L1", "L2", "L3"]
                current_idx = levels.index(ticket.support_level.value) if ticket.support_level.value in levels else 0
                from_level = levels[max(0, current_idx - 1)]
                event_metadata = {
                    "from_level": from_level,
                    "to_level": ticket.support_level.value,
                }
            elif action == "TICKET_RESOLVED":
                event_metadata = {
                    "from_status": "IN_PROGRESS",
                    "to_status": "RESOLVED",
                }
            elif action == "TICKET_CLOSED":
                event_metadata = {
                    "from_status": "RESOLVED",
                    "to_status": "CLOSED",
                }

            audit = AuditLog(
                ticket_id=ticket.id,
                actor_id=actor.id,
                actor_name=actor.full_name,
                actor_email=actor.email,
                action=action,
                entity_type=EntityType.TICKET,
                entity_id=str(ticket.id),
                old_value=old_value,
                new_value=new_value,
                event_metadata=event_metadata,
                created_at=event_time,
            )
            db.add(audit)
            total_logs += 1

    db.flush()
    print(f"  ✓ Created {total_logs} audit log entries\n")
    return total_logs


# ──────────────────────────────────────────────
# 7. print_summary()
# ──────────────────────────────────────────────

def print_summary(
    db: Session,
    user_map: dict[str, User],
) -> None:
    """Print a rich verification summary."""
    now = datetime.now(timezone.utc)

    ticket_count = db.query(Ticket).count()
    audit_count = db.query(AuditLog).count()

    # Status counts
    status_counts: dict[str, int] = {}
    for status in TicketStatus:
        count = db.query(Ticket).filter(Ticket.status == status).count()
        status_counts[status.value] = count

    # Priority counts
    priority_counts: dict[str, int] = {}
    for priority in TicketPriority:
        count = db.query(Ticket).filter(Ticket.priority == priority).count()
        priority_counts[priority.value] = count

    # Level counts
    level_counts: dict[str, int] = {}
    for level in TicketLevel:
        count = db.query(Ticket).filter(Ticket.support_level == level).count()
        level_counts[level.value] = count

    # Assignment counts
    assignment_counts: dict[str, int] = {}
    for u in DEMO_USERS:
        user = user_map[u["email"]]
        count = db.query(Ticket).filter(Ticket.assigned_to_id == user.id).count()
        if count > 0:
            assignment_counts[u["full_name"]] = count
    unassigned = db.query(Ticket).filter(Ticket.assigned_to_id.is_(None)).count()
    assignment_counts["Unassigned"] = unassigned

    # SLA distribution
    sla_healthy = 0
    sla_near_breach = 0
    sla_breached = 0
    all_tickets = db.query(Ticket).all()
    for t in all_tickets:
        if t.status in (TicketStatus.CLOSED, TicketStatus.RESOLVED):
            # Use closed_at or updated_at for comparison
            check_time = t.closed_at or t.updated_at
            if check_time and check_time > t.sla_due_at:
                sla_breached += 1
            else:
                sla_healthy += 1
        else:
            # Open/In Progress: check against now
            if now > t.sla_due_at:
                sla_breached += 1
            elif (t.sla_due_at - now).total_seconds() < 3600 * 4:  # within 4 hours
                sla_near_breach += 1
            else:
                sla_healthy += 1

    # Print
    print()
    print("═" * 50)
    print("  Enterprise Demo Dataset Seeded")
    print("═" * 50)
    print()
    print(f"  Users               : {len(user_map)}")
    print(f"  Tickets             : {ticket_count}")
    print(f"  Audit Logs          : {audit_count}")
    print()
    print("  Status")
    print("  " + "─" * 30)
    for status, count in status_counts.items():
        print(f"  {status:<20}: {count}")
    print()
    print("  Priority")
    print("  " + "─" * 30)
    for priority, count in priority_counts.items():
        print(f"  {priority:<20}: {count}")
    print()
    print("  Support Level")
    print("  " + "─" * 30)
    for level, count in level_counts.items():
        print(f"  {level:<20}: {count}")
    print()
    print("  Assignments")
    print("  " + "─" * 30)
    for name, count in assignment_counts.items():
        print(f"  {name:<20}: {count}")
    print()
    print("  SLA")
    print("  " + "─" * 30)
    print(f"  {'Healthy':<20}: {sla_healthy}")
    print(f"  {'Near Breach':<20}: {sla_near_breach}")
    print(f"  {'Breached':<20}: {sla_breached}")
    print()

    # Validation
    all_pass = True
    checks = [
        ("55 tickets", ticket_count == TOTAL_TICKETS),
        ("Audit logs created", audit_count > 0),
        ("Status OPEN", status_counts.get("OPEN", 0) == STATUS_DISTRIBUTION[TicketStatus.OPEN]),
        ("Status IN_PROGRESS", status_counts.get("IN_PROGRESS", 0) == STATUS_DISTRIBUTION[TicketStatus.IN_PROGRESS]),
        ("Status RESOLVED", status_counts.get("RESOLVED", 0) == STATUS_DISTRIBUTION[TicketStatus.RESOLVED]),
        ("Status CLOSED", status_counts.get("CLOSED", 0) == STATUS_DISTRIBUTION[TicketStatus.CLOSED]),
        ("No orphan audit logs", db.query(AuditLog).filter(AuditLog.ticket_id.is_(None)).count() == 0),
    ]

    for label, passed in checks:
        symbol = "✓" if passed else "✗"
        print(f"  {symbol} {label}")
        if not passed:
            all_pass = False

    print()
    if all_pass:
        print("  ✓ All validations passed")
    else:
        print("  ✗ Some validations failed — review data above")
    print()
    print("═" * 50)


# ──────────────────────────────────────────────
# Main orchestrator
# ──────────────────────────────────────────────

def seed_data(db_session: Session | None = None) -> None:
    """Main entry point. Orchestrates the full seed pipeline."""
    db: Session = db_session if db_session else SessionLocal()
    try:
        # 1. Ensure users exist
        user_map = ensure_users(db)

        # 2. Clear old demo data
        clear_demo_data(db)

        # 3. Build ticket specifications (in-memory)
        specs = build_ticket_specs()

        # 4. Validate BEFORE writing
        validate_specs(specs)

        # 5. Persist tickets
        tickets = seed_tickets(db, specs, user_map)

        # 6. Generate audit logs from lifecycle templates
        seed_audit_logs(db, specs, tickets, user_map)

        # 7. Commit everything
        db.commit()

        # 8. Print rich summary
        print_summary(db, user_map)

    except Exception as e:
        db.rollback()
        print(f"\n  ✗ ERROR: {e}")
        raise
    finally:
        if not db_session:
            db.close()


if __name__ == "__main__":
    seed_data()
