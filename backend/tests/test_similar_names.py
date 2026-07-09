from ai.confidence.confidence_engine import ConfidenceEngine
from ai.reasoning.evidence_collector import EvidenceCollector
from events.event import Event
from events.event_types import EventType
from meeting_simulator.event_generator import EventGenerator


def test_similar_name_event_generates_negative_evidence():
    collector = EvidenceCollector()
    event = Event(
        type=EventType.SIMILAR_NAME_DETECTED,
        meeting_id=1,
        participant_id="candidate_001",
        payload={
            "display_name": "John Doe",
            "similar_names": ["Jon Doe"],
        },
    )

    evidence = collector.collect(event)

    assert evidence is not None
    assert evidence.evidence_type == "similar_name"
    assert evidence.confidence_delta < 0
    assert "similar" in evidence.reason.lower()


def test_event_generator_emits_similar_name_event():
    generator = EventGenerator()

    class Participant:
        participant_id = "candidate_001"
        role = type("Role", (), {"value": "candidate"})()
        display_name = "John Doe"

    participant = Participant()
    event = generator.similar_name_detected(
        1,
        participant,
        ["Jon Doe"],
    )

    assert event.type == EventType.SIMILAR_NAME_DETECTED
    assert event.participant_id == "candidate_001"
    assert event.payload["similar_names"] == ["Jon Doe"]


def test_confidence_decreases_for_similar_names():
    engine = ConfidenceEngine()
    collector = EvidenceCollector()

    evidence = collector.collect(
        Event(
            type=EventType.SIMILAR_NAME_DETECTED,
            meeting_id=1,
            participant_id="candidate_001",
            payload={
                "display_name": "John Doe",
                "similar_names": ["Jon Doe"],
            },
        )
    )

    participant = engine.update(evidence)

    assert participant.confidence < 0.50
    assert "similar" in participant.last_reason.lower()
