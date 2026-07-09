from typing import List, Dict


class AnswerLengthAnalyzer:
    """
    Analyzes the length of candidate answers as a proxy for
    engagement and content depth.
    """

    SHORT_THRESHOLD_WORDS = 10
    LONG_THRESHOLD_WORDS = 50

    def analyze(self, text: str) -> Dict:
        """
        Classify an answer segment by length.

        Returns:
            {
                "word_count": int,
                "label": "short" | "medium" | "long",
                "confidence_delta": float,
            }
        """
        word_count = len(text.strip().split())

        if word_count < self.SHORT_THRESHOLD_WORDS:
            label = "short"
            delta = -0.05
        elif word_count >= self.LONG_THRESHOLD_WORDS:
            label = "long"
            delta = 0.10
        else:
            label = "medium"
            delta = 0.03

        return {
            "word_count": word_count,
            "label": label,
            "confidence_delta": delta,
        }

    def analyze_many(self, segments: List[str]) -> List[Dict]:
        return [self.analyze(s) for s in segments]
