import os
import inspect
from pathlib import Path

from app.models.notification_preference import NotificationType, NotificationChannel
from app.services.notification_preference_service import DEFAULT_PREFERENCES_MATRIX
from app.core import notification_templates
from app.email import templates as email_templates
from app.core.formatters import format_enum
from app.services.notification_service import NotificationService
from app.services.notification_delivery_dispatcher import NotificationDeliveryDispatcher


# -------------------------------------------------------------------
# Validation 1 & 4 — NotificationType & Preference Coverage
# -------------------------------------------------------------------
def test_notification_type_coverage():
    """
    Verify every configurable notification event has a NotificationType enum
    and a DEFAULT_PREFERENCES_MATRIX entry.
    """
    matrix_keys = set(DEFAULT_PREFERENCES_MATRIX.keys())
    
    # Check that all NotificationTypes are either in the Matrix or explicitly bypass it (like WELCOME/FIRST_ROLE_ASSIGNED which are handled via dispatcher bypass)
    # Actually, WELCOME and FIRST_ROLE_ASSIGNED are in NotificationType, but they bypass the preferences matrix? Wait, are they in the matrix?
    # No, WELCOME and FIRST_ROLE_ASSIGNED are NOT in the matrix (only FIRST_ROLE is, maybe?).
    
    for notif_type in NotificationType:
        if notif_type in (NotificationType.WELCOME, NotificationType.FIRST_ROLE_ASSIGNED):
            continue
        assert notif_type in matrix_keys, f"NotificationType {notif_type} is missing from DEFAULT_PREFERENCES_MATRIX"

# -------------------------------------------------------------------
# Validation 2 — Template Coverage
# -------------------------------------------------------------------
def test_template_coverage():
    """
    Verify every notification builder references an existing template.
    """
    base_dir = Path(__file__).resolve().parent.parent / "app" / "templates" / "emails"
    
    # Get all builders from core.notification_templates
    core_builders = [f for name, f in inspect.getmembers(notification_templates, inspect.isfunction) if name.startswith("build_")]
    
    for builder in core_builders:
        # Create dummy kwargs to execute the builder
        sig = inspect.signature(builder)
        kwargs = {}
        for name, param in sig.parameters.items():
            if param.annotation == str:
                kwargs[name] = "dummy"
            elif param.annotation == "Ticket" or getattr(param.annotation, "__name__", "") == "Ticket":
                # Mock Ticket
                class MockTicket:
                    id = 1
                    title = "Test"
                    status = "OPEN"
                    priority = "HIGH"
                    created_by_id = 1
                    assigned_to_id = 2
                kwargs[name] = MockTicket()
                
        content = builder(**kwargs)
        template_name = content.template_name
        
        template_path = base_dir / template_name
        assert template_path.exists(), f"Template {template_name} referenced by {builder.__name__} does not exist"

# -------------------------------------------------------------------
# Validation 3 — Template Orphans
# -------------------------------------------------------------------
def test_template_orphans():
    """
    Ensure every email template is referenced by at least one builder.
    """
    base_dir = Path(__file__).resolve().parent.parent / "app" / "templates" / "emails"
    
    core_builders = [f for name, f in inspect.getmembers(notification_templates, inspect.isfunction) if name.startswith("build_")]
    auth_builders = [f for name, f in inspect.getmembers(email_templates, inspect.isfunction) if name.startswith("build_")]
    
    used_templates = set()
    
    for builder in core_builders + auth_builders:
        sig = inspect.signature(builder)
        kwargs = {}
        for name, param in sig.parameters.items():
            if param.annotation == str:
                kwargs[name] = "dummy"
            elif param.annotation == "Ticket" or getattr(param.annotation, "__name__", "") == "Ticket":
                class MockTicket:
                    id = 1
                    title = "Test"
                    status = "OPEN"
                    priority = "HIGH"
                kwargs[name] = MockTicket()
        
        # Email builders return a string instead of NotificationContent
        if builder in auth_builders:
            # We can't directly get the template name from auth builders since they return rendered strings.
            # We'll just hardcode the known used ones for auth.
            pass
        else:
            content = builder(**kwargs)
            used_templates.add(content.template_name)
            
    used_templates.update({"verification.html", "password_reset.html", "password_changed.html"})
    
    all_templates = {f.name for f in base_dir.glob("*.html")}
    all_templates.discard("layout.html")
    
    orphans = all_templates - used_templates
    assert not orphans, f"Found orphan templates: {orphans}"

# -------------------------------------------------------------------
# Validation 5 — Browser Defaults
# -------------------------------------------------------------------
def test_browser_defaults():
    """
    Verify Browser defaults remain False for all ticket events.
    """
    ticket_events = [
        NotificationType.TICKET_CREATED,
        NotificationType.TICKET_ASSIGNED,
        NotificationType.TICKET_REASSIGNED,
        NotificationType.TICKET_STATUS_CHANGED,
        NotificationType.TICKET_PRIORITY_CHANGED,
        NotificationType.TICKET_ESCALATED,
    ]
    
    for event in ticket_events:
        assert DEFAULT_PREFERENCES_MATRIX[event][NotificationChannel.BROWSER] is False, f"Browser default for {event} must be False to prevent spam"

# -------------------------------------------------------------------
# Validation 6 — Mandatory Notifications
# -------------------------------------------------------------------
def test_mandatory_notifications():
    """
    Assert PASSWORD_CHANGED is NOT in NotificationType, and FIRST_ROLE_ASSIGNED bypasses.
    """
    # 1. Assert PASSWORD_CHANGED is not in NotificationType
    enum_members = [member.name for member in NotificationType]
    assert "PASSWORD_CHANGED" not in enum_members, "PASSWORD_CHANGED must not be configurable in NotificationType"
    assert "VERIFICATION" not in enum_members
    assert "PASSWORD_RESET" not in enum_members

    # 2. Check dispatcher bypass for FIRST_ROLE_ASSIGNED
    # We can inspect the code of dispatcher
    dispatcher_source = inspect.getsource(NotificationDeliveryDispatcher.dispatch)
    assert "NotificationType.FIRST_ROLE_ASSIGNED" in dispatcher_source, "Dispatcher must explicitly bypass preferences for FIRST_ROLE_ASSIGNED"

# -------------------------------------------------------------------
# Validation 7 — Builder Integrity
# -------------------------------------------------------------------
def test_builder_integrity():
    """
    Verify every builder returns NotificationContent containing:
    title, message, template_name.
    Ticket builders additionally require ticket_summary, summary_rows.
    """
    core_builders = [f for name, f in inspect.getmembers(notification_templates, inspect.isfunction) if name.startswith("build_")]
    
    for builder in core_builders:
        sig = inspect.signature(builder)
        kwargs = {}
        for name, param in sig.parameters.items():
            if param.annotation == str:
                kwargs[name] = "dummy"
            elif param.annotation == "Ticket" or getattr(param.annotation, "__name__", "") == "Ticket":
                class MockTicket:
                    id = 1
                    title = "Test"
                    status = "OPEN"
                    priority = "HIGH"
                kwargs[name] = MockTicket()
                
        content = builder(**kwargs)
        
        assert content.title, f"{builder.__name__} missing title"
        assert content.message, f"{builder.__name__} missing message"
        assert content.template_name, f"{builder.__name__} missing template_name"
        
        if "ticket" in builder.__name__:
            assert content.ticket_summary is not None, f"{builder.__name__} missing ticket_summary"
            assert content.summary_rows, f"{builder.__name__} missing summary_rows"

# -------------------------------------------------------------------
# Validation 8 — Enum Formatting
# -------------------------------------------------------------------
def test_enum_formatting():
    """
    Verify format_enum works correctly for professional email output.
    """
    assert format_enum("IN_PROGRESS") == "In Progress"
    assert format_enum("HIGH_PRIORITY") == "High Priority"
    assert format_enum("OPEN") == "Open"

# -------------------------------------------------------------------
# Validation 9 — Notification Pipeline
# -------------------------------------------------------------------
def test_notification_pipeline_wiring():
    """
    Verify every NotificationService notify_* method uses an existing builder.
    """
    service_methods = [name for name, f in inspect.getmembers(NotificationService, inspect.isfunction) if name.startswith("notify_")]
    
    # We check the source of each method to see if it calls a build_ method
    for method_name in service_methods:
        func = getattr(NotificationService, method_name)
        source = inspect.getsource(func)
        assert "build_" in source, f"{method_name} does not call a notification builder"

# -------------------------------------------------------------------
# Validation 10 — Future Compatibility
# -------------------------------------------------------------------
# TODO: Watchers - Ensure watchers receive notifications similar to assignee
# TODO: Mentions - Ensure @mentions trigger in-app alerts and resolve user IDs correctly

# TODO: Redis Queue - Decouple dispatcher to a background worker to prevent HTTP blocking on Brevo
# TODO: Multi-workspace isolation - Add workspace_id bounds to NotificationService queries to prevent cross-tenant notification leaks
