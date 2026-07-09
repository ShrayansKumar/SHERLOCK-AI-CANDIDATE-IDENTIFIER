from typing import List, Dict


class RoleClassifier:
    """
    Classifies participant roles (candidate vs. interviewer)
    from transcript speech patterns.
    """

    _INTERVIEWER_PHRASES = [
        "tell me about", "can you describe", "how would you",
        "what is your experience", "why did you", "walk me through",
        "next question", "let's move on", "great, thank you",
        "we'll be in touch", "do you have any questions for us",
    ]

    _CANDIDATE_PHRASES = [
        "in my experience", "i worked on", "i implemented",
        "i designed", "we built", "my role was", "i was responsible",
        "i used", "i learned", "i helped", "at my previous company",
    ]

    def classify_segment(self, text: str) -> str:
        """
        Classify a single transcript segment as 'interviewer',
        'candidate', or 'unknown'.
        """
        lower = text.lower()
        interviewer_score = sum(
            1 for p in self._INTERVIEWER_PHRASES if p in lower
        )
        candidate_score = sum(
            1 for p in self._CANDIDATE_PHRASES if p in lower
        )

        if interviewer_score > candidate_score:
            return "interviewer"
        elif candidate_score > interviewer_score:
            return "candidate"
        return "unknown"

    def classify_speaker(
        self,
        speaker_segments: List[Dict],
    ) -> str:
        """
        Classify a speaker's overall role from their segments.
        """
        counts = {"interviewer": 0, "candidate": 0, "unknown": 0}
        for seg in speaker_segments:
            role = self.classify_segment(seg.get("text", ""))
            counts[role] += 1

        if counts["candidate"] > counts["interviewer"]:
            return "candidate"
        elif counts["interviewer"] > counts["candidate"]:
            return "interviewer"
        return "unknown"
