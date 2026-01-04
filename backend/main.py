from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from authentication.database import init_db
from authentication.routes import router as auth_router
from posture.websocket import router as posture_router

app = FastAPI(title="Project1 API")

# CORS settings: allow the frontend dev server and localhost for local testing
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "*"  # Allow all origins for testing purposes; restrict in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include posture websocket router and other routers
app.include_router(posture_router)

# Create tables on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Include auth routes
app.include_router(auth_router)

# Recommended run command (install uvicorn[standard] in your Python env):
# python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload