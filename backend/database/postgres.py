import importlib
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from config import settings

DATABASE_URL = settings.DATABASE_URL

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if DATABASE_URL and DATABASE_URL.startswith("postgresql://") and "+" not in DATABASE_URL.split("://")[0]:
    try:
        importlib.import_module("psycopg2")
    except ImportError:
        try:
            importlib.import_module("psycopg")
            DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
        except ImportError:
            try:
                importlib.import_module("pg8000")
                DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+pg8000://", 1)
            except ImportError:
                pass


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

import models.participant
import models.meeting
import models.confidence
import models.evidence
import models.explanation
import models.transcript
import models.audio
import models.embedding
import models.video

try:
    Base.metadata.create_all(bind=engine)
except Exception:
    pass