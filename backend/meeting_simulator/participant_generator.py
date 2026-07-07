from dataclasses import dataclass
from enum import Enum
import random


class ParticipantRole(str, Enum):
    CANDIDATE = "candidate"
    INTERVIEWER = "interviewer"
    OBSERVER = "observer"


@dataclass
class FakeParticipant:
    participant_id: str
    display_name: str
    role: ParticipantRole


class ParticipantGenerator:

    def generate(self):

        return [

            FakeParticipant(
                "candidate_001",
                "MacBook Pro",
                ParticipantRole.CANDIDATE
            ),

            FakeParticipant(
                "interviewer_001",
                "Alice",
                ParticipantRole.INTERVIEWER
            ),

            FakeParticipant(
                "interviewer_002",
                "Bob",
                ParticipantRole.INTERVIEWER
            ),

            FakeParticipant(
                "observer_001",
                "HR Observer",
                ParticipantRole.OBSERVER
            )
        ]