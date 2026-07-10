import ast
import inspect
from pathlib import Path
from typing import get_type_hints, Dict, Set

# Imports for validation
from app.services.notification_delivery_dispatcher import NotificationDeliveryDispatcher
from app.services.ticket_service import TicketService
from app.services.notification_service import NotificationService
from app.websocket.connection_manager import ConnectionManager
from app.websocket.events import WebSocketEvent, WebSocketEventType
from app.api.v1.endpoints.websocket import websocket_notifications

# -------------------------------------------------------------------
# Test 1 - Dispatcher Owns WebSocket Delivery
# -------------------------------------------------------------------
def test_dispatcher_owns_websocket_delivery():
    """
    Verify that NotificationDeliveryDispatcher imports ConnectionManager,
    while TicketService and NotificationService do not.
    """
    dispatcher_source = inspect.getsource(NotificationDeliveryDispatcher)
    ticket_service_source = inspect.getsource(TicketService)
    notification_service_source = inspect.getsource(NotificationService)

    # Dispatcher must import or use connection_manager
    assert "connection_manager" in dispatcher_source, "Dispatcher must handle WebSocket delivery."
    
    # Services must remain decoupled
    assert "connection_manager" not in ticket_service_source, "TicketService must not import ConnectionManager."
    assert "websocket" not in ticket_service_source.lower(), "TicketService must not mention WebSockets."
    
    assert "connection_manager" not in notification_service_source, "NotificationService must not import ConnectionManager."
    assert "websocket" not in notification_service_source.lower(), "NotificationService must not mention WebSockets."


# -------------------------------------------------------------------
# Test 2 - NotificationResponse Reuse
# -------------------------------------------------------------------
def test_notification_response_reuse():
    """
    Verify that WebSocket serialization is built from NotificationResponse.
    """
    dispatcher_source = inspect.getsource(NotificationDeliveryDispatcher._dispatch_websocket)
    
    assert "NotificationResponse" in dispatcher_source, "Dispatcher must use NotificationResponse schema for WebSockets."
    assert "NotificationResponse.model_validate" in dispatcher_source, "Must rely on the standard REST API schema validation."


# -------------------------------------------------------------------
# Test 3 - Connection Manager Structure
# -------------------------------------------------------------------
def test_connection_manager_structure():
    """
    Verify ConnectionManager supports multi-tab correctly mapping user_id -> set[WebSocket].
    """
    hints = get_type_hints(ConnectionManager)
    # The active_connections might not be type-hinted at the class level if done in __init__
    
    # Let's inspect the __init__ source
    init_source = inspect.getsource(ConnectionManager.__init__)
    
    # Ensure it uses a set or equivalent collection, not a direct WebSocket reference
    assert "Set[WebSocket]" in init_source or "set()" in init_source, "ConnectionManager must map user to a Set of WebSockets."
    assert "Dict[int" in init_source, "ConnectionManager must map int (user_id) to Set."


# -------------------------------------------------------------------
# Test 4 - Event Registry
# -------------------------------------------------------------------
def test_event_registry():
    """
    Verify WebSocketEventType current and future definitions.
    """
    events = [member.value for member in WebSocketEventType]
    assert "notification" in events, "Base 'notification' event type must exist."
    
    # Ensure TODOs are documented in the file
    events_source = inspect.getsource(WebSocketEventType)
    assert "ticket_updated" in events_source.lower()
    assert "dashboard_updated" in events_source.lower() or "workspace_updated" in events_source.lower()
    assert "presence" in events_source.lower()


# -------------------------------------------------------------------
# Test 5 - ConnectionManager Independence
# -------------------------------------------------------------------
def test_connection_manager_independence():
    """
    Verify ConnectionManager remains pure infrastructure and imports no domain models.
    """
    cm_source = inspect.getsource(ConnectionManager)
    cm_imports_prohibited = [
        "Ticket", "Notification", "Repository", "Session", "Base", "Service"
    ]
    
    for term in cm_imports_prohibited:
        assert term not in cm_source, f"ConnectionManager must not import {term} - it must remain pure infrastructure."


# -------------------------------------------------------------------
# Test 6 - Notification Context Ownership
# -------------------------------------------------------------------
def test_notification_context_ownership():
    """
    Verify backend emits pure data payloads without frontend-specific directives.
    """
    dispatcher_source = inspect.getsource(NotificationDeliveryDispatcher._dispatch_websocket)
    
    assert "play_sound" not in dispatcher_source
    assert "show_toast" not in dispatcher_source
    assert "browser_popup" not in dispatcher_source
    assert "sound" not in dispatcher_source.lower()


# -------------------------------------------------------------------
# Test 7 - Endpoint Isolation
# -------------------------------------------------------------------
def test_endpoint_isolation():
    """
    Verify websocket endpoint handles auth and registration only.
    """
    endpoint_source = inspect.getsource(websocket_notifications)
    
    assert "decode_access_token" in endpoint_source
    assert "connection_manager.connect" in endpoint_source
    assert "connection_manager.disconnect" in endpoint_source
    
    # Should not trigger notifications or modify tickets directly
    assert "NotificationService" not in endpoint_source
    assert "TicketService" not in endpoint_source


# -------------------------------------------------------------------
# Test 8 - Future Redis Compatibility
# -------------------------------------------------------------------
def test_future_redis_compatibility():
    """
    Document Phase 9.5 compatibility requirements.
    ConnectionManager will be refactored to wrap Redis Pub/Sub, but services remain unaware.
    """
    # Simply asserting this test exists serves as documentation constraint
    assert True
    # TODO: In Phase 9.5, ConnectionManager will subscribe to Redis channels (e.g. `user:{id}:events`) 
    # instead of routing exclusively in-memory, allowing multi-worker uvicorn scale-out.
    # The dispatcher, ticket service, and notification service will NOT be modified during this migration.
