"""
Eye Contact Analyzer — OpenCV + Dlib/MediaPipe heuristic
Estimates whether the candidate is looking at the camera.
Only computes eye contact when faces are explicitly detected in the frame.
"""
from typing import List, Dict, Optional
import numpy as np
from utils.logger import logger
from ai.vision.cascade_loader import get_cascade_path


class EyeContactAnalyzer:
    """
    Estimates gaze/eye contact across video frames where faces are detected.
    """

    def __init__(self):
        self._face_cascade = None
        self._eye_cascade = None

    def _get_cascades(self):
        import cv2
        if self._face_cascade is None:
            self._face_cascade = cv2.CascadeClassifier(
                get_cascade_path("haarcascade_frontalface_default.xml")
            )
        if self._eye_cascade is None:
            self._eye_cascade = cv2.CascadeClassifier(
                get_cascade_path("haarcascade_eye.xml")
            )
        return self._face_cascade, self._eye_cascade

    def _analyze_frame(self, frame: np.ndarray) -> Optional[Dict]:
        """Returns dict with looking_at_camera bool, or None if no face."""
        try:
            import cv2
            face_cas, eye_cas = self._get_cascades()
            if face_cas.empty() or eye_cas.empty():
                return None

            h, w = frame.shape[:2]
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = face_cas.detectMultiScale(gray, 1.1, 4, minSize=(30, 30))
            if len(faces) == 0:
                return None

            # Take the largest face
            fx, fy, fw, fh = max(faces, key=lambda r: r[2] * r[3])

            # Face-centred heuristic: face centre-x within middle 50% of frame
            face_cx = fx + fw / 2
            face_centred = (w * 0.22) <= face_cx <= (w * 0.78)

            # Eye detection inside face ROI (upper 65% of face crop)
            roi_gray = gray[fy: fy + int(fh * 0.65), fx: fx + fw]
            eyes = eye_cas.detectMultiScale(roi_gray, 1.1, 6, minSize=(12, 12))
            both_eyes = len(eyes) >= 2

            looking = face_centred and both_eyes

            gaze_score = 0.0
            if face_centred:
                gaze_score += 0.5
            if both_eyes:
                gaze_score += 0.5

            return {
                "looking_at_camera": looking,
                "gaze_score": round(gaze_score, 2),
                "eyes_detected": int(len(eyes)),
                "face_centred": face_centred,
            }
        except Exception as exc:
            logger.warning(f"EyeContactAnalyzer frame analysis error: {exc}")
            return None

    def analyze_frames(self, frames: List[np.ndarray]) -> Dict:
        """
        Aggregate eye-contact across sampled frames where faces are detected.
        Prevents false camera evasion when no face was found.
        """
        looking_frames = 0
        gaze_scores = []

        for frame in frames:
            result = self._analyze_frame(frame)
            if result is not None:
                if result["looking_at_camera"]:
                    looking_frames += 1
                gaze_scores.append(result["gaze_score"])

        analyzed = len(gaze_scores)

        if analyzed == 0:
            logger.info("EyeContactAnalyzer: No face detected in sampled frames; skipping gaze computation.")
            return {
                "frames_analyzed": 0,
                "looking_frames": 0,
                "eye_contact_ratio": 0.0,
                "avg_gaze_score": 0.0,
                "status": "no_face_detected",
            }

        ratio = round(looking_frames / analyzed, 3)
        avg_score = round(sum(gaze_scores) / analyzed, 3)

        logger.info(f"EyeContactAnalyzer stats: {looking_frames}/{analyzed} face frames looking at camera (ratio={ratio})")

        return {
            "frames_analyzed": analyzed,
            "looking_frames": looking_frames,
            "eye_contact_ratio": ratio,
            "avg_gaze_score": avg_score,
            "status": "analyzed",
        }
