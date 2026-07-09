from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies import get_db
from services.transcript_service import TranscriptService
from models.confidence import ConfidenceSnapshot
from models.explanation import ExplanationLog

router = APIRouter(
    prefix="/api/v1/transcripts",
    tags=["Transcripts"],
)

transcript_service = TranscriptService()


@router.get("/{participant_id}")
def get_transcripts(
    participant_id: str,
    db: Session = Depends(get_db),
):
    """Get all transcript segments for a participant."""

    transcripts = transcript_service.get_by_participant(db, participant_id)

    return [
        {
            "id": t.id,
            "participant_id": t.participant_id,
            "speaker": t.speaker,
            "text": t.text,
            "confidence": t.confidence,
            "created_at": t.created_at,
        }
        for t in transcripts
    ]


@router.get("/meeting/{meeting_id}")
def get_transcripts_by_meeting(
    meeting_id: str,
    db: Session = Depends(get_db),
):
    """Get all transcript segments for an entire meeting."""

    transcripts = transcript_service.get_by_meeting(db, meeting_id)

    return [
        {
            "id": t.id,
            "participant_id": t.participant_id,
            "speaker": t.speaker,
            "text": t.text,
            "confidence": t.confidence,
            "created_at": t.created_at,
        }
        for t in transcripts
    ]


@router.delete("/clear/{participant_id}")
def clear_participant_transcripts(
    participant_id: str,
    db: Session = Depends(get_db),
):
    """Clear historical transcripts, confidence snapshots, and explanations for a participant to reset session."""
    deleted_count = transcript_service.delete_by_participant(db, participant_id)
    db.query(ConfidenceSnapshot).filter(ConfidenceSnapshot.participant_id == participant_id).delete()
    db.query(ExplanationLog).filter(ExplanationLog.participant_id == participant_id).delete()
    db.commit()
    return {"status": "ok", "deleted": deleted_count}
