from enum import Enum
from app.models.user import User
from app.models.ticket import TicketLevel

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
