# AI Video Generator

A full-stack web application that converts text prompts or image uploads into AI-generated videos. Built with React, FastAPI, and MongoDB.

## 🌐 Deployment Status & Access

> **Status:** The project is **not yet deployed** to a public URL. All deployment infrastructure (Dockerfiles, CI/CD, platform configs) is in place and ready to use.

### Quick Access — Run Locally with Docker

The fastest way to run the full application:

```bash
git clone https://github.com/SealesEmpire/ai-video-generator.git
cd ai-video-generator
docker compose up --build -d
```

Once running, open:

| Service   | URL                          |
|-----------|------------------------------|
| Frontend  | http://localhost:3000        |
| Backend API | http://localhost:8001      |
| API Docs (Swagger) | http://localhost:8001/docs |
| API Docs (ReDoc) | http://localhost:8001/redoc |

To stop: `docker compose down`

### Deploy to the Cloud

Ready-to-use configs are included for several platforms — see [DEPLOYMENT.md](DEPLOYMENT.md) for full instructions:

| Platform | Config File | What it deploys |
|----------|-------------|-----------------|
| **Docker** (any server) | `docker-compose.yml` | Full stack + MongoDB |
| **Render** | `render.yaml` | Backend + static frontend |
| **Vercel** | `vercel.json` | Frontend only |
| **Heroku / Railway** | `Procfile` | Backend only |
| **GitHub Actions** | `.github/workflows/deploy.yml` | CI/CD pipeline (targets commented — uncomment your provider) |

## 🚀 Features

- **Text-to-Video**: Generate videos from text prompts with multiple style options
- **Image-to-Video**: Upload images and transform them with animation styles
- **Video Gallery**: View and manage all generated videos
- **Mobile-First Design**: Responsive dark mode interface
- **Video Styles**: Realistic, Anime, Cartoon, Surreal, Talking Image, Character Animation, Movement Overlay, Talking Face
- **Duration Control**: Adjustable video length (5-10 seconds)
- **NSFW Content**: Premium feature with payment integration ready
- **Admin Override**: Full access for creators/admins

## 🏗️ Architecture

- **Frontend**: React 19 + Tailwind CSS
- **Backend**: FastAPI + Python
- **Database**: MongoDB
- **File Storage**: Local uploads directory
- **Authentication**: JWT-based (register / login endpoints)
- **Payments**: Stripe integration ready

## 📁 Project Structure

```
ai-video-generator/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── App.js           # Main application component
│   │   ├── App.test.js      # Frontend tests
│   │   ├── App.css          # Tailwind + custom styles
│   │   └── index.js         # React entry point
│   ├── public/              # Static assets
│   ├── package.json         # Frontend dependencies
│   ├── tailwind.config.js   # Tailwind configuration
│   └── .env.example         # Frontend environment template
├── backend/                 # FastAPI backend
│   ├── server.py           # Application entry-point / assembly
│   ├── config.py           # Environment configuration
│   ├── models.py           # Pydantic request/response models
│   ├── routes/             # API route handlers
│   │   ├── auth.py         # Registration & login
│   │   ├── health.py       # Health check
│   │   ├── styles.py       # Video styles
│   │   └── videos.py       # Video generation & gallery
│   ├── services/           # Business logic
│   │   ├── auth_service.py # JWT & password hashing
│   │   └── video_service.py# Video generation simulation
│   ├── api/                # External API integrations
│   │   └── api_runway.py   # RunwayML integration (WIP)
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Backend environment template
│   └── uploads/            # File upload directory
├── tests/                  # Test files
│   ├── conftest.py         # Test configuration
│   └── test_api.py         # Backend API tests (23 tests)
└── README.md              # This file
```

## 🛠️ Local Development Setup

### Prerequisites

- Node.js 16+ and npm/yarn
- Python 3.8+
- MongoDB (local or cloud)

### 1. Clone the Repository

```bash
git clone https://github.com/SealesEmpire/ai-video-generator.git
cd ai-video-generator
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration:
# MONGO_URL=mongodb://localhost:27017
# DB_NAME=ai_video_generator
# JWT_SECRET=your-secret-key
# STRIPE_SECRET_KEY=sk_test_...
# RUNWAYML_API_KEY=your-key
# STABILITY_API_KEY=your-key

# Start the backend server
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (in new terminal)
cd frontend

# Install dependencies
yarn install

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration:
# REACT_APP_BACKEND_URL=http://localhost:8001
# REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_test_...

# Start the frontend server
yarn start
```

### 4. Database Setup

The application will automatically create the required MongoDB collections:
- `videos` - Stores video generation data
- `users` - User authentication data (when implemented)
- `status_checks` - System health checks

## 🔧 Hosting Options

### Option 1: Replit

1. Create a new Replit project
2. Upload all project files
3. Set up the following environment variables in Replit:
   - `MONGO_URL`: Your MongoDB connection string
   - `DB_NAME`: Your database name
   - `REACT_APP_BACKEND_URL`: Your Replit backend URL
4. Install dependencies:
   ```bash
   # Backend
   cd backend && pip install -r requirements.txt
   
   # Frontend
   cd frontend && yarn install
   ```
5. Start both servers (Replit can run multiple processes)

### Option 2: Glitch

1. Import GitHub repo to Glitch
2. Set up environment variables in `.env` files
3. Glitch will automatically install dependencies and start the servers

### Option 3: Vercel (Frontend) + Railway/Heroku (Backend)

**Frontend (Vercel):**
1. Connect your GitHub repo to Vercel
2. Set build command: `cd frontend && yarn build`
3. Set build directory: `frontend/build`
4. Add environment variables in Vercel dashboard

**Backend (Railway/Heroku):**
1. Connect your GitHub repo
2. Set root directory to `backend`
3. Add environment variables
4. Deploy with auto-scaling

### Option 4: Docker

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 🎯 API Endpoints

### Video Generation
- `POST /api/generate-text-to-video` - Generate video from text
- `POST /api/generate-image-to-video` - Generate video from image
- `GET /api/video/{id}` - Get video by ID
- `GET /api/videos` - Get user's video gallery
- `GET /api/styles` - Get available video styles

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and receive a JWT

### Runway ML (Work-in-Progress)
- `POST /api/runway/generate` - Generate video via RunwayML (requires API key)

### System
- `GET /api/` - Health check

### Interactive API Documentation

FastAPI auto-generates interactive docs:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## 🔐 Environment Variables

### Backend (.env)
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=ai_video_generator
JWT_SECRET=your-super-secret-jwt-key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
RUNWAYML_API_KEY=your_runwayml_api_key
STABILITY_API_KEY=your_stability_api_key
PIKA_API_KEY=your_pika_api_key
ADMIN_EMAILS=admin@example.com,creator@example.com
```

### Frontend (.env)
```env
REACT_APP_BACKEND_URL=http://localhost:8001
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
```

## 🔮 Future Integrations (Ready to Implement)

### Video Generation APIs
- **RunwayML**: Placeholder integration exists in `backend/api/api_runway.py` with a `/api/runway/generate` endpoint. Requires a valid `RUNWAYML_API_KEY` in the environment. Currently returns a 503 when no key is configured.
- **Pika Labs**: High-quality video generation
- **Stability AI**: Video diffusion models

### Authentication & Payments
- **JWT Authentication**: User signup and login implemented; token-protected endpoints ready
- **Stripe Integration**: Premium subscriptions for NSFW content
- **Admin Controls**: Creator whitelist for unlimited access

### Additional Features
- **Video History**: Enhanced gallery with filters
- **Download System**: High-quality video exports
- **Social Sharing**: Direct sharing to social platforms
- **Batch Processing**: Multiple video generation
- **Custom Styles**: User-defined video styles

## 🧪 Testing

Run the test suite:
```bash
# Backend API tests (23 tests using FastAPI TestClient)
python -m pytest tests/ -v

# Frontend tests
cd frontend && yarn test
```

## 📱 Mobile Support

The application is fully responsive and works on:
- Mobile phones (iOS/Android)
- Tablets
- Desktop browsers
- Progressive Web App (PWA) ready

## 🔒 Security Features

- CORS restricted to configured origins (`ALLOWED_ORIGINS`)
- JWT authentication (register / login)
- File upload validation (type, size, extension)
- Rate limiting via slowapi
- Input sanitization
- HTTPS deployment ready

## 🎨 Customization

### Adding New Video Styles
1. Update `SAMPLE_VIDEOS` in `backend/server.py`
2. Add style definitions in `/api/styles` endpoint
3. Update frontend style selectors

### Modifying UI
- Tailwind classes in `frontend/src/App.js`
- Custom styles in `frontend/src/App.css`
- Responsive breakpoints in Tailwind config

## 📊 Monitoring

- Built-in health checks
- Error logging configured
- Performance monitoring ready
- Database connection monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions:
1. Check the GitHub issues
2. Review the setup documentation
3. Test with the provided examples
4. Contact the development team

## 🔄 Version History

- v1.0.0 - Initial release with stubbed video generation
- v1.1.0 - Security hardening, JWT auth, rate limiting, modular backend, test suite
- v1.2.0 - Real API integration (coming soon)
- v1.3.0 - Stripe payments (coming soon)

---

**Ready to generate amazing AI videos!** 🎬✨