from datetime import datetime

from events.event import Event
from events.event_types import EventType


class EventGenerator:

    def participant_join(
        self,
        meeting_id,
        participant
    ):

        return Event(

            type=EventType.PARTICIPANT_JOINED,

            meeting_id=meeting_id,

            participant_id=participant.participant_id,

            payload={

                "display_name": participant.display_name,

                "role": participant.role.value

            },

            timestamp=datetime.utcnow()

        )