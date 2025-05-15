import json
import time
from uuid import uuid4
import logging

import redis

from app import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connect to Redis using settings from settings.py
# This establishes connection to the same Redis broker used by the model service
db = redis.Redis(
    host=settings.REDIS_HOST, 
    port=settings.REDIS_PORT, 
    db=settings.REDIS_DB,
    decode_responses=False
)


async def predict_fare_duration(data):
    """
    Receives trip data and queues the job into Redis.
    Will loop until getting the answer from the ML service.

    Parameters
    ----------
    data : dict
        Dictionary containing the features required for prediction.

    Returns
    -------
    fare_amount, trip_duration : tuple
        The predicted fare amount and trip duration.
    """
    # Generate a unique job ID with a prefix to identify the job type
    job_id = f"fare_duration:{str(uuid4())}"

    # Create a dict with the job data including ID and input data
    job_data = {
        "id": job_id,
        "data": data
    }

    logger.info(f"===== API SENDING PREDICTION REQUEST =====")
    logger.info(f"Job ID: {job_id}")
    logger.info(f"Input data: {data}")

    # Send the job to the model service using Redis lpush to the fare_duration queue
    db.lpush(settings.FARE_DURATION_QUEUE, json.dumps(job_data))

    # Loop until we receive response, with timeout to prevent infinite wait
    max_retries = 100  # Add a maximum retry count for safety
    retry_count = 0
    
    while retry_count < max_retries:
        # Attempt to get model predictions using job_id as the key
        output = db.get(job_id)

        # Check if prediction is ready
        if output is not None:
            # Decode the JSON response
            output = json.loads(output.decode("utf-8"))
            
            # Extract prediction results
            fare_amount = output["fare_amount"]
            trip_duration = output["trip_duration"]

            # Add detailed logging
            logger.info(f"===== API RECEIVED PREDICTION RESULT =====")
            logger.info(f"Job ID: {job_id}")
            logger.info(f"Fare: ${fare_amount:.2f}, Duration: {trip_duration:.2f} seconds ({trip_duration/60:.1f} minutes)")

            # Clean up by deleting the job from Redis
            db.delete(job_id)
            
            # Return the prediction values
            return fare_amount, trip_duration

        # Sleep some time waiting for model results
        time.sleep(settings.API_SLEEP)
        retry_count += 1

    # If we reach here, prediction timed out
    logger.error(f"Prediction timed out for job ID: {job_id}")
    raise TimeoutError("Prediction timed out. The model service might be unavailable.")


async def predict_demand(data):
    """
    Receives region and time data and queues the job into Redis.
    Will loop until getting the answer from the ML service.

    Parameters
    ----------
    data : dict
        Dictionary containing the features required for prediction.

    Returns
    -------
    demand : int
        The predicted demand.
    """
    # Generate a unique job ID with a prefix to identify the job type
    job_id = f"demand:{str(uuid4())}"

    # Create a dict with the job data including ID and input data
    job_data = {
        "id": job_id,
        "data": data
    }

    # Send the job to the model service using Redis lpush to the demand queue
    db.lpush(settings.DEMAND_QUEUE, json.dumps(job_data))

    # Loop until we receive response, with timeout to prevent infinite wait
    max_retries = 100  # Add a maximum retry count for safety
    retry_count = 0
    
    while retry_count < max_retries:
        # Attempt to get model predictions using job_id as the key
        output = db.get(job_id)

        # Check if prediction is ready
        if output is not None:
            # Decode the JSON response
            output = json.loads(output.decode("utf-8"))
            
            # Extract prediction results
            demand = output["demand"]

            # Clean up by deleting the job from Redis
            db.delete(job_id)
            
            # Return the prediction values
            return demand

        # Sleep some time waiting for model results
        time.sleep(settings.API_SLEEP)
        retry_count += 1

    # If we reach here, prediction timed out
    raise TimeoutError("Prediction timed out. The model service might be unavailable.") 