from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.sql import func
from database.postgres import Base


class Transcript(Base):

    __tablename__ = "transcripts"

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

    speaker = Column(String(100), nullable=True)

    text = Column(Text, nullable=False)

    confidence = Column(Float, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
