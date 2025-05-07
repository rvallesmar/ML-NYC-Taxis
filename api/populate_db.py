import psycopg2
from app import settings as config
from app.db import Base
from app.feedback.models import Feedback
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

# Create a dgallardo
test_user_dga = User(
    name="Douglas Gallardo",
    password="Sofia2017",
    email="dgallardo@example.com",
)

session.add(admin_user)
session.add(test_user)
session.add(test_user_dga)
session.commit()
print("Default users added")

# Add some sample feedback entries
sample_feedback = [
    Feedback(
        user_id=1,
        predicted_fare=25.50,
        predicted_duration=15.75,
        actual_fare=26.00,
        actual_duration=16.25,
        pickup_location="40.7580,-73.9855",
        dropoff_location="40.7278,-74.0031",
        timestamp="2023-09-15 13:45:00",
        rating=4
    ),
    Feedback(
        user_id=1,
        predicted_fare=15.25,
        predicted_duration=10.50,
        actual_fare=14.75,
        actual_duration=9.90,
        pickup_location="40.7580,-73.9855",
        dropoff_location="40.7641,-73.9722",
        timestamp="2023-09-15 14:30:00",
        rating=5
    ),
    Feedback(
        user_id=2,
        predicted_fare=30.75,
        predicted_duration=22.25,
        actual_fare=32.50,
        actual_duration=24.00,
        pickup_location="40.7641,-73.9722",
        dropoff_location="40.7061,-74.0086",
        timestamp="2023-09-16 09:15:00",
        rating=3
    )
]

for feedback in sample_feedback:
    session.add(feedback)

session.commit()
print("Sample feedback entries added")

session.close()
print("Database population completed successfully") 