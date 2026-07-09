from datetime import datetime

from events.event import Event
from events.event_types import EventType


class EventGenerator:

    def participant_join(
        self,
        meeting_id,
        participant,
        joined_late=False
    ):

        return Event(

            type=EventType.PARTICIPANT_JOINED,

            meeting_id=meeting_id,

            participant_id=participant.participant_id,

            payload={

                "display_name": participant.display_name,

                "role": participant.role.value,

                "joined_late": joined_late,

                "silent_observer": participant.role.value == "observer"

            },

            timestamp=datetime.utcnow()

        )

    def display_name_changed(
        self,
        meeting_id,
        participant,
        previous_display_name,
        new_display_name
    ):

        return Event(

            type=EventType.DISPLAY_NAME_CHANGED,

            meeting_id=meeting_id,

            participant_id=participant.participant_id,

            payload={

                "display_name": new_display_name,

                "previous_display_name": previous_display_name,

                "role": participant.role.value

            },

            timestamp=datetime.utcnow()

        )

    def camera_on(self, meeting_id, participant):

        return Event(

            type=EventType.CAMERA_ON,

            meeting_id=meeting_id,

            participant_id=participant.participant_id,

            payload={
                "role": participant.role.value
            },

            timestamp=datetime.utcnow()

        )

    def camera_off(self, meeting_id, participant):

        return Event(

            type=EventType.CAMERA_OFF,

            meeting_id=meeting_id,

            participant_id=participant.participant_id,

            payload={
                "role": participant.role.value
            },

            timestamp=datetime.utcnow()

        )

    def transcript_received(
        self,
        meeting_id,
        participant,
        transcript_text,
        speaker="candidate",
        confidence=0.95
    ):
        return Event(
            type=EventType.TRANSCRIPT_RECEIVED,
            meeting_id=meeting_id,
            participant_id=participant.participant_id,
            payload={
                "transcript": transcript_text,
                "speaker": speaker,
                "confidence": confidence,
                "role": participant.role.value
            },
            timestamp=datetime.utcnow()
        )

    def camera_never_on(self, meeting_id, participant):

        return Event(

            type=EventType.CAMERA_NEVER_ON,

            meeting_id=meeting_id,

            participant_id=participant.participant_id,

            payload={
                "role": participant.role.value
            },

            timestamp=datetime.utcnow()

        )

    def disconnect(self, meeting_id, participant):

        return Event(

            type=EventType.PARTICIPANT_LEFT,

            meeting_id=meeting_id,

            participant_id=participant.participant_id,

            payload={
                "role": participant.role.value,
                "reason": "disconnect"
            },

            timestamp=datetime.utcnow()

        )

    def reconnect(self, meeting_id, participant):

        return Event(

            type=EventType.RECONNECTED,

            meeting_id=meeting_id,

            participant_id=participant.participant_id,

            payload={
                "role": participant.role.value
            },

            timestamp=datetime.utcnow()

        )

    def network_lag(self, meeting_id, participant, duration_seconds=1):

        return Event(

            type=EventType.NETWORK_LAG,

            meeting_id=meeting_id,

            participant_id=participant.participant_id,

            payload={
                "role": participant.role.value,
                "duration_seconds": duration_seconds
            },

            timestamp=datetime.utcnow()

        )

    def similar_name_detected(self, meeting_id, participant, similar_names=None):

        return Event(

            type=EventType.SIMILAR_NAME_DETECTED,

            meeting_id=meeting_id,

            participant_id=participant.participant_id,

            payload={
                "role": participant.role.value,
                "display_name": participant.display_name,
                "similar_names": similar_names or []
            },

            timestamp=datetime.utcnow()

        )