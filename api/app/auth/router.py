from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import settings
from app.db import get_db
from app.user.models import User
from app.auth.schema import Token, TokenData
from app.auth.jwt import get_current_user, create_access_token

# Router definition
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)


async def authenticate_user(email: str, password: str, db: Session = None) -> Optional[User]:
    """
    Authenticates a user by checking their email and password.
    
    Parameters
    ----------
    email : str
        User's email.
    password : str
        User's plain text password.
    db : Session, optional
        Database session.
        
    Returns
    -------
    User or None
        The authenticated user if credentials are valid, None otherwise.
    """
    if db is None:
        # Get a new database session if one wasn't provided
        db_generator = get_db()
        db = next(db_generator)
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    
    if not user.verify_password(password):
        return None
    
    return user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Endpoint to authenticate a user and get an access token.
    
    Parameters
    ----------
    form_data : OAuth2PasswordRequestForm
        Form containing username (email) and password.
    db : Session
        Database session.
        
    Returns
    -------
    dict
        Access token and token type.
        
    Raises
    ------
    HTTPException
        If the credentials are invalid.
    """
    user = await authenticate_user(form_data.username, form_data.password, db)
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
    
    return {"access_token": access_token, "token_type": "bearer"} 