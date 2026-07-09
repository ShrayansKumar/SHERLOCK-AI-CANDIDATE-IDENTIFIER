"""
Emotion Analyzer
Priority order (first available wins):
  1. DeepFace (most accurate, pip install deepface)
  2. FER — Facial Expression Recognition (pip install fer)
  3. OpenCV HSV skin-tone heuristic fallback (always available)

All three paths return the same structured dict so VideoService
doesn't need to know which backend ran.
"""
from typing import List, Dict, Optional
import numpy as np


_POSITIVE_EMOTIONS = {"happy", "surprised"}
_NEGATIVE_EMOTIONS = {"angry", "fearful", "sad", "disgusted"}


class EmotionDetector:
    """
    Detects dominant facial emotion per frame and aggregates results.
    """

    def _detect_frame_deepface(self, frame: np.ndarray) -> Optional[Dict]:
        try:
            from deepface import DeepFace
            result = DeepFace.analyze(
                img_path=frame,
                actions=["emotion"],
                enforce_detection=False,
                silent=True,
            )
            # DeepFace may return a list
            if isinstance(result, list):
                result = result[0]
            dominant = result.get("dominant_emotion", "neutral")
            scores = result.get("emotion", {})
            return {"dominant_emotion": dominant, "scores": scores, "backend": "deepface"}
        except Exception:
            return None

    def _detect_frame_fer(self, frame: np.ndarray) -> Optional[Dict]:
        try:
            import cv2
            from fer import FER
            detector = FER(mtcnn=False)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            detections = detector.detect_emotions(rgb)
            if not detections:
                return None
            top = detections[0]["emotions"]
            dominant = max(top, key=top.get)
            return {"dominant_emotion": dominant, "scores": top, "backend": "fer"}
        except Exception:
            return None

    def _detect_frame_heuristic(self, frame: np.ndarray) -> Optional[Dict]:
        """
        OpenCV heuristic: estimate 'neutral' by default.
        Uses brightness variance as a very rough proxy for expressiveness.
        """
        try:
            import cv2
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            std = float(gray.std())
            # High std → more facial movement → 'expressive'
            dominant = "happy" if std > 55 else "neutral"
            scores = {dominant: 1.0}
            return {"dominant_emotion": dominant, "scores": scores, "backend": "heuristic"}
        except Exception:
            return None

    def detect_frame(self, frame: np.ndarray) -> Optional[Dict]:
        """Detect emotion in a single BGR frame."""
        result = self._detect_frame_deepface(frame)
        if result:
            return result
        result = self._detect_frame_fer(frame)
        if result:
            return result
        return self._detect_frame_heuristic(frame)

    def analyze_frames(self, frames: List[np.ndarray]) -> Dict:
        """
        Aggregate emotion analysis across sampled frames.

        Returns:
            {
                "backend": str,
                "dominant_emotion": str,     # most frequent across frames
                "emotion_distribution": dict,
                "positive_ratio": float,
                "negative_ratio": float,
                "engagement_score": float,   # 0-1
            }
        """
        emotion_counts: Dict[str, int] = {}
        backends_used = set()

        for frame in frames:
            result = self.detect_frame(frame)
            if result:
                em = result.get("dominant_emotion", "neutral")
                emotion_counts[em] = emotion_counts.get(em, 0) + 1
                backends_used.add(result.get("backend", "unknown"))

        if not emotion_counts:
            return {
                "backend": "none",
                "dominant_emotion": "unknown",
                "emotion_distribution": {},
                "positive_ratio": 0.0,
                "negative_ratio": 0.0,
                "engagement_score": 0.0,
            }

        total = sum(emotion_counts.values())
        dominant = max(emotion_counts, key=emotion_counts.get)
        positive = sum(v for k, v in emotion_counts.items() if k in _POSITIVE_EMOTIONS)
        negative = sum(v for k, v in emotion_counts.items() if k in _NEGATIVE_EMOTIONS)

        # Engagement = positive / (positive + negative + 1) with neutral counted neutral
        engagement = round(positive / max(total, 1), 3)

        return {
            "backend": ", ".join(backends_used),
            "dominant_emotion": dominant,
            "emotion_distribution": {k: round(v / total, 3) for k, v in emotion_counts.items()},
            "positive_ratio": round(positive / total, 3),
            "negative_ratio": round(negative / total, 3),
            "engagement_score": engagement,
        }
