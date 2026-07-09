from typing import List, Dict


class WeightedFusion:
    """
    Fuses multiple evidence signals into a single confidence score
    using weighted averaging.

    Useful when running multiple independent detectors simultaneously
    (e.g., display name + camera + speech) and combining their outputs.
    """

    def fuse(
        self,
        signals: List[Dict],
        base_confidence: float = 0.5,
    ) -> float:
        """
        Fuse a list of evidence signals into one confidence score.

        Each signal dict should have:
            - 'confidence_delta': signed float
            - 'weight': relative importance [0, 1], defaults to 1.0

        Args:
            signals: List of signal dicts.
            base_confidence: Starting confidence before applying signals.

        Returns:
            Fused confidence value clamped to [0, 1].
        """
        if not signals:
            return round(base_confidence, 4)

        total_weight = sum(s.get("weight", 1.0) for s in signals)

        if total_weight == 0:
            return round(base_confidence, 4)

        weighted_delta = sum(
            s.get("confidence_delta", 0.0) * s.get("weight", 1.0)
            for s in signals
        ) / total_weight

        fused = base_confidence + weighted_delta
        return round(max(0.0, min(1.0, fused)), 4)
