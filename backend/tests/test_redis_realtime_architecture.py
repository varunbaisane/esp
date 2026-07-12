# pyrefly: ignore [missing-import]
import pytest
import sys
from importlib import import_module
from pydantic import BaseModel
import ast

def check_imports(file_path: str, forbidden_imports: list[str]) -> list[str]:
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=file_path)

    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for forbidden in forbidden_imports:
                    if alias.name == forbidden or alias.name.startswith(f"{forbidden}."):
                        violations.append(f"Import {alias.name} at line {node.lineno}")
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for forbidden in forbidden_imports:
                    if node.module == forbidden or node.module.startswith(f"{forbidden}."):
                        violations.append(f"From {node.module} import at line {node.lineno}")
    return violations

def test_ticket_service_layering():
    # TicketService never imports Redis or infrastructure.realtime
    violations = check_imports(
        "app/services/ticket_service.py",
        ["redis", "app.infrastructure.realtime"]
    )
    assert not violations, f"TicketService has forbidden imports: {violations}"

def test_notification_service_layering():
    # NotificationService never imports Redis or infrastructure.realtime
    violations = check_imports(
        "app/services/notification_service.py",
        ["redis", "app.infrastructure.realtime"]
    )
    assert not violations, f"NotificationService has forbidden imports: {violations}"

def test_connection_manager_layering():
    # ConnectionManager never imports Redis
    violations = check_imports(
        "app/websocket/connection_manager.py",
        ["redis", "app.infrastructure.realtime"]
    )
    assert not violations, f"ConnectionManager has forbidden imports: {violations}"

def test_publisher_layering():
    # Publisher never imports business logic
    violations = check_imports(
        "app/infrastructure/realtime/publisher.py",
        ["app.services"]
    )
    assert not violations, f"Publisher has forbidden imports: {violations}"

def test_subscriber_layering():
    # Subscriber never imports business logic (TicketService, NotificationService)
    violations = check_imports(
        "app/infrastructure/realtime/subscriber.py",
        ["app.services.ticket_service", "app.services.notification_service", "app.services"]
    )
    assert not violations, f"Subscriber has forbidden imports: {violations}"

def test_redis_payload_schema():
    # The payload passed into redis must be identical to the payload delivered to websocket.
    # No wrapper envelop should be used.
    from app.infrastructure.realtime.publisher import RealtimePublisher
    import inspect
    
    # Check signature of publish_broadcast
    sig = inspect.signature(RealtimePublisher.publish_broadcast)
    assert "event_json" in sig.parameters
    
    sig_user = inspect.signature(RealtimePublisher.publish_to_user)
    assert "event_json" in sig_user.parameters
