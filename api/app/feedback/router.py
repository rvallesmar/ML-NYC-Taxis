from typing import List
import numpy as np
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_user
from app.db import get_db
from app.feedback import schema
from app.feedback.models import Feedback
from app.user.models import User

# Router definition
router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"],
    responses={404: {"description": "Not found"}},
)


@router.post("/submit", response_model=dict)
async def submit_feedback(
    feedback: schema.FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit feedback on a prediction.
    
    Parameters
    ----------
    feedback : schema.FeedbackCreate
        Feedback data.
    db : Session
        Database session.
    current_user : User
        Current authenticated user.
        
    Returns
    -------
    dict
        Confirmation message and feedback ID.
    """
    db_feedback = Feedback(
        user_id=current_user.id,
        predicted_fare=feedback.predicted_fare,
        predicted_duration=feedback.predicted_duration,
        actual_fare=feedback.actual_fare,
        actual_duration=feedback.actual_duration,
        pickup_location=feedback.pickup_location,
        dropoff_location=feedback.dropoff_location,
        rating=feedback.rating
    )
    
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    
    return {
        "message": "Feedback submitted successfully",
        "feedback_id": db_feedback.id
    }


@router.get("/user", response_model=List[schema.Feedback])
async def get_user_feedback(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get feedback submitted by the current user.
    
    Parameters
    ----------
    db : Session
        Database session.
    current_user : User
        Current authenticated user.
        
    Returns
    -------
    List[schema.Feedback]
        List of feedback entries.
    """
    user_feedback = db.query(Feedback).filter(Feedback.user_id == current_user.id).all()
    return user_feedback


@router.get("/stats", response_model=schema.FeedbackStats)
async def get_feedback_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get statistics on prediction accuracy based on feedback.
    
    Parameters
    ----------
    db : Session
        Database session.
    current_user : User
        Current authenticated user.
        
    Returns
    -------
    schema.FeedbackStats
        Feedback statistics.
    """
    # Get all feedback
    feedback_entries = db.query(Feedback).all()
    
    # Calculate statistics
    if feedback_entries:
        feedback_count = len(feedback_entries)
        avg_rating = sum(f.rating for f in feedback_entries) / feedback_count
        
        # Mean absolute error for fare and duration
        fare_errors = [abs(f.predicted_fare - f.actual_fare) for f in feedback_entries]
        duration_errors = [abs(f.predicted_duration - f.actual_duration) for f in feedback_entries]
        
        fare_mae = sum(fare_errors) / feedback_count
        duration_mae = sum(duration_errors) / feedback_count
    else:
        # No feedback yet
        feedback_count = 0
        avg_rating = 0
        fare_mae = 0
        duration_mae = 0
    
    return schema.FeedbackStats(
        feedback_count=feedback_count,
        avg_rating=avg_rating,
        fare_mae=fare_mae,
        duration_mae=duration_mae
    ) 