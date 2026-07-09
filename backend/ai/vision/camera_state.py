from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class CameraStatus(str, Enum):
    ON = "on"
    OFF = "off"
    NEVER_ON = "never_on"
    UNKNOWN = "unknown"


@dataclass
class CameraState:
    """Tracks the camera state for a participant during a meeting."""

    participant_id: str
    status: CameraStatus = CameraStatus.UNKNOWN
    last_changed: datetime = None
    total_on_seconds: float = 0.0

    def turn_on(self, timestamp: datetime = None):
        self.status = CameraStatus.ON
        self.last_changed = timestamp or datetime.utcnow()

    def turn_off(self, on_duration_seconds: float = 0.0, timestamp: datetime = None):
        self.status = CameraStatus.OFF
        self.total_on_seconds += on_duration_seconds
        self.last_changed = timestamp or datetime.utcnow()

    def mark_never_on(self):
        self.status = CameraStatus.NEVER_ON

    def confidence_delta(self) -> float:
        """Return confidence delta based on current camera status."""
        deltas = {
            CameraStatus.ON: 0.05,
            CameraStatus.OFF: -0.08,
            CameraStatus.NEVER_ON: -0.12,
            CameraStatus.UNKNOWN: 0.0,
        }
        return deltas[self.status]
