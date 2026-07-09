from ai.confidence.confidence_engine import ConfidenceEngine
from ai.reasoning.evidence_collector import EvidenceCollector
from events.event import Event
from events.event_types import EventType


def test_silent_observer_evidence_is_generated_for_observer():
    collector = EvidenceCollector()
    event = Event(
        type=EventType.PARTICIPANT_JOINED,
        meeting_id=1,
        participant_id="observer_001",
        payload={
            "display_name": "HR Observer",
            "role": "observer",
            "silent_observer": True,
        },
    )

    evidence = collector.collect(event)

    assert evidence is not None
    assert evidence.evidence_type == "silent_observer"
    assert evidence.confidence_delta == 0.0
    assert "silent" in evidence.reason.lower()


def test_silent_observer_does_not_change_confidence():
    engine = ConfidenceEngine()
    collector = EvidenceCollector()

    evidence = collector.collect(
        Event(
            type=EventType.PARTICIPANT_JOINED,
            meeting_id=1,
            participant_id="observer_001",
            payload={
                "display_name": "HR Observer",
                "role": "observer",
                "silent_observer": True,
            },
        )
    )

    participant = engine.update(evidence)

    assert participant.confidence == 0.50
    assert participant.last_reason == "Silent observer"
