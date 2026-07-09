from typing import Optional
from datetime import datetime


class FeedbackCollector:
    """
    Collects explicit human feedback on Sherlock's candidate
    identification decisions.
    """

    def __init__(self):
        self._records = []

    def submit(
        self,
        meeting_id: str,
        participant_id: str,
        predicted_candidate: bool,
        actual_candidate: bool,
        notes: Optional[str] = None,
    ):
        """
        Submit human-verified feedback for a participant decision.

        Args:
            meeting_id: The meeting where identification occurred.
            participant_id: The participant that was evaluated.
            predicted_candidate: What Sherlock predicted.
            actual_candidate: Ground truth from recruiter/HR.
            notes: Optional free-text notes.
        """
        self._records.append({
            "meeting_id": meeting_id,
            "participant_id": participant_id,
            "predicted_candidate": predicted_candidate,
            "actual_candidate": actual_candidate,
            "correct": predicted_candidate == actual_candidate,
            "notes": notes,
            "submitted_at": datetime.utcnow().isoformat(),
        })

    def accuracy(self) -> float:
        """Return overall prediction accuracy from submitted feedback."""
        if not self._records:
            return 0.0
        correct = sum(1 for r in self._records if r["correct"])
        return round(correct / len(self._records), 4)

    def all_records(self):
        return list(self._records)
