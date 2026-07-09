from datetime import datetime

from ai.confidence.participant_confidence import (
    ParticipantConfidence,
)

from ai.confidence.confidence_history import (
    ConfidenceHistory,
)


class ConfidenceEngine:

    def __init__(self):

        self.participants = {}

        self.history = ConfidenceHistory()

    def update(
        self,
        evidence
    ):

        pid = evidence.participant_id

        if pid not in self.participants:

            self.participants[pid] = ParticipantConfidence(
                participant_id=pid
            )

        participant = self.participants[pid]

        participant.confidence += evidence.confidence_delta

        participant.confidence = max(
            0,
            min(1, participant.confidence)
        )

        participant.last_reason = evidence.reason
        participant.explanation = (
            f"{evidence.evidence_type}: {evidence.reason}"
        )
        participant.fused_score = participant.confidence
        participant.last_updated = datetime.utcnow()

        self.history.add(
            pid,
            participant.confidence,
            reason=evidence.reason,
            evidence_type=evidence.evidence_type,
            timestamp=participant.last_updated,
        )

        return participant

    def get_confidence(
        self,
        participant_id
    ):

        return self.participants.get(
            participant_id
        )