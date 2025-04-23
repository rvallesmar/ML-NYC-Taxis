import json
import random
import time
from datetime import datetime, timedelta

from locust import HttpUser, between, task

# Test coordinates within NYC area
NYC_COORDINATES = [
    (-73.98, 40.73),  # Manhattan - Greenwich Village
    (-73.96, 40.78),  # Manhattan - Upper East Side
    (-73.92, 40.82),  # Manhattan - Harlem
    (-73.95, 40.65),  # Brooklyn - Prospect Park
    (-73.83, 40.70),  # Queens - Jackson Heights
    (-73.86, 40.75),  # Queens - Astoria
    (-73.90, 40.84),  # Bronx - South Bronx
    (-74.08, 40.64),  # Staten Island - St. George
]

# Test region IDs
REGION_IDS = list(range(1, 101))


class TaxiPredictionUser(HttpUser):
    wait_time = between(1, 3)
    token = None
    
    def on_start(self):
        """Login at the start of each simulated user session."""
        # TODO: Implement login process
        login_response = self.client.post(
            "/login",
            data={
                "username": "admin@example.com",
                "password": "admin"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if login_response.status_code == 200:
            self.token = login_response.json().get("access_token")
        else:
            print(f"Login failed: {login_response.text}")
    
    @task(3)
    def predict_fare_duration(self):
        """Test the fare and duration prediction endpoint."""
        if not self.token:
            return
        
        # Generate random pickup and dropoff locations from NYC coordinates
        pickup_idx = random.randint(0, len(NYC_COORDINATES) - 1)
        dropoff_idx = random.randint(0, len(NYC_COORDINATES) - 1)
        while dropoff_idx == pickup_idx:  # Ensure different pickup and dropoff
            dropoff_idx = random.randint(0, len(NYC_COORDINATES) - 1)
        
        pickup_long, pickup_lat = NYC_COORDINATES[pickup_idx]
        dropoff_long, dropoff_lat = NYC_COORDINATES[dropoff_idx]
        
        # Generate random datetime within the past week
        now = datetime.now()
        days_ago = random.randint(0, 7)
        hours_ago = random.randint(0, 23)
        random_datetime = now - timedelta(days=days_ago, hours=hours_ago)
        pickup_datetime_str = random_datetime.strftime("%Y-%m-%d %H:%M:%S")
        
        # Generate random passenger count
        passenger_count = random.randint(1, 6)
        
        # Prepare request data
        data = {
            "pickup_longitude": pickup_long,
            "pickup_latitude": pickup_lat,
            "dropoff_longitude": dropoff_long,
            "dropoff_latitude": dropoff_lat,
            "passenger_count": passenger_count,
            "pickup_datetime": pickup_datetime_str
        }
        
        # Send request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        
        response = self.client.post(
            "/model/predict/fare_duration",
            json=data,
            headers=headers,
            name="/model/predict/fare_duration"
        )
        
        # Log any errors (for debugging)
        if response.status_code != 200:
            print(f"Fare/duration prediction failed: {response.text}")
    
    @task(1)
    def predict_demand(self):
        """Test the demand prediction endpoint."""
        if not self.token:
            return
        
        # Generate random region and datetime
        region_id = random.choice(REGION_IDS)
        
        now = datetime.now()
        days_ago = random.randint(0, 7)
        hours_ago = random.randint(0, 23)
        random_datetime = now - timedelta(days=days_ago, hours=hours_ago)
        date_hour_str = random_datetime.strftime("%Y-%m-%d %H:%M:%S")
        
        # Prepare request data
        data = {
            "region_id": region_id,
            "date_hour": date_hour_str
        }
        
        # Send request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        
        response = self.client.post(
            "/model/predict/demand",
            json=data,
            headers=headers,
            name="/model/predict/demand"
        )
        
        # Log any errors (for debugging)
        if response.status_code != 200:
            print(f"Demand prediction failed: {response.text}")
    
    @task(1)
    def index(self):
        """Test the root endpoint."""
        self.client.get("/", name="index") 