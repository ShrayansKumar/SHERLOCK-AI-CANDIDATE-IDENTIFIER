from typing import List, Dict


class SpeechDurationTracker:
    """
    Tracks total speaking duration per speaker from diarization segments.
    """

    def compute(self, segments: List[Dict]) -> Dict[str, float]:
        """
        Compute total speaking duration per speaker.

        Args:
            segments: List of dicts with 'speaker', 'start', 'end'.

        Returns:
            Dict mapping speaker_id -> total_seconds_spoken.
        """
        durations: Dict[str, float] = {}

        for seg in segments:
            speaker = seg.get("speaker", "unknown")
            duration = seg.get("end", 0.0) - seg.get("start", 0.0)
            durations[speaker] = durations.get(speaker, 0.0) + duration

        return {
            speaker: round(duration, 2)
            for speaker, duration in durations.items()
        }

    def speaking_ratio(
        self,
        durations: Dict[str, float],
        total_duration: float,
    ) -> Dict[str, float]:
        """
        Compute each speaker's fraction of total meeting time.
        """
        if total_duration == 0:
            return {}

        return {
            speaker: round(duration / total_duration, 4)
            for speaker, duration in durations.items()
        }
