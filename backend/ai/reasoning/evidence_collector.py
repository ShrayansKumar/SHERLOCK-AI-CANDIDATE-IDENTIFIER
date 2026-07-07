from datetime import datetime

from ai.reasoning.evidence import Evidence
from ai.reasoning.evidence_weights import WEIGHTS

from events.event_types import EventType
from ai.display_name.display_name_detector import DisplayNameDetector

display_detector = DisplayNameDetector()

class EvidenceCollector:

    def collect(self, event):

        if event.type == EventType.CAMERA_OFF:

            return Evidence(

                participant_id=event.participant_id,

                evidence_type="camera_off",

                confidence_delta=WEIGHTS["camera_off"],

                reason="Camera turned off",

                timestamp=datetime.utcnow()

            )

        if event.type == EventType.PARTICIPANT_JOINED:

            result = display_detector.detect(event.payload["display_name"])

            return Evidence(

                participant_id=event.participant_id,

                evidence_type="display_name",

                confidence_delta=result["weight"],

                reason=result["reason"],

                timestamp=datetime.utcnow()

            )

        return None