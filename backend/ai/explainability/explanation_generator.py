from typing import List, Dict


class ExplanationGenerator:
    """
    Generates human-readable explanations from AI evidence signals.
    Rule-based for now; designed to be replaced/augmented by an LLM.
    """

    _TEMPLATES = {
        "display_name": (
            "The participant's display name {reason}. "
            "This {direction} the likelihood they are the candidate."
        ),
        "camera_on": (
            "The participant turned their camera on, which is a positive "
            "engagement signal."
        ),
        "camera_off": (
            "The participant turned their camera off. This reduces "
            "confidence that they are the candidate."
        ),
        "camera_never_on": (
            "The camera was never turned on during the session. "
            "This is a notable absence of a key identity signal."
        ),
        "speech_analysis": (
            "Speech was detected from the participant consistent with "
            "the candidate role."
        ),
        "metadata_match": (
            "The participant's name or email matched the meeting's "
            "calendar metadata — a strong identity signal."
        ),
        "missing_metadata": (
            "Calendar metadata was missing for this participant. "
            "Unable to verify identity from scheduling data."
        ),
        "disconnect": (
            "The participant disconnected from the meeting. "
            "This may indicate a shared or unstable device."
        ),
        "reconnect": (
            "The participant reconnected. Repeated reconnections "
            "may indicate a shared device."
        ),
        "network_lag": (
            "Network lag was detected. This may indicate a shared "
            "or poor-quality connection."
        ),
        "similar_name": (
            "A participant with a similar name was also in the meeting. "
            "This creates ambiguity in candidate identification."
        ),
        "joined_late": (
            "The participant joined the meeting late, which is a "
            "mild negative signal."
        ),
        "silent_observer": (
            "The participant joined but remained silent throughout — "
            "possibly an observer or recruiter."
        ),
        "screen_share_without_speaking": (
            "The participant shared their screen without speaking, "
            "which is unusual for a candidate."
        ),
    }

    def generate(
        self,
        evidence_type: str,
        reason: str,
        confidence_delta: float,
    ) -> str:
        """
        Generate a human-readable explanation string.

        Args:
            evidence_type: The type of evidence signal.
            reason: Short machine-generated reason from the collector.
            confidence_delta: Signed confidence change.

        Returns:
            Human-readable explanation string.
        """
        direction = "increases" if confidence_delta >= 0 else "decreases"

        template = self._TEMPLATES.get(evidence_type)

        if template:
            try:
                return template.format(
                    reason=reason,
                    direction=direction,
                )
            except KeyError:
                pass

        # Fallback — generic explanation
        delta_str = f"{confidence_delta:+.2f}"
        return (
            f"Evidence: {evidence_type} — {reason} "
            f"(confidence change: {delta_str})"
        )
