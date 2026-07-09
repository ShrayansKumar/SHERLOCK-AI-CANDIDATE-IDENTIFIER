from collections import defaultdict
from typing import Dict


class WeightOptimizer:
    """
    Adjusts evidence weights based on accumulated feedback.
    Uses a simple gradient-descent-style update:
        new_weight = old_weight + learning_rate * mean_error
    """

    def __init__(self, learning_rate: float = 0.01):
        self.learning_rate = learning_rate

    def optimize(
        self,
        feedback_log: list,
        current_weights: Dict[str, float],
    ) -> Dict[str, float]:
        """
        Compute updated weights from feedback errors.

        Args:
            feedback_log: List of feedback dicts from ContinualLearner.
            current_weights: Current WEIGHTS dict.

        Returns:
            Updated weights dict.
        """
        error_sums: Dict[str, float] = defaultdict(float)
        counts: Dict[str, int] = defaultdict(int)

        for record in feedback_log:
            et = record.get("evidence_type")
            err = record.get("error", 0.0)
            if et:
                error_sums[et] += err
                counts[et] += 1

        updated = dict(current_weights)

        for evidence_type, total_err in error_sums.items():
            mean_err = total_err / counts[evidence_type]
            old_w = updated.get(evidence_type, 0.0)
            new_w = old_w + self.learning_rate * mean_err
            # Clamp weights to a reasonable range
            updated[evidence_type] = round(max(-1.0, min(1.0, new_w)), 4)

        return updated
