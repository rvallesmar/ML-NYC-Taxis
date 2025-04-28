from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_user
from app.db import get_db
from app.user import schema
from app.user.models import User

# Router definition
router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schema.User, status_code=status.HTTP_201_CREATED)
def create_user(
    user: schema.UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new user.
    
    Parameters
    ----------
    user : schema.UserCreate
        User data.
    db : Session
        Database session.
    current_user : User
        Current authenticated user (must be admin).
        
    Returns
    -------
    schema.User
        Created user.
        
    Raises
    ------
    HTTPException
        If the email is already registered.
    """
    # Check if the email is already registered
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create the new user
    new_user = User(
        name=user.name,
        email=user.email,
        password=user.password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.get("/me", response_model=schema.User)
def read_current_user(current_user: User = Depends(get_current_user)):
    """
    Get the current authenticated user.
    
    Parameters
    ----------
    current_user : User
        Current authenticated user.
        
    Returns
    -------
    schema.User
        Current user data.
    """
    return current_user


@router.put("/me", response_model=schema.User)
def update_current_user(
    user_update: schema.UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update the current authenticated user.
    
    Parameters
    ----------
    user_update : schema.UserUpdate
        User data to update.
    db : Session
        Database session.
    current_user : User
        Current authenticated user.
        
    Returns
    -------
    schema.User
        Updated user data.
    """
    # Update user fields if provided
    if user_update.name is not None:
        current_user.name = user_update.name
    
    if user_update.email is not None:
        # Check if the email is already taken by another user
        db_user = db.query(User).filter(User.email == user_update.email).first()
        if db_user and db_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        current_user.email = user_update.email
    
    if user_update.password is not None:
        current_user.hashed_password = User.get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user 