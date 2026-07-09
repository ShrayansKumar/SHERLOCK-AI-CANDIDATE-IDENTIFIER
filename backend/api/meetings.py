from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import get_db
from services.meeting_service import MeetingService
from schemas.meeting_schema import MeetingCreate, MeetingResponse

router = APIRouter(
    prefix="/api/v1/meetings",
    tags=["Meetings"]
)

service = MeetingService()


@router.post(
    "",
    response_model=MeetingResponse,
    status_code=201
)
def create_meeting(
    meeting: MeetingCreate,
    db: Session = Depends(get_db)
):
    return service.create_meeting(db, meeting)


@router.get(
    "",
    response_model=list[MeetingResponse]
)
def get_meetings(
    db: Session = Depends(get_db)
):
    return service.get_all(db)


# NOTE: /history MUST be defined before /{meeting_id} to avoid routing conflict
@router.get(
    "/history",
    response_model=list[MeetingResponse]
)
def get_meeting_history(
    db: Session = Depends(get_db)
):
    return service.get_history(db)


@router.post(
    "/{meeting_db_id}/start",
    response_model=MeetingResponse
)
def start_interview(
    meeting_db_id: int,
    db: Session = Depends(get_db)
):
    meeting = service.start_interview(db, meeting_db_id)

    if meeting is None:
        raise HTTPException(
            status_code=404,
            detail="Meeting not found"
        )

    return meeting


@router.post(
    "/{meeting_db_id}/end",
    response_model=MeetingResponse
)
def end_interview(
    meeting_db_id: int,
    db: Session = Depends(get_db)
):
    meeting = service.end_interview(db, meeting_db_id)

    if meeting is None:
        raise HTTPException(
            status_code=404,
            detail="Meeting not found"
        )

    return meeting


@router.get(
    "/{meeting_id}",
    response_model=MeetingResponse
)
def get_meeting(
    meeting_id: int,
    db: Session = Depends(get_db)
):

    meeting = service.get_by_id(db, meeting_id)

    if meeting is None:
        raise HTTPException(
            status_code=404,
            detail="Meeting not found"
        )

    return meeting


@router.delete("/{meeting_id}")
def delete_meeting(
    meeting_id: int,
    db: Session = Depends(get_db)
):
    meeting = service.get_by_id(db, meeting_id)
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    db.delete(meeting)
    db.commit()
    return {"status": "ok", "deleted": meeting_id}