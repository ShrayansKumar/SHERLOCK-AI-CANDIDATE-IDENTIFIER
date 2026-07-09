from typing import Optional
from datetime import datetime

from pydantic import BaseModel
from pydantic import EmailStr


class MeetingCreate(BaseModel):

    meeting_id: str

    platform: str

    candidate_name: Optional[str] = None

    candidate_email: Optional[EmailStr] = None

    interviewer_names: Optional[str] = None

    job_role: Optional[str] = None

    meeting_link: Optional[str] = None

    expected_duration_minutes: Optional[int] = None


class MeetingResponse(BaseModel):

    id: int

    meeting_id: str

    platform: str

    candidate_name: Optional[str]

    candidate_email: Optional[str]

    interviewer_names: Optional[str]

    status: str

    job_role: Optional[str] = None

    meeting_link: Optional[str] = None

    expected_duration_minutes: Optional[int] = None

    session_start: Optional[datetime] = None

    session_end: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }