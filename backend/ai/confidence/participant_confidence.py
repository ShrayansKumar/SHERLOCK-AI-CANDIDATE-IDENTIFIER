from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ParticipantConfidence:

    participant_id: str

    confidence: float = 0.50

    last_updated: datetime = field(default_factory=datetime.utcnow)