from models.participant import Participant
from repositories.participant_repository import ParticipantRepository


class ParticipantService:

    def __init__(self):

        self.repository = ParticipantRepository()


    def create_participant(
        self,
        db,
        data
    ):

        participant = Participant(

    meeting_id=data.meeting_id,

    participant_id=data.participant_id,

    display_name=data.display_name,

    email=data.email

)

        return self.repository.create(
            db,
            participant
        )


    def get_all(
        self,
        db
    ):

        return self.repository.get_all(db)


    def get_by_id(
        self,
        db,
        participant_id
    ):

        return self.repository.get_by_id(
            db,
            participant_id
        )


    def delete(
        self,
        db,
        participant_id
    ):

        return self.repository.delete(
            db,
            participant_id
        )