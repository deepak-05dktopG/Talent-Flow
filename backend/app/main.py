"""
main.py - Application Entry Point
===================================
This is the STARTING POINT of the entire TalentFlow backend server.
When you run the server, this file is executed first.

It does three main things:
1. Creates the FastAPI application (the web server)
2. Sets up security rules so the frontend can talk to the backend
3. Connects all the different feature modules (login, jobs, applications, etc.)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import config
from app.routers import auth, jobs, applications, interviews, analytics

# Print a status report showing which services are configured
config.print_service_statuses()

# ──────────────────────────────────────────────
# CREATE THE WEB SERVER
# ──────────────────────────────────────────────
# This creates the main FastAPI application object.
# 'docs_url' and 'redoc_url' provide automatic API documentation pages
# that developers can visit in their browser to test endpoints.
app = FastAPI(
    title=config.APP_NAME,
    description="AI-Powered Recruitment Assistant for HR Teams",
    version="1.0.0",
    docs_url="/api/docs",       # Visit http://localhost:8000/api/docs to see interactive API docs
    redoc_url="/api/redoc"      # Visit http://localhost:8000/api/redoc for alternative docs
)
 
# ──────────────────────────────────────────────
# CORS (Cross-Origin Resource Sharing)
# ──────────────────────────────────────────────
# CORS is a security feature that controls which websites can access our API.
# We allow requests from our React frontend (localhost:3000) and any other origin.
# Without this, the browser would block the frontend from talking to the backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,     # Allow cookies and auth tokens
    allow_methods=["*"],        # Allow all HTTP methods (GET, POST, PATCH, DELETE)
    allow_headers=["*"],        # Allow all headers (including Authorization)
)

# ──────────────────────────────────────────────
# REGISTER FEATURE MODULES (Routers)
# ──────────────────────────────────────────────
# Each router handles a specific feature of the application.
# They are like departments in a company — each one manages its own area.
app.include_router(auth.router)           # Handles: Login, Registration, User accounts
app.include_router(jobs.router)           # Handles: Creating, editing, listing job postings
app.include_router(applications.router)   # Handles: Candidate applications, resume parsing, status updates
app.include_router(interviews.router)     # Handles: Scheduling interviews, sending invites
app.include_router(analytics.router)      # Handles: Dashboard statistics and charts

# ──────────────────────────────────────────────
# BASIC HEALTH CHECK ENDPOINTS
# ──────────────────────────────────────────────

@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint — returns basic info about the application.
    Useful for checking if the server is running.
    Visit: http://localhost:8000/
    """
    return {
        "app": config.APP_NAME,
        "version": "1.0.0",
        "docs": "/api/docs",
        "status": "running"
    }

@app.get("/health", tags=["root"])
async def health():
    """
    Health check endpoint — returns a simple "ok" response.
    Used by monitoring tools to verify the server is alive.
    Visit: http://localhost:8000/health
    """
    return {"status": "ok"}
