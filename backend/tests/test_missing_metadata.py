from ai.confidence.confidence_engine import ConfidenceEngine
from ai.reasoning.evidence_collector import EvidenceCollector
from events.event import Event
from events.event_types import EventType


def test_missing_metadata_generates_negative_evidence():
    collector = EvidenceCollector()
    event = Event(
        type=EventType.PARTICIPANT_JOINED,
        meeting_id=1,
        participant_id="candidate_001",
        payload={
            "display_name": "John Doe",
            "email": "john@example.com",
        },
    )

    evidence = collector.collect(event)

    assert evidence is not None
    assert evidence.evidence_type == "missing_metadata"
    assert evidence.confidence_delta < 0
    assert "metadata" in evidence.reason.lower()


def test_confidence_decreases_for_missing_metadata():
    engine = ConfidenceEngine()
    collector = EvidenceCollector()

    evidence = collector.collect(
        Event(
            type=EventType.PARTICIPANT_JOINED,
            meeting_id=1,
            participant_id="candidate_001",
            payload={
                "display_name": "John Doe",
                "email": "john@example.com",
            },
        )
    )

    participant = engine.update(evidence)

    assert participant.confidence < 0.50
    assert "metadata" in participant.last_reason.lower()
