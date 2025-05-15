import psycopg2
from app import settings as config
from app.db import Base
from app.feedback.models import Feedback, PredictionType
from app.user.models import User
from psycopg2.errors import DuplicateDatabase
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_USERNAME = config.POSTGRES_USER
DATABASE_PASSWORD = config.POSTGRES_PASSWORD
DATABASE_HOST = config.DATABASE_HOST
DATABASE_NAME = config.POSTGRES_DB

# Create the initial connection URL to PostgreSQL (without specifying the database)
initial_connection_url = (
    f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}/postgres"
)

print(initial_connection_url)

conn = None

# Connect to PostgreSQL to create the database if it doesn't exist
try:
    conn = psycopg2.connect(initial_connection_url)
    conn.autocommit = True
    cursor = conn.cursor()

    # Create the database
    cursor.execute(f"CREATE DATABASE {DATABASE_NAME}")
    print(f"Database '{DATABASE_NAME}' created successfully")

except DuplicateDatabase as e:
    if "already exists" in str(e):
        print(f"Database '{DATABASE_NAME}' already exists.")
    else:
        print(f"Error creating database: {e}")
finally:
    if conn:
        cursor.close()
        conn.close()

# Database connection URL to the newly created database
SQLALCHEMY_DATABASE_URL = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"
print(SQLALCHEMY_DATABASE_URL)

# Create engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Drop all tables if they exist
Base.metadata.drop_all(engine)
print("Tables dropped")

# Create all tables
Base.metadata.create_all(engine)
print("Tables created")

# Populate database with a default user
print("Populating database with default user")
Session = sessionmaker(bind=engine)
session = Session()

# Create admin user
admin_user = User(
    name="Admin User",
    password="admin",
    email="admin@example.com",
)

# Create a test user
test_user = User(
    name="Test User",
    password="test123",
    email="test@example.com",
)

session.add(admin_user)
session.add(test_user)
session.commit()
print("Default users added")

# Add some feedback entries for testing
print("Populating database with sample feedback")

# Fare/duration feedback examples
feedback1 = Feedback(
    user_id=1,
    prediction_type=PredictionType.FARE_DURATION,
    predicted_fare=25.50,
    predicted_duration=1200.0,  # 20 minutes in seconds
    passenger_count=2,
    trip_distance=3.5,
    rating=4,
    comment="Good prediction, but the ride was a bit more expensive than expected."
)
session.add(feedback1)

feedback2 = Feedback(
    user_id=1,
    prediction_type=PredictionType.FARE_DURATION,
    predicted_fare=15.75,
    predicted_duration=900.0,  # 15 minutes in seconds
    passenger_count=1,
    trip_distance=2.2,
    rating=5,
    comment="Perfect prediction, thanks!"
)
session.add(feedback2)

feedback3 = Feedback(
    user_id=2,
    prediction_type=PredictionType.FARE_DURATION,
    predicted_fare=32.20,
    predicted_duration=1500.0,  # 25 minutes in seconds
    passenger_count=3,
    trip_distance=4.8,
    rating=3,
    comment="The duration estimate was a bit off."
)
session.add(feedback3)

# Demand feedback examples
feedback4 = Feedback(
    user_id=1,
    prediction_type=PredictionType.DEMAND,
    predicted_demand=25,
    region_id=5,
    date_hour="2023-09-15 14:30:00",
    rating=5,
    comment="Very accurate demand prediction for this region."
)
session.add(feedback4)

feedback5 = Feedback(
    user_id=2,
    prediction_type=PredictionType.DEMAND,
    predicted_demand=12,
    region_id=3,
    date_hour="2023-09-16 08:45:00",
    rating=2,
    comment="Demand was much higher than predicted."
)
session.add(feedback5)

session.commit()
print("Sample feedback entries added")

session.close()
print("Database population completed successfully") 