import os
from dotenv import load_dotenv

load_dotenv()

# API settings
API_SLEEP = float(os.getenv("API_SLEEP", 0.05))

# Redis settings
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Database settings
POSTGRES_DB = os.getenv("POSTGRES_DB", "taxi_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DATABASE_HOST = os.getenv("DATABASE_HOST", "db")

# Authentication settings
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# File upload settings
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"csv", "json", "parquet"} 