"""AI Video Generator – FastAPI application entry-point.

This module wires together configuration, middleware, routers, and the
database connection.  Business logic lives in *services/* and route
handlers live in *routes/*.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import MONGO_URL, DB_NAME, ALLOWED_ORIGINS, RATE_LIMIT_PER_MINUTE, logger
from routes import health, styles, videos, auth
from api.api_runway import router as runway_router

# ---------------------------------------------------------------------------
# Rate limiter (Rec #4)
# ---------------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address, default_limits=[f"{RATE_LIMIT_PER_MINUTE}/minute"])

# ---------------------------------------------------------------------------
# Lifespan – replaces deprecated @app.on_event (Rec #12, #17)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.mongo_client = AsyncIOMotorClient(MONGO_URL)
    db = app.state.mongo_client[DB_NAME]

    # Inject db into route modules
    videos._set_db(db)
    auth._set_db(db)

    # Create indexes (Rec #17)
    await db.videos.create_index("id", unique=True)
    await db.videos.create_index([("created_at", -1)])
    await db.users.create_index("email", unique=True)

    logger.info("Application started – database indexes ensured")
    yield

    # Shutdown
    app.state.mongo_client.close()
    logger.info("Application shut down – database connection closed")


# ---------------------------------------------------------------------------
# App assembly
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AI Video Generator",
    description="Generate AI videos from text prompts or images",
    version="1.1.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- Routers ---
api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(styles.router)
api_router.include_router(videos.router)
api_router.include_router(auth.router)

app.include_router(api_router)
app.include_router(runway_router, prefix="/api/runway")

# --- CORS (Rec #2) ---
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Consistent error responses (Rec #11) ---
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )
