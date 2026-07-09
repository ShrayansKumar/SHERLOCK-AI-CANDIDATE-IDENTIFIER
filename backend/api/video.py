import os
import shutil
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from dependencies import get_db
from services.video_service import VideoService
from utils.logger import logger

router = APIRouter(
    prefix="/api/v1/video",
    tags=["Video"],
)

video_service = VideoService()

ALLOWED_EXTENSIONS = {"mp4", "webm", "mov", "avi", "mkv", "jpg", "jpeg", "png"}


def _get_extension(filename: str) -> str:
    if "." not in filename:
        return ""
    return filename.rsplit(".", 1)[-1].lower()


@router.post("/upload")
async def upload_video(
    participant_id: str = Form(...),
    meeting_id: Optional[str] = Form(None),
    video_file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a video file or live frame image (.mp4, .webm, .jpg, etc.) for frame-level
    analysis: camera presence, screen-share detection, speaking activity.
    """
    ext = _get_extension(video_file.filename or "")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    upload_dir = os.path.join("uploads", "video")
    os.makedirs(upload_dir, exist_ok=True)

    safe_filename = f"{participant_id}_{video_file.filename}"
    file_path = os.path.join(upload_dir, safe_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(video_file.file, buffer)
    except Exception as e:
        logger.error(f"Failed to save uploaded video file: {e}")
        raise HTTPException(status_code=500, detail="Could not save file")

    result = await video_service.process_video_upload(
        db=db,
        meeting_id=meeting_id,
        participant_id=participant_id,
        file_path=file_path,
        file_name=video_file.filename or "video.mp4",
        file_format=ext,
    )

    return result


@router.get("/meeting/{meeting_id}")
def get_video_by_meeting(
    meeting_id: str,
    db: Session = Depends(get_db),
):
    """Get all video upload records for a meeting."""
    uploads = video_service.get_by_meeting(db, meeting_id)
    return [
        {
            "id": u.id,
            "participant_id": u.participant_id,
            "meeting_id": u.meeting_id,
            "file_name": u.file_name,
            "file_format": u.file_format,
            "duration": u.duration,
            "frame_count": u.frame_count,
            "created_at": u.created_at,
        }
        for u in uploads
    ]


@router.get("/{participant_id}")
def get_video_by_participant(
    participant_id: str,
    db: Session = Depends(get_db),
):
    """Get all video upload records for a participant."""
    uploads = video_service.get_by_participant(db, participant_id)
    return [
        {
            "id": u.id,
            "participant_id": u.participant_id,
            "meeting_id": u.meeting_id,
            "file_name": u.file_name,
            "file_format": u.file_format,
            "duration": u.duration,
            "frame_count": u.frame_count,
            "created_at": u.created_at,
        }
        for u in uploads
    ]


@router.get("")
def get_video_root():
    """Video endpoint root status."""
    return {"status": "Video API active", "upload_endpoint": "POST /api/v1/video/upload"}
