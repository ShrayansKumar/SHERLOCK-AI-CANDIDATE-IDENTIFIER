from ai.reasoning.evidence_collector import EvidenceCollector


class ReasoningService:
    """
    Thin service-layer wrapper around EvidenceCollector.
    Routes events through the AI evidence pipeline.
    """

    def __init__(self):
        self.collector = EvidenceCollector()

    def collect_evidence(self, event):
        """
        Collect evidence for a single event.
        Returns an Evidence dataclass or None if no evidence applies.
        """
        return self.collector.collect(event)
