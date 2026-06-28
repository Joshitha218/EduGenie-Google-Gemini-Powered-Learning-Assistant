import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import logging

from backend.app.config import settings
from backend.app.database import engine, Base
from backend.app.routes import auth_router, modules_router, history_router, views_router
from backend.app.services.lamini import start_background_load

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="EduGenie",
    description="Google Gemini Powered AI Learning Assistant",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)
    os.makedirs(os.path.join(static_dir, "css"), exist_ok=True)
    os.makedirs(os.path.join(static_dir, "js"), exist_ok=True)
    os.makedirs(os.path.join(static_dir, "images"), exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include Routers
app.include_router(views_router)
app.include_router(auth_router)
app.include_router(modules_router)
app.include_router(history_router)

@app.on_event("startup")
def on_startup():
    logger.info("Initializing EduGenie Application...")
    
    # 1. Create database tables if they do not exist
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        
    # 2. Pre-load LaMini model in background thread (CPU execution)
    try:
        start_background_load()
    except Exception as e:
        logger.error(f"Failed to trigger LaMini model pre-load: {str(e)}")

# Global Exception Handlers for JSON APIs
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception at {request.url.path}: {str(exc)}", exc_info=True)
    # Check if request is an API request or view request
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred. Please try again later."}
        )
    # Return raw text or default for view pages (handled gracefully by frontend JS in most actions)
    raise exc
