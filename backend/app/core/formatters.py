from datetime import datetime
from enum import Enum
from typing import Any

from app.models.user import User

def format_enum(value: Enum | str | Any) -> str:
    """
    Converts enum values like 'IN_PROGRESS' or 'WAITING_CUSTOMER' 
    to human-readable formats like 'In Progress' or 'Waiting Customer'.
    """
    if isinstance(value, Enum):
        name = value.value
    else:
        name = str(value)
        
    return name.replace("_", " ").title()

def format_support_level(level: Enum | str | Any) -> str:
    """
    Formats support levels like 'L1', 'L2' exactly as they are without title casing,
    or formats them appropriately.
    """
    if isinstance(level, Enum):
        val = level.value
    else:
        val = str(level)
    return val.upper()

def format_user(user: User | None) -> str:
    """
    Formats a user object to their full name, or 'Unassigned' if None.
    """
    if not user:
        return "Unassigned"
    return user.full_name

def format_datetime(dt: datetime | None) -> str:
    """
    Formats a datetime object to a string like '12 Jul 2026, 2:15 PM'.
    """
    if not dt:
        return "N/A"
    return dt.strftime("%d %b %Y, %I:%M %p")
