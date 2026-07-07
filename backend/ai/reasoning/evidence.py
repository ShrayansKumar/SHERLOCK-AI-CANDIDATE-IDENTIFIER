from dataclasses import dataclass
from datetime import datetime


@dataclass
class Evidence:

    participant_id: str

    evidence_type: str

    confidence_delta: float

    reason: str

    timestamp: datetime