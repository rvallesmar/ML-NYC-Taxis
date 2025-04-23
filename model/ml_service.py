import json
import os
import time
from pathlib import Path

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
        - distance
        - hour_of_day
        - day_of_week
        - etc.

    Returns
    -------
    dict
        Dictionary containing the predicted fare and duration:
        - fare_amount: float
        - trip_duration: float
        - fare_score: float (model confidence for fare)
        - duration_score: float (model confidence for duration)
    """
    # TODO: Implement fare and duration prediction
    # 1. Convert input data to DataFrame or numpy array
    # 2. Preprocess features
    # 3. Make predictions with the models
    # 4. Return results

    # Temporary mock response
    return {
        "fare_amount": 15.0,
        "trip_duration": 1200.0,  # in seconds
        "fare_score": 0.85,
        "duration_score": 0.80
    }

def predict_demand(data):
    """
    Predict taxi demand for a specific area and time.

    Parameters
    ----------
    data : dict
        Dictionary containing the features required for prediction:
        - region_id
        - hour_of_day
        - day_of_week
        - etc.

    Returns
    -------
    dict
        Dictionary containing the predicted demand:
        - demand: int (predicted number of pickups)
        - demand_score: float (model confidence)
    """
    # TODO: Implement demand prediction
    # 1. Convert input data to DataFrame or numpy array
    # 2. Preprocess features
    # 3. Make predictions with the model
    # 4. Return results

    # Temporary mock response
    return {
        "demand": 25,
        "demand_score": 0.75
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