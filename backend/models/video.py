from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from database.postgres import Base


class VideoUpload(Base):

    __tablename__ = "video_uploads"

    id = Column(Integer, primary_key=True, index=True)

    participant_id = Column(String(100), nullable=False, index=True)

    meeting_id = Column(String(100), nullable=True, index=True)

    file_path = Column(String(500), nullable=False)

    file_name = Column(String(255), nullable=False)

    file_format = Column(String(50), nullable=False)

    duration = Column(Float, nullable=True, default=0.0)

    # Simple frame-level analysis results stored as JSON text
    frame_count = Column(Integer, nullable=True, default=0)

    analysis_summary = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
