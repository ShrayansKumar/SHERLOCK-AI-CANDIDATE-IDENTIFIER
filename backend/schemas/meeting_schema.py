from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr


class MeetingCreate(BaseModel):

    meeting_id: str

    platform: str

    candidate_name: Optional[str] = None

    candidate_email: Optional[EmailStr] = None

    interviewer_names: Optional[str] = None


class MeetingResponse(BaseModel):

    id: int

    meeting_id: str

    platform: str

    candidate_name: Optional[str]

    candidate_email: Optional[str]

    interviewer_names: Optional[str]

    status: str

    model_config = {
        "from_attributes": True
    }