from collections import defaultdict


class ConfidenceHistory:

    def __init__(self):

        self.history = defaultdict(list)

    def add(
        self,
        participant_id,
        confidence,
        reason=None,
        evidence_type=None,
        timestamp=None,
    ):

        self.history[participant_id].append({
            "confidence": confidence,
            "reason": reason,
            "evidence_type": evidence_type,
            "timestamp": timestamp,
        })

    def get(
        self,
        participant_id
    ):

        return self.history.get(
            participant_id,
            []
        )

    def get_timeline(
        self,
        participant_id
    ):

        return self.history.get(
            participant_id,
            []
        )