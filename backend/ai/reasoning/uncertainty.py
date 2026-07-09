import math
from typing import Tuple


class UncertaintyEstimator:
    """
    Estimates uncertainty around a confidence score using a
    Wilson score interval approximation.

    Provides a confidence interval and an uncertainty label
    based on the number of evidence events observed.
    """

    def estimate(
        self,
        confidence: float,
        n_observations: int,
        z: float = 1.96,
    ) -> Tuple[float, float]:
        """
        Compute a Wilson score confidence interval.

        Args:
            confidence: Point estimate in [0, 1].
            n_observations: Number of evidence events seen.
            z: Z-score for desired CI level (1.96 = 95%).

        Returns:
            (lower, upper) bounds of the confidence interval.
        """
        if n_observations == 0:
            return (0.0, 1.0)

        p = confidence
        n = n_observations
        z2 = z * z

        centre = (p + z2 / (2 * n)) / (1 + z2 / n)
        margin = (z / (1 + z2 / n)) * math.sqrt(
            p * (1 - p) / n + z2 / (4 * n * n)
        )

        lower = round(max(0.0, centre - margin), 4)
        upper = round(min(1.0, centre + margin), 4)

        return (lower, upper)

    def label(self, lower: float, upper: float) -> str:
        """Return a human-readable uncertainty label from the interval width."""
        width = upper - lower
        if width < 0.10:
            return "very certain"
        elif width < 0.25:
            return "fairly certain"
        elif width < 0.40:
            return "uncertain"
        else:
            return "highly uncertain"
