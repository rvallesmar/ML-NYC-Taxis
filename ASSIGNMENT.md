# NYC Taxi Prediction Project: Implementation Tasks

This project aims to predict taxi fare, duration, and demand in NYC. The backbone of the application has been set up, but several key components need to be implemented.

## Project Structure

```
nyc-taxi-prediction/
├── api/                  # FastAPI backend
│   ├── app/              # Application code
│   │   ├── auth/         # Authentication and user management
│   │   │   ├── __init__.py
│   │   │   ├── jwt.py    # JWT token generation and validation
│   │   │   ├── router.py # Authentication endpoints
│   │   │   └── schema.py # Authentication data schemas
│   │   ├── feedback/     # User feedback collection endpoints
│   │   │   ├── __init__.py
│   │   │   ├── models.py # Database models for feedback
│   │   │   ├── router.py # Feedback collection endpoints
│   │   │   └── schema.py # Feedback data schemas
│   │   ├── model/        # Prediction endpoints for fare, duration, and demand
│   │   │   ├── router.py # ML model prediction endpoints
│   │   │   ├── schema.py # Prediction request/response schemas
│   │   │   └── services.py # Service integration with ML service
│   │   ├── user/         # User management
│   │   │   ├── __init__.py
│   │   │   ├── models.py # Database models for users
│   │   │   ├── router.py # User management endpoints
│   │   │   └── schema.py # User data schemas
│   │   ├── db.py         # Database connection and session management
│   │   ├── settings.py   # API configuration settings
│   │   └── utils.py      # Utility functions
│   ├── Dockerfile        # API Docker configuration
│   ├── main.py           # FastAPI application entry point
│   └── populate_db.py    # Database initialization script
├── data/                 # Data files for the project
│   └── taxi_zones/       # NYC taxi zone shapefiles
├── db_data/              # Database-related files and persistent storage
├── model/                # ML model service
│   ├── ml_service.py     # Model service implementation for predictions
│   ├── settings.py       # ML service configuration settings
│   ├── __init__.py       # Package initialization
│   ├── models/           # Directory for stored ML models
│   │   ├── model_fa.pkl  # Fare prediction model
│   │   ├── model_tt.pkl  # Duration prediction model
│   │   ├── min_max_scaler.pkl   # Scaler for preprocessing
│   │   └── oneh_time_of_day.pkl # OneHotEncoder for time features
│   └── Dockerfile        # Model Docker configuration
├── notebooks/            # Jupyter notebooks for exploration
│   └── XGBooots_model_training/ # Model training notebooks
├── stress_test/          # Load testing with Locust
├── tests/                # Integration tests
├── ui/                   # Streamlit UI
│   ├── app/              # UI application
│   │   ├── settings.py   # UI configuration settings
│   │   └── taxi_prediction_app.py # Main UI application
│   ├── tests/            # UI tests
│   └── Dockerfile        # UI Docker configuration
├── docker-compose.yml    # Services orchestration
└── README.md             # Project documentation
```

## Implementation Tasks

### 1. Model Service (`model/`)

- [x] Implement data loading and preprocessing utilities
- [x] Develop feature engineering functions for taxi data
- [x] Train and save fare prediction model
- [x] Train and save duration prediction model
- [x] Implement the `predict_fare_duration()` function in `ml_service.py`
- [x] Implement the `predict_demand()` function in `ml_service.py`
- [ ] Add unit tests for model performance

### 2. API Service (`api/`)

- [x] Implement database models for user, feedback, and other entities
- [x] Complete authentication mechanisms
- [x] Implement user management endpoints
- [x] Implement the prediction endpoints in `model/router.py`
- [x] Implement feedback collection and storage
- [x] Add proper validation and error handling
- [ ] Add unit tests for API endpoints

### 3. UI (`ui/`)

- [x] Implement the UI layout and design
- [x] Implement geospatial visualizations for routes
- [x] Implement the rating system for user feedback
- [ ] Add heatmap visualization for demand prediction
- [ ] Implement additional data visualizations (time trends, etc.)
- [ ] Improve error handling and user feedback

### 4. Deployment and Testing

- [ ] Complete integration tests
- [ ] Implement stress testing scenarios
- [ ] Document API endpoints
- [ ] Create user documentation

## Development Workflow

### 1. Using Jupyter Notebooks

The project includes the following Jupyter notebooks for data exploration and model development:

- **Data Exploration**:
  - `data_exploration.ipynb`: Analyze NYC taxi trip data distributions and patterns
  - `eda.ipynb`: Additional exploratory data analysis
  - `zones.ipynb`: Analysis of NYC taxi zones for demand prediction

- **Model Development**:
  - `model_training.ipynb`: General model training pipeline
  - `basic_models.ipynb`: Implementation of baseline regression models
  - `rf_model_training.ipynb`: Random Forest model implementation
  - `lr_model_training.ipynb`: Linear Regression model implementation
  - `mlp_model_train.ipynb`: Multi-layer Perceptron neural network implementation
  - `XGBooots_model_training/`: Directory with XGBoost model implementation notebooks

- **Model Evaluation**:
  - `model_evaluation.ipynb`: Evaluation metrics and performance analysis

To work with the notebooks:
```bash
$ pip install -r notebooks/requirements.txt
$ pip install jupyter
$ jupyter notebook
```

### 2. Code Style

This project follows the [Black](https://black.readthedocs.io/) code style and uses [isort](https://pycqa.github.io/isort/) for import sorting.

```bash
$ isort --profile=black . && black --line-length 88 .
```

### 3. Development Process

1. Start by implementing the models in the `model/` directory
2. Next, complete the API endpoints in `api/`
3. Finally, enhance the UI with visualizations and improved UX
4. Run tests to ensure everything works together

## Evaluation Metrics

- Fare prediction: RMSE, MAE, R²
- Duration prediction: RMSE, MAE, R²
- Demand prediction: RMSE, MAE, R²

## Completion Criteria

- All Docker containers start successfully
- API endpoints return correct predictions
- UI displays predictions and visualizations
- All tests pass
- System can handle concurrent requests 