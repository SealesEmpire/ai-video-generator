# backend/api/api_runway.py

import requests
import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

load_dotenv()  # Load variables from .env file

RUNWAYML_API_KEY = os.getenv("RUNWAYML_API_KEY")

router = APIRouter()


class RunwayGenerateRequest(BaseModel):
    prompt: str
    image_url: Optional[str] = None


def generate_video(prompt, image_url=None):
    url = "https://api.runwayml.com/v1/generate"

    headers = {
        "Authorization": f"Bearer {RUNWAYML_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": prompt
    }

    if image_url:
        payload["image_url"] = image_url

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Runway API error: {response.text}")


@router.post("/generate")
async def runway_generate(request: RunwayGenerateRequest):
    """Generate video using Runway API"""
    if not RUNWAYML_API_KEY:
        raise HTTPException(status_code=500, detail="Runway API key not configured")
    try:
        result = generate_video(request.prompt, request.image_url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
