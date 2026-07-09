from ai.confidence.confidence_engine import ConfidenceEngine
from ai.reasoning.evidence_collector import EvidenceCollector
from events.event import Event
from events.event_types import EventType
from meeting_simulator.event_generator import EventGenerator


def test_late_join_event_generates_negative_evidence():
    collector = EvidenceCollector()
    event = Event(
        type=EventType.PARTICIPANT_JOINED,
        meeting_id=1,
        participant_id="candidate_001",
        payload={
            "display_name": "John Doe",
            "role": "candidate",
            "joined_late": True,
        },
    )

    evidence = collector.collect(event)

    assert evidence is not None
    assert evidence.evidence_type == "joined_late"
    assert evidence.confidence_delta < 0
    assert "late" in evidence.reason.lower()


def test_late_join_event_generator_emits_expected_event():
    generator = EventGenerator()

    class Participant:
        participant_id = "candidate_001"
        role = type("Role", (), {"value": "candidate"})()
        display_name = "John Doe"

    participant = Participant()
    event = generator.participant_join(1, participant, joined_late=True)

    assert event.type == EventType.PARTICIPANT_JOINED
    assert event.payload["joined_late"] is True


def test_confidence_decreases_for_late_join():
    engine = ConfidenceEngine()
    collector = EvidenceCollector()

    evidence = collector.collect(
        Event(
            type=EventType.PARTICIPANT_JOINED,
            meeting_id=1,
            participant_id="candidate_001",
            payload={
                "display_name": "John Doe",
                "role": "candidate",
                "joined_late": True,
            },
        )
    )

    participant = engine.update(evidence)

    assert participant.confidence < 0.50
    assert "late" in participant.last_reason.lower()
