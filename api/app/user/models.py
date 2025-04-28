from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from passlib.context import CryptContext

from app.db import Base

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    """
    Database model for users.
    
    Attributes
    ----------
    id : int
        User ID.
    name : str
        User's name.
    email : str
        User's email (used for login).
    hashed_password : str
        Hashed password.
    created_at : datetime
        When the user was created.
    updated_at : datetime
        When the user was last updated.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.hashed_password = self.get_password_hash(password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        Hashes a password using bcrypt.
        
        Parameters
        ----------
        password : str
            Plain text password.
            
        Returns
        -------
        str
            Hashed password.
        """
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str) -> bool:
        """
        Verifies a password against the hashed password.
        
        Parameters
        ----------
        plain_password : str
            Plain text password to verify.
            
        Returns
        -------
        bool
            True if the password matches, False otherwise.
        """
        return pwd_context.verify(plain_password, self.hashed_password) 