from collections import defaultdict


class ConfidenceHistory:

    def __init__(self):

        self.history = defaultdict(list)

    def add(
        self,
        participant_id,
        confidence
    ):

        self.history[participant_id].append(confidence)

    def get(
        self,
        participant_id
    ):

        return self.history.get(
            participant_id,
            []
        )