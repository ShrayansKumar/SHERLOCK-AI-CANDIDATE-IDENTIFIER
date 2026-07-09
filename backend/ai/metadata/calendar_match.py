from typing import Optional, Dict


class CalendarMatcher:
    """
    Matches participant identity against calendar/scheduling metadata.
    Checks candidate name and email from meeting invite against
    participant-provided display name and email.
    """

    def match(
        self,
        candidate_name: Optional[str],
        candidate_email: Optional[str],
        participant_display_name: Optional[str],
        participant_email: Optional[str],
    ) -> Dict:
        """
        Returns a match result dict with:
            - matched: bool
            - match_type: 'name', 'email', 'both', or 'none'
            - confidence_delta: float
        """
        name_match = (
            candidate_name
            and participant_display_name
            and candidate_name.strip().lower()
            == participant_display_name.strip().lower()
        )
        email_match = (
            candidate_email
            and participant_email
            and candidate_email.strip().lower()
            == participant_email.strip().lower()
        )

        if name_match and email_match:
            match_type = "both"
            delta = 0.40
        elif email_match:
            match_type = "email"
            delta = 0.35
        elif name_match:
            match_type = "name"
            delta = 0.25
        else:
            match_type = "none"
            delta = 0.0

        return {
            "matched": match_type != "none",
            "match_type": match_type,
            "confidence_delta": delta,
        }
