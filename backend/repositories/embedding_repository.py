from sqlalchemy.orm import Session
from models.embedding import TranscriptEmbedding


class EmbeddingRepository:

    def create(self, db: Session, embedding: TranscriptEmbedding):
        db.add(embedding)
        db.commit()
        db.refresh(embedding)
        return embedding

    def get_by_participant(self, db: Session, participant_id: str):
        return (
            db.query(TranscriptEmbedding)
            .filter(TranscriptEmbedding.participant_id == participant_id)
            .order_by(TranscriptEmbedding.created_at.asc())
            .all()
        )

    def get_by_meeting(self, db: Session, meeting_id: str):
        return (
            db.query(TranscriptEmbedding)
            .filter(TranscriptEmbedding.meeting_id == meeting_id)
            .order_by(TranscriptEmbedding.created_at.asc())
            .all()
        )

    def get_by_transcript_id(self, db: Session, transcript_id: int):
        return (
            db.query(TranscriptEmbedding)
            .filter(TranscriptEmbedding.transcript_id == transcript_id)
            .order_by(TranscriptEmbedding.created_at.asc())
            .all()
        )
