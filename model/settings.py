import os
from dotenv import load_dotenv

load_dotenv()

# Model service settings
SERVER_SLEEP = float(os.getenv("SERVER_SLEEP", 0.05))

# Redis settings
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Queue names
FARE_DURATION_QUEUE = os.getenv("FARE_DURATION_QUEUE", "fare_duration_queue")
DEMAND_QUEUE = os.getenv("DEMAND_QUEUE", "demand_queue")

# Model paths - modified to use environment variable or fallback to the common directory
MODEL_DIR = os.getenv("MODEL_DIR", "models")
FARE_MODEL_PATH = os.path.join(MODEL_DIR, "model_fa.pkl")
DURATION_MODEL_PATH = os.path.join(MODEL_DIR, "model_tt.pkl")
DEMAND_MODEL_PATH = os.path.join(MODEL_DIR, "demand_model.joblib")
SCALER_PATH = os.path.join(MODEL_DIR, "min_max_scaler.pkl")
ONEHOT_ENCODER_PATH = os.path.join(MODEL_DIR, "oneh_time_of_day.pkl")

# API timeout for waiting for ML results (seconds)
API_TIMEOUT = float(os.getenv("API_TIMEOUT", 5.0)) 