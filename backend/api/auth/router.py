from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional, Dict
from pydantic import BaseModel, ConfigDict, ValidationError, EmailStr
import logging
import re
from slowapi import Limiter
from slowapi.util import get_remote_address

from api.database.database import get_db
from api.models.database import User, AuditLog
from api.models.user import UserCreate, UserLogin, UserResponse, Token, TokenData
from config.settings import settings

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

class TokenResponse(BaseModel):
    """Response model for token responses"""
    user: UserResponse
    token: str
    token_type: str = "bearer"
    expires_in: int

    model_config = ConfigDict(from_attributes=True)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Password validation regex
PASSWORD_REGEX = re.compile(r'.{6,}$')  # Just require minimum 6 characters for now

def validate_password(password: str) -> bool:
    """Validate password strength."""
    return bool(PASSWORD_REGEX.match(password))

def validate_email(email: str) -> bool:
    """Validate email format."""
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    """
    logger.debug("Verifying password")
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        logger.debug(f"Password verification result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}")
        return False

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user by email and password.
    """
    logger.debug(f"Attempting to authenticate user: {email}")
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        logger.warning(f"User not found: {email}")
        return None
    
    if not verify_password(password, user.hashed_password):
        logger.warning(f"Invalid password for user: {email}")
        return None
    
    logger.info(f"User authenticated successfully: {email}")
    return user

def get_password_hash(password: str) -> str:
    """
    Hash a password for storing.
    """
    logger.debug("Hashing password")
    try:
        hashed = pwd_context.hash(password)
        logger.debug("Password hashed successfully")
        return hashed
    except Exception as e:
        logger.error(f"Error hashing password: {str(e)}")
        raise

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    try:
        user = db.query(User).filter(User.email == token_data.email).first()
        if user is None:
            raise credentials_exception
        return user
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise credentials_exception

@router.post("/register", response_model=TokenResponse)
@limiter.limit("5/minute")
async def register(
    request: Request,
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    """
    # Log the raw request body
    body = await request.body()
    logger.info(f"Raw request body: {body}")
    logger.info(f"Content-Type header: {request.headers.get('content-type')}")
    logger.info(f"Parsed user_data: {user_data}")
    logger.info(f"Attempting to register user: {user_data.email}")
    
    try:
        # Validate email
        if not validate_email(user_data.email):
            logger.warning(f"Invalid email format: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        # Validate password
        if not validate_password(user_data.password):
            logger.warning("Invalid password format")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            logger.warning(f"User already exists: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        logger.info("Creating new user...")
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=True
        )
        
        db.add(db_user)
        db.flush()  # Flush to get the user ID
        
        # Create single audit log
        audit_log = AuditLog(
            user_id=db_user.id,
            action_type="register",
            resource_type="user",
            resource_id=db_user.id,
            meta_data={
                "ip_address": request.client.host if request.client else None,
                "details": f"User registered: {db_user.email}"
            }
        )
        db.add(audit_log)
        
        # Commit both user and audit log in a single transaction
        db.commit()
        logger.info(f"User created successfully: {db_user.id}")
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_data.email},
            expires_delta=access_token_expires
        )
        
        return TokenResponse(
            user=UserResponse.from_orm(db_user),
            token=access_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except Exception as e:
        logger.error(f"Error in registration: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    try:
        # Use email as username since that's what we're using for authentication
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        # Create single audit log
        audit_log = AuditLog(
            user_id=user.id,
            action_type="login",
            resource_type="user",
            resource_id=user.id,
            meta_data={
                "ip_address": request.client.host if request.client else None,
                "details": f"User logged in: {user.email}"
            }
        )
        db.add(audit_log)
        db.commit()
        
        return TokenResponse(
            user=UserResponse.from_orm(user),
            token=access_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout the current user.
    """
    try:
        # Create single audit log
        audit_log = AuditLog(
            user_id=current_user.id,
            action_type="logout",
            resource_type="user",
            resource_id=current_user.id,
            meta_data={
                "ip_address": request.client.host if request.client else None,
                "details": f"User logged out: {current_user.email}"
            }
        )
        db.add(audit_log)
        db.commit()
        
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during logout"
        )

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user information.
    """
    return UserResponse.from_orm(current_user) 