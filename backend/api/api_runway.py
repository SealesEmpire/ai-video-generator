# backend/api/api_runway.py

import httpx
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

RUNWAYML_API_KEY = os.getenv("RUNWAYML_API_KEY")

router = APIRouter()


class RunwayGenerateRequest(BaseModel):
    prompt: str
    image_url: Optional[str] = None


@router.post("/generate")
async def generate_video(request: RunwayGenerateRequest):
    """Generate video via Runway ML API"""
    if not RUNWAYML_API_KEY:
        raise HTTPException(status_code=500, detail="Runway API key not configured")

    url = "https://api.runwayml.com/v1/generate"

    headers = {
        "Authorization": f"Bearer {RUNWAYML_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {"prompt": request.prompt}
    if request.image_url:
        payload["image_url"] = request.image_url

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Runway API error: {response.text}",
        )
