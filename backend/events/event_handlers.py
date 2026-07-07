from utils.logger import logger


def log_event(event):

    logger.info(
        f"{event.type} | "
        f"{event.participant_id}"
    )


def confidence_handler(event):

    logger.info(
        "Confidence Engine received event"
    )


def websocket_handler(event):

    logger.info(
        "WebSocket received event"
    )