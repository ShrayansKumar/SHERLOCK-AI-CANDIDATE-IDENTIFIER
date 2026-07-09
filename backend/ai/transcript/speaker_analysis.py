from typing import List, Dict
from collections import defaultdict


class SpeakerAnalyzer:
    """
    Aggregates per-speaker statistics from transcript segments.
    """

    def analyze(self, segments: List[Dict]) -> Dict[str, Dict]:
        """
        Build per-speaker stats from a list of transcript segments.

        Each segment: {'speaker': str, 'text': str}

        Returns:
            Dict of speaker_id -> {
                "total_segments": int,
                "total_words": int,
                "avg_words_per_segment": float,
                "longest_segment_words": int,
            }
        """
        by_speaker: Dict[str, List[int]] = defaultdict(list)

        for seg in segments:
            speaker = seg.get("speaker", "unknown")
            word_count = len(seg.get("text", "").split())
            by_speaker[speaker].append(word_count)

        result = {}
        for speaker, word_counts in by_speaker.items():
            result[speaker] = {
                "total_segments": len(word_counts),
                "total_words": sum(word_counts),
                "avg_words_per_segment": round(
                    sum(word_counts) / len(word_counts), 1
                ),
                "longest_segment_words": max(word_counts),
            }

        return result
