# pyrefly: ignore [missing-import]
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
import logging

from app.api.deps import get_db
from app.core.jwt import decode_access_token
from app.exceptions.auth import InvalidTokenError, TokenExpiredError
from app.repositories.user_repository import UserRepository
from app.websocket.connection_manager import connection_manager

logger = logging.getLogger(__name__)

router = APIRouter()

@router.websocket("/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    await websocket.accept()

    # Authenticate using existing JWT
    try:
        payload = decode_access_token(token)
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(int(payload.sub))
        if not user:
            logger.warning("WebSocket authentication failed: User not found")
            await websocket.close(code=1008, reason="User not found")
            return
    except (InvalidTokenError, TokenExpiredError) as e:
        logger.warning(f"WebSocket authentication failed: {e}")
        await websocket.close(code=1008, reason="Token invalid or expired")
        return

    # Register authenticated socket
    await connection_manager.connect(user.id, websocket)

    try:
        # Keep-alive loop to consume client payloads (e.g. heartbeat) and handle disconnects
        while True:
            # We don't expect specific client payloads right now, just ignore them or handle ping
            data = await websocket.receive_text()
            # If client sends ping, we could send pong if needed. For now, native ping/pong is supported by ASGI.
    except WebSocketDisconnect:
        connection_manager.disconnect(user.id, websocket)
    except Exception as e:
        logger.error(f"WebSocket error for user {user.id}: {e}")
        connection_manager.disconnect(user.id, websocket)
