"""Pydantic models used across the application."""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# --- Video Models ---

class VideoGenerationRequest(BaseModel):
    prompt: str
    style: str  # realistic, anime, cartoon, surreal, talking_image
    duration: int = Field(default=7, ge=5, le=10)
    nsfw_enabled: bool = Field(default=False)


class ImageToVideoRequest(BaseModel):
    style: str  # character_animation, movement_overlay, talking_face
    duration: int = Field(default=7, ge=5, le=10)
    nsfw_enabled: bool = Field(default=False)


class VideoResponse(BaseModel):
    id: str
    prompt: Optional[str] = None
    image_filename: Optional[str] = None
    style: str
    duration: int
    status: str  # generating, completed, failed
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    created_at: datetime
    nsfw_enabled: bool = Field(default=False)


class UserGallery(BaseModel):
    videos: List[VideoResponse]
    total_count: int


# --- Auth Models ---

class UserRegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=8)


class UserLoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Error Model ---

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
