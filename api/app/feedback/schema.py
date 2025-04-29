from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class FeedbackBase(BaseModel):
    """
    Base schema for feedback data.
    
    Attributes
    ----------
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
    rating : int
        User rating of the prediction (1-5).
    """
    predicted_fare: float
    predicted_duration: float
    actual_fare: float
    actual_duration: float
    pickup_location: str
    dropoff_location: str
    rating: int = Field(..., ge=1, le=5)


class FeedbackCreate(FeedbackBase):
    """
    Schema for creating feedback.
    """
    pass


class Feedback(FeedbackBase):
    """
    Schema for feedback data.
    
    Attributes
    ----------
    id : int
        Feedback ID.
    user_id : int
        ID of the user who provided the feedback.
    timestamp : datetime
        When the feedback was submitted.
    """
    id: int
    user_id: int
    timestamp: datetime
    
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
    fare_mae : float
        Mean absolute error for fare predictions.
    duration_mae : float
        Mean absolute error for duration predictions.
    """
    feedback_count: int
    avg_rating: float
    fare_mae: float
    duration_mae: float 