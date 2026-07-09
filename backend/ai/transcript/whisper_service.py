import os
import math
import httpx
from typing import Optional, Dict, List
from utils.logger import logger
from config import settings


class WhisperService:
    """
    Speech-to-text transcription service using Groq API (whisper-large-v3)
    with local faster-whisper fallback.
    Transcribes audio to text with timestamps and language detection.
    """

    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8"
    ):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model = None

    @property
    def model(self):
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
                self._model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type=self.compute_type
                )
            except Exception as e:
                logger.error(f"Failed to load faster-whisper model: {e}")
                raise
        return self._model

    def _transcribe_via_groq(self, audio_path: str, groq_key: str) -> Optional[Dict]:
        try:
            with open(audio_path, "rb") as f:
                files = {"file": (os.path.basename(audio_path), f)}
                data = {"model": "whisper-large-v3", "response_format": "verbose_json"}
                headers = {"Authorization": f"Bearer {groq_key}"}
                with httpx.Client(timeout=30.0) as client:
                    res = client.post(
                        "https://api.groq.com/openai/v1/audio/transcriptions",
                        files=files,
                        data=data,
                        headers=headers,
                    )
                    if res.status_code != 200:
                        logger.warning(f"Groq Whisper API returned {res.status_code}: {res.text}")
                        return None
                    payload = res.json()

            full_text = payload.get("text", "").strip()
            raw_segments = payload.get("segments", [])
            segments = []
            for seg in raw_segments:
                seg_text = seg.get("text", "").strip()
                if seg_text:
                    segments.append({
                        "start": round(float(seg.get("start", 0.0)), 2),
                        "end": round(float(seg.get("end", 0.0)), 2),
                        "text": seg_text,
                        "confidence": 0.95,
                    })

            duration = round(float(payload.get("duration", 10.0)), 2)
            detected_lang = payload.get("language", "en")

            logger.info(f"Groq Whisper API transcribed '{audio_path}': '{full_text[:60]}...'")
            return {
                "text": full_text,
                "segments": segments,
                "language": detected_lang,
                "duration": duration,
            }
        except Exception as e:
            logger.warning(f"Error calling Groq Whisper API: {e}")
            return None

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict]:
        """
        Transcribe an audio file to text.
        """
        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return None

        # 1. Try Groq fast Whisper API first
        groq_key = settings.GROQ_API_KEY or os.environ.get("GROQ_API_KEY")
        if groq_key:
            res = self._transcribe_via_groq(audio_path, groq_key)
            if res is not None:
                return res

        # 2. Fallback to local faster-whisper
        try:
            segments_gen, info = self.model.transcribe(
                audio_path,
                language=language,
                **kwargs
            )

            segments: List[Dict] = []
            full_text_parts: List[str] = []

            for seg in segments_gen:
                seg_text = seg.text.strip()
                full_text_parts.append(seg_text)

                conf = 0.95
                if hasattr(seg, "avg_logprob") and seg.avg_logprob is not None:
                    try:
                        conf = round(math.exp(seg.avg_logprob), 3)
                    except Exception:
                        conf = 0.95

                segments.append({
                    "start": round(float(getattr(seg, "start", 0.0)), 2),
                    "end": round(float(getattr(seg, "end", 0.0)), 2),
                    "text": seg_text,
                    "confidence": conf,
                })

            full_text = " ".join(full_text_parts).strip()
            detected_lang = getattr(info, "language", language or "en")
            duration = round(float(getattr(info, "duration", 0.0)), 2)

            return {
                "text": full_text,
                "segments": segments,
                "language": detected_lang,
                "duration": duration,
            }
        except Exception as e:
            logger.error(f"Whisper transcription error for {audio_path}: {e}")
            return None

