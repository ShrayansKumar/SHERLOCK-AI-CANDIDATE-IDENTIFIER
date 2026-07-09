from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from database.postgres import Base


class EvidenceLog(Base):

    __tablename__ = "evidence_logs"

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

    evidence_type = Column(String(100), nullable=False)

    confidence_delta = Column(Float, nullable=False)

    reason = Column(String(500), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
