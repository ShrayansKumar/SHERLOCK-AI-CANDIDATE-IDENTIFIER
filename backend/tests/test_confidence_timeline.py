from datetime import datetime

from ai.confidence.confidence_engine import ConfidenceEngine
from ai.reasoning.evidence import Evidence


def test_confidence_history_tracks_timeline_entries():
    engine = ConfidenceEngine()

    first = Evidence(
        participant_id="candidate_001",
        evidence_type="camera_on",
        confidence_delta=0.05,
        reason="Camera turned on",
        timestamp=datetime.utcnow(),
    )
    second = Evidence(
        participant_id="candidate_001",
        evidence_type="camera_off",
        confidence_delta=-0.08,
        reason="Camera turned off",
        timestamp=datetime.utcnow(),
    )

    engine.update(first)
    engine.update(second)

    timeline = engine.history.get_timeline("candidate_001")

    assert len(timeline) == 2
    assert round(timeline[0]["confidence"], 2) == 0.55
    assert round(timeline[1]["confidence"], 2) == 0.47
    assert timeline[1]["reason"] == "Camera turned off"
    assert timeline[1]["evidence_type"] == "camera_off"


def test_confidence_history_returns_empty_list_for_unknown_participant():
    engine = ConfidenceEngine()

    assert engine.history.get_timeline("unknown") == []
