from typing import Dict, List


class ReportGenerator:
    """
    Assembles the final Sherlock candidate evaluation report.
    Combines confidence timeline, evidence summary, and explanation
    logs into a structured report dict ready for API responses or export.
    """

    def generate(
        self,
        participant_id: str,
        final_confidence: float,
        confidence_timeline: list,
        evidence_logs: list,
        explanation_logs: list,
        candidate_name: str = None,
        meeting_id: str = None,
    ) -> Dict:
        """
        Build a complete evaluation report for a participant.

        Args:
            participant_id: Unique participant identifier.
            final_confidence: Final confidence score [0, 1].
            confidence_timeline: List of ConfidenceSnapshot ORM objects.
            evidence_logs: List of EvidenceLog ORM objects.
            explanation_logs: List of ExplanationLog ORM objects.
            candidate_name: Optional candidate display name.
            meeting_id: Optional meeting identifier.

        Returns:
            Structured report dict.
        """

        if final_confidence >= 0.75:
            verdict = "High confidence — likely the candidate"
        elif final_confidence >= 0.50:
            verdict = "Medium confidence — probably the candidate"
        elif final_confidence >= 0.25:
            verdict = "Low confidence — unlikely the candidate"
        else:
            verdict = "Very low confidence — probably not the candidate"

        evidence_breakdown = {}
        for log in evidence_logs:
            t = log.evidence_type
            if t not in evidence_breakdown:
                evidence_breakdown[t] = {"count": 0, "total_delta": 0.0}
            evidence_breakdown[t]["count"] += 1
            evidence_breakdown[t]["total_delta"] += log.confidence_delta

        return {
            "participant_id": participant_id,
            "candidate_name": candidate_name,
            "meeting_id": meeting_id,
            "final_confidence": round(final_confidence, 4),
            "verdict": verdict,
            "evidence_count": len(evidence_logs),
            "evidence_breakdown": {
                k: {
                    "count": v["count"],
                    "total_delta": round(v["total_delta"], 4),
                }
                for k, v in evidence_breakdown.items()
            },
            "timeline_points": len(confidence_timeline),
            "explanations": [
                {
                    "evidence_type": log.evidence_type,
                    "explanation": log.explanation,
                    "created_at": log.created_at.isoformat() if log.created_at else None,
                }
                for log in explanation_logs
            ],
        }
