# Google Maps API Setup

This application uses Google Maps API for geocoding addresses and visualizing routes. To properly configure the API key, follow these instructions:

## Getting a Google Maps API Key

1. Visit the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Maps JavaScript API
   - Directions API
   - Geocoding API
4. Create an API key with appropriate restrictions (preferably limit to HTTP referrers)

## Configuring the API Key

### Method 1: Environment Variable (Recommended)

When running the application with Docker Compose:

1. Create a `.env` file in the root directory of the project with the following content:
   ```
   # Database settings
   POSTGRES_DB=postgres
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   DATABASE_HOST=db
   
   # Security
   SECRET_KEY=your-super-secret-key
   
   # Google Maps API
   GOOGLE_MAPS_API_KEY=your-google-maps-api-key
   ```

2. Replace `your-google-maps-api-key` with your actual API key
3. Run Docker Compose:
   ```
   docker-compose up --build -d
   ```

### Method 2: Manual Configuration

If you prefer not to use environment variables, you can set the API key directly in the settings file:

1. Open `ui/app/settings.py`
2. Locate the line with `GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")`
3. Replace it with `GOOGLE_MAPS_API_KEY = "your-google-maps-api-key"` (not recommended for production)

## Security Considerations

- Never commit your API key to version control
- Use environment variables in production environments
- Add appropriate restrictions to your API key in the Google Cloud Console
- If using Method 2, ensure your settings file is included in .gitignore

## Troubleshooting

If you see the error message "Google Maps API key is not configured" in the UI:

1. Check that you've correctly set the environment variable
2. Verify that the Docker Compose file is correctly passing the variable to the UI service
3. Restart the UI container after making changes to environment variables 