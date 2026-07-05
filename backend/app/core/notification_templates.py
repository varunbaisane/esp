from dataclasses import dataclass
from app.models.ticket import Ticket

@dataclass
class NotificationContent:
    title: str
    message: str

def _format_name(name: str) -> str:
    return name.replace("_", " ")

def build_ticket_assigned(actor_name: str, ticket: Ticket) -> NotificationContent:
    return NotificationContent(
        title="Ticket Assigned",
        message=f"{actor_name} assigned Ticket #{ticket.id} to you."
    )

def build_ticket_reassigned(actor_name: str, ticket: Ticket) -> NotificationContent:
    return NotificationContent(
        title="Ticket Reassigned",
        message=f"Ticket #{ticket.id} was reassigned to you by {actor_name}."
    )

def build_ticket_status_changed(actor_name: str, ticket: Ticket, new_status: str) -> NotificationContent:
    return NotificationContent(
        title="Ticket Status Update",
        message=f"{actor_name} changed the status of Ticket #{ticket.id} to {_format_name(new_status)}."
    )

def build_ticket_priority_changed(actor_name: str, ticket: Ticket, new_priority: str) -> NotificationContent:
    return NotificationContent(
        title="Ticket Priority Update",
        message=f"{actor_name} changed the priority of Ticket #{ticket.id} to {_format_name(new_priority)}."
    )

def build_role_assigned(actor_name: str, role_name: str) -> NotificationContent:
    return NotificationContent(
        title="Role Assigned",
        message=f"{actor_name} assigned you the {_format_name(role_name)} role."
    )

def build_role_removed(actor_name: str, role_name: str) -> NotificationContent:
    return NotificationContent(
        title="Role Revoked",
        message=f"Your {_format_name(role_name)} role was removed by {actor_name}."
    )

def build_first_role_assigned(actor_name: str, role_name: str) -> NotificationContent:
    return NotificationContent(
        title="Welcome to the Engineering Support Platform",
        message=f"{actor_name} assigned you the {_format_name(role_name)} role. Your account is now active and you can access the platform."
    )
