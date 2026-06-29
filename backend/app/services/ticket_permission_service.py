from dataclasses import dataclass
from typing import Optional

# pyrefly: ignore [missing-import]
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_409_CONFLICT,
)

from app.core.ticket_permissions import (
    TicketAction,
    TicketStatus,
    PermissionMeta,
    is_transition_allowed,
    get_action_for_transition,
    get_permission_meta,
    ROLE_ADMIN,
    ROLE_ENGINEERING_MANAGER,
    MSG_INVALID_ACTION,
    MSG_INVALID_TRANSITION,
    MSG_TICKET_CLOSED,
    MSG_ROLE_REQUIRED,
    MSG_ASSIGNEE_REQUIRED,
    MSG_OVERRIDE_REQUIRED,
)
from app.models.ticket import Ticket
from app.schemas.ticket import TicketUpdate
from app.models.user import User
from fastapi import HTTPException # pyrefly: ignore [missing-import]

@dataclass(frozen=True)
class PermissionResult:
    """Immutable result of a permission evaluation."""
    allowed: bool
    reason: Optional[str] = None
    http_status: int = HTTP_403_FORBIDDEN


class TicketPermissionService:
    """
    Central authorization engine for ticket lifecycle operations.
    Evaluates business rules based on the static permission matrix.
    """

    def _get_user_roles(self, user: User) -> set[str]:
        """Extract user role names as a set."""
        if not hasattr(user, "roles") or not user.roles:
            return set()
        return {r.name.upper() for r in user.roles}

    def _check_transition(self, ticket: Ticket, new_status: Optional[TicketStatus]) -> Optional[PermissionResult]:
        """Check if the transition is allowed. Returns PermissionResult if denied, None if allowed."""
        if new_status and new_status != ticket.status:
            if not is_transition_allowed(ticket.status, new_status):
                if ticket.status == TicketStatus.CLOSED:
                    return PermissionResult(allowed=False, reason=MSG_TICKET_CLOSED, http_status=HTTP_409_CONFLICT)
                return PermissionResult(allowed=False, reason=MSG_INVALID_TRANSITION, http_status=HTTP_409_CONFLICT)
        return None

    def _check_override(self, user_roles: set[str], meta: PermissionMeta) -> bool:
        """Check if user has an override role that bypasses standard requirements."""
        if ROLE_ADMIN in user_roles and meta.admin_override:
            return True
        if ROLE_ENGINEERING_MANAGER in user_roles and meta.manager_override:
            return True
        return False

    def _check_roles(self, user_roles: set[str], meta: PermissionMeta) -> Optional[PermissionResult]:
        """Check if user has a required role for the action. Returns PermissionResult if denied, None if allowed."""
        has_allowed_role = any(role in meta.allowed_roles for role in user_roles)
        if not has_allowed_role:
            if meta.admin_override and meta.manager_override and not meta.allowed_roles:
                return PermissionResult(allowed=False, reason=MSG_OVERRIDE_REQUIRED, http_status=HTTP_403_FORBIDDEN)
            return PermissionResult(allowed=False, reason=MSG_ROLE_REQUIRED, http_status=HTTP_403_FORBIDDEN)
        return None

    def _check_assignee(self, ticket: Ticket, user: User, meta: PermissionMeta) -> Optional[PermissionResult]:
        """Check if user meets assignee requirements. Returns PermissionResult if denied, None if allowed."""
        if meta.requires_assignee and ticket.assigned_to_id != user.id:
            return PermissionResult(allowed=False, reason=MSG_ASSIGNEE_REQUIRED, http_status=HTTP_403_FORBIDDEN)
        return None

    def validate_action(
        self,
        *,
        user: User,
        ticket: Ticket,
        action: TicketAction,
        new_status: Optional[TicketStatus] = None,
    ) -> PermissionResult:
        """
        Evaluate if a user can perform a specific lifecycle action on a ticket.
        
        Inputs:
        - user: The user attempting the action.
        - ticket: The target ticket.
        - action: The intended action.
        - new_status: The target status (required if the action implies a state transition).
        
        Outputs:
        - PermissionResult object indicating success or specific denial reasons.
        
        Evaluation Order:
        1. Validates lifecycle transition (hard rule for everyone).
        2. Checks for administrator/manager override.
        3. Checks standard role requirements.
        4. Checks assignee requirements.
        """
        meta = get_permission_meta(action)
        if not meta:
            return PermissionResult(allowed=False, reason=MSG_INVALID_ACTION, http_status=HTTP_400_BAD_REQUEST)

        # 1. Validate Transition Validity
        transition_denial = self._check_transition(ticket, new_status)
        if transition_denial:
            return transition_denial

        user_roles = self._get_user_roles(user)

        # 2. Evaluate Manager/Admin Overrides
        if self._check_override(user_roles, meta):
            return PermissionResult(allowed=True, http_status=HTTP_200_OK)

        # 3. Evaluate Role Requirements
        role_denial = self._check_roles(user_roles, meta)
        if role_denial:
            return role_denial

        # 4. Evaluate Assignee Requirements
        assignee_denial = self._check_assignee(ticket, user, meta)
        if assignee_denial:
            return assignee_denial

        return PermissionResult(allowed=True, http_status=HTTP_200_OK)

    def raise_if_denied(self, result: PermissionResult) -> None:
        """Helper to raise an HTTPException if the permission result is denied."""
        if not result.allowed:
            raise HTTPException(status_code=result.http_status, detail=result.reason)

    def validate_ticket_update(self, user: User, ticket: Ticket, update_data: TicketUpdate) -> PermissionResult:
        """Orchestrate permission checks for a general ticket update."""
        if update_data.status is not None and update_data.status != ticket.status:
            perm = self.can_transition(user, ticket, update_data.status)
            if not perm.allowed:
                return perm

        if update_data.priority is not None and update_data.priority != ticket.priority:
            perm = self.can_change_priority(user, ticket)
            if not perm.allowed:
                return perm

        if update_data.assigned_to_id is not None and update_data.assigned_to_id != ticket.assigned_to_id:
            if ticket.assigned_to_id is None:
                perm = self.can_assign(user, ticket)
            else:
                perm = self.can_change_assignee(user, ticket)
            if not perm.allowed:
                return perm
                
        return PermissionResult(allowed=True, http_status=HTTP_200_OK)

    # ==================================================
    # Convenience Wrappers for Readability
    # ==================================================

    def can_assign(self, user: User, ticket: Ticket) -> PermissionResult:
        return self.validate_action(user=user, ticket=ticket, action=TicketAction.ASSIGN)

    def can_unassign(self, user: User, ticket: Ticket) -> PermissionResult:
        return self.validate_action(user=user, ticket=ticket, action=TicketAction.UNASSIGN)

    def can_change_assignee(self, user: User, ticket: Ticket) -> PermissionResult:
        return self.validate_action(user=user, ticket=ticket, action=TicketAction.CHANGE_ASSIGNEE)

    def can_change_priority(self, user: User, ticket: Ticket) -> PermissionResult:
        return self.validate_action(user=user, ticket=ticket, action=TicketAction.CHANGE_PRIORITY)

    def can_start_progress(self, user: User, ticket: Ticket) -> PermissionResult:
        return self.validate_action(user=user, ticket=ticket, action=TicketAction.START_PROGRESS, new_status=TicketStatus.IN_PROGRESS)

    def can_resolve(self, user: User, ticket: Ticket) -> PermissionResult:
        return self.validate_action(user=user, ticket=ticket, action=TicketAction.RESOLVE, new_status=TicketStatus.RESOLVED)

    def can_close(self, user: User, ticket: Ticket) -> PermissionResult:
        return self.validate_action(user=user, ticket=ticket, action=TicketAction.CLOSE, new_status=TicketStatus.CLOSED)

    def can_reopen(self, user: User, ticket: Ticket) -> PermissionResult:
        return self.validate_action(user=user, ticket=ticket, action=TicketAction.REOPEN, new_status=TicketStatus.OPEN)

    def can_transition(self, user: User, ticket: Ticket, new_status: TicketStatus) -> PermissionResult:
        if new_status == ticket.status:
            return PermissionResult(allowed=True, http_status=HTTP_200_OK)
            
        action = get_action_for_transition(ticket.status, new_status)
        if not action:
            return self._check_transition(ticket, new_status) or PermissionResult(allowed=False, reason=MSG_INVALID_TRANSITION, http_status=HTTP_409_CONFLICT)
            
        return self.validate_action(user=user, ticket=ticket, action=action, new_status=new_status)
