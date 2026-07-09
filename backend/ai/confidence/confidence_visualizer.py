from typing import List, Dict


class ConfidenceVisualizer:
    """
    Formats confidence timeline data for API and frontend consumption.
    Converts raw ConfidenceSnapshot ORM objects into clean dicts
    suitable for charting (e.g., time-series line charts).
    """

    def format_timeline(self, snapshots: list) -> List[Dict]:
        """
        Convert a list of ConfidenceSnapshot ORM objects to a
        list of dicts ordered chronologically.
        """
        return [
            {
                "timestamp": s.created_at.isoformat() if s.created_at else None,
                "confidence": round(s.confidence, 4),
                "evidence_type": s.evidence_type,
                "reason": s.reason,
            }
            for s in snapshots
        ]

    def format_summary(self, snapshots: list) -> Dict:
        """
        Compute summary statistics from a confidence timeline.
        Returns min, max, avg, and final confidence value.
        """
        if not snapshots:
            return {
                "count": 0,
                "min": None,
                "max": None,
                "avg": None,
                "final": None,
            }

        scores = [s.confidence for s in snapshots]

        return {
            "count": len(scores),
            "min": round(min(scores), 4),
            "max": round(max(scores), 4),
            "avg": round(sum(scores) / len(scores), 4),
            "final": round(scores[-1], 4),
        }
