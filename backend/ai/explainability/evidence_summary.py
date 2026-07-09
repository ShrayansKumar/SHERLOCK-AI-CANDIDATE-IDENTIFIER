from collections import defaultdict
from typing import List, Dict


class EvidenceSummary:
    """
    Groups and aggregates evidence events by type.
    Provides counts, total delta, and per-type breakdown
    for a participant's full evidence history.
    """

    def summarize(self, evidence_logs: list) -> Dict:
        """
        Build a summary dict from a list of EvidenceLog ORM objects.

        Returns:
            {
                "total_events": int,
                "net_delta": float,
                "by_type": {
                    "camera_on": {"count": 1, "total_delta": 0.05},
                    ...
                }
            }
        """
        by_type: Dict[str, Dict] = defaultdict(lambda: {"count": 0, "total_delta": 0.0})
        net_delta = 0.0

        for log in evidence_logs:
            by_type[log.evidence_type]["count"] += 1
            by_type[log.evidence_type]["total_delta"] += log.confidence_delta
            net_delta += log.confidence_delta

        return {
            "total_events": len(evidence_logs),
            "net_delta": round(net_delta, 4),
            "by_type": {
                k: {
                    "count": v["count"],
                    "total_delta": round(v["total_delta"], 4),
                }
                for k, v in by_type.items()
            },
        }
