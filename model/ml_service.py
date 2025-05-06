import json
import os
import time
from pathlib import Path
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
import redis
import settings

# Connect to Redis using settings from settings.py
# This establishes connection to Redis message broker
db = redis.Redis(
    host=settings.REDIS_HOST, 
    port=settings.REDIS_PORT, 
    db=settings.REDIS_DB,
    decode_responses=False
)

# Load ML models if they exist, otherwise set to None
# Models will be trained and saved separately
try:
    # Load fare prediction model if file exists
    if os.path.exists(settings.FARE_MODEL_PATH):
        fare_model = joblib.load(settings.FARE_MODEL_PATH)
    else:
        fare_model = None
        print(f"Warning: Fare model not found at {settings.FARE_MODEL_PATH}")
    
    # Load duration prediction model if file exists
    if os.path.exists(settings.DURATION_MODEL_PATH):
        duration_model = joblib.load(settings.DURATION_MODEL_PATH)
    else:
        duration_model = None
        print(f"Warning: Duration model not found at {settings.DURATION_MODEL_PATH}")
    
    # Load demand prediction model if file exists
    if os.path.exists(settings.DEMAND_MODEL_PATH):
        demand_model = joblib.load(settings.DEMAND_MODEL_PATH)
    else:
        demand_model = None
        print(f"Warning: Demand model not found at {settings.DEMAND_MODEL_PATH}")
except Exception as e:
    print(f"Error loading models: {e}")
    fare_model = None
    duration_model = None
    demand_model = None

# Create models directory if it doesn't exist
Path(os.path.dirname(settings.FARE_MODEL_PATH)).mkdir(parents=True, exist_ok=True)


def calculate_distance(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon):
    """
    Calculate the Haversine distance between two points.
    
    Parameters
    ----------
    pickup_lat : float
        Pickup latitude
    pickup_lon : float
        Pickup longitude
    dropoff_lat : float
        Dropoff latitude
    dropoff_lon : float
        Dropoff longitude
        
    Returns
    -------
    float
        Distance in kilometers
    """
    # Convert decimal degrees to radians
    pickup_lat, pickup_lon, dropoff_lat, dropoff_lon = map(
        np.radians, [pickup_lat, pickup_lon, dropoff_lat, dropoff_lon]
    )
    
    # Haversine formula
    dlat = dropoff_lat - pickup_lat
    dlon = dropoff_lon - pickup_lon
    a = np.sin(dlat/2)**2 + np.cos(pickup_lat) * np.cos(dropoff_lat) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    
    # Radius of earth in kilometers is 6371
    km = 6371.0 * c
    return km


def extract_time_features(datetime_str):
    """
    Extract time-related features from a datetime string.
    
    Parameters
    ----------
    datetime_str : str
        Datetime string in format 'YYYY-MM-DD HH:MM:SS'
        
    Returns
    -------
    dict
        Dictionary containing extracted time features
    """
    try:
        dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        dt = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S")
        
    return {
        'hour_of_day': dt.hour,
        'day_of_week': dt.weekday(),
        'month': dt.month,
        'is_weekend': 1 if dt.weekday() >= 5 else 0,
        'is_rush_hour': 1 if (dt.hour >= 7 and dt.hour <= 10) or (dt.hour >= 16 and dt.hour <= 19) else 0
    }


def predict_fare_duration(data):
    """
    Predict the fare amount and trip duration using the fare and duration models.

    Parameters
    ----------
    data : dict
        Dictionary containing the features required for prediction:
        - pickup_longitude
        - pickup_latitude
        - dropoff_longitude
        - dropoff_latitude
        - passenger_count
        - pickup_datetime

    Returns
    -------
    dict
        Dictionary containing the predicted fare and duration:
        - fare_amount: float
        - trip_duration: float
        - fare_score: float (model confidence for fare)
        - duration_score: float (model confidence for duration)
    """
    try:
        # Extract input features
        pickup_lon = data.get('pickup_longitude')
        pickup_lat = data.get('pickup_latitude')
        dropoff_lon = data.get('dropoff_longitude')
        dropoff_lat = data.get('dropoff_latitude')
        passenger_count = data.get('passenger_count')
        pickup_datetime = data.get('pickup_datetime')
        
        # Calculate distance if not provided
        if 'distance' in data and data['distance'] is not None:
            distance = data['distance']
        else:
            distance = calculate_distance(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon)
        
        # Extract time features
        time_features = extract_time_features(pickup_datetime)
        
        # Create feature dictionary
        features = {
            'pickup_longitude': pickup_lon,
            'pickup_latitude': pickup_lat,
            'dropoff_longitude': dropoff_lon,
            'dropoff_latitude': dropoff_lat,
            'passenger_count': passenger_count,
            'distance': distance,
            **time_features
        }
        
        # Convert to pandas DataFrame
        features_df = pd.DataFrame([features])
        
        # Make predictions if models are available
        if fare_model is not None:
            fare_pred = fare_model.predict(features_df)[0]
            # Get prediction confidence (if model supports it)
            try:
                fare_score = getattr(fare_model, "predict_proba", lambda x: [[0.8]])(features_df)[0][0]
            except:
                fare_score = 0.8  # Default confidence score
        else:
            # Mock prediction if model is not available
            print("Warning: Using mock fare prediction because model is not available")
            fare_pred = 15.0 + (2.5 * distance) + (0.5 * passenger_count)
            fare_score = 0.6  # Lower confidence for mock prediction
        
        if duration_model is not None:
            duration_pred = duration_model.predict(features_df)[0]
            # Get prediction confidence (if model supports it)
            try:
                duration_score = getattr(duration_model, "predict_proba", lambda x: [[0.8]])(features_df)[0][0]
            except:
                duration_score = 0.8  # Default confidence score
        else:
            # Mock prediction if model is not available
            print("Warning: Using mock duration prediction because model is not available")
            duration_pred = 300.0 + (120.0 * distance) + (time_features['is_rush_hour'] * 300.0)
            duration_score = 0.6  # Lower confidence for mock prediction
        
        # Return predictions
        return {
            "fare_amount": float(fare_pred),
            "trip_duration": float(duration_pred),
            "fare_score": float(fare_score),
            "duration_score": float(duration_score)
        }
    
    except Exception as e:
        print(f"Error in fare/duration prediction: {e}")
        # Return fallback predictions
    return {
        "fare_amount": 15.0,
        "trip_duration": 1200.0,  # in seconds
            "fare_score": 0.5,
            "duration_score": 0.5
    }


def predict_demand(data):
    """
    Predict taxi demand for a specific region and time.

    Parameters
    ----------
    data : dict
        Dictionary containing the features required for prediction:
        - region_id
        - date_hour (string in format 'YYYY-MM-DD HH:MM:SS')

    Returns
    -------
    dict
        Dictionary containing the predicted demand:
        - demand: int (predicted number of pickups)
        - demand_score: float (model confidence)
    """
    try:
        # Extract input features
        region_id = data.get('region_id')
        date_hour = data.get('date_hour')
        
        # Extract time features
        time_features = extract_time_features(date_hour)
        
        # Create feature dictionary
        features = {
            'region_id': region_id,
            **time_features
        }
        
        # Convert to pandas DataFrame
        features_df = pd.DataFrame([features])
        
        # Make predictions if model is available
        if demand_model is not None:
            demand_pred = demand_model.predict(features_df)[0]
            # Get prediction confidence (if model supports it)
            try:
                demand_score = getattr(demand_model, "predict_proba", lambda x: [[0.75]])(features_df)[0][0]
            except:
                demand_score = 0.75  # Default confidence score
        else:
            # Mock prediction if model is not available
            print("Warning: Using mock demand prediction because model is not available")
            base_demand = 20
            # More demand on weekends and rush hours
            weekend_factor = 1.5 if time_features['is_weekend'] else 1.0
            rush_hour_factor = 1.8 if time_features['is_rush_hour'] else 1.0
            hour_factor = 0.5 if (time_features['hour_of_day'] >= 0 and time_features['hour_of_day'] < 6) else 1.0
            
            # Generate different demands based on region_id (for variety)
            region_factor = 0.8 + ((region_id % 10) / 10)
            
            demand_pred = int(base_demand * weekend_factor * rush_hour_factor * hour_factor * region_factor)
            demand_score = 0.6  # Lower confidence for mock prediction
        
        # Return predictions
        return {
                "demand": int(demand_pred),
                "demand_score": float(demand_score)
            }
    
    except Exception as e:
        print(f"Error in demand prediction: {e}")
        # Return fallback predictions
        return {
            "demand": 20,
            "demand_score": 0.5
    }


def classify_process():
    """
    Loop indefinitely asking Redis for new jobs.
    When a new job arrives, takes it from the Redis queue, uses the loaded ML
    models to get predictions and stores the results back in Redis using
    the original job ID so other services can see it was processed and access
    the results.
    """
    while True:
        # Inside this loop you should:
        #   1. Take a new job from Redis queues
        #   2. Run the appropriate ML model on the given data
        #   3. Store model prediction in a dict
        #   4. Store the results on Redis using the original job ID as the key

        # Try to get a fare/duration prediction job first
        fare_duration_job = db.brpop(
            settings.FARE_DURATION_QUEUE,
            timeout=1
        )
        
        if fare_duration_job:
            _, job_data = fare_duration_job
            
            # Decode the JSON data
            job_dict = json.loads(job_data.decode('utf-8'))
            
            # Get the original job ID
            job_id = job_dict['id']
            
            # Get the input data
            input_data = job_dict['data']
            
            # Run the model prediction
            result = predict_fare_duration(input_data)
            
            # Prepare and store results
            db.set(job_id, json.dumps(result))
            
            # Continue to next iteration
            continue
            
        # Try to get a demand prediction job
        demand_job = db.brpop(
            settings.DEMAND_QUEUE,
            timeout=1
        )
        
        if demand_job:
            _, job_data = demand_job
            
            # Decode the JSON data
            job_dict = json.loads(job_data.decode('utf-8'))
            
            # Get the original job ID
            job_id = job_dict['id']
            
            # Get the input data
            input_data = job_dict['data']
            
            # Run the model prediction
            result = predict_demand(input_data)
            
            # Prepare and store results
            db.set(job_id, json.dumps(result))

        # Sleep for a bit if no jobs
        time.sleep(settings.SERVER_SLEEP)


if __name__ == "__main__":
    # Now launch process
    print("Launching NYC Taxi Prediction ML service...")
    classify_process() 