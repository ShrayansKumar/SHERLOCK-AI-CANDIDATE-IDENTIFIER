from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies import get_db
from services.explanation_service import ExplanationService

router = APIRouter(
    prefix="/api/v1/explanations",
    tags=["Explanations"],
)

explanation_service = ExplanationService()


@router.get("/{participant_id}")
def get_explanations(
    participant_id: str,
    db: Session = Depends(get_db),
):
    """Get all persisted AI explanations for a participant."""

    logs = explanation_service.get_by_participant(db, participant_id)

    return [
        {
            "id": log.id,
            "participant_id": log.participant_id,
            "evidence_type": log.evidence_type,
            "explanation": log.explanation,
            "created_at": log.created_at,
        }
        for log in logs
    ]


@router.get("/meeting/{meeting_id}")
def get_explanations_by_meeting(
    meeting_id: str,
    db: Session = Depends(get_db),
):
    """Get all explanations generated during a meeting."""

    logs = explanation_service.get_by_meeting(db, meeting_id)

    return [
        {
            "id": log.id,
            "participant_id": log.participant_id,
            "evidence_type": log.evidence_type,
            "explanation": log.explanation,
            "created_at": log.created_at,
        }
        for log in logs
    ]
