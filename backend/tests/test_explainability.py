from ai.confidence.confidence_engine import ConfidenceEngine
from ai.reasoning.evidence_collector import EvidenceCollector
from events.event import Event
from events.event_types import EventType


def test_explainability_tracks_last_evidence_summary():
    collector = EvidenceCollector()
    engine = ConfidenceEngine()

    evidence = collector.collect(
        Event(
            type=EventType.CAMERA_ON,
            meeting_id=1,
            participant_id="candidate_001",
            payload={"role": "candidate"},
        )
    )

    participant = engine.update(evidence)

    assert participant.last_reason == "Camera turned on"
    assert participant.explanation == "camera_on: Camera turned on"


def test_explainability_records_multiple_updates():
    collector = EvidenceCollector()
    engine = ConfidenceEngine()

    first = collector.collect(
        Event(
            type=EventType.CAMERA_ON,
            meeting_id=1,
            participant_id="candidate_001",
            payload={"role": "candidate"},
        )
    )
    second = collector.collect(
        Event(
            type=EventType.CAMERA_OFF,
            meeting_id=1,
            participant_id="candidate_001",
            payload={"role": "candidate"},
        )
    )

    engine.update(first)
    participant = engine.update(second)

    assert participant.explanation == "camera_off: Camera turned off"
