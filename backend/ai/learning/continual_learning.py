from typing import List, Dict
from ai.reasoning.evidence_weights import WEIGHTS


class ContinualLearner:
    """
    Accumulates feedback signals to enable future weight recalibration.
    Stores feedback as a running log; weight updates are applied
    by WeightOptimizer in a separate step.
    """

    def __init__(self):
        self._feedback_log: List[Dict] = []

    def record_feedback(
        self,
        evidence_type: str,
        predicted_confidence: float,
        actual_outcome: float,
        meeting_id: str = None,
    ):
        """
        Record a labelled outcome for a prediction.

        Args:
            evidence_type: The evidence type that drove the prediction.
            predicted_confidence: Model's confidence output.
            actual_outcome: Ground-truth (1.0 = was candidate, 0.0 = was not).
            meeting_id: Optional meeting context.
        """
        self._feedback_log.append({
            "evidence_type": evidence_type,
            "predicted": predicted_confidence,
            "actual": actual_outcome,
            "error": actual_outcome - predicted_confidence,
            "meeting_id": meeting_id,
        })

    def get_feedback(self) -> List[Dict]:
        return list(self._feedback_log)

    def clear(self):
        self._feedback_log.clear()
