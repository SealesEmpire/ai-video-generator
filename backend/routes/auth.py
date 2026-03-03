"""Authentication endpoints: register and login."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from models import UserRegisterRequest, UserLoginRequest, UserResponse, TokenResponse
from services.auth_service import hash_password, verify_password, create_access_token

router = APIRouter()

# The database handle is injected by server.py after startup.
db = None  # type: ignore[assignment]


def _set_db(database):
    """Called by the application entry-point to inject the DB handle."""
    global db
    db = database


@router.post("/auth/register", response_model=UserResponse, status_code=201)
async def register(request: UserRegisterRequest):
    """Register a new user account."""
    existing = await db.users.find_one({"email": request.email})
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user_id = str(uuid.uuid4())
    user_doc = {
        "id": user_id,
        "email": request.email,
        "password_hash": hash_password(request.password),
        "created_at": datetime.now(timezone.utc),
    }
    await db.users.insert_one(user_doc)

    return UserResponse(id=user_id, email=request.email, created_at=user_doc["created_at"])


@router.post("/auth/login", response_model=TokenResponse)
async def login(request: UserLoginRequest):
    """Authenticate a user and return a JWT."""
    user = await db.users.find_one({"email": request.email})
    if not user or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user["id"], user["email"])
    return TokenResponse(access_token=token)
