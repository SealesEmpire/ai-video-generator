"""Video generation business logic."""

import asyncio
import random

# Sample video URLs and thumbnails for different styles
SAMPLE_VIDEOS = {
    "realistic": [
        {
            "video_url": "https://images.pexels.com/photos/11262264/pexels-photo-11262264.jpeg",
            "thumbnail_url": "https://images.pexels.com/photos/11262264/pexels-photo-11262264.jpeg"
        },
        {
            "video_url": "https://images.pexels.com/photos/7480538/pexels-photo-7480538.jpeg",
            "thumbnail_url": "https://images.pexels.com/photos/7480538/pexels-photo-7480538.jpeg"
        }
    ],
    "anime": [
        {
            "video_url": "https://images.pexels.com/photos/18069362/pexels-photo-18069362.png",
            "thumbnail_url": "https://images.pexels.com/photos/18069362/pexels-photo-18069362.png"
        }
    ],
    "cartoon": [
        {
            "video_url": "https://images.unsplash.com/photo-1733590555923-2aa0e489300e",
            "thumbnail_url": "https://images.unsplash.com/photo-1733590555923-2aa0e489300e"
        }
    ],
    "surreal": [
        {
            "video_url": "https://images.pexels.com/photos/24182512/pexels-photo-24182512.jpeg",
            "thumbnail_url": "https://images.pexels.com/photos/24182512/pexels-photo-24182512.jpeg"
        }
    ],
    "talking_image": [
        {
            "video_url": "https://images.unsplash.com/photo-1717632464005-1f33909e484b",
            "thumbnail_url": "https://images.unsplash.com/photo-1717632464005-1f33909e484b"
        }
    ],
    "character_animation": [
        {
            "video_url": "https://images.pexels.com/photos/17722043/pexels-photo-17722043.jpeg",
            "thumbnail_url": "https://images.pexels.com/photos/17722043/pexels-photo-17722043.jpeg"
        }
    ],
    "movement_overlay": [
        {
            "video_url": "https://images.pexels.com/photos/32539017/pexels-photo-32539017.jpeg",
            "thumbnail_url": "https://images.pexels.com/photos/32539017/pexels-photo-32539017.jpeg"
        }
    ],
    "talking_face": [
        {
            "video_url": "https://images.unsplash.com/photo-1483478550801-ceba5fe50e8e",
            "thumbnail_url": "https://images.unsplash.com/photo-1483478550801-ceba5fe50e8e"
        }
    ]
}

# Available video styles
TEXT_TO_VIDEO_STYLES = [
    {"id": "realistic", "name": "Realistic", "description": "Photorealistic video generation"},
    {"id": "anime", "name": "Anime", "description": "Japanese animation style"},
    {"id": "cartoon", "name": "Cartoon", "description": "Western cartoon style"},
    {"id": "surreal", "name": "Surreal", "description": "Abstract and artistic style"},
    {"id": "talking_image", "name": "Talking Image", "description": "Face animation from image"}
]

IMAGE_TO_VIDEO_STYLES = [
    {"id": "character_animation", "name": "Character Animation", "description": "Animate characters in the image"},
    {"id": "movement_overlay", "name": "Movement Overlay", "description": "Add dynamic movement effects"},
    {"id": "talking_face", "name": "Talking Face", "description": "Make faces speak and move"}
]


async def simulate_video_generation(video_id: str, style: str, db) -> None:
    """Simulate video generation process and update the database."""
    await asyncio.sleep(3)  # Simulate processing time

    sample_content = random.choice(SAMPLE_VIDEOS.get(style, SAMPLE_VIDEOS["realistic"]))

    await db.videos.update_one(
        {"id": video_id},
        {
            "$set": {
                "status": "completed",
                "video_url": sample_content["video_url"],
                "thumbnail_url": sample_content["thumbnail_url"]
            }
        }
    )
