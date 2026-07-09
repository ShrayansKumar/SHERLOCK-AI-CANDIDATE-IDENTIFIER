from ai.confidence.confidence_engine import ConfidenceEngine
from ai.reasoning.evidence_collector import EvidenceCollector
from events.event import Event
from events.event_types import EventType


def test_metadata_matching_generates_positive_evidence():
    collector = EvidenceCollector()

    event = Event(
        type=EventType.PARTICIPANT_JOINED,
        meeting_id=1,
        participant_id="candidate_001",
        payload={
            "display_name": "John Doe",
            "email": "john@example.com",
            "meeting_metadata": {
                "candidate_name": "John Doe",
                "candidate_email": "john@example.com",
            },
        },
    )

    evidence = collector.collect(event)

    assert evidence is not None
    assert evidence.evidence_type == "metadata_match"
    assert evidence.confidence_delta > 0
    assert "metadata" in evidence.reason.lower()

    engine = ConfidenceEngine()
    participant = engine.update(evidence)

    assert participant.confidence > 0.50
    assert participant.last_reason is not None
    assert "metadata" in participant.last_reason.lower()


def test_missing_metadata_is_handled_gracefully():
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

    # Missing metadata should generate negative evidence
    # instead of failing silently.
    assert evidence is not None
    assert evidence.evidence_type == "missing_metadata"
    assert evidence.confidence_delta < 0
    assert "metadata" in evidence.reason.lower()

    engine = ConfidenceEngine()
    participant = engine.update(evidence)

    # Confidence should decrease below the default (0.50)
    assert participant.confidence < 0.50
    assert participant.last_reason is not None
    assert "metadata" in participant.last_reason.lower()