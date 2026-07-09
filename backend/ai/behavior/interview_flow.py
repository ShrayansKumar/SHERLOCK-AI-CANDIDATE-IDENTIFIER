from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import List


class InterviewPhase(str, Enum):
    INTRO = "intro"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    QA = "qa"
    CLOSING = "closing"
    UNKNOWN = "unknown"


@dataclass
class InterviewFlow:
    """
    Tracks the progression of interview phases during a meeting.
    Used to contextualize evidence (e.g., silence during QA is
    different from silence during technical questions).
    """

    current_phase: InterviewPhase = InterviewPhase.UNKNOWN

    phase_history: List[dict] = field(default_factory=list)

    def transition(self, new_phase: InterviewPhase):
        """Record a phase transition."""
        self.phase_history.append({
            "phase": self.current_phase,
            "ended_at": datetime.utcnow().isoformat(),
        })
        self.current_phase = new_phase

    def elapsed_in_phase(self) -> float:
        """Seconds spent in current phase (rough estimate)."""
        if not self.phase_history:
            return 0.0
        # Not tracked precisely without start timestamps; placeholder
        return 0.0
