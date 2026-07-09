from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database.postgres import Base


class ExplanationLog(Base):

    __tablename__ = "explanation_logs"

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

    evidence_type = Column(String(100), nullable=True)

    explanation = Column(Text, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
