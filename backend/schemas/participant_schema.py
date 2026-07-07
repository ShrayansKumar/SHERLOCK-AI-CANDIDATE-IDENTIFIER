from pydantic import BaseModel, EmailStr
from typing import Optional


class ParticipantCreate(BaseModel):
    meeting_id: int
    participant_id: str
    display_name: str
    email: Optional[EmailStr] = None
    


class ParticipantResponse(BaseModel):
    id: int
    participant_id: str
    display_name: str
    email: Optional[str]
    role: str
    webcam_on: bool
    microphone_on: bool
    screen_share: bool
    speaking_duration: float
    confidence: float
    status: str

    model_config = {
        "from_attributes": True
    }