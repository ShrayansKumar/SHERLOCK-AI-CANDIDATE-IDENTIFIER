from datetime import datetime
from typing import Optional


class ScheduleMatcher:
    """
    Evaluates whether a participant's join time matches the
    scheduled meeting start time.
    """

    def evaluate(
        self,
        scheduled_start: datetime,
        actual_join: datetime,
        late_threshold_minutes: float = 5.0,
        early_threshold_minutes: float = 15.0,
    ) -> dict:
        """
        Compare actual join time to scheduled start.

        Args:
            scheduled_start: Meeting start time (UTC).
            actual_join: Participant's join time (UTC).
            late_threshold_minutes: Minutes past start = "late".
            early_threshold_minutes: Minutes before start = "very early" (suspicious).

        Returns:
            {"status": str, "delta_minutes": float, "confidence_delta": float}
        """
        delta = (actual_join - scheduled_start).total_seconds() / 60.0

        if delta > late_threshold_minutes:
            status = "late"
            confidence_delta = -0.10
        elif delta < -early_threshold_minutes:
            status = "very_early"
            confidence_delta = -0.05
        else:
            status = "on_time"
            confidence_delta = 0.05

        return {
            "status": status,
            "delta_minutes": round(delta, 1),
            "confidence_delta": confidence_delta,
        }
