from typing import List, Dict


class InterruptionDetector:
    """
    Detects overlapping speech (interruptions) from diarization segments.
    An interruption occurs when two speakers' segments overlap in time.
    """

    def detect(self, segments: List[Dict]) -> List[Dict]:
        """
        Find interruptions in a list of diarized speech segments.

        Each segment dict should have:
            - 'speaker': str
            - 'start': float (seconds)
            - 'end': float (seconds)

        Returns:
            List of interruption events with 'interrupter' and 'interrupted'.
        """
        interruptions = []
        sorted_segs = sorted(segments, key=lambda s: s["start"])

        for i in range(len(sorted_segs) - 1):
            current = sorted_segs[i]
            nxt = sorted_segs[i + 1]

            if (
                current["speaker"] != nxt["speaker"]
                and nxt["start"] < current["end"]
            ):
                interruptions.append({
                    "interrupter": nxt["speaker"],
                    "interrupted": current["speaker"],
                    "overlap_seconds": round(current["end"] - nxt["start"], 2),
                    "at_second": nxt["start"],
                })

        return interruptions
