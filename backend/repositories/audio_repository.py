from sqlalchemy.orm import Session
from models.audio import AudioUpload


class AudioRepository:

    def create(self, db: Session, audio_upload: AudioUpload):
        db.add(audio_upload)
        db.commit()
        db.refresh(audio_upload)
        return audio_upload

    def get_by_participant(self, db: Session, participant_id: str):
        return (
            db.query(AudioUpload)
            .filter(AudioUpload.participant_id == participant_id)
            .order_by(AudioUpload.created_at.asc())
            .all()
        )

    def get_by_meeting(self, db: Session, meeting_id: str):
        return (
            db.query(AudioUpload)
            .filter(AudioUpload.meeting_id == meeting_id)
            .order_by(AudioUpload.created_at.asc())
            .all()
        )
