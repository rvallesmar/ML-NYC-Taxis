import os

# API settings
API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = os.getenv("API_PORT", "8000")
API_BASE_URL = f"http://{API_HOST}:{API_PORT}"

# UI settings
PAGE_TITLE = "NYC Taxi Prediction"
PAGE_ICON = "🚕"

# Map settings
DEFAULT_MAP_LOCATION = [40.7831, -73.9712]  # NYC Central Park
DEFAULT_ZOOM = 11 

# Google Maps API settings
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "") 