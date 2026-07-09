from ai.confidence.confidence_engine import ConfidenceEngine
from ai.reasoning.evidence_collector import EvidenceCollector
from events.event import Event
from events.event_types import EventType


def test_transcript_with_candidate_speech_generates_positive_evidence():
    collector = EvidenceCollector()
    event = Event(
        type=EventType.TRANSCRIPT_RECEIVED,
        meeting_id=1,
        participant_id="candidate_001",
        payload={
            "transcript": "Hello, I am the candidate and I am speaking clearly.",
            "speaker": "candidate",
        },
    )

    evidence = collector.collect(event)

    assert evidence is not None
    assert evidence.evidence_type == "speech_analysis"
    assert evidence.confidence_delta > 0
    assert "speech" in evidence.reason.lower()


def test_confidence_increases_for_candidate_speech():
    engine = ConfidenceEngine()
    collector = EvidenceCollector()

    evidence = collector.collect(
        Event(
            type=EventType.TRANSCRIPT_RECEIVED,
            meeting_id=1,
            participant_id="candidate_001",
            payload={
                "transcript": "Hello, I am the candidate and I am speaking clearly.",
                "speaker": "candidate",
            },
        )
    )

    participant = engine.update(evidence)

    assert participant.confidence > 0.50
    assert "speech" in participant.last_reason.lower()
