from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class FeedbackBase(BaseModel):
    """
    Base schema for feedback data.
    
    Attributes
    ----------
    rating : int
        User rating of the prediction (1-5).
    comment : Optional[str]
        Optional comment from user about the prediction.
    """
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class FeedbackCreate(BaseModel):
    """
    Schema for creating feedback.
    
    Attributes
    ----------
    prediction_type : str
        Type of prediction (fare_duration or demand)
    rating : int
        User rating of the prediction (1-5).
    comment : Optional[str]
        Optional comment from user.
    
    Fare/Duration specific fields:
    predicted_fare : Optional[float]
        Predicted fare amount.
    predicted_duration : Optional[float]
        Predicted trip duration in seconds.
    passenger_count : Optional[int]
        Number of passengers (1-4).
    trip_distance : Optional[float]
        Trip distance in miles.
        
    Demand specific fields:
    predicted_demand : Optional[int]
        Predicted demand amount.
    region_id : Optional[int]
        ID of the region.
    date_hour : Optional[str]
        Date and hour of the prediction.
    """
    prediction_type: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    
    # Fare/Duration specific fields (Optional)
    predicted_fare: Optional[float] = None
    predicted_duration: Optional[float] = None
    passenger_count: Optional[int] = None
    trip_distance: Optional[float] = None
    
    # Demand specific fields (Optional)
    predicted_demand: Optional[int] = None
    region_id: Optional[int] = None
    date_hour: Optional[str] = None


class FeedbackResponse(BaseModel):
    """
    Schema for feedback data with common fields.
    
    Attributes
    ----------
    id : int
        Feedback ID.
    user_id : int
        ID of the user who provided the feedback.
    timestamp : datetime
        When the feedback was submitted.
    prediction_type : str
        Type of prediction (fare_duration or demand)
    rating : int
        User rating of the prediction (1-5).
    comment : Optional[str]
        Optional user comment.
    """
    id: int
    user_id: int
    timestamp: datetime
    prediction_type: str
    rating: int
    comment: Optional[str]
    
    # Fare/Duration specific fields (Optional)
    predicted_fare: Optional[float] = None
    predicted_duration: Optional[float] = None
    passenger_count: Optional[int] = None
    trip_distance: Optional[float] = None
    
    # Demand specific fields (Optional)
    predicted_demand: Optional[int] = None
    region_id: Optional[int] = None
    date_hour: Optional[str] = None
    
    class Config:
        orm_mode = True


class FeedbackStats(BaseModel):
    """
    Schema for feedback statistics.
    
    Attributes
    ----------
    feedback_count : int
        Number of feedback entries.
    avg_rating : float
        Average rating.
    """
    feedback_count: int
    avg_rating: float 