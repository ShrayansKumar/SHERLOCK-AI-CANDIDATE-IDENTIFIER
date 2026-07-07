from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from events.event_types import EventType


@dataclass
class Event:

    type: EventType

    meeting_id: int

    participant_id: str

    payload: dict[str, Any] = field(default_factory=dict)

    timestamp: datetime = field(default_factory=datetime.utcnow)