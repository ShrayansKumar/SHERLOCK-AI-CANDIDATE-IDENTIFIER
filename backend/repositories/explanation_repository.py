from sqlalchemy.orm import Session

from models.explanation import ExplanationLog


class ExplanationRepository:

    def create(
        self,
        db: Session,
        explanation_log: ExplanationLog
    ):
        db.add(explanation_log)
        db.commit()
        db.refresh(explanation_log)
        return explanation_log

    def get_by_participant(
        self,
        db: Session,
        participant_id: str
    ):
        return (
            db.query(ExplanationLog)
            .filter(ExplanationLog.participant_id == participant_id)
            .order_by(ExplanationLog.created_at.asc())
            .all()
        )

    def get_by_meeting(
        self,
        db: Session,
        meeting_id: str
    ):
        return (
            db.query(ExplanationLog)
            .filter(ExplanationLog.meeting_id == meeting_id)
            .order_by(ExplanationLog.created_at.asc())
            .all()
        )
