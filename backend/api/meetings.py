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