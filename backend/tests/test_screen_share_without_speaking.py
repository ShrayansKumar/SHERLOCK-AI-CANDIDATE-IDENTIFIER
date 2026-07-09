from ai.confidence.confidence_engine import ConfidenceEngine
from ai.reasoning.evidence_collector import EvidenceCollector
from events.event import Event
from events.event_types import EventType


def test_screen_share_without_speaking_generates_negative_evidence():
    collector = EvidenceCollector()
    event = Event(
        type=EventType.SCREEN_SHARE_STARTED,
        meeting_id=1,
        participant_id="candidate_001",
        payload={"role": "candidate", "shared_screen": True},
    )

    evidence = collector.collect(event)

    assert evidence is not None
    assert evidence.evidence_type == "screen_share_without_speaking"
    assert evidence.confidence_delta < 0
    assert "screen" in evidence.reason.lower()


def test_confidence_decreases_for_screen_share_without_speaking():
    engine = ConfidenceEngine()
    collector = EvidenceCollector()

    evidence = collector.collect(
        Event(
            type=EventType.SCREEN_SHARE_STARTED,
            meeting_id=1,
            participant_id="candidate_001",
            payload={"role": "candidate", "shared_screen": True},
        )
    )

    participant = engine.update(evidence)

    assert participant.confidence < 0.50
    assert "screen" in participant.last_reason.lower()
