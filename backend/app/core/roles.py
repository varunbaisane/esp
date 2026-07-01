import enum

class RoleOperation(str, enum.Enum):
    ASSIGN = "assign"
    REMOVE = "remove"

ROLE_HIERARCHY = {
    "ADMIN": 100,
    "ENGINEERING_MANAGER": 90,
    "SUPPORT_L3": 30,
    "SUPPORT_L2": 20,
    "SUPPORT_L1": 10,
}

def get_role_rank(role_code: str) -> int:
    """Returns the numeric rank of a role. Default is 0 if not found."""
    return ROLE_HIERARCHY.get(role_code, 0)
