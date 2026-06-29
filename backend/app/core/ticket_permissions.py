
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Set, Optional, FrozenSet

from app.models.ticket import TicketStatus


ROLE_SUPPORT_L1 = "SUPPORT_L1"
ROLE_SUPPORT_L2 = "SUPPORT_L2"
ROLE_SUPPORT_L3 = "SUPPORT_L3"
ROLE_ENGINEERING_MANAGER = "ENGINEERING_MANAGER"
ROLE_ADMIN = "ADMIN"


# ==========================================
# Permission Messages
# ==========================================
MSG_INVALID_ACTION = "Invalid or unknown action."
MSG_INVALID_TRANSITION = "Invalid lifecycle transition."
MSG_TICKET_CLOSED = "Ticket is already closed."
MSG_ROLE_REQUIRED = "You do not have the required role to perform this action."
MSG_ASSIGNEE_REQUIRED = "Only the assigned engineer may perform this action."
MSG_OVERRIDE_REQUIRED = "Administrator or Manager override required."


class TicketAction(str, Enum):
    ASSIGN = "ASSIGN"
    UNASSIGN = "UNASSIGN"
    START_PROGRESS = "START_PROGRESS"
    RESOLVE = "RESOLVE"
    CLOSE = "CLOSE"
    REOPEN = "REOPEN"
    CHANGE_PRIORITY = "CHANGE_PRIORITY"
    CHANGE_ASSIGNEE = "CHANGE_ASSIGNEE"

ALLOWED_TRANSITIONS: Dict[TicketStatus, FrozenSet[TicketStatus]] = {
    TicketStatus.OPEN: frozenset({TicketStatus.IN_PROGRESS}),
    TicketStatus.IN_PROGRESS: frozenset({TicketStatus.RESOLVED}),
    TicketStatus.RESOLVED: frozenset({TicketStatus.CLOSED}),
    TicketStatus.CLOSED: frozenset({TicketStatus.OPEN}),
}


@dataclass(frozen=True)
class PermissionMeta:
    allowed_roles: tuple[str, ...]
    requires_assignee: bool
    manager_override: bool
    admin_override: bool

ACTION_PERMISSIONS: Dict[TicketAction, PermissionMeta] = {
    TicketAction.ASSIGN: PermissionMeta(
        allowed_roles=(ROLE_ENGINEERING_MANAGER, ROLE_ADMIN),
        requires_assignee=False,
        manager_override=True,
        admin_override=True,
    ),
    TicketAction.UNASSIGN: PermissionMeta(
        allowed_roles=(ROLE_ENGINEERING_MANAGER, ROLE_ADMIN),
        requires_assignee=False,
        manager_override=True,
        admin_override=True,
    ),
    TicketAction.START_PROGRESS: PermissionMeta(
        allowed_roles=(ROLE_SUPPORT_L1, ROLE_SUPPORT_L2, ROLE_SUPPORT_L3),
        requires_assignee=True,
        manager_override=True,
        admin_override=True,
    ),
    TicketAction.RESOLVE: PermissionMeta(
        allowed_roles=(ROLE_SUPPORT_L1, ROLE_SUPPORT_L2, ROLE_SUPPORT_L3),
        requires_assignee=True,
        manager_override=True,
        admin_override=True,
    ),
    TicketAction.CLOSE: PermissionMeta(
        allowed_roles=(ROLE_ENGINEERING_MANAGER, ROLE_ADMIN),
        requires_assignee=False,
        manager_override=True,
        admin_override=True,
    ),
    TicketAction.REOPEN: PermissionMeta(
        allowed_roles=(ROLE_ENGINEERING_MANAGER, ROLE_ADMIN),
        requires_assignee=False,
        manager_override=True,
        admin_override=True,
    ),
    TicketAction.CHANGE_PRIORITY: PermissionMeta(
        allowed_roles=(ROLE_ENGINEERING_MANAGER, ROLE_ADMIN),
        requires_assignee=False,
        manager_override=True,
        admin_override=True,
    ),
    TicketAction.CHANGE_ASSIGNEE: PermissionMeta(
        allowed_roles=(ROLE_ENGINEERING_MANAGER, ROLE_ADMIN),
        requires_assignee=False,
        manager_override=True,
        admin_override=True,
    ),
}

TRANSITION_ACTIONS: Dict[tuple[TicketStatus, TicketStatus], TicketAction] = {
    (TicketStatus.OPEN, TicketStatus.IN_PROGRESS): TicketAction.START_PROGRESS,
    (TicketStatus.IN_PROGRESS, TicketStatus.RESOLVED): TicketAction.RESOLVE,
    (TicketStatus.RESOLVED, TicketStatus.CLOSED): TicketAction.CLOSE,
    (TicketStatus.CLOSED, TicketStatus.OPEN): TicketAction.REOPEN,
}
    

def is_transition_allowed(current_status: TicketStatus | str, new_status: TicketStatus | str) -> bool:
    """Check if transitioning from current_status to new_status is allowed in the matrix."""
    curr = TicketStatus(current_status) if isinstance(current_status, str) else current_status
    new_s = TicketStatus(new_status) if isinstance(new_status, str) else new_status
    return new_s in ALLOWED_TRANSITIONS.get(curr, set())

def get_allowed_transitions(current_status: TicketStatus | str) -> FrozenSet[TicketStatus]:
    """Get all allowed next statuses for a given status."""
    curr = TicketStatus(current_status) if isinstance(current_status, str) else current_status
    return ALLOWED_TRANSITIONS.get(curr, frozenset())

def get_action_for_transition(current_status: TicketStatus | str, new_status: TicketStatus | str) -> Optional[TicketAction]:
    """Get the action representing a specific status transition, if valid."""
    curr = TicketStatus(current_status) if isinstance(current_status, str) else current_status
    new_s = TicketStatus(new_status) if isinstance(new_status, str) else new_status
    return TRANSITION_ACTIONS.get((curr, new_s))

def get_permission_meta(action: TicketAction | str) -> Optional[PermissionMeta]:
    """Get the permission metadata for a given action."""
    act = TicketAction(action) if isinstance(action, str) else action
    return ACTION_PERMISSIONS.get(act)

def action_requires_assignee(action: TicketAction | str) -> bool:
    """Check if the given action requires the user to be the current assignee of the ticket."""
    meta = get_permission_meta(action)
    return meta.requires_assignee if meta else False

def manager_override_allowed(action: TicketAction | str) -> bool:
    """Check if a manager can override the standard rules for this action."""
    meta = get_permission_meta(action)
    return meta.manager_override if meta else False

def admin_override_allowed(action: TicketAction | str) -> bool:
    """Check if an admin can override the standard rules for this action."""
    meta = get_permission_meta(action)
    return meta.admin_override if meta else False

def get_allowed_roles_for_action(action: TicketAction | str) -> tuple[str, ...]:
    """Get the standard allowed roles for a given action."""
    meta = get_permission_meta(action)
    return meta.allowed_roles if meta else ()
