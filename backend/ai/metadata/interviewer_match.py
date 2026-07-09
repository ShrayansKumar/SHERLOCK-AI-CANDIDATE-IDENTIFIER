from typing import List, Optional


class InterviewerMatcher:
    """
    Identifies whether a participant is an interviewer
    based on their display name matching known interviewer names.
    """

    def is_interviewer(
        self,
        display_name: str,
        interviewer_names: Optional[str],
    ) -> bool:
        """
        Args:
            display_name: Participant's current display name.
            interviewer_names: Comma-separated string of interviewer names
                               from calendar metadata.

        Returns:
            True if the participant appears to be an interviewer.
        """
        if not interviewer_names:
            return False

        names = [n.strip().lower() for n in interviewer_names.split(",")]
        return display_name.strip().lower() in names

    def confidence_delta(self, is_interviewer: bool) -> float:
        """
        If the participant is confirmed as interviewer, reduce candidate
        confidence significantly.
        """
        return -0.80 if is_interviewer else 0.0
