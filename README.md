# NYC Taxi Prediction Project

## The Business Problem

Taxi companies in New York City face increasing competition from ridesharing apps. To stay competitive, they need to provide accurate fare and duration estimates to customers. Additionally, predicting taxi demand can help dispatchers optimize their fleet allocation.

This project aims to:
1. Predict the fare and duration of a taxi ride in New York City using available data at the beginning of the ride (pickup/dropoff coordinates, trip distance, start time, etc.)
2. Predict taxi demand per region to aid dispatchers in making decisions about vehicle allocation

Our solution consists of machine learning models served through a FastAPI backend and a Streamlit-based web interface that allows users to get predictions based on input parameters.

## Technical Architecture

The system is built with these technologies:
- Python 3.8 as the main programming language
- FastAPI for the API layer
- Streamlit for the web UI
- Redis for communication between microservices
- PostgreSQL for user management and feedback storage
- Scikit-learn, LightGBM, and XGBoost for predictive models
- Docker and docker-compose for containerization
- Google Maps API for geocoding and route visualization

## Installation

To run the services using docker-compose:

```bash
$ cp .env.original .env
```

**Important**: This application uses Google Maps API for geocoding addresses and visualizing routes. Please see `ui/GOOGLE_MAPS_API_SETUP.md` for instructions on how to set up your API key.

```bash
$ docker network create shared_network
```

```bash
$ docker-compose up --build -d
```

To stop the services:

```bash
$ docker-compose down
```

Populate the database:
```bash
cd api
cp .env.original .env
docker-compose up --build -d
```

## Access FastAPI docs

URL = http://localhost:8000/docs

To try the endpoints you need to authorize with:
- user: `admin@example.com`
- password: `admin`

## Access the UI

URL = http://localhost:9090

- Login with:
  - user: `admin@example.com`
  - pass: `admin`
- You can input trip parameters
- You can get fare and duration predictions
- You can view taxi demand by region
- You can provide feedback on prediction accuracy

## Tests

**Note: Test functionality is not implemented yet and is planned for future releases.**

### 1. Module Tests

#### 1.1. API

```bash
$ cd api/
$ docker build -t fastapi_test --progress=plain --target test .
```

#### 1.2. Model

```bash
$ cd model/
$ docker build -t model_test --progress=plain --target test .
```

#### 1.3 UI

```bash
$ cd ui/
$ docker build -t ui_test --progress=plain --target test .
```

### 2. Integration Tests

```bash
$ pip3 install -r tests/requirements.txt
$ python tests/test_integration.py
```

## Stress Testing

**Note: Stress testing functionality is not implemented yet and is planned for future releases.**

The project includes a Locust configuration for stress testing the API:

```bash
$ cd stress_test
$ locust -f locustfile.py
```

Then access the Locust UI at http://localhost:8089/ 
 