from datetime import datetime

from ai.reasoning.evidence import Evidence
from ai.reasoning.evidence_weights import WEIGHTS

from events.event_types import EventType
from ai.display_name.display_name_detector import DisplayNameDetector

display_detector = DisplayNameDetector()

class EvidenceCollector:

    def _display_name_evidence(
        self,
        participant_id,
        display_name,
        previous_display_name=None
    ):

        result = display_detector.detect(display_name)

        if previous_display_name is not None:

            previous_result = display_detector.detect(
                previous_display_name
            )

            if not previous_result["match"] and result["match"]:

                return Evidence(

                    participant_id=participant_id,

                    evidence_type="display_name",

                    confidence_delta=0.20,

                    reason=(
                        "Display name changed from a generic device "
                        "name to a person's name"
                    ),

                    timestamp=datetime.utcnow()

                )

        return Evidence(

            participant_id=participant_id,

            evidence_type="display_name",

            confidence_delta=result["weight"],

            reason=result["reason"],

            timestamp=datetime.utcnow()

        )

    def _metadata_evidence(self, event):

        payload = event.payload or {}
        meeting_metadata = payload.get("meeting_metadata") or {}

        candidate_name = meeting_metadata.get("candidate_name")
        candidate_email = meeting_metadata.get("candidate_email")
        participant_display_name = payload.get("display_name")
        participant_email = payload.get("email")

        if not candidate_name and not candidate_email:
            return None

        matches = []

        if candidate_name and participant_display_name:
            normalized_candidate_name = str(candidate_name).strip().lower()
            normalized_display_name = str(participant_display_name).strip().lower()
            if normalized_candidate_name and normalized_display_name:
                if normalized_candidate_name == normalized_display_name:
                    matches.append("name")

        if candidate_email and participant_email:
            normalized_candidate_email = str(candidate_email).strip().lower()
            normalized_participant_email = str(participant_email).strip().lower()
            if normalized_candidate_email and normalized_participant_email:
                if normalized_candidate_email == normalized_participant_email:
                    matches.append("email")

        if not matches:
            return None

        reason_parts = []
        if "name" in matches:
            reason_parts.append("participant name matched calendar metadata")
        if "email" in matches:
            reason_parts.append("participant email matched calendar metadata")

        return Evidence(

            participant_id=event.participant_id,

            evidence_type="metadata_match",

            confidence_delta=WEIGHTS["metadata_match"],

            reason="Metadata match: " + "; ".join(reason_parts),

            timestamp=datetime.utcnow()

        )

    def collect(self, event):

        if event.type == EventType.CAMERA_ON:

            return Evidence(

                participant_id=event.participant_id,

                evidence_type="camera_on",

                confidence_delta=WEIGHTS["camera_on"],

                reason="Camera turned on",

                timestamp=datetime.utcnow()

            )

        if event.type == EventType.PARTICIPANT_LEFT:

            return Evidence(

                participant_id=event.participant_id,

                evidence_type="disconnect",

                confidence_delta=WEIGHTS["disconnect"],

                reason="Participant disconnected",

                timestamp=datetime.utcnow()

            )

        if event.type == EventType.RECONNECTED:

            return Evidence(

                participant_id=event.participant_id,

                evidence_type="reconnect",

                confidence_delta=WEIGHTS["reconnect"],

                reason="Participant reconnected",

                timestamp=datetime.utcnow()

            )

        if event.type == EventType.NETWORK_LAG:

            duration_seconds = event.payload.get("duration_seconds", 1)

            return Evidence(

                participant_id=event.participant_id,

                evidence_type="network_lag",

                confidence_delta=WEIGHTS["network_lag"],

                reason=f"Network lag detected for {duration_seconds} seconds",

                timestamp=datetime.utcnow()

            )

        if event.type == EventType.SIMILAR_NAME_DETECTED:

            names = event.payload.get("similar_names") or []
            names_text = ", ".join(str(name) for name in names) if names else "another participant"

            return Evidence(

                participant_id=event.participant_id,

                evidence_type="similar_name",

                confidence_delta=WEIGHTS["similar_name"],

                reason=f"Similar name detected: {names_text}",

                timestamp=datetime.utcnow()

            )

        if event.type == EventType.CAMERA_OFF:

            return Evidence(

                participant_id=event.participant_id,

                evidence_type="camera_off",

                confidence_delta=WEIGHTS["camera_off"],

                reason="Camera turned off",

                timestamp=datetime.utcnow()

            )

        if event.type == EventType.CAMERA_NEVER_ON:

            return Evidence(

                participant_id=event.participant_id,

                evidence_type="camera_never_on",

                confidence_delta=WEIGHTS["camera_never_on"],

                reason="Camera was never turned on",

                timestamp=datetime.utcnow()

            )

        if event.type == EventType.SCREEN_SHARE_STARTED:

            return Evidence(

                participant_id=event.participant_id,

                evidence_type="screen_share_without_speaking",

                confidence_delta=WEIGHTS["screen_share_without_speaking"],

                reason="Screen shared without speaking",

                timestamp=datetime.utcnow()

            )

        if event.type == EventType.TRANSCRIPT_RECEIVED:

            transcript = str(event.payload.get("transcript", "")).strip() if event.payload else ""
            speaker = str(event.payload.get("speaker", "")).strip().lower() if event.payload else ""

            if speaker == "candidate" and transcript:
                return Evidence(

                    participant_id=event.participant_id,

                    evidence_type="speech_analysis",

                    confidence_delta=WEIGHTS["speech_analysis"],

                    reason="Speech detected from the candidate",

                    timestamp=datetime.utcnow()

                )

        if event.type == EventType.PARTICIPANT_JOINED:

            if event.payload and event.payload.get("joined_late"):
                return Evidence(

                    participant_id=event.participant_id,

                    evidence_type="joined_late",

                    confidence_delta=WEIGHTS["joined_late"],

                    reason="Participant joined late",

                    timestamp=datetime.utcnow()

                )

            if event.payload and event.payload.get("silent_observer"):
                return Evidence(

                    participant_id=event.participant_id,

                    evidence_type="silent_observer",

                    confidence_delta=WEIGHTS["silent_observer"],

                    reason="Silent observer",

                    timestamp=datetime.utcnow()

                )

            metadata_evidence = self._metadata_evidence(event)
            if metadata_evidence is not None:
                return metadata_evidence

            if not event.payload or not event.payload.get("meeting_metadata"):
                return Evidence(
                    participant_id=event.participant_id,
                    evidence_type="missing_metadata",
                    confidence_delta=WEIGHTS["missing_metadata"],
                    reason="Calendar metadata missing",
                    timestamp=datetime.utcnow(),
                )

            return self._display_name_evidence(
                event.participant_id,
                event.payload["display_name"],
            )

        if event.type == EventType.DISPLAY_NAME_CHANGED:

            return self._display_name_evidence(
                event.participant_id,
                event.payload["display_name"],
                event.payload.get("previous_display_name"),
            )

        metadata_evidence = self._metadata_evidence(event)
        if metadata_evidence is not None:
            return metadata_evidence

        return None