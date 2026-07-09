from ai.confidence.confidence_engine import ConfidenceEngine
from ai.reasoning.evidence_collector import EvidenceCollector
from events.event import Event
from events.event_types import EventType
from meeting_simulator.event_generator import EventGenerator


def test_network_lag_event_generates_negative_evidence():
    collector = EvidenceCollector()
    event = Event(
        type=EventType.NETWORK_LAG,
        meeting_id=1,
        participant_id="candidate_001",
        payload={"duration_seconds": 3},
    )

    evidence = collector.collect(event)

    assert evidence is not None
    assert evidence.evidence_type == "network_lag"
    assert evidence.confidence_delta < 0
    assert "lag" in evidence.reason.lower()


def test_event_generator_emits_network_lag_event():
    generator = EventGenerator()

    class Participant:
        participant_id = "candidate_001"
        role = type("Role", (), {"value": "candidate"})()
        display_name = "John Doe"

    participant = Participant()
    event = generator.network_lag(1, participant, 3)

    assert event.type == EventType.NETWORK_LAG
    assert event.participant_id == "candidate_001"
    assert event.payload["duration_seconds"] == 3


def test_confidence_decreases_for_network_lag():
    engine = ConfidenceEngine()
    collector = EvidenceCollector()

    evidence = collector.collect(
        Event(
            type=EventType.NETWORK_LAG,
            meeting_id=1,
            participant_id="candidate_001",
            payload={"duration_seconds": 3},
        )
    )

    participant = engine.update(evidence)

    assert participant.confidence < 0.50
    assert "lag" in participant.last_reason.lower()
