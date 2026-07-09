from typing import List, Dict


class SilenceDetector:
    """
    Detects silence gaps in an audio timeline.
    A silence gap is a period with no active speech segments.
    """

    def detect(
        self,
        segments: List[Dict],
        total_duration: float,
        min_silence_seconds: float = 3.0,
    ) -> List[Dict]:
        """
        Find silence periods between speech segments.

        Args:
            segments: List of dicts with 'start' and 'end' (seconds).
            total_duration: Total audio duration in seconds.
            min_silence_seconds: Minimum gap to classify as silence.

        Returns:
            List of silence event dicts with 'start', 'end', 'duration'.
        """
        if not segments:
            return [{"start": 0.0, "end": total_duration, "duration": total_duration}]

        sorted_segs = sorted(segments, key=lambda s: s["start"])
        silences = []

        # Check silence before first segment
        if sorted_segs[0]["start"] > min_silence_seconds:
            silences.append({
                "start": 0.0,
                "end": sorted_segs[0]["start"],
                "duration": round(sorted_segs[0]["start"], 2),
            })

        # Check gaps between segments
        for i in range(len(sorted_segs) - 1):
            gap_start = sorted_segs[i]["end"]
            gap_end = sorted_segs[i + 1]["start"]
            duration = gap_end - gap_start
            if duration >= min_silence_seconds:
                silences.append({
                    "start": round(gap_start, 2),
                    "end": round(gap_end, 2),
                    "duration": round(duration, 2),
                })

        # Check silence after last segment
        trailing = total_duration - sorted_segs[-1]["end"]
        if trailing >= min_silence_seconds:
            silences.append({
                "start": round(sorted_segs[-1]["end"], 2),
                "end": round(total_duration, 2),
                "duration": round(trailing, 2),
            })

        return silences
