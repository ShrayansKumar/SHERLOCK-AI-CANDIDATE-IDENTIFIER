from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
)
from sqlalchemy.sql import func
from database.postgres import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)

    participant_id = Column(String(100), unique=True, nullable=False)

    display_name = Column(String(255), nullable=False)

    email = Column(String(255), nullable=True)

    role = Column(
        String(50),
        default="unknown"
    )

    webcam_on = Column(Boolean, default=False)

    microphone_on = Column(Boolean, default=False)

    screen_share = Column(Boolean, default=False)

    speaking_duration = Column(Float, default=0.0)

    confidence = Column(Float, default=0.0)

    status = Column(
        String(50),
        default="joined"
    )

    joined_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    left_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    meeting = relationship(
    "Meeting",
    back_populates="participants"
    )