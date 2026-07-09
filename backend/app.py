from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from api.health import router as health_router
from api.participants import router as participant_router
from api.meetings import router as meeting_router
from api.confidence import router as confidence_router
from api.explanation import router as explanation_router
from api.transcript import router as transcript_router
from api.audio import router as audio_router
from api.video import router as video_router
from api.ws import router as ws_router
from api.simulate import router as simulate_router
from api.report import router as report_router
from middleware.exception_handler import global_exception_handler
from utils.logger import logger

logger.info("Starting Sherlock Backend...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

# -----------------------------
# CORS
# -----------------------------
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Exception Handler
# -----------------------------
app.add_exception_handler(
    Exception,
    global_exception_handler
)

# -----------------------------
# REST Routers
# -----------------------------
app.include_router(health_router)
app.include_router(participant_router)
app.include_router(meeting_router)
app.include_router(confidence_router)
app.include_router(explanation_router)
app.include_router(transcript_router)
app.include_router(audio_router)
app.include_router(video_router)
app.include_router(simulate_router)
app.include_router(report_router)

# -----------------------------
# WebSocket Router
# -----------------------------
app.include_router(ws_router)

# -----------------------------
# Root
# -----------------------------
@app.get("/")
def root():
    logger.info("Root endpoint called")
    return {
        "message": "Sherlock Backend Running 🚀",
        "version": settings.APP_VERSION
    }