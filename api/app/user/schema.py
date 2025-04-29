from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """
    Base schema for user data.
    
    Attributes
    ----------
    email : EmailStr
        User's email.
    name : str
        User's name.
    """
    email: EmailStr
    name: str


class UserCreate(UserBase):
    """
    Schema for creating a new user.
    
    Attributes
    ----------
    password : str
        User's plain text password.
    """
    password: str


class UserUpdate(BaseModel):
    """
    Schema for updating a user.
    
    Attributes
    ----------
    name : str, optional
        User's name.
    email : EmailStr, optional
        User's email.
    password : str, optional
        User's plain text password.
    """
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class User(UserBase):
    """
    Schema for user data.
    
    Attributes
    ----------
    id : int
        User ID.
    created_at : datetime
        When the user was created.
    updated_at : datetime
        When the user was last updated.
    """
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True 