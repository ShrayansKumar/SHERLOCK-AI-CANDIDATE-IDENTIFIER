from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from dependencies import get_db

from services.participant_service import ParticipantService

from schemas.participant_schema import (
    ParticipantCreate,
    ParticipantResponse
)

router = APIRouter(
    prefix="/api/v1/participants",
    tags=["Participants"]
)

service = ParticipantService()


@router.post(
    "",
    response_model=ParticipantResponse
)
def create_participant(
    participant: ParticipantCreate,
    db: Session = Depends(get_db)
):

    return service.create_participant(
        db,
        participant
    )


@router.get(
    "",
    response_model=list[ParticipantResponse]
)
def get_all_participants(
    db: Session = Depends(get_db)
):

    return service.get_all(db)


@router.get(
    "/{participant_id}",
    response_model=ParticipantResponse
)
def get_participant(
    participant_id: int,
    db: Session = Depends(get_db)
):

    participant = service.get_by_id(
        db,
        participant_id
    )

    if participant is None:

        raise HTTPException(
            status_code=404,
            detail="Participant not found"
        )

    return participant


@router.delete(
    "/{participant_id}"
)
def delete_participant(
    participant_id: int,
    db: Session = Depends(get_db)
):

    participant = service.delete(
        db,
        participant_id
    )

    if participant is None:

        raise HTTPException(
            status_code=404,
            detail="Participant not found"
        )

    return {
        "message": "Participant deleted successfully"
    }