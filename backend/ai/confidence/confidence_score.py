from dataclasses import dataclass
from datetime import datetime


@dataclass
class ConfidenceScore:
    """
    A single scored confidence output with contextual metadata.
    Used as the canonical return type from scoring modules.
    """

    participant_id: str

    score: float
    """Confidence value in [0, 1]. 1.0 = certain candidate."""

    label: str
    """Human-readable label: 'high', 'medium', 'low', 'uncertain'."""

    evidence_type: str

    reason: str

    timestamp: datetime

    @staticmethod
    def from_float(
        participant_id: str,
        score: float,
        evidence_type: str,
        reason: str,
        timestamp: datetime = None,
    ) -> "ConfidenceScore":
        """Factory to build a ConfidenceScore from a raw float."""

        if score >= 0.75:
            label = "high"
        elif score >= 0.50:
            label = "medium"
        elif score >= 0.25:
            label = "low"
        else:
            label = "uncertain"

        return ConfidenceScore(
            participant_id=participant_id,
            score=score,
            label=label,
            evidence_type=evidence_type,
            reason=reason,
            timestamp=timestamp or datetime.utcnow(),
        )
