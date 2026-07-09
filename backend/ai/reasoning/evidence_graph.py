from collections import defaultdict
from typing import Dict, List


class EvidenceGraph:
    """
    Adjacency-list graph linking participants to their evidence events.
    Enables traversal queries like 'all evidence for participant X'
    and 'all participants with evidence type Y'.
    """

    def __init__(self):
        # participant_id -> list of evidence dicts
        self._graph: Dict[str, List[dict]] = defaultdict(list)

    def add_edge(
        self,
        participant_id: str,
        evidence_type: str,
        confidence_delta: float,
        reason: str,
    ):
        """Add an evidence node linked to a participant."""
        self._graph[participant_id].append({
            "evidence_type": evidence_type,
            "confidence_delta": confidence_delta,
            "reason": reason,
        })

    def get_evidence(self, participant_id: str) -> List[dict]:
        """Return all evidence records for a participant."""
        return self._graph.get(participant_id, [])

    def get_participants_with_type(self, evidence_type: str) -> List[str]:
        """Return all participant IDs that have a specific evidence type."""
        return [
            pid
            for pid, edges in self._graph.items()
            if any(e["evidence_type"] == evidence_type for e in edges)
        ]

    def all_participants(self) -> List[str]:
        """Return all participant IDs in the graph."""
        return list(self._graph.keys())
