from datetime import datetime

from models.meeting import Meeting

from repositories.meeting_repository import MeetingRepository


class MeetingService:

    def __init__(self):

        self.repository = MeetingRepository()

    def create_meeting(
        self,
        db,
        data
    ):

        meeting = Meeting(

            meeting_id=data.meeting_id,

            platform=data.platform,

            candidate_name=data.candidate_name,

            candidate_email=data.candidate_email,

            interviewer_names=data.interviewer_names,

            job_role=getattr(data, "job_role", None),

            meeting_link=getattr(data, "meeting_link", None),

            expected_duration_minutes=getattr(data, "expected_duration_minutes", None),

        )

        return self.repository.create(
            db,
            meeting
        )

    def get_all(
        self,
        db
    ):

        return self.repository.get_all(db)

    def get_by_id(
        self,
        db,
        meeting_id
    ):

        return self.repository.get_by_id(
            db,
            meeting_id
        )

    def start_interview(
        self,
        db,
        meeting_db_id: int
    ) -> Meeting:

        meeting = self.repository.get_by_id(db, meeting_db_id)

        if meeting is None:
            return None

        meeting.status = "live"
        meeting.session_start = datetime.utcnow()

        db.commit()
        db.refresh(meeting)

        return meeting

    def end_interview(
        self,
        db,
        meeting_db_id: int
    ) -> Meeting:

        meeting = self.repository.get_by_id(db, meeting_db_id)

        if meeting is None:
            return None

        meeting.status = "completed"
        meeting.session_end = datetime.utcnow()

        db.commit()
        db.refresh(meeting)

        return meeting

    def get_by_string_id(
        self,
        db,
        meeting_id_str: str
    ):

        return self.repository.get_by_string_id(db, meeting_id_str)

    def get_history(
        self,
        db
    ):

        return self.repository.get_all_ordered(db)