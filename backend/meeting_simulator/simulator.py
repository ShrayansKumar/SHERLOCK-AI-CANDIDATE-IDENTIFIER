from events.event_bus import event_bus
from events.event_handlers import log_event
from events.event_types import EventType

from meeting_simulator.participant_generator import (
    ParticipantGenerator,
)

from meeting_simulator.event_generator import (
    EventGenerator,
)

from ai.reasoning.evidence_collector import (
    EvidenceCollector,
)

from ai.confidence.confidence_engine import (
    ConfidenceEngine,
)


collector = EvidenceCollector()
confidence_engine = ConfidenceEngine()

event_bus.subscribe(
    EventType.PARTICIPANT_JOINED,
    log_event
)

generator = ParticipantGenerator()
participants = generator.generate()

events = EventGenerator()

for participant in participants:

    event = events.participant_join(
        1,
        participant
    )

    event_bus.publish(event)
    evidence = collector.collect(event)
    if evidence:
        print()
        print("Evidence Generated")
        print(evidence)
        participant_confidence = confidence_engine.update(
            evidence
        )
        print()
        print("Updated Confidence")
        print(participant_confidence)
        print("-" * 70)