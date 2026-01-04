Project1 — Frontend + FastAPI backend (local dev)

Quick start (cross-platform)

Prerequisites
- Node.js 18+ and npm
- Python 3.10+ and pip

Install everything (single command):

```bash
# from repo root
npm run install:all
```

Run frontend + backend together:

```bash
# from repo root
npm start
```

This runs the backend at http://localhost:8000 and the frontend dev server (Vite) at http://localhost:3000.

Configuration
- Frontend Vite env: `frontend/.env` or `frontend/.env.local`.
  - `VITE_API_BASE_URL` (e.g. http://localhost:8000)
  - `VITE_WS_URL` optional full websocket URL (e.g. ws://localhost:8000/ws/posture)

API endpoints
- Auth: POST /auth/register, POST /auth/login
- WebSocket posture stream: ws://localhost:8000/ws/posture

Notes
- Backend requirements are in `backend/requirements.txt`. The root `npm start` uses `concurrently` to run both services.
- If you prefer to run services separately:

Backend only:
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Frontend only:
```bash
cd frontend
npm install
npm start
```
