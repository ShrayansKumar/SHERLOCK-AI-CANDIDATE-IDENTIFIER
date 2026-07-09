from models.transcript import Transcript
from repositories.transcript_repository import TranscriptRepository


class TranscriptService:

    def __init__(self):
        self.repository = TranscriptRepository()

    def save_transcript(
        self,
        db,
        participant_id: str,
        text: str,
        speaker: str = None,
        confidence: float = None,
        meeting_id: str = None,
    ):
        transcript = Transcript(
            participant_id=participant_id,
            text=text,
            speaker=speaker,
            confidence=confidence,
            meeting_id=meeting_id,
        )
        return self.repository.create(db, transcript)

    def get_by_participant(
        self,
        db,
        participant_id: str
    ):
        return self.repository.get_by_participant(db, participant_id)

    def get_by_meeting(
        self,
        db,
        meeting_id: str
    ):
        return self.repository.get_by_meeting(db, meeting_id)

    def delete_by_participant(
        self,
        db,
        participant_id: str
    ):
        return self.repository.delete_by_participant(db, participant_id)
