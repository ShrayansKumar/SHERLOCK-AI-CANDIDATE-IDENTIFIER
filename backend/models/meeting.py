from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.postgres import Base


class Meeting(Base):

    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)

    meeting_id = Column(
        String(100),
        unique=True,
        nullable=False
    )

    platform = Column(
        String(50),
        nullable=False
    )

    candidate_name = Column(
        String(255),
        nullable=True
    )

    candidate_email = Column(
        String(255),
        nullable=True
    )

    interviewer_names = Column(
        String(500),
        nullable=True
    )

    status = Column(
        String(50),
        default="scheduled"
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

    participants = relationship(
    "Participant",
    back_populates="meeting",
    cascade="all, delete-orphan"
)