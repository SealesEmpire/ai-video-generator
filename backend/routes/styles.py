"""Video styles endpoint with caching headers."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from services.video_service import TEXT_TO_VIDEO_STYLES, IMAGE_TO_VIDEO_STYLES

router = APIRouter()


@router.get("/styles")
async def get_available_styles():
    """Get available video styles.

    Returns cached response (static data that rarely changes).
    """
    content = {
        "text_to_video_styles": TEXT_TO_VIDEO_STYLES,
        "image_to_video_styles": IMAGE_TO_VIDEO_STYLES,
    }
    return JSONResponse(
        content=content,
        headers={"Cache-Control": "public, max-age=3600"},
    )
