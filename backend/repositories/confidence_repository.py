from sqlalchemy.orm import Session
from sqlalchemy import func

from models.confidence import ConfidenceSnapshot


class ConfidenceRepository:

    def create(
        self,
        db: Session,
        snapshot: ConfidenceSnapshot,
    ) -> ConfidenceSnapshot:
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        return snapshot

    def get_latest(
        self,
        db: Session,
        participant_id: str,
    ):
        """
        Return the single most-recent ConfidenceSnapshot for a participant.
        Uses a subquery to get the max created_at, then fetches that row.
        """
        subq = (
            db.query(func.max(ConfidenceSnapshot.created_at))
            .filter(ConfidenceSnapshot.participant_id == participant_id)
            .scalar_subquery()
        )
        return (
            db.query(ConfidenceSnapshot)
            .filter(
                ConfidenceSnapshot.participant_id == participant_id,
                ConfidenceSnapshot.created_at == subq,
            )
            .first()
        )

    def get_timeline(
        self,
        db: Session,
        participant_id: str,
    ):
        """All snapshots for a participant ordered oldest → newest."""
        return (
            db.query(ConfidenceSnapshot)
            .filter(ConfidenceSnapshot.participant_id == participant_id)
            .order_by(ConfidenceSnapshot.created_at.asc())
            .all()
        )

    def get_all_by_meeting(
        self,
        db: Session,
        meeting_id: str,
    ):
        """All snapshots for every participant in a meeting."""
        return (
            db.query(ConfidenceSnapshot)
            .filter(ConfidenceSnapshot.meeting_id == meeting_id)
            .order_by(ConfidenceSnapshot.created_at.asc())
            .all()
        )

    def get_latest_per_participant(
        self,
        db: Session,
        meeting_id: str,
    ):
        """
        Return the most-recent snapshot per participant for a meeting.
        Useful for a meeting-level summary card.
        """
        subq = (
            db.query(
                ConfidenceSnapshot.participant_id,
                func.max(ConfidenceSnapshot.created_at).label("max_ts"),
            )
            .filter(ConfidenceSnapshot.meeting_id == meeting_id)
            .group_by(ConfidenceSnapshot.participant_id)
            .subquery()
        )
        results = (
            db.query(ConfidenceSnapshot)
            .join(
                subq,
                (ConfidenceSnapshot.participant_id == subq.c.participant_id)
                & (ConfidenceSnapshot.created_at == subq.c.max_ts),
            )
            .order_by(ConfidenceSnapshot.created_at.desc())
            .all()
        )
        if not results:
            subq_all = (
                db.query(
                    ConfidenceSnapshot.participant_id,
                    func.max(ConfidenceSnapshot.created_at).label("max_ts"),
                )
                .group_by(ConfidenceSnapshot.participant_id)
                .subquery()
            )
            results = (
                db.query(ConfidenceSnapshot)
                .join(
                    subq_all,
                    (ConfidenceSnapshot.participant_id == subq_all.c.participant_id)
                    & (ConfidenceSnapshot.created_at == subq_all.c.max_ts),
                )
                .order_by(ConfidenceSnapshot.created_at.desc())
                .all()
            )
        return results
