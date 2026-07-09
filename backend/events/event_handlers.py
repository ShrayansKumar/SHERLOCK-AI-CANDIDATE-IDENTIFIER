import asyncio

from utils.logger import logger
from services.fusion_service import fusion_service


def log_event(event):
    logger.info(
        f"{event.type} | {event.participant_id}"
    )


def display_name_change_handler(event):
    logger.info(
        f"Display name changed | "
        f"{event.participant_id} | "
        f"{event.payload.get('display_name')}"
    )


def confidence_handler(event):
    """
    Runs the full Sherlock fusion pipeline for an event:
      Evidence → ConfidenceEngine → DB persist → WebSocket broadcast.

    Uses asyncio.run_coroutine_threadsafe when a loop is running
    (inside uvicorn), or asyncio.run() in standalone/test contexts.
    """
    logger.info(
        f"Confidence pipeline triggered | {event.type} | {event.participant_id}"
    )

    async def _run():
        await fusion_service.process_event(event)

    try:
        # Try to get the currently running event loop (uvicorn context)
        loop = asyncio.get_running_loop()
        # Schedule as a task in the running loop — non-blocking
        loop.create_task(_run())
    except RuntimeError:
        # No running loop (e.g. simulator, test context) — run synchronously
        asyncio.run(_run())
    except Exception as e:
        logger.error(f"confidence_handler error: {e}")


async def websocket_handler(event):
    from websocket import WebSocketBroadcaster
    broadcaster = WebSocketBroadcaster()
    await broadcaster.broadcast({
        "event": event.type,
        "participant_id": event.participant_id,
        "payload": event.payload,
    })