from ai.confidence.confidence_engine import ConfidenceEngine
from ai.reasoning.evidence_collector import EvidenceCollector
from events.event import Event
from events.event_types import EventType
from meeting_simulator.event_generator import EventGenerator


def test_camera_never_on_event_generates_negative_evidence():
    collector = EvidenceCollector()
    event = Event(
        type=EventType.CAMERA_NEVER_ON,
        meeting_id=1,
        participant_id="candidate_001",
        payload={"role": "candidate"},
    )

    evidence = collector.collect(event)

    assert evidence is not None
    assert evidence.evidence_type == "camera_never_on"
    assert evidence.confidence_delta < 0
    assert "camera" in evidence.reason.lower()


def test_event_generator_emits_camera_never_on_event():
    generator = EventGenerator()

    class Participant:
        participant_id = "candidate_001"
        role = type("Role", (), {"value": "candidate"})()
        display_name = "John Doe"

    participant = Participant()
    event = generator.camera_never_on(1, participant)

    assert event.type == EventType.CAMERA_NEVER_ON
    assert event.participant_id == "candidate_001"


def test_confidence_decreases_for_camera_never_on():
    engine = ConfidenceEngine()
    collector = EvidenceCollector()

    evidence = collector.collect(
        Event(
            type=EventType.CAMERA_NEVER_ON,
            meeting_id=1,
            participant_id="candidate_001",
            payload={"role": "candidate"},
        )
    )

    participant = engine.update(evidence)

    assert participant.confidence < 0.50
    assert "camera" in participant.last_reason.lower()
