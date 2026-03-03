"""Runway ML API integration (work-in-progress).

This module provides a placeholder router for future RunwayML API
integration.  The ``generate_video`` helper is not yet wired to any
endpoint; see RECOMMENDATIONS.md #25 for details.
"""

import os

import requests
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

load_dotenv()

RUNWAY_API_KEY = os.getenv("RUNWAYML_API_KEY")

router = APIRouter()


class RunwayGenerateRequest(BaseModel):
    prompt: str
    image_url: Optional[str] = None


def generate_video(prompt: str, image_url: str | None = None) -> dict:
    """Call the RunwayML generation API (requires a valid API key)."""
    url = "https://api.runwayml.com/v1/generate"
    headers = {
        "Authorization": f"Bearer {RUNWAY_API_KEY}",
        "Content-Type": "application/json",
    }
    payload: dict = {"prompt": prompt}
    if image_url:
        payload["image_url"] = image_url

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    raise Exception(f"Runway API error: {response.text}")


@router.post("/generate")
async def runway_generate(request: RunwayGenerateRequest):
    """Generate a video via RunwayML (requires RUNWAYML_API_KEY)."""
    if not RUNWAY_API_KEY:
        raise HTTPException(status_code=503, detail="RunwayML API key not configured")
    try:
        result = generate_video(request.prompt, request.image_url)
        return result
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))
