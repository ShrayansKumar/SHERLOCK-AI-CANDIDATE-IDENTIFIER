"""
Video Processing Service
------------------------
Full AI pipeline for a candidate interview video:

  1.  Frame sampling (OpenCV)
  2.  Face Detection          → ai.vision.face_detection
  3.  Multiple Face Detection → ai.vision.multiple_faces
  4.  Eye Contact Analysis    → ai.vision.eye_contact
  5.  Emotion Detection       → ai.vision.emotion       (DeepFace/FER/heuristic)
  6.  Gesture Recognition     → ai.vision.gesture       (MediaPipe/heuristic)
  7.  Background OCR          → ai.vision.background_ocr (pytesseract/heuristic)
  8.  Face Recognition        → ai.vision.face_recognition (dlib/LBPH/bbox)
  9.  Camera Tracking         → ai.vision.face_tracking
  10. Screen-share Detection  → ai.vision.screen_share
  11. Evidence Generation     → ai.reasoning.evidence_collector
  12. Fusion Service          → Confidence update + WebSocket broadcast
"""
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from models.video import VideoUpload
from repositories.video_repository import VideoRepository
from ai.reasoning.evidence_collector import Evidence
from ai.reasoning.evidence_weights import WEIGHTS
from ai.vision.face_detection import FaceDetector
from ai.vision.multiple_faces import MultipleFaceDetector
from ai.vision.eye_contact import EyeContactAnalyzer
from ai.vision.emotion import EmotionDetector
from ai.vision.gesture import GestureAnalyzer
from ai.vision.background_ocr import BackgroundOCR
from ai.vision.face_recognition import FaceRecognizer
from ai.vision.face_tracking import CameraTracker
from services.fusion_service import fusion_service
from utils.logger import logger

# ── Additional evidence weight keys (merged with existing WEIGHTS) ────────────
_EXTRA_WEIGHTS = {
    "multiple_faces_detected":     -0.35,
    "eye_contact_maintained":       0.08,
    "eye_contact_avoided":         -0.06,
    "positive_emotion":             0.05,
    "negative_emotion":            -0.04,
    "gesture_active":               0.04,
    "suspicious_text_detected":    -0.15,
    "identity_inconsistency":      -0.30,
    "camera_evasion":              -0.10,
    "camera_position_stable":       0.03,
}


def _w(key: str, fallback: float = 0.0) -> float:
    return WEIGHTS.get(key, _EXTRA_WEIGHTS.get(key, fallback))


class VideoService:
    """
    Orchestrates the complete video AI pipeline:
      Video Upload → Frame Sampling → 8 Vision Analyzers →
      Evidence Generation → Fusion Service →
      Confidence Update + WebSocket Broadcast
    """

    def __init__(self):
        self.video_repo          = VideoRepository()
        self.face_detector       = FaceDetector()
        self.multi_face_detector = MultipleFaceDetector()
        self.eye_contact         = EyeContactAnalyzer()
        self.emotion_detector    = EmotionDetector()
        self.gesture_analyzer    = GestureAnalyzer()
        self.background_ocr      = BackgroundOCR()
        self.face_recognizer     = FaceRecognizer()
        self.camera_tracker      = CameraTracker()

    async def process_video_upload(
        self,
        db: Session,
        meeting_id: Optional[str],
        participant_id: str,
        file_path: str,
        file_name: str,
        file_format: str,
    ) -> Dict:
        """
        Full pipeline for one uploaded video file.
        """
        # 1. Persist upload record
        upload = VideoUpload(
            participant_id=participant_id,
            meeting_id=meeting_id,
            file_path=file_path,
            file_name=file_name,
            file_format=file_format,
            duration=0.0,
            frame_count=0,
        )
        upload = self.video_repo.create(db, upload)

        evidence_list: List[Evidence] = []
        analysis: Dict = {}

        try:
            import cv2
            frames, meta = self._sample_frames(file_path)

            analysis["duration"]        = meta["duration"]
            analysis["total_frames"]    = meta["total_frames"]
            analysis["sampled_frames"]  = len(frames)

            upload.duration    = meta["duration"]
            upload.frame_count = len(frames)

            if frames:
                analysis, evidence_list = self._run_all_analyzers(
                    frames, participant_id, analysis
                )

            upload.analysis_summary = str(analysis)
            db.commit()
            db.refresh(upload)

        except ImportError:
            logger.warning(
                "OpenCV not installed — install opencv-python to enable video AI."
            )
            evidence_list.append(Evidence(
                participant_id=participant_id,
                evidence_type="camera_on",
                confidence_delta=_w("camera_on", 0.05),
                reason="Video uploaded (OpenCV not installed — frame analysis unavailable)",
                timestamp=datetime.utcnow(),
            ))
            analysis = {"note": "Install opencv-python for full video AI pipeline."}

        except Exception as exc:
            logger.error(f"VideoService pipeline error: {exc}", exc_info=True)
            evidence_list.append(Evidence(
                participant_id=participant_id,
                evidence_type="camera_on",
                confidence_delta=_w("camera_on", 0.05),
                reason=f"Video uploaded (analysis error: {exc})",
                timestamp=datetime.utcnow(),
            ))

        # 2. Pass all evidence through Fusion Service
        latest_participant = None
        for ev in evidence_list:
            try:
                res = await fusion_service.process_evidence(ev, meeting_id=meeting_id)
                if res is not None:
                    latest_participant = res
            except Exception as e:
                logger.error(f"FusionService evidence error: {e}")

        return {
            "upload_id":         upload.id,
            "participant_id":    upload.participant_id,
            "meeting_id":        upload.meeting_id,
            "file_name":         upload.file_name,
            "file_format":       upload.file_format,
            "duration":          upload.duration,
            "frame_count":       upload.frame_count,
            "analysis":          analysis,
            "evidence_generated": [e.evidence_type for e in evidence_list],
            "confidence":        latest_participant.confidence if latest_participant else None,
            "created_at":        upload.created_at,
        }

    # ── Frame Sampling ─────────────────────────────────────────────────────

    def _sample_frames(self, file_path: str, max_frames: int = 60):
        """
        Sample up to max_frames evenly-spaced frames from the video or load image snapshot.
        Returns (list_of_bgr_frames, meta_dict).
        """
        import cv2
        ext = file_path.rsplit(".", 1)[-1].lower() if "." in file_path else ""
        if ext in {"jpg", "jpeg", "png"}:
            img = cv2.imread(file_path)
            frames = [img] if img is not None else []
            return frames, {
                "duration":     8.0,
                "total_frames": 1,
                "fps":          1.0,
            }

        cap = cv2.VideoCapture(file_path)
        fps          = cap.get(cv2.CAP_PROP_FPS) or 25.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration     = total_frames / fps if fps > 0 else 0.0

        sample_count = min(max_frames, total_frames)
        step         = max(1, total_frames // max(sample_count, 1))

        frames = []
        for i in range(0, total_frames, step):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                frames.append(frame)
            if len(frames) >= max_frames:
                break
        cap.release()

        return frames, {
            "duration":     round(duration, 2),
            "total_frames": total_frames,
            "fps":          round(fps, 2),
        }

    # ── Main Analyzer Orchestrator ─────────────────────────────────────────

    def _run_all_analyzers(
        self,
        frames,
        participant_id: str,
        analysis: Dict,
    ):
        """Run all 8 vision analyzers and collect evidence."""
        evidence_list: List[Evidence] = []

        # ── 1. Face Detection ──────────────────────────────────────────────
        try:
            fd = self.face_detector.analyze_frames(frames)
            analysis["face_detection"] = fd
            logger.info(f"FaceDetection: {fd}")

            if fd["face_detected_ratio"] >= 0.5:
                evidence_list.append(Evidence(
                    participant_id=participant_id,
                    evidence_type="camera_on",
                    confidence_delta=_w("camera_on", 0.05),
                    reason=f"Face detected in {round(fd['face_detected_ratio']*100)}% of sampled frames",
                    timestamp=datetime.utcnow(),
                ))
            else:
                evidence_list.append(Evidence(
                    participant_id=participant_id,
                    evidence_type="camera_off",
                    confidence_delta=_w("camera_off", -0.08),
                    reason=f"Face absent in majority of frames (detected in {round(fd['face_detected_ratio']*100)}%)",
                    timestamp=datetime.utcnow(),
                ))
        except Exception as e:
            logger.warning(f"FaceDetector error: {e}")

        # ── 2. Multiple Face Detection ─────────────────────────────────────
        try:
            mf = self.multi_face_detector.analyze_frames(frames)
            analysis["multiple_faces"] = mf
            logger.info(f"MultipleFaces: {mf}")

            if not mf["single_person_consistent"]:
                evidence_list.append(Evidence(
                    participant_id=participant_id,
                    evidence_type="multiple_faces_detected",
                    confidence_delta=_w("multiple_faces_detected", -0.35),
                    reason=(
                        f"Multiple faces detected in {mf['multi_face_frames']} frames "
                        f"(max {mf['max_faces_in_single_frame']} faces at once) — "
                        "possible proxy assistance"
                    ),
                    timestamp=datetime.utcnow(),
                ))
        except Exception as e:
            logger.warning(f"MultipleFaceDetector error: {e}")

        # ── 3. Eye Contact ─────────────────────────────────────────────────
        try:
            ec = self.eye_contact.analyze_frames(frames)
            analysis["eye_contact"] = ec
            logger.info(f"EyeContact: {ec}")

            ratio = ec.get("eye_contact_ratio", 0.0)
            if ratio >= 0.5:
                evidence_list.append(Evidence(
                    participant_id=participant_id,
                    evidence_type="eye_contact_maintained",
                    confidence_delta=_w("eye_contact_maintained", 0.08),
                    reason=f"Eye contact maintained in {round(ratio*100)}% of frames",
                    timestamp=datetime.utcnow(),
                ))
            elif ratio < 0.25 and ec.get("frames_analyzed", 0) > 0:
                evidence_list.append(Evidence(
                    participant_id=participant_id,
                    evidence_type="eye_contact_avoided",
                    confidence_delta=_w("eye_contact_avoided", -0.06),
                    reason=f"Candidate frequently looking away (eye contact {round(ratio*100)}%)",
                    timestamp=datetime.utcnow(),
                ))
        except Exception as e:
            logger.warning(f"EyeContactAnalyzer error: {e}")

        # ── 4. Emotion Detection ───────────────────────────────────────────
        try:
            em = self.emotion_detector.analyze_frames(frames)
            analysis["emotion"] = em
            logger.info(f"Emotion: {em}")

            dominant = em.get("dominant_emotion", "neutral")
            if em.get("positive_ratio", 0) >= 0.3:
                evidence_list.append(Evidence(
                    participant_id=participant_id,
                    evidence_type="positive_emotion",
                    confidence_delta=_w("positive_emotion", 0.05),
                    reason=f"Positive engagement detected — dominant emotion: {dominant}",
                    timestamp=datetime.utcnow(),
                ))
            elif em.get("negative_ratio", 0) >= 0.4:
                evidence_list.append(Evidence(
                    participant_id=participant_id,
                    evidence_type="negative_emotion",
                    confidence_delta=_w("negative_emotion", -0.04),
                    reason=f"High negative emotion detected — dominant: {dominant}",
                    timestamp=datetime.utcnow(),
                ))
        except Exception as e:
            logger.warning(f"EmotionDetector error: {e}")

        # ── 5. Gesture Recognition ─────────────────────────────────────────
        try:
            gs = self.gesture_analyzer.analyze_frames(frames)
            analysis["gesture"] = gs
            logger.info(f"Gesture: {gs}")

            if gs.get("gesture_active"):
                evidence_list.append(Evidence(
                    participant_id=participant_id,
                    evidence_type="gesture_active",
                    confidence_delta=_w("gesture_active", 0.04),
                    reason=(
                        f"Hand gestures detected in {round(gs['gesture_ratio']*100)}% "
                        "of frames — candidate actively engaged"
                    ),
                    timestamp=datetime.utcnow(),
                ))
        except Exception as e:
            logger.warning(f"GestureAnalyzer error: {e}")

        # ── 6. Background OCR ──────────────────────────────────────────────
        try:
            ocr = self.background_ocr.analyze_frames(frames)
            analysis["background_ocr"] = ocr
            logger.info(f"BackgroundOCR: {ocr}")

            if ocr.get("suspicious_text_detected"):
                kws = ", ".join(ocr.get("suspicious_keywords_found", [])[:3])
                evidence_list.append(Evidence(
                    participant_id=participant_id,
                    evidence_type="suspicious_text_detected",
                    confidence_delta=_w("suspicious_text_detected", -0.15),
                    reason=f"Suspicious text visible in background (keywords: {kws})",
                    timestamp=datetime.utcnow(),
                ))
        except Exception as e:
            logger.warning(f"BackgroundOCR error: {e}")

        # ── 7. Face Recognition (Identity Consistency) ─────────────────────
        try:
            fr = self.face_recognizer.analyze_frames(frames)
            analysis["face_recognition"] = fr
            logger.info(f"FaceRecognition: {fr}")

            if not fr.get("identity_consistent") and fr.get("face_swap_risk") in ("medium", "high"):
                evidence_list.append(Evidence(
                    participant_id=participant_id,
                    evidence_type="identity_inconsistency",
                    confidence_delta=_w("identity_inconsistency", -0.30),
                    reason=(
                        f"Identity inconsistency detected — face-swap risk: "
                        f"{fr['face_swap_risk']} (variance={fr['variance']})"
                    ),
                    timestamp=datetime.utcnow(),
                ))
        except Exception as e:
            logger.warning(f"FaceRecognizer error: {e}")

        # ── 8. Camera Tracking ─────────────────────────────────────────────
        try:
            ct = self.camera_tracker.analyze_frames(frames)
            analysis["camera_tracking"] = ct
            logger.info(f"CameraTracking: {ct}")

            if ct.get("tracking_status") == "camera_evasion":
                evidence_list.append(Evidence(
                    participant_id=participant_id,
                    evidence_type="camera_evasion",
                    confidence_delta=_w("camera_evasion", -0.10),
                    reason=(
                        f"Deliberate camera evasion detected — face dropped out frequently "
                        f"(presence ratio {round(ct['presence_ratio']*100)}%)"
                    ),
                    timestamp=datetime.utcnow(),
                ))
            elif ct.get("position_stable") and ct.get("presence_ratio", 0) >= 0.7:
                evidence_list.append(Evidence(
                    participant_id=participant_id,
                    evidence_type="camera_position_stable",
                    confidence_delta=_w("camera_position_stable", 0.03),
                    reason="Camera position consistently stable throughout the session",
                    timestamp=datetime.utcnow(),
                ))
        except Exception as e:
            logger.warning(f"CameraTracker error: {e}")

        # Fallback evidence if nothing was generated
        if not evidence_list:
            evidence_list.append(Evidence(
                participant_id=participant_id,
                evidence_type="camera_on",
                confidence_delta=_w("camera_on", 0.05),
                reason="Video uploaded and processed — no significant signals detected",
                timestamp=datetime.utcnow(),
            ))

        return analysis, evidence_list

    def get_by_participant(self, db: Session, participant_id: str):
        return self.video_repo.get_by_participant(db, participant_id)

    def get_by_meeting(self, db: Session, meeting_id: str):
        return self.video_repo.get_by_meeting(db, meeting_id)
