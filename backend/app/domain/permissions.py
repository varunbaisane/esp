from enum import Enum
from app.models.user import User
from app.models.ticket import TicketLevel, Ticket

ROLE_RANK = {
    "SUPPORT_L1": 1,
    "SUPPORT_L2": 2,
    "SUPPORT_L3": 3,
    "ENGINEERING_MANAGER": 4,
    "ADMIN": 5,
}

class Permission(Enum):
    ESCALATE_L1 = "ESCALATE_L1"
    ESCALATE_L2 = "ESCALATE_L2"
    # Future permissions can be added here
    # e.g., MANAGE_USERS = "MANAGE_USERS"

def get_user_highest_rank(user: User) -> int:
    """Returns the highest rank value based on the user's assigned roles."""
    if not getattr(user, 'roles', None):
        return 0
    return max([ROLE_RANK.get(role.name, 0) for role in user.roles], default=0)

def can_escalate(user: User, current_level: TicketLevel) -> bool:
    """
    Evaluates whether the user has sufficient rank to escalate a ticket 
    from its current support level.
    """
    user_rank = get_user_highest_rank(user)
    
    if current_level == TicketLevel.L1:
        # L1 escalation requires rank >= 1
        return user_rank >= 1
        
    if current_level == TicketLevel.L2:
        # L2 escalation requires rank >= 2
        return user_rank >= 2
        
    if current_level == TicketLevel.L3:
        # Cannot escalate past L3
        return False
        
    return False

def can_handle_ticket_level(user: User, level: TicketLevel) -> bool:
    """
    Evaluates whether the user's rank is sufficient to handle tickets of the given level.
    """
    user_rank = get_user_highest_rank(user)
    if level == TicketLevel.L1 and user_rank < 1:
        return False
    if level == TicketLevel.L2 and user_rank < 2:
        return False
    if level == TicketLevel.L3 and user_rank < 3:
        return False
    return True

def can_assign_ticket(actor: User, ticket: Ticket, target_user: User) -> bool:
    """
    Evaluates whether the actor has sufficient rank to assign the specific ticket 
    to the target_user based on the target_user's capabilities.
    """
    actor_rank = get_user_highest_rank(actor)
    
    # Target must be capable of handling the ticket's level
    if not can_handle_ticket_level(target_user, ticket.support_level):
        return False

    # Manager/Admin can assign any ticket to any valid engineer
    if actor_rank >= 4:
        return True
        
    # Engineers can only assign tickets they are permitted to handle
    # and only to valid targets (checked above)
    if ticket.support_level == TicketLevel.L1 and actor_rank >= 1:
        return True
    if ticket.support_level == TicketLevel.L2 and actor_rank >= 2:
        return True
    if ticket.support_level == TicketLevel.L3 and actor_rank >= 3:
        return True

    return False

def can_claim_ticket(actor: User, ticket: Ticket) -> bool:
    """
    Evaluates whether the actor has sufficient rank to claim the specific ticket.
    """
    actor_rank = get_user_highest_rank(actor)
    
    # Manager/Admin can claim any ticket
    if actor_rank >= 4:
        return True
        
    return can_handle_ticket_level(actor, ticket.support_level)

def has_permission(user: User, permission: Permission) -> bool:
    """
    Future-proof structure for explicit permission checks.
    Currently routes back to rank-based checks for escalation.
    """
    user_rank = get_user_highest_rank(user)
    
    if permission == Permission.ESCALATE_L1:
        return user_rank >= 1
    elif permission == Permission.ESCALATE_L2:
        return user_rank >= 2
        
    return False
