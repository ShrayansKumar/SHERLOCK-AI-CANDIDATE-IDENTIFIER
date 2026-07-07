from ai.confidence.confidence_engine import ConfidenceEngine

from ai.reasoning.evidence import Evidence

from datetime import datetime


engine = ConfidenceEngine()

evidence = Evidence(

    participant_id="candidate_001",

    evidence_type="camera_off",

    confidence_delta=-0.08,

    reason="Camera turned off",

    timestamp=datetime.utcnow()

)

participant = engine.update(
    evidence
)

print(participant)

print(
    engine.history.get(
        "candidate_001"
    )
)