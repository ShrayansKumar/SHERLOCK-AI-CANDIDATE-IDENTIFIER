from sqlalchemy.orm import Session
from models.video import VideoUpload


class VideoRepository:

    def create(self, db: Session, video_upload: VideoUpload) -> VideoUpload:
        db.add(video_upload)
        db.commit()
        db.refresh(video_upload)
        return video_upload

    def get_by_participant(self, db: Session, participant_id: str):
        return (
            db.query(VideoUpload)
            .filter(VideoUpload.participant_id == participant_id)
            .order_by(VideoUpload.created_at.asc())
            .all()
        )

    def get_by_meeting(self, db: Session, meeting_id: str):
        return (
            db.query(VideoUpload)
            .filter(VideoUpload.meeting_id == meeting_id)
            .order_by(VideoUpload.created_at.asc())
            .all()
        )

    def get_by_id(self, db: Session, upload_id: int):
        return db.query(VideoUpload).filter(VideoUpload.id == upload_id).first()
