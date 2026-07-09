from models.explanation import ExplanationLog
from repositories.explanation_repository import ExplanationRepository


class ExplanationService:

    def __init__(self):
        self.repository = ExplanationRepository()

    def save_explanation(
        self,
        db,
        participant_id: str,
        explanation: str,
        evidence_type: str = None,
        meeting_id: str = None,
    ):
        log = ExplanationLog(
            participant_id=participant_id,
            explanation=explanation,
            evidence_type=evidence_type,
            meeting_id=meeting_id,
        )
        return self.repository.create(db, log)

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
