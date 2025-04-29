from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .. import db, settings
from ..user.models import User

# Define OAuth2 password bearer scheme - Update to match the router endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Function to create access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token with expiration time.
    
    Args:
        data: Dict containing data to encode in the token
        expires_delta: Optional timedelta for custom expiration time
        
    Returns:
        JWT token as string
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    
    # Create JWT token
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Get current user from token
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(db.get_db)):
    """
    Verify the JWT token and get the current user.
    
    Args:
        token: JWT token from OAuth2 dependency
        db: Database session dependency
        
    Returns:
        User object if the token is valid
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Extract email from payload
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
            
        # Get user from database
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise credentials_exception
            
        return user
        
    except JWTError:
        raise credentials_exception 