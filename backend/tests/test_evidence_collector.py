from ai.reasoning.evidence_collector import EvidenceCollector
from events.event import Event
from events.event_types import EventType

collector = EvidenceCollector()

event = Event(
    type=EventType.CAMERA_OFF,
    meeting_id=1,
    participant_id="candidate_001"
)

evidence = collector.collect(event)

print(evidence)