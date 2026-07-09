from ai.confidence.confidence_engine import ConfidenceEngine
from ai.reasoning.evidence_collector import EvidenceCollector
from events.event import Event
from events.event_types import EventType
from meeting_simulator.event_generator import EventGenerator


def test_disconnect_event_generates_negative_evidence():
    collector = EvidenceCollector()
    event = Event(
        type=EventType.PARTICIPANT_LEFT,
        meeting_id=1,
        participant_id="candidate_001",
        payload={"reason": "disconnect"},
    )

    evidence = collector.collect(event)

    assert evidence is not None
    assert evidence.evidence_type == "disconnect"
    assert evidence.confidence_delta < 0
    assert "disconnect" in evidence.reason.lower()


def test_reconnect_event_generates_negative_evidence():
    collector = EvidenceCollector()
    event = Event(
        type=EventType.RECONNECTED,
        meeting_id=1,
        participant_id="candidate_001",
    )

    evidence = collector.collect(event)

    assert evidence is not None
    assert evidence.evidence_type == "reconnect"
    assert evidence.confidence_delta < 0
    assert "reconnect" in evidence.reason.lower()


def test_event_generator_emits_disconnect_and_reconnect_events():
    generator = EventGenerator()

    class Participant:
        participant_id = "candidate_001"
        role = type("Role", (), {"value": "candidate"})()
        display_name = "John Doe"

    participant = Participant()
    disconnect_event = generator.disconnect(1, participant)
    reconnect_event = generator.reconnect(1, participant)

    assert disconnect_event.type == EventType.PARTICIPANT_LEFT
    assert reconnect_event.type == EventType.RECONNECTED


def test_confidence_drops_after_disconnect_and_reconnect():
    engine = ConfidenceEngine()
    collector = EvidenceCollector()

    disconnect_evidence = collector.collect(
        Event(
            type=EventType.PARTICIPANT_LEFT,
            meeting_id=1,
            participant_id="candidate_001",
            payload={"reason": "disconnect"},
        )
    )
    reconnect_evidence = collector.collect(
        Event(
            type=EventType.RECONNECTED,
            meeting_id=1,
            participant_id="candidate_001",
        )
    )

    disconnect_participant = engine.update(disconnect_evidence)
    reconnect_participant = engine.update(reconnect_evidence)

    assert disconnect_participant.confidence < 0.50
    assert reconnect_participant.confidence <= disconnect_participant.confidence
