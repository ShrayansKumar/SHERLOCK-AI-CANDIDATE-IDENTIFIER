from sqlalchemy.orm import Session

from models.meeting import Meeting


class MeetingRepository:

    def create(
        self,
        db: Session,
        meeting: Meeting
    ):

        db.add(meeting)

        db.commit()

        db.refresh(meeting)

        return meeting


    def get_all(
        self,
        db: Session
    ):

        return db.query(Meeting).order_by(Meeting.created_at.desc()).all()


    def get_by_id(
        self,
        db: Session,
        meeting_id: int
    ):

        return (
            db.query(Meeting)
            .filter(Meeting.id == meeting_id)
            .first()
        )


    def get_by_string_id(
        self,
        db: Session,
        meeting_id_str: str
    ):

        return (
            db.query(Meeting)
            .filter(Meeting.meeting_id == meeting_id_str)
            .first()
        )


    def get_all_ordered(
        self,
        db: Session
    ):

        return (
            db.query(Meeting)
            .order_by(Meeting.created_at.desc())
            .all()
        )