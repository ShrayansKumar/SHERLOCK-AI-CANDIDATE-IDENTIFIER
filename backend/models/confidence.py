from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.postgres import Base


class ConfidenceSnapshot(Base):

    __tablename__ = "confidence_snapshots"

    id = Column(Integer, primary_key=True, index=True)

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

    confidence = Column(Float, nullable=False)

    evidence_type = Column(String(100), nullable=True)

    reason = Column(String(500), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
