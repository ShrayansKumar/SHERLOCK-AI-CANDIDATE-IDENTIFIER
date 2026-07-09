"""
Multiple Face Detection
Wraps FaceDetector to specifically flag frames where more than one face
appears — a strong signal that a proxy may be assisting the candidate.
"""
from typing import List, Dict
import numpy as np

from ai.vision.face_detection import FaceDetector


class MultipleFaceDetector:
    """
    Detects and flags when multiple faces appear across video frames.
    Multiple faces → possible proxy / person assisting the candidate.
    """

    def __init__(self):
        self._detector = FaceDetector()

    def analyze_frames(self, frames: List[np.ndarray]) -> Dict:
        """
        Scan all frames for multi-face incidents.

        Returns:
            {
                "frames_checked": int,
                "multi_face_frames": int,
                "multi_face_ratio": float,       # 0-1
                "max_faces_in_single_frame": int,
                "single_person_consistent": bool, # True if always ≤1 face
            }
        """
        multi_face_frames = 0
        max_faces = 0

        for frame in frames:
            detections = self._detector.detect_in_frame(frame)
            count = len(detections)
            max_faces = max(max_faces, count)
            if count > 1:
                multi_face_frames += 1

        total = max(len(frames), 1)
        ratio = multi_face_frames / total

        return {
            "frames_checked": len(frames),
            "multi_face_frames": multi_face_frames,
            "multi_face_ratio": round(ratio, 3),
            "max_faces_in_single_frame": max_faces,
            "single_person_consistent": max_faces <= 1,
        }
