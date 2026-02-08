# Build and Run Instructions

## Quick Start

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) (v20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+)

### Build and Run

```bash
# Build both services
docker-compose build

# Start both services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Services

### Frontend
- **URL**: http://localhost:3000
- **Technology**: React + Vite + TypeScript
- **Port**: 3000

### Backend
- **URL**: http://localhost:5000
- **Technology**: Python FastAPI
- **Port**: 5000
- **API Docs**: http://localhost:5000/docs (Swagger UI)

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Frontend (Port 3000)                │
│              React + Vite + TypeScript               │
│                   (Nginx Server)                     │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ HTTP/WebSocket
                  │ Via Docker Network
                  ▼
┌─────────────────────────────────────────────────────┐
│                  Backend (Port 5000)                 │
│              Python FastAPI + Uvicorn                │
│                  SQLAlchemy ORM                      │
└─────────────────────────────────────────────────────┘
```

## Key Features

### Frontend Dockerfile
- **Multi-stage build** for optimized image size
- Node.js 18 Alpine for building
- Nginx Alpine for serving
- Static asset caching (30 days)
- Gzip compression enabled
- Client-side routing support (SPA)
- API proxy to backend via `/api` endpoint

### Backend Dockerfile
- **Python 3.11 Alpine** for minimal footprint
- System dependencies for compiled packages (opencv-python, mediapipe)
- Uvicorn ASGI server
- Health check via FastAPI `/docs` endpoint
- Environment-based configuration

### Docker Compose
- **Service networking** via `project1-network`
- **Service discovery** - frontend can reach backend via `backend` hostname
- **Persistent volumes** for backend data (`backend-data`)
- **Health checks** for both services
- **Restart policy** - automatic restart unless manually stopped
- **Dependency management** - frontend waits for backend readiness

## Environment Variables

### Backend
- `PYTHONUNBUFFERED=1` - Real-time Python output
- `DATABASE_URL=sqlite:///./data/project1.db` - SQLite database location

### Frontend
- `VITE_API_URL=http://backend:5000` - Backend API URL for container environment

## Development

### Local Development (without Docker)

Frontend:
```bash
cd frontend
npm install
npm run dev
```

Backend:
```bash
cd backend
python -m venv p1_env
source p1_env/bin/activate  # On Windows: p1_env\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 5000
```

### Production Deployment Tips

1. **CORS Settings**: Update the allowed origins in `backend/main.py` for production domains
2. **Environment Variables**: Use `.env` files instead of hardcoding values
3. **Database**: Replace SQLite with PostgreSQL/MySQL for production
4. **SSL/TLS**: Add Let's Encrypt certificates and HTTPS to nginx.conf
5. **Registry**: Push images to Docker Hub or your private registry

Example production CORS:
```python
origins = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
```

## Troubleshooting

### Frontend can't reach backend
- Check if backend container is running: `docker-compose ps`
- Verify they're on the same network: `docker network inspect project1-network`
- Check backend logs: `docker-compose logs backend`

### Port already in use
```bash
# Find what's using the port
lsof -i :3000  # Frontend
lsof -i :5000  # Backend

# Or change ports in docker-compose.yml
```

### Rebuild without cache
```bash
docker-compose build --no-cache
```

### Remove all containers and volumes
```bash
docker-compose down -v
```
