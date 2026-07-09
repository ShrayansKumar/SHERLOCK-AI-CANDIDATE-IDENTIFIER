import os
import shutil
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from dependencies import get_db
from services.audio_service import AudioService
from utils.logger import logger

router = APIRouter(
    prefix="/api/v1/audio",
    tags=["Audio"],
)

audio_service = AudioService()

ALLOWED_EXTENSIONS = {"wav", "mp3", "m4a"}


def _get_extension(filename: str) -> str:
    if "." not in filename:
        return ""
    return filename.rsplit(".", 1)[-1].lower()


@router.post("/upload")
async def upload_audio(
    participant_id: str = Form(...),
    meeting_id: Optional[str] = Form(None),
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload an audio file (.wav, .mp3, .m4a) for speech transcription,
    embedding generation, and confidence evaluation.
    """
    ext = _get_extension(audio_file.filename or "")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed formats: wav, mp3, m4a",
        )

    upload_dir = os.path.join("uploads", "audio")
    os.makedirs(upload_dir, exist_ok=True)

    safe_filename = f"{participant_id}_{audio_file.filename}"
    file_path = os.path.join(upload_dir, safe_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
    except Exception as e:
        logger.error(f"Failed to save uploaded audio file: {e}")
        raise HTTPException(status_code=500, detail="Could not save file")

    result = await audio_service.process_audio_upload(
        db=db,
        meeting_id=meeting_id,
        participant_id=participant_id,
        file_path=file_path,
        file_name=audio_file.filename or "audio.wav",
        file_format=ext,
    )

    return result


@router.get("/meeting/{meeting_id}")
def get_audio_by_meeting(
    meeting_id: str,
    db: Session = Depends(get_db),
):
    """Get all audio upload records for a meeting."""
    uploads = audio_service.get_by_meeting(db, meeting_id)
    return [
        {
            "id": u.id,
            "participant_id": u.participant_id,
            "meeting_id": u.meeting_id,
            "file_name": u.file_name,
            "file_format": u.file_format,
            "duration": u.duration,
            "created_at": u.created_at,
        }
        for u in uploads
    ]


from pydantic import BaseModel
from services.vb_cable_service import vb_cable_service


class StartCaptureRequest(BaseModel):
    meeting_id: str
    participant_id: str = "candidate_001"
    device_index: Optional[int] = None
    chunk_seconds: int = 10


@router.get("/devices")
def list_audio_devices():
    """List available Windows audio input devices, highlighting VB-Audio Cable."""
    return vb_cable_service.list_devices()


@router.get("/live-capture/status")
def get_live_capture_status():
    """Get current VB-Audio Cable live capture status."""
    return vb_cable_service.get_status()


@router.post("/live-capture/start")
def start_live_capture(req: StartCaptureRequest):
    """Start listening to Google Meet / system audio via VB-Audio Cable."""
    return vb_cable_service.start_capture(
        meeting_id=req.meeting_id,
        participant_id=req.participant_id,
        device_index=req.device_index,
        chunk_seconds=req.chunk_seconds,
    )


@router.post("/live-capture/stop")
def stop_live_capture():
    """Stop live VB-Audio Cable capture."""
    return vb_cable_service.stop_capture()


@router.get("/{participant_id}")
def get_audio_by_participant(
    participant_id: str,
    db: Session = Depends(get_db),
):
    """Get all audio upload records for a participant."""
    uploads = audio_service.get_by_participant(db, participant_id)
    return [
        {
            "id": u.id,
            "participant_id": u.participant_id,
            "meeting_id": u.meeting_id,
            "file_name": u.file_name,
            "file_format": u.file_format,
            "duration": u.duration,
            "created_at": u.created_at,
        }
        for u in uploads
    ]



@router.get("")
def get_audio_root():
    """Audio endpoint root status."""
    return []

