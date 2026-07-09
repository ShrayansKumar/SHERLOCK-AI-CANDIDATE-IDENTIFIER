from ai.confidence.confidence_engine import ConfidenceEngine
from ai.reasoning.evidence_collector import EvidenceCollector
from events.event import Event
from events.event_types import EventType
from meeting_simulator.event_generator import EventGenerator


def test_camera_on_event_generates_positive_evidence():
    collector = EvidenceCollector()
    event = Event(
        type=EventType.CAMERA_ON,
        meeting_id=1,
        participant_id="candidate_001",
    )

    evidence = collector.collect(event)

    assert evidence is not None
    assert evidence.evidence_type == "camera_on"
    assert evidence.confidence_delta > 0
    assert "camera" in evidence.reason.lower()


def test_camera_off_event_generates_negative_evidence():
    collector = EvidenceCollector()
    event = Event(
        type=EventType.CAMERA_OFF,
        meeting_id=1,
        participant_id="candidate_001",
    )

    evidence = collector.collect(event)

    assert evidence is not None
    assert evidence.evidence_type == "camera_off"
    assert evidence.confidence_delta < 0
    assert "camera" in evidence.reason.lower()


def test_simulator_generates_camera_events_for_candidate():
    generator = EventGenerator()
    participant = type("Participant", (), {"participant_id": "candidate_001", "role": type("Role", (), {"value": "candidate"})()})()

    on_event = generator.camera_on(1, participant)
    off_event = generator.camera_off(1, participant)

    assert on_event.type == EventType.CAMERA_ON
    assert off_event.type == EventType.CAMERA_OFF
    assert on_event.participant_id == "candidate_001"
    assert off_event.participant_id == "candidate_001"


def test_confidence_updates_follow_camera_timeline():
    engine = ConfidenceEngine()
    collector = EvidenceCollector()

    start = engine.get_confidence("candidate_001")
    assert start is None

    on_evidence = collector.collect(Event(type=EventType.CAMERA_ON, meeting_id=1, participant_id="candidate_001"))
    on_participant = engine.update(on_evidence)

    assert on_participant.confidence == 0.55

    off_evidence = collector.collect(Event(type=EventType.CAMERA_OFF, meeting_id=1, participant_id="candidate_001"))
    off_participant = engine.update(off_evidence)

    assert abs(off_participant.confidence - 0.47) < 1e-9
