from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.models.ticket import Ticket
from app.core.formatters import format_enum, format_support_level

@dataclass
class TicketSummary:
    id: int
    title: str
    actor: str

@dataclass
class SummaryRow:
    label: str
    old_value: str | None = None
    new_value: str = ""
    highlight: bool = False

@dataclass
class NotificationContent:
    title: str
    message: str
    template_name: str | None = None
    template_context: dict = field(default_factory=dict)
    ticket_summary: TicketSummary | None = None
    summary_rows: list[SummaryRow] = field(default_factory=list)

def _format_name(name: str) -> str:
    return name.replace("_", " ")

def build_ticket_created(actor_name: str, ticket: Ticket) -> NotificationContent:
    summary = TicketSummary(
        id=ticket.id,
        title=ticket.title,
        actor=actor_name
    )
    rows = [
        SummaryRow(label="Status", new_value=format_enum(ticket.status)),
        SummaryRow(label="Priority", new_value=format_enum(ticket.priority)),
    ]
    return NotificationContent(
        title=f"Ticket #{ticket.id} Created",
        message=f"{actor_name} created Ticket #{ticket.id}.",
        template_name="ticket_created.html",
        ticket_summary=summary,
        summary_rows=rows
    )

def build_ticket_assigned(actor_name: str, ticket: Ticket, assignee_name: str) -> NotificationContent:
    summary = TicketSummary(
        id=ticket.id,
        title=ticket.title,
        actor=actor_name
    )
    rows = [
        SummaryRow(label="Assigned To", new_value=assignee_name)
    ]
    return NotificationContent(
        title=f"Ticket #{ticket.id} Assigned",
        message=f"{actor_name} assigned Ticket #{ticket.id} to {assignee_name}.",
        template_name="ticket_assigned.html",
        ticket_summary=summary,
        summary_rows=rows
    )

def build_ticket_reassigned(actor_name: str, ticket: Ticket, old_assignee_name: str, new_assignee_name: str) -> NotificationContent:
    summary = TicketSummary(
        id=ticket.id,
        title=ticket.title,
        actor=actor_name
    )
    rows = [
        SummaryRow(label="Assignee", old_value=old_assignee_name, new_value=new_assignee_name)
    ]
    return NotificationContent(
        title=f"Ticket #{ticket.id} Reassigned",
        message=f"Ticket #{ticket.id} was reassigned from {old_assignee_name} to {new_assignee_name} by {actor_name}.",
        template_name="ticket_reassigned.html",
        ticket_summary=summary,
        summary_rows=rows
    )

def build_ticket_status_changed(actor_name: str, ticket: Ticket, old_status: str, new_status: str) -> NotificationContent:
    summary = TicketSummary(
        id=ticket.id,
        title=ticket.title,
        actor=actor_name
    )
    rows = [
        SummaryRow(label="Status", old_value=format_enum(old_status), new_value=format_enum(new_status))
    ]
    return NotificationContent(
        title=f"Ticket #{ticket.id} Status Update",
        message=f"{actor_name} changed the status of Ticket #{ticket.id} from {format_enum(old_status)} to {format_enum(new_status)}.",
        template_name="ticket_status_changed.html",
        ticket_summary=summary,
        summary_rows=rows
    )

def build_ticket_priority_changed(actor_name: str, ticket: Ticket, old_priority: str, new_priority: str) -> NotificationContent:
    summary = TicketSummary(
        id=ticket.id,
        title=ticket.title,
        actor=actor_name
    )
    rows = [
        SummaryRow(label="Priority", old_value=format_enum(old_priority), new_value=format_enum(new_priority))
    ]
    return NotificationContent(
        title=f"Ticket #{ticket.id} Priority Update",
        message=f"{actor_name} changed the priority of Ticket #{ticket.id} from {format_enum(old_priority)} to {format_enum(new_priority)}.",
        template_name="ticket_priority_changed.html",
        ticket_summary=summary,
        summary_rows=rows
    )

def build_ticket_escalated(actor_name: str, ticket: Ticket, old_level: str, new_level: str) -> NotificationContent:
    summary = TicketSummary(
        id=ticket.id,
        title=ticket.title,
        actor=actor_name
    )
    rows = [
        SummaryRow(label="Support Level", old_value=format_support_level(old_level), new_value=format_support_level(new_level), highlight=True)
    ]
    return NotificationContent(
        title=f"Ticket #{ticket.id} Escalated",
        message=f"Ticket #{ticket.id} was escalated from {format_support_level(old_level)} to {format_support_level(new_level)} by {actor_name}.",
        template_name="ticket_escalated.html",
        ticket_summary=summary,
        summary_rows=rows
    )

def build_role_assigned(actor_name: str, role_name: str) -> NotificationContent:
    return NotificationContent(
        title="Role Assigned",
        message=f"{actor_name} assigned you the {_format_name(role_name)} role.",
        template_name="role_assigned.html",
        template_context={
            "actor_name": actor_name,
            "role_name": _format_name(role_name)
        }
    )

def build_role_removed(actor_name: str, role_name: str) -> NotificationContent:
    return NotificationContent(
        title="Role Revoked",
        message=f"Your {_format_name(role_name)} role was removed by {actor_name}.",
        template_name="role_removed.html",
        template_context={
            "actor_name": actor_name,
            "role_name": _format_name(role_name)
        }
    )

def build_first_role_assigned(actor_name: str, role_name: str) -> NotificationContent:
    return NotificationContent(
        title="Welcome to the Engineering Support Platform",
        message=f"{actor_name} assigned you the {_format_name(role_name)} role. Your account is now active and you can access the platform.",
        template_name="first_role_assigned.html",
        template_context={
            "actor_name": actor_name,
            "role_name": _format_name(role_name)
        }
    )
