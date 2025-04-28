from typing import Optional
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """
    Schema for access token response.
    
    Attributes
    ----------
    access_token : str
        JWT access token.
    token_type : str
        Token type, always 'bearer'.
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Schema for token data.
    
    Attributes
    ----------
    email : str, optional
        User's email extracted from the token.
    """
    email: Optional[str] = None 