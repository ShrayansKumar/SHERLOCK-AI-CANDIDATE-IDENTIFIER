"""
Gesture Recognition
Uses MediaPipe Hands when available; falls back to an OpenCV
skin-detection heuristic (hand-blob presence in lower frame region).

Both paths return the same structured result dict.
"""
from typing import List, Dict, Optional
import numpy as np


class GestureAnalyzer:
    """
    Detects hand gesture activity across video frames.
    Active hand gestures correlate with candidate engagement.
    """

    def _detect_frame_mediapipe(self, frame: np.ndarray) -> Optional[Dict]:
        """MediaPipe Hands detection."""
        try:
            import cv2
            import mediapipe as mp
            mp_hands = mp.solutions.hands
            with mp_hands.Hands(
                static_image_mode=True,
                max_num_hands=2,
                min_detection_confidence=0.5,
            ) as hands:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb)
                if results.multi_hand_landmarks:
                    count = len(results.multi_hand_landmarks)
                    return {
                        "hands_detected": count,
                        "gesture_active": True,
                        "backend": "mediapipe",
                    }
                return {
                    "hands_detected": 0,
                    "gesture_active": False,
                    "backend": "mediapipe",
                }
        except Exception:
            return None

    def _detect_frame_heuristic(self, frame: np.ndarray) -> Optional[Dict]:
        """
        OpenCV skin-blob heuristic.
        Detects skin-coloured blobs in the lower 40% of the frame
        (where hands typically appear in a webcam interview).
        """
        try:
            import cv2
            h, w = frame.shape[:2]
            lower_region = frame[int(h * 0.6):, :]  # bottom 40%

            # Convert to HSV; skin tone range
            hsv = cv2.cvtColor(lower_region, cv2.COLOR_BGR2HSV)
            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)
            mask = cv2.inRange(hsv, lower_skin, upper_skin)

            skin_pixels = int(np.count_nonzero(mask))
            total_pixels = lower_region.shape[0] * lower_region.shape[1]
            skin_ratio = skin_pixels / max(total_pixels, 1)

            gesture_active = skin_ratio > 0.05  # >5% skin in lower region
            return {
                "hands_detected": 1 if gesture_active else 0,
                "gesture_active": gesture_active,
                "skin_ratio": round(skin_ratio, 3),
                "backend": "heuristic",
            }
        except Exception:
            return None

    def detect_frame(self, frame: np.ndarray) -> Optional[Dict]:
        result = self._detect_frame_mediapipe(frame)
        if result:
            return result
        return self._detect_frame_heuristic(frame)

    def analyze_frames(self, frames: List[np.ndarray]) -> Dict:
        """
        Aggregate gesture detection across sampled frames.

        Returns:
            {
                "backend": str,
                "frames_with_gesture": int,
                "gesture_ratio": float,
                "gesture_active": bool,
            }
        """
        frames_with_gesture = 0
        backends_used = set()

        for frame in frames:
            result = self.detect_frame(frame)
            if result:
                if result.get("gesture_active"):
                    frames_with_gesture += 1
                backends_used.add(result.get("backend", "unknown"))

        total = max(len(frames), 1)
        ratio = frames_with_gesture / total

        return {
            "backend": ", ".join(backends_used) if backends_used else "none",
            "frames_with_gesture": frames_with_gesture,
            "gesture_ratio": round(ratio, 3),
            "gesture_active": ratio > 0.15,
        }
