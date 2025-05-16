from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum

from app.db import Base


class PredictionType(enum.Enum):
    """Enum for prediction types"""
    FARE_DURATION = "fare_duration"
    DEMAND = "demand"


class Feedback(Base):
    """
    Database model for user feedback on predictions.
    
    Attributes
    ----------
    id : int
        Feedback ID.
    user_id : int
        ID of the user who provided the feedback.
    prediction_type : str
        Type of prediction (fare_duration or demand)
    rating : int
        User rating of the prediction (1-5).
    comment : str
        Optional comment from user about the prediction.
    timestamp : datetime
        When the feedback was submitted.
        
    Fare/Duration specific fields:
    predicted_fare : float
        Predicted fare.
    predicted_duration : float
        Predicted duration in seconds.
    passenger_count : int
        Number of passengers (1-4).
    trip_distance : float
        Trip distance in miles.
        
    Demand specific fields:
    predicted_demand : int
        Predicted number of pickups in the region.
    region_id : int
        ID of the region for demand prediction.
    date_hour : str
        The datetime string used for demand prediction.
    """
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    prediction_type = Column(Enum(PredictionType), nullable=False)
    rating = Column(Integer)
    comment = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Fare/Duration specific fields
    predicted_fare = Column(Float, nullable=True)
    predicted_duration = Column(Float, nullable=True)
    passenger_count = Column(Integer, nullable=True)
    trip_distance = Column(Float, nullable=True)
    
    # Demand specific fields
    predicted_demand = Column(Integer, nullable=True)
    region_id = Column(Integer, nullable=True)
    date_hour = Column(String, nullable=True)
    
    # Relationship with User
    user = relationship("User", backref="feedback") 