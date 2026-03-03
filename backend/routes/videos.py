"""Video generation and gallery endpoints."""

import uuid
import shutil
from datetime import datetime, timezone
from pathlib import PurePath

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile

from config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, UPLOADS_DIR
from models import VideoGenerationRequest, VideoResponse, UserGallery
from services.video_service import simulate_video_generation

router = APIRouter()

# The database handle is injected by server.py after startup.
db = None  # type: ignore[assignment]


def _set_db(database):
    """Called by the application entry-point to inject the DB handle."""
    global db
    db = database


@router.post("/generate-text-to-video", response_model=VideoResponse)
async def generate_text_to_video(
    request: VideoGenerationRequest,
    background_tasks: BackgroundTasks,
):
    """Generate video from text prompt."""
    video_id = str(uuid.uuid4())

    video_data = {
        "id": video_id,
        "prompt": request.prompt,
        "style": request.style,
        "duration": request.duration,
        "status": "generating",
        "created_at": datetime.now(timezone.utc),
        "nsfw_enabled": request.nsfw_enabled,
    }

    await db.videos.insert_one(video_data)
    background_tasks.add_task(simulate_video_generation, video_id, request.style, db)

    return VideoResponse(**video_data)


@router.post("/generate-image-to-video", response_model=VideoResponse)
async def generate_image_to_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    style: str = Form(...),
    duration: int = Form(7),
    nsfw_enabled: bool = Form(False),
):
    """Generate video from uploaded image."""
    # Validate content type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Validate extension safely (Rec #5)
    file_extension = PurePath(file.filename or "upload.jpg").suffix.lstrip(".").lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Validate file size (Rec #5)
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 50 MB)")
    await file.seek(0)

    video_id = str(uuid.uuid4())
    filename = f"{video_id}.{file_extension}"
    file_path = UPLOADS_DIR / filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    video_data = {
        "id": video_id,
        "image_filename": filename,
        "style": style,
        "duration": duration,
        "status": "generating",
        "created_at": datetime.now(timezone.utc),
        "nsfw_enabled": nsfw_enabled,
    }

    await db.videos.insert_one(video_data)
    background_tasks.add_task(simulate_video_generation, video_id, style, db)

    return VideoResponse(**video_data)


@router.get("/video/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str):
    """Get video by ID."""
    video = await db.videos.find_one({"id": video_id})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return VideoResponse(**video)


@router.get("/videos", response_model=UserGallery)
async def get_user_videos(limit: int = 20, offset: int = 0):
    """Get user's video gallery with enforced pagination limits."""
    limit = min(max(limit, 1), 100)  # Cap between 1 and 100
    offset = max(offset, 0)

    videos = (
        await db.videos.find()
        .skip(offset)
        .limit(limit)
        .sort("created_at", -1)
        .to_list(limit)
    )
    total_count = await db.videos.count_documents({})

    return UserGallery(
        videos=[VideoResponse(**video) for video in videos],
        total_count=total_count,
    )
