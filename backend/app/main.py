from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import config
from app.routers import auth, jobs, applications, interviews, analytics

config.print_service_statuses()

app = FastAPI(
    title=config.APP_NAME,
    description="AI-Powered Recruitment Assistant for HR Teams",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)
 
# CORS – allow React dev server and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(applications.router)
app.include_router(interviews.router)
app.include_router(analytics.router)


@app.get("/", tags=["root"])
async def root():
    return {
        "app": config.APP_NAME,
        "version": "1.0.0",
        "docs": "/api/docs",
        "status": "running"
    }

@app.get("/health", tags=["root"])
async def health():
    return {"status": "ok"}
