from typing import List, Tuple


class QADetector:
    """
    Detects question-answer pairs in a transcript.
    Classifies segments as questions or answers based on
    punctuation and phrasing heuristics.
    """

    _QUESTION_STARTERS = [
        "what", "how", "why", "when", "where", "who",
        "can you", "could you", "tell me", "describe",
        "explain", "walk me through", "have you", "do you",
    ]

    def is_question(self, text: str) -> bool:
        """Return True if the text segment is likely a question."""
        text = text.strip()
        if text.endswith("?"):
            return True
        lower = text.lower()
        return any(lower.startswith(s) for s in self._QUESTION_STARTERS)

    def extract_pairs(
        self,
        segments: List[dict],
    ) -> List[Tuple[dict, dict]]:
        """
        Extract Q&A pairs from diarized transcript segments.

        Args:
            segments: List of {'speaker': str, 'text': str} dicts.

        Returns:
            List of (question_segment, answer_segment) tuples.
        """
        pairs = []
        i = 0
        while i < len(segments) - 1:
            current = segments[i]
            nxt = segments[i + 1]
            if (
                self.is_question(current["text"])
                and current["speaker"] != nxt["speaker"]
            ):
                pairs.append((current, nxt))
                i += 2
            else:
                i += 1
        return pairs
