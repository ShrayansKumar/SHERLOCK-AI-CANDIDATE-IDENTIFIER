from ai.confidence.confidence_engine import ConfidenceEngine
from ai.reasoning.evidence import Evidence
from datetime import datetime


def test_fusion_engine_combines_evidence_into_score():
    engine = ConfidenceEngine()

    engine.update(
        Evidence(
            participant_id="candidate_001",
            evidence_type="camera_on",
            confidence_delta=0.05,
            reason="Camera turned on",
            timestamp=datetime.utcnow(),
        )
    )
    engine.update(
        Evidence(
            participant_id="candidate_001",
            evidence_type="metadata_match",
            confidence_delta=0.35,
            reason="Metadata match",
            timestamp=datetime.utcnow(),
        )
    )

    participant = engine.get_confidence("candidate_001")

    assert participant.confidence == 0.9
    assert participant.fused_score == 0.9
