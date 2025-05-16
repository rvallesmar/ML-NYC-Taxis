from typing import List
import numpy as np
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_user
from app.db import get_db
from app.feedback import schema
from app.feedback.models import Feedback, PredictionType
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
    if feedback.prediction_type == "fare_duration":
        db_feedback = Feedback(
            user_id=current_user.id,
            prediction_type=PredictionType.FARE_DURATION,
            predicted_fare=feedback.predicted_fare,
            predicted_duration=feedback.predicted_duration,
            passenger_count=feedback.passenger_count,
            trip_distance=feedback.trip_distance,
            rating=feedback.rating,
            comment=feedback.comment
        )
    else:  # demand
        db_feedback = Feedback(
            user_id=current_user.id,
            prediction_type=PredictionType.DEMAND,
            predicted_demand=feedback.predicted_demand,
            region_id=feedback.region_id,
            date_hour=feedback.date_hour,
            rating=feedback.rating,
            comment=feedback.comment
        )
    
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    
    return {
        "message": "Feedback submitted successfully",
        "feedback_id": db_feedback.id
    }


@router.post("", response_model=dict)
async def handle_ui_feedback(
    feedback_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Handle feedback from the UI.
    
    Parameters
    ----------
    feedback_data : dict
        Contains rating, optional comment, and prediction details
    db : Session
        Database session.
    current_user : User
        Current authenticated user.
        
    Returns
    -------
    dict
        Confirmation message.
    """
    rating = feedback_data.get("rating", 3)
    comment = feedback_data.get("comment", "")
    prediction_type = feedback_data.get("prediction_type", "")
    prediction_data = feedback_data.get("prediction_data", {})
    last_prediction = feedback_data.get("last_prediction", {})
    
    if prediction_type == "fare_duration":
        # Extract values from the prediction data
        passenger_count = prediction_data.get("passenger_count", 1)
        trip_distance = prediction_data.get("trip_distance", 1.0)
        
        # Get predicted values from the last_prediction
        predicted_fare = last_prediction.get("fare_amount", 0.0)
        predicted_duration = last_prediction.get("trip_duration", 0.0)
        
        # Create a feedback entry
        db_feedback = Feedback(
            user_id=current_user.id,
            prediction_type=PredictionType.FARE_DURATION,
            predicted_fare=predicted_fare,
            predicted_duration=predicted_duration,
            passenger_count=passenger_count,
            trip_distance=trip_distance,
            rating=rating,
            comment=comment
        )
        
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        
        return {
            "message": "Feedback submitted successfully",
            "feedback_id": db_feedback.id
        }
    
    elif prediction_type == "demand":
        # Extract values from the prediction data
        region_id = prediction_data.get("region_id", 1)
        date_hour = prediction_data.get("date_hour", "")
        
        # Get predicted value from the last_prediction
        predicted_demand = last_prediction.get("demand", 0)
        
        # Create a feedback entry
        db_feedback = Feedback(
            user_id=current_user.id,
            prediction_type=PredictionType.DEMAND,
            predicted_demand=predicted_demand,
            region_id=region_id,
            date_hour=date_hour,
            rating=rating,
            comment=comment
        )
        
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        
        return {
            "message": "Feedback submitted successfully",
            "feedback_id": db_feedback.id
        }
    
    # Handle unknown prediction types
    return {
        "message": "Feedback received but not stored in database - unknown prediction type",
        "feedback_type": prediction_type
    }


@router.get("/user", response_model=List[schema.FeedbackResponse])
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
    List[schema.FeedbackResponse]
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
    else:
        # No feedback yet
        feedback_count = 0
        avg_rating = 0
    
    return schema.FeedbackStats(
        feedback_count=feedback_count,
        avg_rating=avg_rating
    ) 