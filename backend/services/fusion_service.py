from database.postgres import SessionLocal
from events.event_types import EventType
from ai.confidence.confidence_instance import confidence_engine
from ai.reasoning.evidence_collector import EvidenceCollector, Evidence
from models.confidence import ConfidenceSnapshot

from models.evidence import EvidenceLog
from models.explanation import ExplanationLog
from models.transcript import Transcript
from repositories.confidence_repository import ConfidenceRepository
from repositories.evidence_repository import EvidenceRepository
from repositories.explanation_repository import ExplanationRepository
from repositories.participant_repository import ParticipantRepository
from repositories.transcript_repository import TranscriptRepository
from websocket import WebSocketBroadcaster
from utils.logger import logger


_collector = EvidenceCollector()
_confidence_repo = ConfidenceRepository()
_evidence_repo = EvidenceRepository()
_explanation_repo = ExplanationRepository()
_participant_repo = ParticipantRepository()
_transcript_repo = TranscriptRepository()
_broadcaster = WebSocketBroadcaster()


class FusionService:
    """
    Central pipeline orchestrator:
      Event → EvidenceCollector → ConfidenceEngine (in-memory delta)
            → Persist ConfidenceSnapshot to Postgres
            → Persist EvidenceLog to Postgres
            → Persist ExplanationLog to Postgres
            → Sync participants.confidence column in Postgres
            → Broadcast via WebSocket
    """

    async def process_event(self, event):
        """
        Full pipeline for one event.
        Returns the updated ParticipantConfidence or None if no evidence matched.
        """
        meeting_val = getattr(event, "meeting_id", None)
        if meeting_val is None and event.payload:
            meeting_val = event.payload.get("meeting_id")
        meeting_id = str(meeting_val) if meeting_val is not None else None

        if event.type == EventType.TRANSCRIPT_RECEIVED and event.payload:
            transcript_text = str(event.payload.get("transcript", "")).strip()
            if transcript_text:
                speaker_val = str(event.payload.get("speaker", "candidate")).strip()
                conf_val = event.payload.get("confidence", 0.95)
                db_t = SessionLocal()
                try:
                    t_obj = Transcript(
                        participant_id=event.participant_id,
                        text=transcript_text,
                        speaker=speaker_val,
                        confidence=conf_val,
                        meeting_id=meeting_id,
                    )
                    _transcript_repo.create(db_t, t_obj)
                finally:
                    db_t.close()

        # 1. Collect evidence from the event
        evidence = _collector.collect(event)

        if evidence is None:
            logger.debug(
                f"No evidence for event {event.type} "
                f"| participant {event.participant_id}"
            )
            return None

        return await self.process_evidence(evidence, meeting_id)

    async def process_evidence(self, evidence: Evidence, meeting_id: str = None):
        """
        Process a single Evidence object through the fusion engine,
        database persistence, and WebSocket broadcasting.
        """
        # 2. Apply delta via in-memory engine (handles clamping to [0,1])
        participant = confidence_engine.update(evidence)

        explanation_text = (
            f"[{evidence.evidence_type}] {evidence.reason} "
            f"(Δ {evidence.confidence_delta:+.2f})"
        )

        # 3. Persist everything to Postgres in one session
        db = SessionLocal()
        try:
            # 3a. Confidence snapshot (the authoritative persistent record)
            snapshot = ConfidenceSnapshot(
                participant_id=evidence.participant_id,
                confidence=participant.confidence,
                evidence_type=evidence.evidence_type,
                reason=evidence.reason,
                meeting_id=meeting_id,
            )
            _confidence_repo.create(db, snapshot)

            # 3b. Evidence log
            evidence_log = EvidenceLog(
                participant_id=evidence.participant_id,
                evidence_type=evidence.evidence_type,
                confidence_delta=evidence.confidence_delta,
                reason=evidence.reason,
                meeting_id=meeting_id,
            )
            _evidence_repo.create(db, evidence_log)

            # 3c. Explanation log
            explanation_log = ExplanationLog(
                participant_id=evidence.participant_id,
                evidence_type=evidence.evidence_type,
                explanation=explanation_text,
                meeting_id=meeting_id,
            )
            _explanation_repo.create(db, explanation_log)

            # 3d. Keep participants.confidence column in sync
            _participant_repo.update_confidence(
                db,
                evidence.participant_id,
                participant.confidence,
            )

        except Exception as e:
            logger.error(f"FusionService DB persist error: {e}")
        finally:
            db.close()

        # 4. Broadcast live update to all WebSocket clients
        try:
            await _broadcaster.broadcast({
                "type": "confidence_updated",
                "participant_id": evidence.participant_id,
                "confidence": participant.confidence,
                "evidence_type": evidence.evidence_type,
                "reason": evidence.reason,
                "confidence_delta": evidence.confidence_delta,
                "explanation": explanation_text,
            })
        except Exception as e:
            logger.error(f"FusionService broadcast error: {e}")

        logger.info(
            f"Fusion | {evidence.participant_id} | "
            f"{evidence.evidence_type} | "
            f"confidence={participant.confidence:.2f}"
        )

        return participant


# Shared singleton used by event_handlers
fusion_service = FusionService()
