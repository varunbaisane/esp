import logging
from app.websocket.connection_manager import connection_manager
from app.websocket.events import WebSocketEvent, WebSocketEventType
from enum import Enum

logger = logging.getLogger(__name__)

class TicketEvent(str, Enum):
    CREATED = "created"
    ASSIGNED = "assigned"
    REASSIGNED = "reassigned"
    STATUS_CHANGED = "status_changed"
    PRIORITY_CHANGED = "priority_changed"
    ESCALATED = "escalated"

class TicketEventDispatcher:
    """
    Handles publishing of ticket synchronization events via WebSocket.
    This class owns all ticket WebSocket event construction.
    """
    def publish_ticket_event(self, ticket_id: int, event: TicketEvent) -> None:
        """
        Constructs and publishes an ENTITY_UPDATED event for a ticket.
        """
        logger.debug(f"Publishing ticket event: ticket_id={ticket_id}, event={event.value}")
        
        try:
            ws_event = WebSocketEvent(
                version=1,
                type=WebSocketEventType.ENTITY_UPDATED,
                payload={
                    "entity_type": "ticket",
                    "entity_id": ticket_id,
                    "event": event.value
                }
            )
            
            event_json = ws_event.model_dump_json()
            from app.infrastructure.realtime.publisher import realtime_publisher
            
            realtime_publisher.publish_broadcast_fire_and_forget(event_json)
        except Exception as e:
            logger.error(f"Failed to dispatch ticket sync event for ticket {ticket_id}: {e}")
