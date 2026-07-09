from datetime import datetime, timedelta


class ConfidenceDecay:
    """
    Applies time-based exponential decay to a confidence score.
    Scores drift toward 0.5 (neutral) when no new evidence arrives.
    """

    def __init__(self, half_life_minutes: float = 30.0):
        """
        Args:
            half_life_minutes: Time (in minutes) for confidence to
                               decay halfway toward 0.5.
        """
        self.half_life_minutes = half_life_minutes

    def apply(
        self,
        confidence: float,
        last_updated: datetime,
        reference_time: datetime = None,
    ) -> float:
        """
        Decay the confidence score toward 0.5 based on elapsed time.

        Args:
            confidence: Current confidence value [0, 1].
            last_updated: Timestamp of last evidence.
            reference_time: Time to decay to (defaults to now).

        Returns:
            Decayed confidence value [0, 1].
        """
        if reference_time is None:
            reference_time = datetime.utcnow()

        elapsed = (reference_time - last_updated).total_seconds() / 60.0
        decay_factor = 0.5 ** (elapsed / self.half_life_minutes)

        # Decay toward neutral (0.5)
        decayed = 0.5 + (confidence - 0.5) * decay_factor

        return round(max(0.0, min(1.0, decayed)), 4)
