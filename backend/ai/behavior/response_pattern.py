from typing import List, Dict


class ResponsePatternAnalyzer:
    """
    Analyzes patterns in a participant's responses:
    - Average response length
    - Response latency (if timestamps available)
    - Keyword diversity
    """

    def analyze(self, transcript_segments: List[Dict]) -> Dict:
        """
        Args:
            transcript_segments: List of dicts with 'text' and
                                 optionally 'duration_seconds'.

        Returns:
            Pattern analysis dict.
        """
        if not transcript_segments:
            return {
                "avg_length_words": 0,
                "total_segments": 0,
                "longest_response_words": 0,
                "short_responses": 0,
            }

        lengths = [
            len(seg.get("text", "").split())
            for seg in transcript_segments
        ]

        short_threshold = 5

        return {
            "avg_length_words": round(sum(lengths) / len(lengths), 1),
            "total_segments": len(lengths),
            "longest_response_words": max(lengths),
            "short_responses": sum(1 for l in lengths if l < short_threshold),
        }
