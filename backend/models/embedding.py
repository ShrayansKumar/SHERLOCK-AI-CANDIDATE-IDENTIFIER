from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database.postgres import Base


class TranscriptEmbedding(Base):

    __tablename__ = "transcript_embeddings"

    id = Column(Integer, primary_key=True, index=True)

    transcript_id = Column(
        Integer,
        nullable=True,
        index=True
    )

    participant_id = Column(
        String(100),
        nullable=False,
        index=True
    )

    meeting_id = Column(
        String(100),
        nullable=True,
        index=True
    )

    chunk_text = Column(Text, nullable=False)

    embedding_vector = Column(Text, nullable=False)

    model_name = Column(
        String(255),
        default="sentence-transformers/all-MiniLM-L6-v2"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
