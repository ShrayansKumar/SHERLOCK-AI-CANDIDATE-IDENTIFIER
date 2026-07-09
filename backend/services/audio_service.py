from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from models.audio import AudioUpload
from repositories.audio_repository import AudioRepository
from ai.transcript.whisper_service import WhisperService
from ai.transcript.embedding_service import TranscriptEmbeddingService
from ai.transcript.answer_length import AnswerLengthAnalyzer
from ai.transcript.keyword_detector import KeywordDetector
from ai.speech.silence_detector import SilenceDetector
from ai.reasoning.evidence_collector import Evidence
from ai.reasoning.evidence_weights import WEIGHTS
from services.transcript_service import TranscriptService
from services.fusion_service import fusion_service
from websocket import WebSocketBroadcaster
from utils.logger import logger

_broadcaster = WebSocketBroadcaster()


class AudioService:
    """
    Orchestrates the complete audio processing pipeline:
      Audio Upload -> Whisper -> Transcript -> Embeddings (HuggingFace) ->
      Evidence Collector -> Fusion Service -> Confidence Engine ->
      Confidence Snapshot -> Explanation -> WebSocket Broadcast
    """

    def __init__(self):
        self.audio_repo = AudioRepository()
        self.whisper_service = WhisperService()
        self.embedding_service = TranscriptEmbeddingService()
        self.transcript_service = TranscriptService()
        self.answer_length_analyzer = AnswerLengthAnalyzer()
        self.keyword_detector = KeywordDetector()
        self.silence_detector = SilenceDetector()

    async def process_audio_upload(
        self,
        db: Session,
        meeting_id: Optional[str],
        participant_id: str,
        file_path: str,
        file_name: str,
        file_format: str,
    ) -> Dict:
        """
        Processes an uploaded audio file end-to-end.
        """
        # 1. Save audio upload metadata in PostgreSQL
        upload = AudioUpload(
            participant_id=participant_id,
            meeting_id=meeting_id,
            file_path=file_path,
            file_name=file_name,
            file_format=file_format,
            duration=0.0,
        )
        upload = self.audio_repo.create(db, upload)

        # 2. Transcribe using Whisper
        transcription = self.whisper_service.transcribe(file_path)

        transcript_text = ""
        segments = []
        duration = 0.0
        language = "en"
        embeddings_count = 0
        evidence_list: List[Evidence] = []

        if transcription:
            transcript_text = transcription.get("text", "").strip()
            segments = transcription.get("segments", [])
            duration = transcription.get("duration", 0.0)
            language = transcription.get("language", "en")

            # Update duration on upload record
            upload.duration = duration
            db.commit()
            db.refresh(upload)

            # 3. Save transcript to database
            if transcript_text:
                avg_conf = 0.95
                if segments:
                    avg_conf = sum(s.get("confidence", 0.95) for s in segments) / len(segments)

                saved_transcript = self.transcript_service.save_transcript(
                    db=db,
                    participant_id=participant_id,
                    text=transcript_text,
                    speaker="candidate",
                    confidence=round(avg_conf, 3),
                    meeting_id=meeting_id,
                )

                try:
                    await _broadcaster.broadcast({
                        "type": "new_transcript",
                        "participant_id": participant_id,
                        "text": transcript_text,
                        "speaker": "candidate",
                        "confidence": round(avg_conf, 3),
                    })
                except Exception as e:
                    logger.warning(f"Failed to broadcast new_transcript: {e}")

                # 4. Generate HuggingFace embeddings for every transcript chunk/segment
                chunk_texts = [seg.get("text", "").strip() for seg in segments if seg.get("text", "").strip()]
                if not chunk_texts and transcript_text:
                    chunk_texts = [transcript_text]

                vectors = self.embedding_service.generate_embeddings(chunk_texts)
                for chunk, vec in zip(chunk_texts, vectors):
                    self.embedding_service.save_embedding(
                        db=db,
                        chunk_text=chunk,
                        embedding_vector=vec,
                        participant_id=participant_id,
                        meeting_id=meeting_id,
                        transcript_id=saved_transcript.id if saved_transcript else None,
                    )
                embeddings_count = len(vectors)

                # 5. Generate Evidence objects
                # Positive evidence: candidate speaking
                evidence_list.append(
                    Evidence(
                        participant_id=participant_id,
                        evidence_type="speaking",
                        confidence_delta=WEIGHTS["speaking"],
                        reason="Speech detected from candidate audio upload",
                        timestamp=datetime.utcnow(),
                    )
                )

                # Check answer length
                len_analysis = self.answer_length_analyzer.analyze(transcript_text)
                if len_analysis["label"] == "short":
                    evidence_list.append(
                        Evidence(
                            participant_id=participant_id,
                            evidence_type="short_answer",
                            confidence_delta=WEIGHTS["short_answer"],
                            reason=f"Very short answer detected ({len_analysis['word_count']} words)",
                            timestamp=datetime.utcnow(),
                        )
                    )
                elif len_analysis["label"] == "long":
                    evidence_list.append(
                        Evidence(
                            participant_id=participant_id,
                            evidence_type="long_answer",
                            confidence_delta=WEIGHTS["long_answer"],
                            reason=f"Detailed answer provided ({len_analysis['word_count']} words)",
                            timestamp=datetime.utcnow(),
                        )
                    )

                # Check technical content
                kw_analysis = self.keyword_detector.detect(transcript_text)
                if kw_analysis["tech_count"] > 0:
                    tech_words = ", ".join(kw_analysis["tech_keywords"][:3])
                    evidence_list.append(
                        Evidence(
                            participant_id=participant_id,
                            evidence_type="technical_answer",
                            confidence_delta=WEIGHTS["technical_answer"],
                            reason=f"Technical answer detected ({kw_analysis['tech_count']} keywords: {tech_words})",
                            timestamp=datetime.utcnow(),
                        )
                    )

                # Check confident speech
                if avg_conf >= 0.85 and len_analysis["label"] != "short":
                    evidence_list.append(
                        Evidence(
                            participant_id=participant_id,
                            evidence_type="confident_speech",
                            confidence_delta=WEIGHTS["confident_speech"],
                            reason=f"Confident speech detected (confidence {avg_conf:.2f})",
                            timestamp=datetime.utcnow(),
                        )
                    )
            else:
                # Empty transcript evidence
                evidence_list.append(
                    Evidence(
                        participant_id=participant_id,
                        evidence_type="empty_transcript",
                        confidence_delta=WEIGHTS["empty_transcript"],
                        reason="Audio uploaded but transcript was empty",
                        timestamp=datetime.utcnow(),
                    )
                )

            # Check long silence using SilenceDetector
            if duration > 0 and segments:
                silences = self.silence_detector.detect(segments, duration, min_silence_seconds=3.0)
                long_silences = [s for s in silences if s.get("duration", 0.0) >= 3.0]
                if long_silences:
                    max_sil = max(s["duration"] for s in long_silences)
                    evidence_list.append(
                        Evidence(
                            participant_id=participant_id,
                            evidence_type="long_silence",
                            confidence_delta=WEIGHTS["long_silence"],
                            reason=f"Long silence gap detected ({max_sil}s)",
                            timestamp=datetime.utcnow(),
                        )
                    )
        else:
            # Empty transcript if transcription returned None/empty
            evidence_list.append(
                Evidence(
                    participant_id=participant_id,
                    evidence_type="empty_transcript",
                    confidence_delta=WEIGHTS["empty_transcript"],
                    reason="Audio upload could not be transcribed",
                    timestamp=datetime.utcnow(),
                )
            )

        # 6. Pass generated evidence through the existing Fusion Service
        latest_participant = None
        for ev in evidence_list:
            res = await fusion_service.process_evidence(ev, meeting_id=meeting_id)
            if res is not None:
                latest_participant = res

        return {
            "upload_id": upload.id,
            "participant_id": upload.participant_id,
            "meeting_id": upload.meeting_id,
            "file_name": upload.file_name,
            "file_format": upload.file_format,
            "duration": upload.duration,
            "transcript": transcript_text,
            "language": language,
            "segments": segments,
            "embeddings_count": embeddings_count,
            "evidence_generated": [e.evidence_type for e in evidence_list],
            "confidence": latest_participant.confidence if latest_participant else None,
            "created_at": upload.created_at,
        }

    def get_by_participant(self, db: Session, participant_id: str):
        return self.audio_repo.get_by_participant(db, participant_id)

    def get_by_meeting(self, db: Session, meeting_id: str):
        return self.audio_repo.get_by_meeting(db, meeting_id)
