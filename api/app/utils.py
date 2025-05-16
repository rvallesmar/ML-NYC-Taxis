import os
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional


def parse_datetime(datetime_str: str) -> Optional[datetime]:
    """
    Parse a datetime string into a datetime object.
    
    Parameters
    ----------
    datetime_str : str
        Datetime string to parse.
        
    Returns
    -------
    datetime or None
        Parsed datetime object, or None if parsing failed.
    """
    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%m/%d/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M:%S"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(datetime_str, fmt)
        except ValueError:
            continue
    
    return None


def extract_features(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract features from taxi trip data for prediction.
    
    Parameters
    ----------
    data : Dict[str, Any]
        Raw taxi trip data.
        
    Returns
    -------
    Dict[str, Any]
        Extracted features.
    """
    features = {}
    
    # Parse pickup datetime
    pickup_datetime = parse_datetime(data.get("pickup_datetime"))
    if pickup_datetime:
        features["pickup_hour"] = pickup_datetime.hour
        features["pickup_day"] = pickup_datetime.day
        features["pickup_month"] = pickup_datetime.month
        features["pickup_weekday"] = pickup_datetime.weekday()
    
    # Use trip_distance directly from the input data (from Google API, in miles)
    if "trip_distance" in data:
        features["trip_distance"] = data["trip_distance"]
    
    # Include passenger count
    if "passenger_count" in data:
        features["passenger_count"] = data["passenger_count"]
    
    return features 