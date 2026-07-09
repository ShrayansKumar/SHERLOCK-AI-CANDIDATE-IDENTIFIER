from ai.confidence.confidence_engine import ConfidenceEngine
from ai.reasoning.evidence_collector import EvidenceCollector
from events.event import Event
from events.event_types import EventType
from meeting_simulator.event_generator import EventGenerator
from meeting_simulator.participant_generator import ParticipantGenerator


def test_display_name_changed_event_produces_positive_evidence():
    collector = EvidenceCollector()
    event = Event(
        type=EventType.DISPLAY_NAME_CHANGED,
        meeting_id=1,
        participant_id="candidate_001",
        payload={"display_name": "John Doe"},
    )

    evidence = collector.collect(event)

    assert evidence is not None
    assert evidence.evidence_type == "display_name"
    assert evidence.confidence_delta > 0
    assert "person" in evidence.reason.lower()


def test_display_name_change_pipeline_increases_confidence():
    generator = ParticipantGenerator()
    participant = generator.generate()[0]
    event_generator = EventGenerator()

    event = event_generator.display_name_changed(
        1,
        participant,
        "MacBook Pro",
        "John Doe",
    )

    collector = EvidenceCollector()
    evidence = collector.collect(event)

    engine = ConfidenceEngine()
    participant_confidence = engine.update(evidence)

    assert evidence is not None
    assert participant_confidence.confidence > 0.50
    assert participant_confidence.participant_id == "candidate_001"
