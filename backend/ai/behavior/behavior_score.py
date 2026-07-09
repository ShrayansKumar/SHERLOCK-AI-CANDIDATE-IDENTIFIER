from dataclasses import dataclass, field
from typing import List


@dataclass
class BehaviorScore:
    """
    Aggregate behavioral score for a participant,
    computed from all behavioral signals during a meeting.
    """

    participant_id: str

    engagement_score: float = 0.0
    """How actively the participant engaged: answers, questions, reactions."""

    responsiveness_score: float = 0.0
    """Speed and relevance of responses to interview questions."""

    consistency_score: float = 0.0
    """Consistency of behavior across the session."""

    signals: List[str] = field(default_factory=list)
    """List of behavioral signal names that contributed."""

    def overall(self) -> float:
        """Weighted average of the three sub-scores."""
        weights = [0.4, 0.35, 0.25]
        scores = [
            self.engagement_score,
            self.responsiveness_score,
            self.consistency_score,
        ]
        return round(sum(w * s for w, s in zip(weights, scores)), 4)
