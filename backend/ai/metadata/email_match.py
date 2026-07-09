from typing import Optional


class EmailMatcher:
    """
    Dedicated email-based identity matching.
    Normalises email addresses before comparing.
    """

    @staticmethod
    def _normalise(email: str) -> str:
        return email.strip().lower()

    def match(
        self,
        expected_email: Optional[str],
        observed_email: Optional[str],
    ) -> bool:
        """
        Return True if both emails are non-empty and equal after normalisation.
        """
        if not expected_email or not observed_email:
            return False

        return (
            self._normalise(expected_email)
            == self._normalise(observed_email)
        )

    def confidence_delta(self, matched: bool) -> float:
        """Confidence contribution of an email match/non-match."""
        return 0.35 if matched else 0.0
