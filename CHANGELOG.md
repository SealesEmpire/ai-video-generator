# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-06-22

### Added

#### Backend (`backend/`)
- `server.py` — FastAPI application with endpoints for text-to-video and image-to-video generation, video gallery retrieval, and available style listing; includes MongoDB integration via Motor and background task simulation for video generation
- `api/api_runway.py` — RunwayML API router stub for future real video generation integration
- `requirements.txt` — Python dependencies (FastAPI, Motor, Pydantic, python-dotenv, etc.)
- `.env.example` — Template for backend environment variables (`MONGO_URL`, `DB_NAME`, `JWT_SECRET`, `STRIPE_SECRET_KEY`, `RUNWAYML_API_KEY`, `STABILITY_API_KEY`, `PIKA_API_KEY`, `ADMIN_EMAILS`)
- `uploads/` — Directory for storing uploaded image files

#### Frontend (`frontend/`)
- `src/App.js` — Main React component with text-to-video form, image-to-video upload, video gallery, and mobile-first dark mode UI
- `src/App.css` — Tailwind CSS and custom styles for the application
- `src/index.js` — React entry point
- `public/index.html` — HTML shell with Tailwind CDN and meta tags
- `package.json` — Frontend dependencies (React 19, Tailwind CSS, Axios, etc.)
- `tailwind.config.js` — Tailwind CSS configuration
- `postcss.config.js` — PostCSS configuration
- `.env.example` — Template for frontend environment variables (`REACT_APP_BACKEND_URL`, `REACT_APP_STRIPE_PUBLISHABLE_KEY`)

#### Tests
- `backend_test.py` — Backend API integration tests covering health checks, style listing, text-to-video, image-to-video, video retrieval, and gallery endpoints
- `tests/__init__.py` — Python test package marker

#### Documentation
- `README.md` — Project overview, architecture, local development setup, hosting options (Replit, Glitch, Vercel, Railway/Heroku, Docker), API endpoints, environment variables, and version history
- `SETUP.md` — Detailed setup and configuration guide
- `DEPLOYMENT.md` — Deployment instructions for multiple hosting platforms
- `EXPORT_INSTRUCTIONS.md` — Instructions for exporting and migrating the project
- `LICENSE` — MIT License

#### Configuration
- `.gitignore` — Git ignore rules for Node modules, Python cache, environment files, and build artifacts
- `.gitconfig` — Git configuration
- `package.json` — Root-level package configuration and scripts
- `plugin_requirements.txt` — Plugin/tool dependencies
- `requirements.txt` — Top-level Python requirements
- `yarn.lock` — Yarn lockfile for root dependencies
- `.emergent/emergent.yml` — Emergent platform configuration
