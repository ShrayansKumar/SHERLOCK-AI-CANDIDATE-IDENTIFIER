from events.event import Event
from events.event_bus import event_bus
from events.event_handlers import (
    log_event,
)

from events.event_types import EventType


event_bus.subscribe(
    EventType.CAMERA_OFF,
    log_event
)

event = Event(

    type=EventType.CAMERA_OFF,

    meeting_id=1,

    participant_id="participant_01"
)

event_bus.publish(event)