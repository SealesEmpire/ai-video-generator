"""Backend API tests using FastAPI TestClient and in-memory fake DB."""

import sys
from pathlib import Path

# Make sure the backend package is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

import pytest
from contextlib import asynccontextmanager
from io import BytesIO


# ---------------------------------------------------------------------------
# Fake in-memory MongoDB replacement
# ---------------------------------------------------------------------------

class FakeCollection:
    """Minimal in-memory MongoDB-like collection for testing."""

    def __init__(self):
        self._docs = []

    async def insert_one(self, doc):
        self._docs.append(dict(doc))

    async def find_one(self, query):
        for doc in self._docs:
            if all(doc.get(k) == v for k, v in query.items()):
                return dict(doc)
        return None

    async def update_one(self, query, update):
        for doc in self._docs:
            if all(doc.get(k) == v for k, v in query.items()):
                for k, v in update.get("$set", {}).items():
                    doc[k] = v
                return

    async def count_documents(self, query):
        if not query:
            return len(self._docs)
        return sum(
            1 for doc in self._docs
            if all(doc.get(k) == v for k, v in query.items())
        )

    def find(self):
        return FakeCursor(list(self._docs))

    async def create_index(self, *args, **kwargs):
        pass  # no-op


class FakeCursor:
    """Minimal async cursor supporting skip/limit/sort/to_list."""

    def __init__(self, docs):
        self._docs = docs

    def skip(self, n):
        self._docs = self._docs[n:]
        return self

    def limit(self, n):
        self._docs = self._docs[:n]
        return self

    def sort(self, key, direction=-1):
        return self

    async def to_list(self, length=None):
        return self._docs


class FakeDB:
    """Minimal fake MongoDB database."""

    def __init__(self):
        self.videos = FakeCollection()
        self.users = FakeCollection()

    def __getitem__(self, name):
        return getattr(self, name, FakeCollection())


class FakeMongoClient:
    """Fake Motor client that returns a FakeDB."""

    def __init__(self, *args, **kwargs):
        self._db = FakeDB()

    def __getitem__(self, name):
        return self._db

    def close(self):
        pass


# ---------------------------------------------------------------------------
# Fixture: patch Motor client so the lifespan uses fake DB
# ---------------------------------------------------------------------------

@pytest.fixture()
def client(monkeypatch):
    """Create a FastAPI TestClient that uses a fake in-memory database."""
    import motor.motor_asyncio
    monkeypatch.setattr(motor.motor_asyncio, "AsyncIOMotorClient", FakeMongoClient)

    # Re-import server so the lifespan picks up the patched client
    import importlib
    import server as server_mod
    importlib.reload(server_mod)

    from starlette.testclient import TestClient
    with TestClient(server_mod.app, raise_server_exceptions=False) as c:
        yield c


# ---------------------------------------------------------------------------
# Health Check (Rec #10)
# ---------------------------------------------------------------------------

class TestHealthCheck:
    def test_health_check(self, client):
        response = client.get("/api/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ai-video-generator"


# ---------------------------------------------------------------------------
# Styles Endpoint (Rec #19 – caching headers)
# ---------------------------------------------------------------------------

class TestStyles:
    def test_get_styles(self, client):
        response = client.get("/api/styles")
        assert response.status_code == 200
        data = response.json()
        assert "text_to_video_styles" in data
        assert "image_to_video_styles" in data
        assert len(data["text_to_video_styles"]) == 5
        assert len(data["image_to_video_styles"]) == 3

    def test_styles_cache_header(self, client):
        response = client.get("/api/styles")
        assert "cache-control" in response.headers
        assert "max-age" in response.headers["cache-control"]

    def test_style_structure(self, client):
        response = client.get("/api/styles")
        data = response.json()
        style = data["text_to_video_styles"][0]
        assert "id" in style
        assert "name" in style
        assert "description" in style


# ---------------------------------------------------------------------------
# Text-to-Video Generation
# ---------------------------------------------------------------------------

class TestTextToVideo:
    def test_generate_text_to_video(self, client):
        response = client.post("/api/generate-text-to-video", json={
            "prompt": "A dragon flying",
            "style": "realistic",
            "duration": 7,
            "nsfw_enabled": False,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["prompt"] == "A dragon flying"
        assert data["style"] == "realistic"
        assert data["duration"] == 7
        assert data["status"] == "generating"
        assert "id" in data

    def test_generate_text_to_video_validation(self, client):
        response = client.post("/api/generate-text-to-video", json={
            "prompt": "test",
            "style": "anime",
            "duration": 99,
        })
        assert response.status_code == 422

    def test_generate_text_to_video_missing_prompt(self, client):
        response = client.post("/api/generate-text-to-video", json={
            "style": "anime",
        })
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# Image-to-Video Generation (Rec #5 – file upload constraints)
# ---------------------------------------------------------------------------

class TestImageToVideo:
    def test_generate_image_to_video(self, client):
        image_data = BytesIO(b"\xff\xd8\xff\xe0" + b"\x00" * 100)
        response = client.post(
            "/api/generate-image-to-video",
            files={"file": ("test.jpg", image_data, "image/jpeg")},
            data={"style": "character_animation", "duration": "7", "nsfw_enabled": "false"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["style"] == "character_animation"
        assert data["status"] == "generating"

    def test_reject_non_image(self, client):
        response = client.post(
            "/api/generate-image-to-video",
            files={"file": ("test.txt", BytesIO(b"hello"), "text/plain")},
            data={"style": "character_animation"},
        )
        assert response.status_code == 400

    def test_reject_unsupported_extension(self, client):
        response = client.post(
            "/api/generate-image-to-video",
            files={"file": ("test.bmp", BytesIO(b"\x00" * 100), "image/bmp")},
            data={"style": "character_animation"},
        )
        assert response.status_code == 400

    def test_reject_oversized_file(self, client):
        # Create a file slightly over 50 MB
        big_data = BytesIO(b"\x00" * (50 * 1024 * 1024 + 1))
        response = client.post(
            "/api/generate-image-to-video",
            files={"file": ("big.jpg", big_data, "image/jpeg")},
            data={"style": "character_animation"},
        )
        assert response.status_code == 413


# ---------------------------------------------------------------------------
# Video Retrieval
# ---------------------------------------------------------------------------

class TestVideoRetrieval:
    def test_get_video_not_found(self, client):
        response = client.get("/api/video/nonexistent-id")
        assert response.status_code == 404

    def test_get_video_after_creation(self, client):
        resp = client.post("/api/generate-text-to-video", json={
            "prompt": "test prompt",
            "style": "anime",
            "duration": 5,
        })
        video_id = resp.json()["id"]
        response = client.get(f"/api/video/{video_id}")
        assert response.status_code == 200
        assert response.json()["id"] == video_id


# ---------------------------------------------------------------------------
# Gallery / Pagination (Rec #18)
# ---------------------------------------------------------------------------

class TestGallery:
    def test_empty_gallery(self, client):
        response = client.get("/api/videos")
        assert response.status_code == 200
        data = response.json()
        assert data["videos"] == []
        assert data["total_count"] == 0

    def test_gallery_with_video(self, client):
        client.post("/api/generate-text-to-video", json={
            "prompt": "gallery test",
            "style": "surreal",
            "duration": 6,
        })
        response = client.get("/api/videos")
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] >= 1

    def test_pagination_limit_capped(self, client):
        response = client.get("/api/videos?limit=999999")
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Authentication (Rec #3)
# ---------------------------------------------------------------------------

class TestAuth:
    def test_register(self, client):
        response = client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "securepassword123",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "id" in data

    def test_register_duplicate_email(self, client):
        client.post("/api/auth/register", json={
            "email": "dup@example.com",
            "password": "securepassword123",
        })
        response = client.post("/api/auth/register", json={
            "email": "dup@example.com",
            "password": "anotherpassword123",
        })
        assert response.status_code == 409

    def test_login_success(self, client):
        client.post("/api/auth/register", json={
            "email": "login@example.com",
            "password": "securepassword123",
        })
        response = client.post("/api/auth/login", json={
            "email": "login@example.com",
            "password": "securepassword123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        client.post("/api/auth/register", json={
            "email": "wrong@example.com",
            "password": "securepassword123",
        })
        response = client.post("/api/auth/login", json={
            "email": "wrong@example.com",
            "password": "badpassword123",
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post("/api/auth/login", json={
            "email": "nobody@example.com",
            "password": "whatever123",
        })
        assert response.status_code == 401

    def test_register_short_password(self, client):
        response = client.post("/api/auth/register", json={
            "email": "short@example.com",
            "password": "123",
        })
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# Error Response Format (Rec #11)
# ---------------------------------------------------------------------------

class TestErrorFormat:
    def test_404_returns_error_key(self, client):
        response = client.get("/api/video/does-not-exist")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
