from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db import Base


class Feedback(Base):
    """
    Database model for user feedback on predictions.
    
    Attributes
    ----------
    id : int
        Feedback ID.
    user_id : int
        ID of the user who provided the feedback.
    predicted_fare : float
        Predicted fare.
    predicted_duration : float
        Predicted duration in minutes.
    actual_fare : float
        Actual fare paid.
    actual_duration : float
        Actual duration in minutes.
    pickup_location : str
        Pickup location (latitude,longitude).
    dropoff_location : str
        Dropoff location (latitude,longitude).
    timestamp : datetime
        When the feedback was submitted.
    rating : int
        User rating of the prediction (1-5).
    """
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    predicted_fare = Column(Float)
    predicted_duration = Column(Float)
    actual_fare = Column(Float)
    actual_duration = Column(Float)
    pickup_location = Column(String)
    dropoff_location = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    rating = Column(Integer)
    
    # Relationship with User
    user = relationship("User", backref="feedback") 