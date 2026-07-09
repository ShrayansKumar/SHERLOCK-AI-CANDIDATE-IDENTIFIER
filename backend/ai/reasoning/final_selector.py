from typing import Dict, Optional


class FinalSelector:
    """
    Selects the most-likely candidate participant from a meeting.
    Operates over the in-memory confidence engine state.
    """

    def select(
        self,
        participants: Dict[str, object],
        min_confidence: float = 0.5,
    ) -> Optional[object]:
        """
        Return the participant with the highest confidence score,
        provided it exceeds min_confidence.

        Args:
            participants: Dict mapping participant_id -> ParticipantConfidence.
            min_confidence: Minimum score threshold to be selected.

        Returns:
            ParticipantConfidence of the top candidate, or None if
            no participant meets the threshold.
        """
        if not participants:
            return None

        top = max(participants.values(), key=lambda p: p.confidence)

        if top.confidence < min_confidence:
            return None

        return top

    def rank(
        self,
        participants: Dict[str, object],
    ) -> list:
        """
        Return all participants sorted by confidence descending.
        """
        return sorted(
            participants.values(),
            key=lambda p: p.confidence,
            reverse=True,
        )
