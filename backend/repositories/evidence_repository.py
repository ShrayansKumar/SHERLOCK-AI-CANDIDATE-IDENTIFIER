from sqlalchemy.orm import Session

from models.evidence import EvidenceLog


class EvidenceRepository:

    def create(
        self,
        db: Session,
        evidence_log: EvidenceLog
    ):
        db.add(evidence_log)
        db.commit()
        db.refresh(evidence_log)
        return evidence_log

    def get_by_participant(
        self,
        db: Session,
        participant_id: str
    ):
        return (
            db.query(EvidenceLog)
            .filter(EvidenceLog.participant_id == participant_id)
            .order_by(EvidenceLog.created_at.asc())
            .all()
        )

    def get_by_meeting(
        self,
        db: Session,
        meeting_id: str
    ):
        return (
            db.query(EvidenceLog)
            .filter(EvidenceLog.meeting_id == meeting_id)
            .order_by(EvidenceLog.created_at.asc())
            .all()
        )
