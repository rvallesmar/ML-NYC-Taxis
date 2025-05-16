# Data Science Notebooks

This directory contains Jupyter notebooks for exploratory data analysis and model development for the NYC Taxi Prediction project.

## Setup

### Create a Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Available Notebooks

### Data Exploration

1. **data_exploration.ipynb**: Exploratory data analysis of the NYC taxi dataset.
   - Analyzes data distributions
   - Visualizes relationships between features
   - Identifies patterns and outliers

2. **eda.ipynb**: Additional exploratory data analysis with a focus on:
   - Temporal patterns (time of day, day of week, seasonality)
   - Geographical patterns of pickups and dropoffs
   - Passenger count distribution

3. **zones.ipynb**: Analysis of NYC taxi zones for demand prediction.
   - Visualizes taxi zone boundaries
   - Analyzes pickup and dropoff distributions by zone
   - Maps demand patterns across different regions

### Model Development

4. **model_training.ipynb**: General model development pipeline.
   - Data preprocessing
   - Feature engineering
   - Model training and hyperparameter tuning
   - Performance evaluation

5. **basic_models.ipynb**: Implementation of baseline regression models.
   - Linear Regression
   - Decision Trees
   - Simple ensemble methods
   - Comparative analysis of baseline performance

6. **rf_model_training.ipynb**: Random Forest model implementation.
   - Hyperparameter optimization
   - Feature importance analysis
   - Cross-validation evaluation

7. **lr_model_training.ipynb**: Linear Regression model implementation.
   - Feature selection
   - Regularization techniques (Ridge, Lasso)
   - Model diagnostics

8. **mlp_model_train.ipynb**: Multi-layer Perceptron neural network implementation.
   - Network architecture design
   - Hyperparameter tuning
   - Training and validation analysis

9. **XGBooots_model_training/**: Directory with XGBoost model implementation notebooks.
   - Gradient boosting implementation
   - Hyperparameter optimization
   - Advanced feature engineering
   - Final model selection

### Model Evaluation

10. **model_evaluation.ipynb**: Comprehensive model evaluation and interpretation.
    - Performance metrics calculation
    - Model comparison
    - Error analysis
    - Feature importance visualization

## Best Practices

When working with these notebooks:

1. **Reproducibility**: Always set random seeds where applicable
2. **Memory Management**: Use efficient data types and clear memory when processing large datasets
3. **Documentation**: Document your findings and methodology within the notebook
4. **Version Control**: Commit significant changes to the notebooks with clear messages
5. **Sharing Results**: When sharing insights, export static versions (HTML/PDF) for teammates who don't run the notebooks

## Adding New Notebooks

When adding new notebooks to this directory, please:

1. Follow the naming convention: `purpose_description.ipynb`
2. Add a brief description to this README
3. Include markdown cells explaining the notebook's purpose and approach
4. Add any new dependencies to `requirements.txt` 