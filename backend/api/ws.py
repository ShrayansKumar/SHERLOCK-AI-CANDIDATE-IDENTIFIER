from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from websocket import WebSocketBroadcaster
from utils.logger import logger

router = APIRouter(tags=["WebSocket"])

broadcaster = WebSocketBroadcaster()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for live Sherlock updates.
    Clients connect here to receive real-time confidence,
    evidence, and explanation broadcasts as events occur.
    """
    await websocket.accept()
    broadcaster.register(websocket)

    logger.info(f"WebSocket client connected: {websocket.client}")

    try:
        while True:
            # Keep connection alive — await any incoming ping/messages
            data = await websocket.receive_text()
            logger.debug(f"WS message from client: {data}")

    except WebSocketDisconnect:
        broadcaster.unregister(websocket)
        logger.info(f"WebSocket client disconnected: {websocket.client}")
