import os
from dotenv import load_dotenv

load_dotenv()

# Model service settings
SERVER_SLEEP = float(os.getenv("SERVER_SLEEP", 0.05))

# Redis settings
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Model settings
FARE_MODEL_PATH = os.path.join("models", "fare_model.joblib")
DURATION_MODEL_PATH = os.path.join("models", "duration_model.joblib")
DEMAND_MODEL_PATH = os.path.join("models", "demand_model.joblib")

# Queue names
FARE_DURATION_QUEUE = "nyc_taxi_fare_duration_queue"
DEMAND_QUEUE = "nyc_taxi_demand_queue" 