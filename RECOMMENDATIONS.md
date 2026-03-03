# Recommendations for AI Video Generator

This document provides a prioritized list of recommendations for improving the AI Video Generator application across security, reliability, code quality, testing, performance, and documentation.

---

## 🔴 Critical: Security

### 1. Remove Exposed API Key from `.env.example`

**File:** `backend/.env.example`

The `RUNWAYML_API_KEY` value in `.env.example` appears to be a real API key. Example files should only contain clearly fake placeholder values.

```diff
- RUNWAYML_API_KEY=key_f6e0d186c26101a9492409c79d6d0e483984c5974e06eb12ff75b59aafd74271487738f04f670096818cdc66dbe5bf03670dd08c151b9350574c80e5bc13c8f3
+ RUNWAYML_API_KEY=your_runwayml_api_key_here
```

If this key is real, rotate it immediately as `.env.example` is committed to the repository and publicly visible.

### 2. Restrict CORS Origins

**File:** `backend/server.py`

The CORS middleware currently allows all origins (`allow_origins=["*"]`). In production this permits any website to make authenticated requests to the API.

```python
# Current (insecure)
allow_origins=["*"]

# Recommended
allowed_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Implement Authentication

The README mentions JWT-based authentication as "ready for implementation," but no endpoints are protected. Any user can generate videos, view all videos in the database, and upload files without identification. Implement:
- User registration and login endpoints
- JWT token issuance and validation
- Middleware to protect video generation and gallery endpoints

### 4. Add Rate Limiting

The `.env.example` defines `RATE_LIMIT_PER_MINUTE` and `RATE_LIMIT_PER_HOUR` but no rate limiting is implemented. Without it, the API is vulnerable to abuse. Consider using [`slowapi`](https://github.com/laurentS/slowapi) for FastAPI rate limiting.

### 5. Enforce File Upload Constraints

**File:** `backend/server.py`

The image upload endpoint only checks `content_type` but does not enforce:
- **Maximum file size**: Large uploads could exhaust server disk/memory.
- **Allowed file extensions**: The content type check alone is insufficient since it can be spoofed.
- **Filename sanitization**: The filename is derived from user input (`file.filename.split('.')[-1]`), which could be manipulated.

```python
from pathlib import PurePath

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}

# Validate extension safely
file_extension = PurePath(file.filename).suffix.lstrip('.').lower()
if file_extension not in ALLOWED_EXTENSIONS:
    raise HTTPException(status_code=400, detail="Unsupported file type")

# Validate file size
contents = await file.read()
if len(contents) > MAX_FILE_SIZE:
    raise HTTPException(status_code=413, detail="File too large")
await file.seek(0)
```

---

## 🟠 High: Critical Bugs

### 6. Fix Broken Import in `server.py`

**File:** `backend/server.py` (line 16)

```python
from api_runway import router as runway_router
```

`backend/api/api_runway.py` defines a `generate_video` function but does **not** export a `router` object. This import will raise an `ImportError` at startup, preventing the application from running. Either:
- Add an `APIRouter` to `api_runway.py`, or
- Remove the import and `app.include_router(runway_router, ...)` line until the Runway integration is complete.

### 7. Replace Deprecated `datetime.utcnow()`

**File:** `backend/server.py` (lines 152, 189)

`datetime.utcnow()` is deprecated since Python 3.12. Use timezone-aware datetimes instead:

```python
from datetime import datetime, timezone

# Replace
datetime.utcnow()
# With
datetime.now(timezone.utc)
```

### 8. Handle Missing Environment Variables Gracefully

**File:** `backend/server.py` (lines 22–24)

```python
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]
```

If `MONGO_URL` or `DB_NAME` are not set, the application crashes with a `KeyError` instead of a descriptive error. Use `os.environ.get()` with defaults or raise a clear startup error.

---

## 🟡 Medium: Code Quality

### 9. Store Background Task References

**File:** `backend/server.py` (lines 158, 197)

`asyncio.create_task()` is called without storing the returned task reference. If the background task raises an exception, it will be silently ignored. Store the reference or use FastAPI's `BackgroundTasks`:

```python
from fastapi import BackgroundTasks

@api_router.post("/generate-text-to-video", response_model=VideoResponse)
async def generate_text_to_video(request: VideoGenerationRequest, background_tasks: BackgroundTasks):
    # ...
    background_tasks.add_task(simulate_video_generation, video_id, request.style)
```

### 10. Add a Health Check Endpoint

The README lists `GET /api/` as a health check, but no such route is defined in `server.py`. Add one:

```python
@api_router.get("/")
async def health_check():
    return {"status": "healthy", "service": "ai-video-generator"}
```

### 11. Use Consistent Error Response Format

API errors currently return mixed formats (FastAPI's default `HTTPException` detail strings, raw exceptions, etc.). Define a standard error model:

```python
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )
```

### 12. Replace Deprecated `@app.on_event("shutdown")`

**File:** `backend/server.py` (line 256)

The `@app.on_event()` decorator is deprecated in recent FastAPI versions. Use the `lifespan` context manager instead:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    client.close()

app = FastAPI(lifespan=lifespan)
```

### 13. Separate Backend Code into Modules

All backend logic lives in a single `server.py` file (~260 lines). As the application grows, split into:
- `models.py` – Pydantic models
- `routes/videos.py` – Video generation endpoints
- `routes/styles.py` – Styles endpoint
- `services/video_service.py` – Video generation logic
- `config.py` – Environment and app configuration

---

## 🔵 Medium: Testing

### 14. Add Unit Tests Using FastAPI `TestClient`

**File:** `backend_test.py`

The existing test suite sends HTTP requests to a running server (`requests.get(...)`) and reads the backend URL from `/app/frontend/.env`. This makes tests:
- Impossible to run without a live server and MongoDB
- Coupled to a specific deployment environment

Use FastAPI's `TestClient` and mock the database for isolated, repeatable tests:

```python
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from server import app

client = TestClient(app)

def test_get_styles():
    response = client.get("/api/styles")
    assert response.status_code == 200
    data = response.json()
    assert "text_to_video_styles" in data
```

### 15. Add Frontend Tests

The `frontend/` directory has no test files. Add tests for:
- Component rendering (Text-to-Video and Image-to-Video tabs)
- Form validation (empty prompt, no image)
- API call behavior (mocked with tools like `msw` or `jest.mock`)
- Gallery rendering with mock data

### 16. Populate the `tests/` Directory

`tests/__init__.py` is empty. Move or create properly organized test modules here rather than having `backend_test.py` at the project root.

---

## 🟢 Low: Performance

### 17. Add MongoDB Indexes

**File:** `backend/server.py`

The `videos` collection is queried by `id` and sorted by `created_at`, but no indexes are defined. Add indexes during the application lifespan (see recommendation #12 for the `lifespan` pattern):

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create indexes
    await db.videos.create_index("id", unique=True)
    await db.videos.create_index([("created_at", -1)])
    yield
    # Shutdown
    client.close()

app = FastAPI(lifespan=lifespan)
```

### 18. Enforce Pagination Limits

**File:** `backend/server.py` (line 211)

The `get_user_videos` endpoint accepts an arbitrary `limit` parameter with no upper bound. A request for `?limit=1000000` could strain the database. Cap it:

```python
@api_router.get("/videos", response_model=UserGallery)
async def get_user_videos(limit: int = 20, offset: int = 0):
    limit = min(limit, 100)  # Cap at 100
    # ...
```

### 19. Cache Static Responses

The `/api/styles` endpoint returns hardcoded data but hits the Python runtime on every request. For a production deployment, add response caching headers or use an in-memory cache.

---

## ⚪ Low: Dependencies & Project Hygiene

### 20. Consolidate Requirements Files

There are two `requirements.txt` files with different contents:
- `requirements.txt` (root) – 26 dependencies including `pandas`, `numpy`, `boto3`
- `backend/requirements.txt` – 6 lightweight dependencies

The root file includes heavy packages (`pandas`, `numpy`, `boto3`, `jq`) that are not used anywhere in the codebase. Either:
- Remove the root `requirements.txt` and use only `backend/requirements.txt`, or
- Consolidate into one file containing only what is actually imported.

### 21. Clarify Purpose of `plugin_requirements.txt`

This file is empty. Either remove it or document its intended use.

### 22. Pin Dependency Versions Consistently

`backend/requirements.txt` mixes pinned (`fastapi==0.110.1`) and unpinned (`requests>=2.31.0`) versions. For reproducible builds, pin all dependencies or use a lockfile tool like `pip-compile`.

---

## 📝 Low: Documentation

### 23. Replace Placeholder Repository URLs

Multiple files (`README.md`, `EXPORT_INSTRUCTIONS.md`, `SETUP.md`, `DEPLOYMENT.md`, `package.json`) reference `yourusername/ai-video-generator`. Update these to the actual repository owner/name.

### 24. Advertise Auto-Generated API Docs

FastAPI automatically generates interactive API documentation at `/docs` (Swagger UI) and `/redoc`. Mention these in `README.md` and `SETUP.md` so users can explore the API interactively.

### 25. Document the Runway API Integration Status

`backend/api/api_runway.py` exists but is not properly wired into the application (see recommendation #6). Document whether this is a work-in-progress or a placeholder so contributors know its current status.

---

## Summary Table

| # | Category | Priority | Recommendation | Status |
|---|----------|----------|----------------|--------|
| 1 | Security | 🔴 Critical | Remove exposed API key from `.env.example` | ✅ Done |
| 2 | Security | 🔴 Critical | Restrict CORS origins | ✅ Done |
| 3 | Security | 🔴 Critical | Implement authentication | ✅ Done |
| 4 | Security | 🔴 Critical | Add rate limiting | ✅ Done |
| 5 | Security | 🔴 Critical | Enforce file upload constraints | ✅ Done |
| 6 | Bug | 🟠 High | Fix broken import in `server.py` | ✅ Done |
| 7 | Bug | 🟠 High | Replace deprecated `datetime.utcnow()` | ✅ Done |
| 8 | Bug | 🟠 High | Handle missing environment variables | ✅ Done |
| 9 | Code Quality | 🟡 Medium | Store background task references | ✅ Done |
| 10 | Code Quality | 🟡 Medium | Add a health check endpoint | ✅ Done |
| 11 | Code Quality | 🟡 Medium | Use consistent error response format | ✅ Done |
| 12 | Code Quality | 🟡 Medium | Replace deprecated `@app.on_event()` | ✅ Done |
| 13 | Code Quality | 🟡 Medium | Separate backend code into modules | ✅ Done |
| 14 | Testing | 🔵 Medium | Add unit tests using `TestClient` | ✅ Done |
| 15 | Testing | 🔵 Medium | Add frontend tests | ✅ Done |
| 16 | Testing | 🔵 Medium | Populate the `tests/` directory | ✅ Done |
| 17 | Performance | 🟢 Low | Add MongoDB indexes | ✅ Done |
| 18 | Performance | 🟢 Low | Enforce pagination limits | ✅ Done |
| 19 | Performance | 🟢 Low | Cache static responses | ✅ Done |
| 20 | Hygiene | ⚪ Low | Consolidate requirements files | ✅ Done |
| 21 | Hygiene | ⚪ Low | Clarify `plugin_requirements.txt` | ✅ Done |
| 22 | Hygiene | ⚪ Low | Pin dependency versions consistently | ✅ Done |
| 23 | Documentation | 📝 Low | Replace placeholder repository URLs | ✅ Done |
| 24 | Documentation | 📝 Low | Advertise auto-generated API docs | ✅ Done |
| 25 | Documentation | 📝 Low | Document Runway API integration status | ✅ Done |
