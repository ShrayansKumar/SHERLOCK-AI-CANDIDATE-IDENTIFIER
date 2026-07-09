from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from dependencies import get_db
from services.confidence_service import ConfidenceService
from repositories.participant_repository import ParticipantRepository

router = APIRouter(
    prefix="/api/v1/confidence",
    tags=["Confidence"],
)

_confidence_svc = ConfidenceService()
_participant_repo = ParticipantRepository()


def _snapshot_to_dict(s, source: str = "postgres") -> dict:
    return {
        "participant_id": s.participant_id,
        "confidence": round(s.confidence, 4),
        "fused_score": round(s.confidence, 4),
        "evidence_type": s.evidence_type,
        "last_reason": s.reason,
        "explanation": (
            f"[{s.evidence_type}] {s.reason}"
            if s.evidence_type and s.reason
            else s.reason
        ),
        "last_updated": s.created_at,
        "source": source,
    }


@router.get("/{participant_id}")
def get_confidence(
    participant_id: str,
    db: Session = Depends(get_db),
):
    """
    Return the current confidence score for a participant.

    Reads exclusively from PostgreSQL:
    1. Latest row in confidence_snapshots  → live/persisted score
    2. participants.confidence column      → fallback if no snapshot yet
    3. 404 if participant doesn't exist at all
    """

    # 1. Query confidence_snapshots for the latest persisted score
    snapshot = _confidence_svc.get_current(db, participant_id)
    if snapshot is not None:
        return _snapshot_to_dict(snapshot, source="postgres")

    # 2. No snapshot yet — check the participants table for the base confidence
    db_participant = _participant_repo.get_by_participant_identifier(
        db, participant_id
    )
    if db_participant is not None:
        return {
            "participant_id": participant_id,
            "confidence": round(db_participant.confidence or 0.50, 4),
            "fused_score": round(db_participant.confidence or 0.50, 4),
            "evidence_type": None,
            "last_reason": "No events processed yet",
            "explanation": (
                f"Participant '{db_participant.display_name}' registered. "
                "Confidence will update as events are processed."
            ),
            "last_updated": db_participant.created_at,
            "source": "participant_default",
        }

    # 3. Unknown participant
    raise HTTPException(
        status_code=404,
        detail=f"Participant '{participant_id}' not found.",
    )


@router.get("/{participant_id}/timeline")
def get_confidence_timeline(
    participant_id: str,
    db: Session = Depends(get_db),
):
    """
    Full confidence timeline for a participant ordered oldest → newest.
    Returns every persisted snapshot from confidence_snapshots.
    """
    snapshots = _confidence_svc.get_timeline(db, participant_id)

    return [
        {
            "id": s.id,
            "participant_id": s.participant_id,
            "confidence": round(s.confidence, 4),
            "evidence_type": s.evidence_type,
            "reason": s.reason,
            "created_at": s.created_at,
        }
        for s in snapshots
    ]


@router.get("/meeting/{meeting_id}")
def get_confidence_by_meeting(
    meeting_id: str,
    db: Session = Depends(get_db),
):
    """
    Latest confidence snapshot per participant for a meeting.
    Returns one entry per participant (most recent snapshot only).
    """
    snapshots = _confidence_svc.get_latest_per_participant(db, meeting_id)

    return [
        {
            "participant_id": s.participant_id,
            "confidence": round(s.confidence, 4),
            "evidence_type": s.evidence_type,
            "reason": s.reason,
            "last_updated": s.created_at,
        }
        for s in snapshots
    ]


@router.get("/meeting/{meeting_id}/all")
def get_all_confidence_by_meeting(
    meeting_id: str,
    db: Session = Depends(get_db),
):
    """
    All confidence snapshots (every event) for a meeting — full history.
    """
    snapshots = _confidence_svc.get_all_by_meeting(db, meeting_id)

    return [
        {
            "id": s.id,
            "participant_id": s.participant_id,
            "confidence": round(s.confidence, 4),
            "evidence_type": s.evidence_type,
            "reason": s.reason,
            "created_at": s.created_at,
        }
        for s in snapshots
    ]