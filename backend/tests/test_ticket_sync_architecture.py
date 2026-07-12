import pytest
import inspect
from app.services.ticket_service import TicketService
from app.services.ticket_event_dispatcher import TicketEvent, TicketEventDispatcher
from app.websocket.connection_manager import connection_manager, ConnectionManager
from app.websocket.events import WebSocketEvent, WebSocketEventType

def test_ticket_service_depends_on_dispatcher():
    """
    Ensure TicketService uses TicketEventDispatcher and does NOT import ConnectionManager directly.
    """
    import app.services.ticket_service as ts_module
    
    # Check imports
    assert "ConnectionManager" not in dir(ts_module)
    assert "connection_manager" not in dir(ts_module)
    
    # Check that TicketService instantiates TicketEventDispatcher
    assert "TicketEventDispatcher" in inspect.getsource(TicketService.__init__)

def test_ticket_event_dispatcher_ownership():
    """
    TicketEventDispatcher must be the ONLY class allowed to construct WebSocket events
    for tickets and publish them to realtime_publisher.
    """
    # Verify TicketService does not call realtime_publisher or connection_manager directly
    ts_source = inspect.getsource(TicketService)
    assert "connection_manager.publish" not in ts_source
    assert "realtime_publisher.publish" not in ts_source
    
    # Verify TicketEventDispatcher DOES call realtime_publisher
    dispatcher_source = inspect.getsource(TicketEventDispatcher.publish_ticket_event)
    assert "realtime_publisher.publish_broadcast_fire_and_forget" in dispatcher_source

def test_event_payload_schema():
    """
    Ensure payloads conform to the generic entity schema.
    """
    # A dummy payload that a dispatcher would build
    ws_event = WebSocketEvent(
        version=1,
        type=WebSocketEventType.ENTITY_UPDATED,
        payload={
            "entity_type": "ticket",
            "entity_id": 123,
            "event": TicketEvent.STATUS_CHANGED.value
        }
    )
    
    dump = ws_event.model_dump()
    assert dump["version"] == 1
    assert dump["type"] == "entity_updated"
    assert "entity_type" in dump["payload"]
    assert "entity_id" in dump["payload"]
    assert "event" in dump["payload"]

def test_event_registry():
    """
    Ensure generic ENTITY_UPDATED and TicketEvent enums are registered.
    """
    assert hasattr(WebSocketEventType, "ENTITY_UPDATED")
    assert WebSocketEventType.ENTITY_UPDATED.value == "entity_updated"
    
    assert hasattr(TicketEvent, "CREATED")
    assert hasattr(TicketEvent, "STATUS_CHANGED")
