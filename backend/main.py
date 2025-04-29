from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
import os
import logging
from logging.handlers import RotatingFileHandler

from api.database.database import get_db, engine, SessionLocal
from api.models.database import Base, User as UserModel
from api.models.schemas import User
from api.routes import api_router
from api.auth.router import router as auth_router, get_current_user, get_password_hash, create_access_token
from config.settings import settings

# Set up logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create a file handler
file_handler = RotatingFileHandler(
    os.path.join(log_dir, 'app.log'),
    maxBytes=1024*1024,  # 1MB
    backupCount=5
)
file_handler.setLevel(logging.DEBUG)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Check if tables exist, create if they don't
try:
    logger.info("Checking database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified successfully")
except Exception as e:
    logger.error(f"Error initializing database: {str(e)}")
    raise

# Determine if we're in development or production
is_development = os.getenv("ENVIRONMENT", "development") == "development"

app = FastAPI(
    title="EchosysAI API",
    description="API for EchosysAI platform - Trace Analysis and Issue Management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS - MUST be before any routes
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Add CORS middleware with explicit configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
    expose_headers=["Content-Length", "X-Total-Count"],
    max_age=3600,
)

# Add database session middleware
@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = None
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Error in request: {str(e)}")
        raise
    finally:
        # Ensure the session is closed
        db = request.state.db if hasattr(request.state, 'db') else None
        if db:
            db.close()
    return response

# Include the auth router
app.include_router(auth_router)

# Include the main API router
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Welcome to EchosysAI API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    # In development, use HTTP. In production, use HTTPS
    ssl_keyfile = os.getenv("SSL_KEYFILE")
    ssl_certfile = os.getenv("SSL_CERTFILE")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=is_development,
        ssl_keyfile=ssl_keyfile if not is_development else None,
        ssl_certfile=ssl_certfile if not is_development else None
    ) 