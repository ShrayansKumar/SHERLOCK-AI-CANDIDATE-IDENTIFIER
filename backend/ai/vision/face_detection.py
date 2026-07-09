"""
Face Detection — OpenCV Haar Cascade
Uses haarcascade_frontalface_default.xml with histogram equalization
and multi-pass detection for robust face localization.
"""
from typing import List, Dict, Optional
import numpy as np
from utils.logger import logger
from ai.vision.cascade_loader import get_cascade_path


class FaceDetector:
    """Detects faces per frame using OpenCV Haar Cascades with robust fallbacks."""

    def __init__(self):
        self._cascade_default = None
        self._cascade_alt2 = None

    def _get_cascades(self):
        import cv2
        if self._cascade_default is None:
            default_path = get_cascade_path("haarcascade_frontalface_default.xml")
            self._cascade_default = cv2.CascadeClassifier(default_path)
            if self._cascade_default.empty():
                logger.error(f"Failed to load Haar Cascade from {default_path}")
            else:
                logger.debug(f"Successfully loaded haarcascade_frontalface_default.xml from {default_path}")

        if self._cascade_alt2 is None:
            alt2_path = get_cascade_path("haarcascade_frontalface_alt2.xml")
            self._cascade_alt2 = cv2.CascadeClassifier(alt2_path)
        return self._cascade_default, self._cascade_alt2

    def detect_in_frame(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect all faces in a BGR numpy frame using multi-pass detection
        (raw gray -> equalized histogram -> alt2 cascade fallback).
        """
        try:
            import cv2
            default_cascade, alt2_cascade = self._get_cascades()
            if default_cascade is None or default_cascade.empty():
                return []

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Pass 1: Standard detection
            faces = default_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=4,
                minSize=(25, 25),
            )

            # Pass 2: Histogram Equalization if pass 1 found nothing
            if len(faces) == 0:
                eq_gray = cv2.equalizeHist(gray)
                faces = default_cascade.detectMultiScale(
                    eq_gray,
                    scaleFactor=1.08,
                    minNeighbors=3,
                    minSize=(25, 25),
                )

            # Pass 3: Alt2 cascade fallback
            if len(faces) == 0 and alt2_cascade and not alt2_cascade.empty():
                faces = alt2_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=3,
                    minSize=(25, 25),
                )

            if len(faces) == 0:
                return []

            return [
                {"x": int(x), "y": int(y), "width": int(w), "height": int(h)}
                for x, y, w, h in faces
            ]
        except Exception as exc:
            logger.warning(f"FaceDetector detect_in_frame error: {exc}")
            return []

    def analyze_frames(self, frames: List[np.ndarray]) -> Dict:
        """
        Run face detection across multiple sampled frames and log statistics.
        """
        frames_with_face = 0
        frames_without_face = 0
        max_faces = 0
        total_faces = 0

        for frame in frames:
            detections = self.detect_in_frame(frame)
            count = len(detections)
            total_faces += count
            if count > 0:
                frames_with_face += 1
                max_faces = max(max_faces, count)
            else:
                frames_without_face += 1

        total = max(len(frames), 1)
        ratio = round(frames_with_face / total, 3)

        logger.info(
            f"FaceDetector stats: {frames_with_face}/{len(frames)} frames with face "
            f"(presence_ratio={ratio}, max_faces={max_faces}, total_faces={total_faces})"
        )

        return {
            "frames_with_face": frames_with_face,
            "frames_without_face": frames_without_face,
            "face_detected_ratio": ratio,
            "max_faces_in_frame": max_faces,
            "avg_faces_per_frame": round(total_faces / total, 2),
        }
