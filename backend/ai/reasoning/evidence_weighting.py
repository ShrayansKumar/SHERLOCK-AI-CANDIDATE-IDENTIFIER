from ai.reasoning.evidence_weights import WEIGHTS


class EvidenceWeighter:
    """
    Applies the canonical WEIGHTS dict to evidence types.
    Supports optional per-call weight overrides for A/B testing
    or meeting-specific calibration.
    """

    def get_weight(
        self,
        evidence_type: str,
        override: float = None,
    ) -> float:
        """
        Return the weight for an evidence type.

        Args:
            evidence_type: Key into WEIGHTS dict.
            override: If provided, return this value instead.

        Returns:
            Weight as a signed float (positive = boosts confidence,
            negative = reduces confidence).
        """
        if override is not None:
            return override

        return WEIGHTS.get(evidence_type, 0.0)

    def apply(
        self,
        evidence_type: str,
        current_confidence: float,
        override: float = None,
    ) -> float:
        """
        Apply weight delta to current confidence and clamp to [0, 1].
        """
        delta = self.get_weight(evidence_type, override)
        updated = current_confidence + delta
        return round(max(0.0, min(1.0, updated)), 4)
