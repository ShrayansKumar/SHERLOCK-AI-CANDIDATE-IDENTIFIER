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

            interviewer_names=data.interviewer_names

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