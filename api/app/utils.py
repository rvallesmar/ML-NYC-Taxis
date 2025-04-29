import os
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Validates that latitude and longitude values are within valid ranges.
    
    Parameters
    ----------
    latitude : float
        The latitude value to validate.
    longitude : float
        The longitude value to validate.
        
    Returns
    -------
    bool
        True if both values are valid, False otherwise.
    """
    return -90 <= latitude <= 90 and -180 <= longitude <= 180


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the Haversine distance between two points.
    
    Parameters
    ----------
    lat1 : float
        Latitude of the first point.
    lon1 : float
        Longitude of the first point.
    lat2 : float
        Latitude of the second point.
    lon2 : float
        Longitude of the second point.
        
    Returns
    -------
    float
        Distance in kilometers.
    """
    # Convert coordinates from degrees to radians
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371  # Radius of Earth in kilometers
    
    return c * r


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
    
    # Calculate trip distance
    if all(k in data for k in ["pickup_latitude", "pickup_longitude", 
                               "dropoff_latitude", "dropoff_longitude"]):
        features["trip_distance"] = calculate_distance(
            data["pickup_latitude"], data["pickup_longitude"],
            data["dropoff_latitude"], data["dropoff_longitude"]
        )
    
    # Include passenger count
    if "passenger_count" in data:
        features["passenger_count"] = data["passenger_count"]
    
    return features 