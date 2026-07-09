from sqlalchemy.orm import Session

from models.transcript import Transcript


class TranscriptRepository:

    def create(
        self,
        db: Session,
        transcript: Transcript
    ):
        db.add(transcript)
        db.commit()
        db.refresh(transcript)
        return transcript

    def get_by_participant(
        self,
        db: Session,
        participant_id: str
    ):
        return (
            db.query(Transcript)
            .filter(Transcript.participant_id == participant_id)
            .order_by(Transcript.created_at.asc())
            .all()
        )

    def get_by_meeting(
        self,
        db: Session,
        meeting_id: str
    ):
        return (
            db.query(Transcript)
            .filter(Transcript.meeting_id == meeting_id)
            .order_by(Transcript.created_at.asc())
            .all()
        )

    def delete_by_participant(
        self,
        db: Session,
        participant_id: str
    ):
        count = db.query(Transcript).filter(Transcript.participant_id == participant_id).delete()
        db.commit()
        return count
