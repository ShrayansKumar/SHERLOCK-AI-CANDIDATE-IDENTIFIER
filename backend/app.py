from fastapi import FastAPI

from config import settings
from api.health import router as health_router
from utils.logger import logger
from middleware.exception_handler import global_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from api.participants import router as participant_router
from api.meetings import router as meeting_router

logger.info("Starting Sherlock Backend...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

app.include_router(health_router)
app.include_router(participant_router)
app.include_router(meeting_router)

app.add_exception_handler(
    Exception,
    global_exception_handler
)

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)

@app.get("/")
def root():
    logger.info("Root endpoint called")
    return {
        "message": "Sherlock Backend Running 🚀",
        "version": settings.APP_VERSION
    }