from models.confidence import ConfidenceSnapshot
from repositories.confidence_repository import ConfidenceRepository


class ConfidenceService:

    def __init__(self):
        self.repository = ConfidenceRepository()

    def save_snapshot(
        self,
        db,
        participant_id: str,
        confidence: float,
        evidence_type: str = None,
        reason: str = None,
        meeting_id: str = None,
    ) -> ConfidenceSnapshot:
        """Persist a new confidence snapshot to Postgres."""
        snapshot = ConfidenceSnapshot(
            participant_id=participant_id,
            confidence=confidence,
            evidence_type=evidence_type,
            reason=reason,
            meeting_id=meeting_id,
        )
        return self.repository.create(db, snapshot)

    def get_current(
        self,
        db,
        participant_id: str,
    ):
        """
        Get the current confidence for a participant from Postgres.
        Returns the latest ConfidenceSnapshot row, or None.
        """
        return self.repository.get_latest(db, participant_id)

    def get_latest(
        self,
        db,
        participant_id: str,
    ):
        """Alias for get_current — returns latest snapshot."""
        return self.repository.get_latest(db, participant_id)

    def get_timeline(
        self,
        db,
        participant_id: str,
    ):
        """Full ordered history of confidence snapshots for a participant."""
        return self.repository.get_timeline(db, participant_id)

    def get_all_by_meeting(
        self,
        db,
        meeting_id: str,
    ):
        """All snapshots for all participants in a meeting."""
        return self.repository.get_all_by_meeting(db, meeting_id)

    def get_latest_per_participant(
        self,
        db,
        meeting_id: str,
    ):
        """Latest confidence snapshot per participant for a meeting summary."""
        return self.repository.get_latest_per_participant(db, meeting_id)
