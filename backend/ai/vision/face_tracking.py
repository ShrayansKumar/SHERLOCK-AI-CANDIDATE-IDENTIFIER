"""
Camera Tracking
Tracks face position across video frames to detect:
  - Consistent camera presence
  - Camera evasion (frequent disappearances / deliberate look-away)
  - Face temporarily lost
  - No face detected (distinguished from evasion)
"""
from typing import List, Dict, Tuple, Optional
import numpy as np
from utils.logger import logger
from ai.vision.cascade_loader import get_cascade_path


class CameraTracker:
    """
    Analyses face trajectory across video frames and distinguishes between
    no face detected, temporary dropouts, and deliberate camera evasion.
    """

    def _get_cascade(self):
        import cv2
        return cv2.CascadeClassifier(
            get_cascade_path("haarcascade_frontalface_default.xml")
        )

    def _detect_face_centroid(
        self, frame: np.ndarray
    ) -> Optional[Tuple[float, float, int, int]]:
        try:
            import cv2
            cascade = self._get_cascade()
            if cascade.empty():
                return None
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = cascade.detectMultiScale(gray, 1.1, 4, minSize=(30, 30))
            if len(faces) == 0:
                eq_gray = cv2.equalizeHist(gray)
                faces = cascade.detectMultiScale(eq_gray, 1.08, 3, minSize=(30, 30))
            if len(faces) == 0:
                return None
            x, y, w, h = max(faces, key=lambda r: r[2] * r[3])
            return (x + w / 2, y + h / 2, w, h)
        except Exception:
            return None

    def analyze_frames(self, frames: List[np.ndarray]) -> Dict:
        """
        Track face across all frames and compute stability & evasion classification.
        """
        centroids: List[Tuple[float, float]] = []
        sizes: List[float] = []
        frames_with_face = 0
        frame_h, frame_w = frames[0].shape[:2] if frames else (480, 640)

        for frame in frames:
            result = self._detect_face_centroid(frame)
            if result:
                cx, cy, w, h = result
                centroids.append((cx, cy))
                sizes.append(w * h)
                frames_with_face += 1

        total = max(len(frames), 1)
        presence_ratio = round(frames_with_face / total, 3)

        if centroids:
            xs = [c[0] for c in centroids]
            ys = [c[1] for c in centroids]
            avg_cx = float(np.mean(xs))
            avg_cy = float(np.mean(ys))
            position_std = float(np.sqrt(np.std(xs)**2 + np.std(ys)**2))
            norm_std = position_std / max(frame_w, frame_h)

            size_arr = np.array(sizes, dtype=float)
            size_cv = float(np.std(size_arr) / max(np.mean(size_arr), 1))
        else:
            avg_cx, avg_cy = 0.0, 0.0
            norm_std = 0.0
            size_cv = 0.0

        # Distinguish tracking events:
        if frames_with_face == 0:
            tracking_status = "no_face_detected"
            camera_evasion = False
        elif presence_ratio >= 0.70:
            tracking_status = "consistent_presence"
            camera_evasion = False
        elif presence_ratio >= 0.35:
            tracking_status = "face_temporarily_lost"
            camera_evasion = False
        else:
            tracking_status = "camera_evasion"
            camera_evasion = True

        position_stable = norm_std < 0.15

        logger.info(
            f"CameraTracker stats: {frames_with_face}/{total} frames (ratio={presence_ratio}), "
            f"status={tracking_status}, evasion={camera_evasion}"
        )

        return {
            "frames_tracked": frames_with_face,
            "presence_ratio": presence_ratio,
            "tracking_status": tracking_status,
            "avg_position": [round(avg_cx, 1), round(avg_cy, 1)],
            "position_std": round(norm_std, 4),
            "size_consistency": round(1.0 - min(size_cv, 1.0), 3),
            "camera_evasion_detected": camera_evasion,
            "position_stable": position_stable,
        }
