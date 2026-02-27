# Train and Deploy a Machine Learning Model

## Overview

This tutorial guides you through building, training, and deploying a machine learning classification model on Databricks. You'll use scikit-learn to predict wine quality, MLflow to track experiments, and Hyperopt for automated hyperparameter tuning.

## Prerequisites

- Access to a Databricks workspace with Unity Catalog enabled
- A running cluster with ML Runtime (see [Quick Start Guide](quickstart.md))
- Basic knowledge of Python and machine learning concepts
- MLflow and scikit-learn libraries (pre-installed on ML Runtime)

## What You'll Learn

- How to load and explore datasets for ML
- How to prepare data for machine learning
- How to train classification models with scikit-learn
- How to track experiments with MLflow
- How to perform hyperparameter tuning with Hyperopt
- How to register and deploy models
- How to make predictions with deployed models

## Step 1: Load and Explore the Dataset

### Load Wine Quality Dataset

```python
# Import required libraries
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

# Load wine quality dataset
# Using UCI Machine Learning Repository wine quality data
wine_data_url = "https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv"

# Read data
wine_df = pd.read_csv(wine_data_url, sep=';')

print(f"Dataset shape: {wine_df.shape}")
print(f"Number of features: {wine_df.shape[1] - 1}")
print(f"Number of samples: {wine_df.shape[0]}")

# Display first few rows
display(wine_df.head(10))
```

### Explore Data Statistics

```python
# Statistical summary
print("=== Dataset Statistics ===")
display(wine_df.describe())

# Check for missing values
print("\n=== Missing Values ===")
print(wine_df.isnull().sum())

# Check data types
print("\n=== Data Types ===")
print(wine_df.dtypes)

# Quality distribution
print("\n=== Quality Distribution ===")
print(wine_df['quality'].value_counts().sort_index())
```

### Visualize Data Distribution

```python
# Create visualizations
fig, axes = plt.subplots(3, 4, figsize=(16, 12))
fig.suptitle('Wine Features Distribution', fontsize=16, fontweight='bold')

for idx, column in enumerate(wine_df.columns[:-1]):  # Exclude quality column
    ax = axes[idx // 4, idx % 4]
    ax.hist(wine_df[column], bins=30, edgecolor='black', alpha=0.7)
    ax.set_title(column)
    ax.set_xlabel('Value')
    ax.set_ylabel('Frequency')

plt.tight_layout()
display(fig)

# Quality distribution
fig, ax = plt.subplots(figsize=(10, 6))
wine_df['quality'].value_counts().sort_index().plot(kind='bar', ax=ax, color='steelblue')
ax.set_title('Wine Quality Distribution', fontsize=14, fontweight='bold')
ax.set_xlabel('Quality Score')
ax.set_ylabel('Count')
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
display(fig)
```

### Correlation Analysis

```python
# Correlation heatmap
fig, ax = plt.subplots(figsize=(12, 10))
correlation_matrix = wine_df.corr()
sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm',
            center=0, ax=ax, square=True, linewidths=1)
ax.set_title('Feature Correlation Heatmap', fontsize=14, fontweight='bold')
plt.tight_layout()
display(fig)

# Top correlations with quality
quality_correlations = correlation_matrix['quality'].sort_values(ascending=False)
print("\n=== Correlations with Quality ===")
print(quality_correlations)
```

## Step 2: Prepare Data for Machine Learning

### Create Binary Classification Target

```python
# Convert to binary classification: high quality (>=7) vs lower quality (<7)
wine_df['high_quality'] = (wine_df['quality'] >= 7).astype(int)

print(f"High quality wines: {wine_df['high_quality'].sum()}")
print(f"Lower quality wines: {len(wine_df) - wine_df['high_quality'].sum()}")
print(f"High quality percentage: {wine_df['high_quality'].mean() * 100:.2f}%")

# Visualize class distribution
fig, ax = plt.subplots(figsize=(8, 6))
wine_df['high_quality'].value_counts().plot(kind='bar', ax=ax, color=['#e74c3c', '#2ecc71'])
ax.set_title('Binary Classification Target Distribution', fontsize=14, fontweight='bold')
ax.set_xlabel('Class (0=Lower Quality, 1=High Quality)')
ax.set_ylabel('Count')
ax.set_xticklabels(['Lower Quality', 'High Quality'], rotation=0)
plt.tight_layout()
display(fig)
```

### Split Data into Train and Test Sets

```python
# Separate features and target
X = wine_df.drop(['quality', 'high_quality'], axis=1)
y = wine_df['high_quality']

# Split data: 80% train, 20% test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Training set size: {len(X_train)} samples")
print(f"Test set size: {len(X_test)} samples")
print(f"Training set high quality: {y_train.mean() * 100:.2f}%")
print(f"Test set high quality: {y_test.mean() * 100:.2f}%")
```

### Feature Scaling

```python
# Standardize features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Convert back to DataFrame for easier handling
X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns, index=X_train.index)
X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns, index=X_test.index)

print("Features scaled successfully")
print(f"Training set mean: {X_train_scaled.mean().mean():.4f}")
print(f"Training set std: {X_train_scaled.std().mean():.4f}")
```

## Step 3: Train Baseline Model with MLflow Tracking

### Set up MLflow Experiment

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.metrics import confusion_matrix, classification_report

# Set experiment name
mlflow.set_experiment("/Users/user@company.com/wine-quality-classification")

print("MLflow tracking URI:", mlflow.get_tracking_uri())
print("Experiment ID:", mlflow.get_experiment_by_name("/Users/user@company.com/wine-quality-classification").experiment_id)
```

### Train Baseline Random Forest Model

```python
def evaluate_model(model, X_test, y_test):
    """
    Evaluate model and return metrics
    """
    # Make predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]

    # Calculate metrics
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1_score': f1_score(y_test, y_pred),
        'roc_auc': roc_auc_score(y_test, y_pred_proba)
    }

    return metrics, y_pred, y_pred_proba

# Start MLflow run
with mlflow.start_run(run_name="baseline_random_forest"):
    # Log parameters
    params = {
        'n_estimators': 100,
        'max_depth': 10,
        'random_state': 42
    }
    mlflow.log_params(params)

    # Train model
    rf_model = RandomForestClassifier(**params)
    rf_model.fit(X_train_scaled, y_train)

    # Evaluate model
    metrics, y_pred, y_pred_proba = evaluate_model(rf_model, X_test_scaled, y_test)

    # Log metrics
    mlflow.log_metrics(metrics)

    # Log model
    mlflow.sklearn.log_model(rf_model, "model")

    # Log feature importance
    feature_importance = pd.DataFrame({
        'feature': X_train.columns,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)

    mlflow.log_dict(feature_importance.to_dict(), "feature_importance.json")

    print("=== Baseline Model Performance ===")
    for metric_name, metric_value in metrics.items():
        print(f"{metric_name}: {metric_value:.4f}")

    # Print classification report
    print("\n=== Classification Report ===")
    print(classification_report(y_test, y_pred, target_names=['Lower Quality', 'High Quality']))
```

### Visualize Model Performance

```python
from sklearn.metrics import confusion_matrix, roc_curve, auc

# Confusion matrix
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Plot confusion matrix
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[0],
            xticklabels=['Lower', 'High'], yticklabels=['Lower', 'High'])
axes[0].set_title('Confusion Matrix', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Predicted Quality')
axes[0].set_ylabel('Actual Quality')

# ROC curve
fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
roc_auc = auc(fpr, tpr)

axes[1].plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
axes[1].plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Classifier')
axes[1].set_xlim([0.0, 1.0])
axes[1].set_ylim([0.0, 1.05])
axes[1].set_xlabel('False Positive Rate')
axes[1].set_ylabel('True Positive Rate')
axes[1].set_title('ROC Curve', fontsize=12, fontweight='bold')
axes[1].legend(loc="lower right")
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
display(fig)

# Feature importance
fig, ax = plt.subplots(figsize=(10, 6))
feature_importance.plot(kind='barh', x='feature', y='importance', ax=ax, color='steelblue', legend=False)
ax.set_title('Feature Importance', fontsize=14, fontweight='bold')
ax.set_xlabel('Importance')
ax.set_ylabel('Feature')
ax.invert_yaxis()
plt.tight_layout()
display(fig)
```

## Step 4: Hyperparameter Tuning with Hyperopt

### Define Search Space

```python
from hyperopt import fmin, tpe, hp, Trials, STATUS_OK
from hyperopt.pyll import scope

# Define hyperparameter search space
search_space = {
    'n_estimators': scope.int(hp.quniform('n_estimators', 50, 300, 10)),
    'max_depth': scope.int(hp.quniform('max_depth', 5, 30, 1)),
    'min_samples_split': scope.int(hp.quniform('min_samples_split', 2, 20, 1)),
    'min_samples_leaf': scope.int(hp.quniform('min_samples_leaf', 1, 10, 1)),
    'max_features': hp.choice('max_features', ['sqrt', 'log2', None]),
    'random_state': 42
}

print("Hyperparameter search space defined")
```

### Define Objective Function

```python
def objective_function(params):
    """
    Objective function for Hyperopt optimization
    """
    with mlflow.start_run(nested=True):
        # Log parameters
        mlflow.log_params(params)

        # Train model
        model = RandomForestClassifier(**params)
        model.fit(X_train_scaled, y_train)

        # Evaluate
        metrics, _, _ = evaluate_model(model, X_test_scaled, y_test)

        # Log metrics
        mlflow.log_metrics(metrics)

        # Return loss (negative F1 score for minimization)
        loss = -metrics['f1_score']

        return {'loss': loss, 'status': STATUS_OK, 'metrics': metrics}
```

### Run Hyperparameter Optimization

```python
# Create parent run for hyperparameter tuning
with mlflow.start_run(run_name="hyperparameter_tuning"):
    # Initialize trials object
    trials = Trials()

    # Run optimization
    print("Starting hyperparameter optimization...")
    best_params = fmin(
        fn=objective_function,
        space=search_space,
        algo=tpe.suggest,
        max_evals=20,
        trials=trials
    )

    # Convert best params back to correct format
    best_params['n_estimators'] = int(best_params['n_estimators'])
    best_params['max_depth'] = int(best_params['max_depth'])
    best_params['min_samples_split'] = int(best_params['min_samples_split'])
    best_params['min_samples_leaf'] = int(best_params['min_samples_leaf'])
    best_params['max_features'] = ['sqrt', 'log2', None][best_params['max_features']]
    best_params['random_state'] = 42

    # Log best parameters
    mlflow.log_params({"best_" + k: v for k, v in best_params.items()})

    print("\n=== Best Hyperparameters ===")
    for param, value in best_params.items():
        print(f"{param}: {value}")

    # Train final model with best parameters
    print("\nTraining final model with best parameters...")
    best_model = RandomForestClassifier(**best_params)
    best_model.fit(X_train_scaled, y_train)

    # Evaluate best model
    best_metrics, best_y_pred, best_y_pred_proba = evaluate_model(best_model, X_test_scaled, y_test)

    # Log best metrics
    mlflow.log_metrics({"best_" + k: v for k, v in best_metrics.items()})

    # Log best model
    mlflow.sklearn.log_model(best_model, "best_model")

    print("\n=== Best Model Performance ===")
    for metric_name, metric_value in best_metrics.items():
        print(f"{metric_name}: {metric_value:.4f}")
```

### Visualize Hyperparameter Tuning Results

```python
# Extract results from trials
trial_losses = [trial['result']['loss'] for trial in trials.trials]
trial_f1_scores = [-loss for loss in trial_losses]

# Plot optimization progress
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(range(1, len(trial_f1_scores) + 1), trial_f1_scores, marker='o', linestyle='-', linewidth=2)
ax.axhline(y=max(trial_f1_scores), color='r', linestyle='--', label=f'Best F1: {max(trial_f1_scores):.4f}')
ax.set_xlabel('Iteration', fontsize=12)
ax.set_ylabel('F1 Score', fontsize=12)
ax.set_title('Hyperparameter Optimization Progress', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend()
plt.tight_layout()
display(fig)
```

## Step 5: Compare Multiple Models

### Train Different Model Types

```python
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.naive_bayes import GaussianNB

models = {
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
    'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
    'SVM': SVC(probability=True, random_state=42),
    'Naive Bayes': GaussianNB()
}

# Train and evaluate all models
results = []

for model_name, model in models.items():
    with mlflow.start_run(run_name=f"comparison_{model_name}"):
        print(f"\nTraining {model_name}...")

        # Log model type
        mlflow.log_param("model_type", model_name)

        # Train
        model.fit(X_train_scaled, y_train)

        # Evaluate
        metrics, _, _ = evaluate_model(model, X_test_scaled, y_test)

        # Log metrics
        mlflow.log_metrics(metrics)

        # Log model
        mlflow.sklearn.log_model(model, "model")

        # Store results
        results.append({
            'Model': model_name,
            **metrics
        })

        print(f"{model_name} - F1 Score: {metrics['f1_score']:.4f}")

# Create comparison DataFrame
results_df = pd.DataFrame(results)
display(results_df.sort_values('f1_score', ascending=False))
```

### Visualize Model Comparison

```python
# Compare models
fig, ax = plt.subplots(figsize=(12, 6))

metrics_to_plot = ['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc']
x = np.arange(len(results_df))
width = 0.15

for idx, metric in enumerate(metrics_to_plot):
    offset = width * (idx - 2)
    ax.bar(x + offset, results_df[metric], width, label=metric.replace('_', ' ').title())

ax.set_xlabel('Model', fontsize=12)
ax.set_ylabel('Score', fontsize=12)
ax.set_title('Model Comparison', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(results_df['Model'], rotation=45, ha='right')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')
ax.set_ylim([0, 1.1])

plt.tight_layout()
display(fig)
```

## Step 6: Register Model to MLflow Model Registry

### Register Best Model

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Get the best run
experiment = mlflow.get_experiment_by_name("/Users/user@company.com/wine-quality-classification")
runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id], order_by=["metrics.f1_score DESC"])
best_run_id = runs.iloc[0]['run_id']

print(f"Best run ID: {best_run_id}")
print(f"Best F1 score: {runs.iloc[0]['metrics.f1_score']:.4f}")

# Register model
model_name = "wine_quality_classifier"
model_uri = f"runs:/{best_run_id}/best_model"

try:
    # Register model
    model_version = mlflow.register_model(model_uri, model_name)
    print(f"\nModel registered: {model_name}")
    print(f"Version: {model_version.version}")
except Exception as e:
    print(f"Model already exists: {e}")
    # Get latest version
    latest_versions = client.get_latest_versions(model_name)
    model_version = latest_versions[0]
    print(f"Using existing model version: {model_version.version}")
```

### Add Model Description and Tags

```python
# Update model description
client.update_registered_model(
    name=model_name,
    description="Random Forest classifier for wine quality prediction. Predicts whether a wine is high quality (score >= 7) based on physicochemical properties."
)

# Add tags to model version
client.set_model_version_tag(
    name=model_name,
    version=model_version.version,
    key="task",
    value="binary_classification"
)

client.set_model_version_tag(
    name=model_name,
    version=model_version.version,
    key="dataset",
    value="wine_quality_red"
)

print("Model description and tags updated")
```

### Transition Model to Production

```python
# Transition model to Production stage
client.transition_model_version_stage(
    name=model_name,
    version=model_version.version,
    stage="Production",
    archive_existing_versions=True
)

print(f"Model {model_name} version {model_version.version} transitioned to Production")
```

## Step 7: Load and Use Registered Model

### Load Production Model

```python
# Load production model
production_model = mlflow.pyfunc.load_model(f"models:/{model_name}/Production")

print(f"Loaded production model: {model_name}")
```

### Make Predictions

```python
# Prepare new data for prediction
new_wine_samples = pd.DataFrame({
    'fixed acidity': [7.4, 8.1, 7.9],
    'volatile acidity': [0.70, 0.56, 0.48],
    'citric acid': [0.00, 0.15, 0.28],
    'residual sugar': [1.9, 2.0, 2.3],
    'chlorides': [0.076, 0.071, 0.070],
    'free sulfur dioxide': [11.0, 15.0, 18.0],
    'total sulfur dioxide': [34.0, 40.0, 45.0],
    'density': [0.9978, 0.9980, 0.9968],
    'pH': [3.51, 3.42, 3.36],
    'sulphates': [0.56, 0.68, 0.58],
    'alcohol': [9.4, 9.8, 10.5]
})

print("=== New Wine Samples ===")
display(new_wine_samples)

# Scale features
new_samples_scaled = scaler.transform(new_wine_samples)
new_samples_scaled = pd.DataFrame(new_samples_scaled, columns=new_wine_samples.columns)

# Make predictions
predictions = production_model.predict(new_samples_scaled)
prediction_labels = ['Lower Quality' if pred == 0 else 'High Quality' for pred in predictions]

# Display predictions
results = new_wine_samples.copy()
results['Predicted Quality'] = prediction_labels
results['Prediction Confidence'] = predictions

print("\n=== Predictions ===")
display(results)
```

### Batch Scoring

```python
def batch_score(model, data, batch_size=100):
    """
    Score data in batches
    """
    predictions = []

    for i in range(0, len(data), batch_size):
        batch = data.iloc[i:i+batch_size]
        batch_scaled = scaler.transform(batch)
        batch_predictions = model.predict(batch_scaled)
        predictions.extend(batch_predictions)

    return np.array(predictions)

# Score test set in batches
batch_predictions = batch_score(production_model, X_test, batch_size=50)

print(f"Batch scoring completed: {len(batch_predictions)} predictions")
print(f"Accuracy: {accuracy_score(y_test, batch_predictions):.4f}")
```

## Step 8: Deploy Model as REST API (Conceptual)

### Create Model Serving Endpoint

```python
# Note: Actual model serving requires Databricks Model Serving feature
# This is a conceptual example

# Example: Create serving endpoint via API
serving_config = {
    "name": "wine-quality-endpoint",
    "config": {
        "served_models": [{
            "model_name": model_name,
            "model_version": model_version.version,
            "workload_size": "Small",
            "scale_to_zero_enabled": True
        }]
    }
}

print("Model serving configuration:")
print(serving_config)
print("\nNote: Use Databricks UI or REST API to create actual serving endpoint")
```

### Test Model Endpoint (Conceptual)

```python
# Example inference request
import json

inference_request = {
    "dataframe_records": [
        {
            "fixed acidity": 7.4,
            "volatile acidity": 0.70,
            "citric acid": 0.00,
            "residual sugar": 1.9,
            "chlorides": 0.076,
            "free sulfur dioxide": 11.0,
            "total sulfur dioxide": 34.0,
            "density": 0.9978,
            "pH": 3.51,
            "sulphates": 0.56,
            "alcohol": 9.4
        }
    ]
}

print("Example inference request:")
print(json.dumps(inference_request, indent=2))
```

## Best Practices

### 1. Experiment Tracking

```python
# Always use MLflow tracking
with mlflow.start_run():
    mlflow.log_params(params)
    mlflow.log_metrics(metrics)
    mlflow.log_artifacts("plots/")
    mlflow.sklearn.log_model(model, "model")
```

### 2. Model Versioning

```python
# Use semantic versioning in model descriptions
client.update_model_version(
    name=model_name,
    version=model_version.version,
    description="v1.0.0 - Initial production model with Random Forest"
)
```

### 3. Model Validation

```python
def validate_model(model, X_test, y_test, threshold=0.85):
    """
    Validate model meets performance requirements
    """
    metrics, _, _ = evaluate_model(model, X_test, y_test)

    if metrics['f1_score'] < threshold:
        raise ValueError(f"Model F1 score {metrics['f1_score']:.4f} below threshold {threshold}")

    print(f"Model validation passed: F1 = {metrics['f1_score']:.4f}")
    return True
```

### 4. Feature Engineering Pipeline

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# Create complete pipeline
ml_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', RandomForestClassifier(**best_params))
])

# Fit pipeline
ml_pipeline.fit(X_train, y_train)

# Log complete pipeline
mlflow.sklearn.log_model(ml_pipeline, "pipeline_model")
```

## Troubleshooting

### MLflow Tracking Issues

```python
# Verify MLflow setup
print("MLflow tracking URI:", mlflow.get_tracking_uri())
print("Active experiment:", mlflow.get_experiment(mlflow.active_run().info.experiment_id).name if mlflow.active_run() else "None")
```

### Model Registry Connection

```python
# Test model registry connection
try:
    registered_models = client.search_registered_models()
    print(f"Connected to model registry. Found {len(registered_models)} models.")
except Exception as e:
    print(f"Error connecting to model registry: {e}")
```

## Next Steps

- **[Deploy with Model Serving](../ml/model-serving.md)**: Production deployment
- **[Feature Store](../ml/feature-store.md)**: Centralized feature management
- **[AutoML](../ml/automl.md)**: Automated model training
- **[MLflow Guide](../ml/mlflow.md)**: Advanced MLflow features

## Summary

In this tutorial, you learned how to:

✅ Load and explore datasets for machine learning
✅ Prepare and split data for training
✅ Train classification models with scikit-learn
✅ Track experiments with MLflow
✅ Perform hyperparameter tuning with Hyperopt
✅ Compare multiple model types
✅ Register models in MLflow Model Registry
✅ Deploy models to production
✅ Make predictions with registered models

You're now ready to build and deploy production ML models on Databricks!
