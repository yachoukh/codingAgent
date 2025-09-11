"""Authentication utilities for FastAPI app."""

import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select

from .models import User, engine

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security scheme for authorization header
security = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user_by_username(username: str) -> Optional[User]:
    """Get user by username from database."""
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        return user


def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email from database."""
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        return user


def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate user with username and password."""
    user = get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_current_user_from_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[User]:
    """Get current user from JWT token in Authorization header."""
    if not credentials:
        return None
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    
    user = get_user_by_username(username)
    return user


def get_current_user_from_session(request: Request) -> Optional[User]:
    """Get current user from session cookie."""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    
    with Session(engine) as session:
        user = session.get(User, user_id)
        return user


def get_current_user(request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[User]:
    """Get current user from session or token."""
    # Try session first
    user = get_current_user_from_session(request)
    if user:
        return user
    
    # Fall back to token
    return get_current_user_from_token(credentials)


def require_authentication(request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> User:
    """Require user to be authenticated."""
    user = get_current_user(request, credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user