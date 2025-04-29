from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
import os
import logging

from api.database.database import get_db, engine, SessionLocal
from api.models.database import Base, User as UserModel
from api.models.schemas import User
from api.routes import api_router
from api.auth.router import get_current_user, get_password_hash, create_access_token
from config.settings import settings

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Check if tables exist, create if they don't
try:
    logger.info("Checking database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified successfully")
    
    # Create a hardcoded test user if it doesn't exist
    db = SessionLocal()
    try:
        test_user = db.query(UserModel).filter(UserModel.email == "amulya@example.com").first()
        if not test_user:
            test_user = UserModel(
                email="amulya@example.com",
                hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password is "password"
                full_name="Amulya Test",
                is_active=True
            )
            db.add(test_user)
            db.commit()
            logger.info("Test user created successfully with email: amulya@example.com")
        else:
            logger.info("Test user already exists")
        
        # Generate and log the token
        access_token = create_access_token(data={"sub": "amulya@example.com"})
        logger.info(f"Generated access token: {access_token}")
        
    except Exception as e:
        logger.error(f"Error creating test user: {str(e)}")
        db.rollback()
    finally:
        db.close()
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

# Include routers
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to EchosysAI API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/me", response_model=User)
async def read_users_me(
    current_user: UserModel = Depends(get_current_user)
):
    return current_user

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