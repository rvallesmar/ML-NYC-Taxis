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

1. **data_exploration.ipynb**: Exploratory data analysis of the NYC taxi dataset.
   - Analyzes data distributions
   - Visualizes relationships between features
   - Identifies patterns and outliers

2. **model_training.ipynb**: Model development and evaluation.
   - Data preprocessing
   - Feature engineering
   - Model training and hyperparameter tuning
   - Performance evaluation

3. **model_evaluation.ipynb**: Comprehensive model evaluation and interpretation.
   - Classification metrics calculation
   - Confusion matrix visualization
   - ROC and Precision-Recall curves
   - Feature importance analysis
   - SHAP-based model interpretation
   - Error analysis

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