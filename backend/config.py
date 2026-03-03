"""Application configuration loaded from environment variables."""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'ai_video_generator')

# JWT Authentication
JWT_SECRET = os.environ.get('JWT_SECRET', 'change-this-in-production')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 60 * 24  # 24 hours

# CORS
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
    if origin.strip()
]

# Rate Limiting
RATE_LIMIT_PER_MINUTE = os.environ.get('RATE_LIMIT_PER_MINUTE', '10')

# File Upload
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}

# Uploads directory
UPLOADS_DIR = ROOT_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

# Admin
ADMIN_EMAILS = [
    e.strip()
    for e in os.environ.get('ADMIN_EMAILS', '').split(',')
    if e.strip()
]

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
