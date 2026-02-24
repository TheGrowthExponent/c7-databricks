# MLflow with Databricks SDK

## Overview

MLflow is an open-source platform for managing the end-to-end machine learning lifecycle. This guide covers using MLflow on Databricks for experiment tracking, model management, and deployment.

## Table of Contents

1. [Experiment Tracking](#experiment-tracking)
2. [Model Logging](#model-logging)
3. [Model Registry](#model-registry)
4. [Model Deployment](#model-deployment)
5. [AutoML Integration](#automl-integration)
6. [Advanced Patterns](#advanced-patterns)

---

## Experiment Tracking

### Basic Experiment Setup

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

# Set experiment
mlflow.set_experiment("/Users/user@example.com/my-ml-experiment")

# Start a run
with mlflow.start_run(run_name="random-forest-v1"):
    # Log parameters
    n_estimators = 100
    max_depth = 10
    
    mlflow.log_param("n_estimators", n_estimators)
    mlflow.log_param("max_depth", max_depth)
    mlflow.log_param("model_type", "RandomForest")
    
    # Train model
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Log metrics
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')
    
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("f1_score", f1)
    
    # Log model
    mlflow.sklearn.log_model(model, "model")
    
    print(f"Accuracy: {accuracy:.4f}")
    print(f"F1 Score: {f1:.4f}")
```

### Nested Runs

```python
import mlflow

# Parent run for hyperparameter tuning
with mlflow.start_run(run_name="hyperparameter-tuning") as parent_run:
    mlflow.log_param("tuning_strategy", "grid_search")
    
    # Child runs for each configuration
    for n_estimators in [50, 100, 200]:
        for max_depth in [5, 10, 15]:
            with mlflow.start_run(nested=True, run_name=f"n{n_estimators}_d{max_depth}"):
                mlflow.log_param("n_estimators", n_estimators)
                mlflow.log_param("max_depth", max_depth)
                
                # Train and evaluate
                model = RandomForestClassifier(
                    n_estimators=n_estimators,
                    max_depth=max_depth
                )
                model.fit(X_train, y_train)
                
                accuracy = accuracy_score(y_test, model.predict(X_test))
                mlflow.log_metric("accuracy", accuracy)
                
                print(f"Config: n={n_estimators}, d={max_depth}, acc={accuracy:.4f}")
```

### Logging Artifacts

```python
import mlflow
import matplotlib.pyplot as plt
import pandas as pd

with mlflow.start_run():
    # Log parameters and metrics
    mlflow.log_param("algorithm", "xgboost")
    mlflow.log_metric("rmse", 0.85)
    
    # Save and log confusion matrix
    plt.figure(figsize=(8, 6))
    # ... create confusion matrix plot ...
    plt.savefig("confusion_matrix.png")
    mlflow.log_artifact("confusion_matrix.png")
    
    # Log feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    feature_importance.to_csv("feature_importance.csv", index=False)
    mlflow.log_artifact("feature_importance.csv")
    
    # Log entire directory
    mlflow.log_artifacts("output_data/", artifact_path="data")
```

### Autologging

```python
import mlflow

# Enable autologging for scikit-learn
mlflow.sklearn.autolog()

# Enable autologging for TensorFlow/Keras
mlflow.tensorflow.autolog()

# Enable autologging for PyTorch
mlflow.pytorch.autolog()

# Enable autologging for XGBoost
mlflow.xgboost.autolog()

# Now training automatically logs parameters, metrics, and models
from sklearn.ensemble import GradientBoostingClassifier

model = GradientBoostingClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Autolog captures everything automatically!
```

---

## Model Logging

### Scikit-learn Models

```python
import mlflow.sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

with mlflow.start_run():
    # Create pipeline
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', LogisticRegression())
    ])
    
    pipeline.fit(X_train, y_train)
    
    # Log the entire pipeline
    mlflow.sklearn.log_model(
        pipeline,
        "model",
        signature=mlflow.models.infer_signature(X_train, y_train)
    )
    
    # Log with input example
    mlflow.sklearn.log_model(
        pipeline,
        "model_with_example",
        input_example=X_train[:5]
    )
```

### TensorFlow/Keras Models

```python
import mlflow.tensorflow
import tensorflow as tf

with mlflow.start_run():
    # Build model
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(128, activation='relu', input_shape=(n_features,)),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(n_classes, activation='softmax')
    ])
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Train
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=10,
        batch_size=32
    )
    
    # Log model
    mlflow.tensorflow.log_model(
        model,
        "model",
        signature=mlflow.models.infer_signature(X_train, model.predict(X_train))
    )
    
    # Log training history
    for epoch, (loss, val_loss) in enumerate(zip(history.history['loss'], 
                                                   history.history['val_loss'])):
        mlflow.log_metric("train_loss", loss, step=epoch)
        mlflow.log_metric("val_loss", val_loss, step=epoch)
```

### PyTorch Models

```python
import mlflow.pytorch
import torch
import torch.nn as nn

class NeuralNetwork(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(NeuralNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, num_classes)
    
    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        return out

with mlflow.start_run():
    model = NeuralNetwork(input_size=n_features, hidden_size=128, num_classes=10)
    
    # Training loop
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()
    
    for epoch in range(10):
        # Training code...
        loss = train_epoch(model, train_loader, optimizer, criterion)
        mlflow.log_metric("train_loss", loss, step=epoch)
    
    # Log model
    mlflow.pytorch.log_model(
        model,
        "model",
        signature=mlflow.models.infer_signature(X_train.numpy(), 
                                                model(X_train).detach().numpy())
    )
```

### Custom Python Models

```python
import mlflow.pyfunc
import pandas as pd

class CustomPredictor(mlflow.pyfunc.PythonModel):
    """Custom model with preprocessing and postprocessing"""
    
    def load_context(self, context):
        """Load artifacts and setup model"""
        import joblib
        self.model = joblib.load(context.artifacts["model"])
        self.scaler = joblib.load(context.artifacts["scaler"])
    
    def predict(self, context, model_input):
        """Custom prediction logic"""
        # Preprocess
        scaled_input = self.scaler.transform(model_input)
        
        # Predict
        predictions = self.model.predict(scaled_input)
        
        # Postprocess
        result = pd.DataFrame({
            'prediction': predictions,
            'confidence': self.model.predict_proba(scaled_input).max(axis=1)
        })
        
        return result

# Log custom model
with mlflow.start_run():
    artifacts = {
        "model": "trained_model.pkl",
        "scaler": "scaler.pkl"
    }
    
    mlflow.pyfunc.log_model(
        artifact_path="custom_model",
        python_model=CustomPredictor(),
        artifacts=artifacts
    )
```

---

## Model Registry

### Register Model

```python
import mlflow

# Register model from run
with mlflow.start_run() as run:
    # Train and log model
    mlflow.sklearn.log_model(model, "model")
    
    # Register to Model Registry
    model_uri = f"runs:/{run.info.run_id}/model"
    mlflow.register_model(model_uri, "production_model")

# Register from existing run
run_id = "abc123def456"
model_uri = f"runs:/{run_id}/model"
result = mlflow.register_model(model_uri, "my_model")

print(f"Model registered: {result.name}")
print(f"Version: {result.version}")
```

### Model Versioning

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# List all versions
versions = client.search_model_versions("name='production_model'")
for version in versions:
    print(f"Version {version.version}: {version.current_stage}")

# Get specific version
model_version = client.get_model_version("production_model", version=3)
print(f"Version {model_version.version}")
print(f"Status: {model_version.status}")
print(f"Stage: {model_version.current_stage}")
```

### Model Stages

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Transition to Staging
client.transition_model_version_stage(
    name="production_model",
    version=2,
    stage="Staging",
    archive_existing_versions=False
)

# Transition to Production
client.transition_model_version_stage(
    name="production_model",
    version=2,
    stage="Production",
    archive_existing_versions=True  # Archive old production versions
)

# Archive a version
client.transition_model_version_stage(
    name="production_model",
    version=1,
    stage="Archived"
)
```

### Model Aliases (New Feature)

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Set alias for a version
client.set_registered_model_alias(
    name="production_model",
    alias="champion",
    version=3
)

# Load model by alias
champion_model = mlflow.pyfunc.load_model("models:/production_model@champion")

# List all aliases
model = client.get_registered_model("production_model")
print(f"Aliases: {model.aliases}")
```

### Model Metadata

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Update model description
client.update_registered_model(
    name="production_model",
    description="Production model for customer churn prediction"
)

# Update version description
client.update_model_version(
    name="production_model",
    version=2,
    description="Trained on Q4 2024 data with improved features"
)

# Add tags
client.set_registered_model_tag(
    name="production_model",
    key="task",
    value="classification"
)

client.set_model_version_tag(
    name="production_model",
    version=2,
    key="validation_accuracy",
    value="0.94"
)
```

---

## Model Deployment

### Load and Use Models

```python
import mlflow

# Load model from Model Registry (by stage)
model = mlflow.pyfunc.load_model("models:/production_model/Production")
predictions = model.predict(X_test)

# Load model (by version)
model = mlflow.pyfunc.load_model("models:/production_model/3")
predictions = model.predict(X_test)

# Load model (by alias)
model = mlflow.pyfunc.load_model("models:/production_model@champion")
predictions = model.predict(X_test)

# Load from run
model = mlflow.pyfunc.load_model(f"runs:/{run_id}/model")
predictions = model.predict(X_test)
```

### Batch Inference

```python
import mlflow
from pyspark.sql.functions import struct, col

# Load model as Spark UDF
model_uri = "models:/production_model/Production"
predict_udf = mlflow.pyfunc.spark_udf(spark, model_uri)

# Apply to Spark DataFrame
predictions_df = df.withColumn(
    "prediction",
    predict_udf(struct(*[col(c) for c in feature_columns]))
)

predictions_df.select("customer_id", "prediction").show()

# Write predictions to Delta table
predictions_df.write.format("delta").mode("overwrite").saveAsTable("predictions")
```

### Real-time Inference with Model Serving

```python
import requests
import json

# Deploy model to Model Serving endpoint (via Databricks UI or API)
# Then use the endpoint:

endpoint_url = "https://<databricks-instance>/model/production_model/Production/invocations"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Prepare input
input_data = {
    "dataframe_split": {
        "columns": ["feature1", "feature2", "feature3"],
        "data": [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
    }
}

# Make prediction request
response = requests.post(endpoint_url, headers=headers, json=input_data)
predictions = response.json()

print(predictions)
```

### A/B Testing

```python
import mlflow
import random

def predict_with_ab_test(features, traffic_split=0.5):
    """
    Route traffic between champion and challenger models
    
    Args:
        features: Input features
        traffic_split: Fraction of traffic to send to challenger (0-1)
    """
    
    # Load both models
    champion = mlflow.pyfunc.load_model("models:/production_model@champion")
    challenger = mlflow.pyfunc.load_model("models:/production_model@challenger")
    
    # Random routing
    if random.random() < traffic_split:
        model_used = "challenger"
        prediction = challenger.predict(features)
    else:
        model_used = "champion"
        prediction = champion.predict(features)
    
    # Log for analysis
    with mlflow.start_run(nested=True):
        mlflow.log_param("model_used", model_used)
        mlflow.log_metric("prediction", prediction[0])
    
    return prediction, model_used

# Usage
prediction, model = predict_with_ab_test(input_features, traffic_split=0.2)
print(f"Prediction: {prediction}, Model: {model}")
```

---

## AutoML Integration

### MLflow with Databricks AutoML

```python
import databricks.automl

# Run AutoML
summary = databricks.automl.classify(
    train_df,
    target_col="label",
    primary_metric="f1",
    timeout_minutes=30,
    max_trials=10
)

# Best model is automatically logged to MLflow
print(f"Best model run ID: {summary.best_trial.mlflow_run_id}")
print(f"Best metric: {summary.best_trial.metrics['val_f1_score']}")

# Load best model
best_model = mlflow.pyfunc.load_model(f"runs:/{summary.best_trial.mlflow_run_id}/model")

# Register to Model Registry
mlflow.register_model(
    f"runs:/{summary.best_trial.mlflow_run_id}/model",
    "automl_production_model"
)
```

---

## Advanced Patterns

### Model Comparison Dashboard

```python
import mlflow
from mlflow.tracking import MlflowClient
import pandas as pd

def compare_models(experiment_name, metric_name="accuracy"):
    """Compare all runs in an experiment"""
    
    client = MlflowClient()
    experiment = client.get_experiment_by_name(experiment_name)
    
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=[f"metrics.{metric_name} DESC"]
    )
    
    results = []
    for run in runs:
        results.append({
            'run_id': run.info.run_id,
            'run_name': run.data.tags.get('mlflow.runName', 'N/A'),
            metric_name: run.data.metrics.get(metric_name, None),
            'model_type': run.data.params.get('model_type', 'N/A'),
            'start_time': pd.to_datetime(run.info.start_time, unit='ms')
        })
    
    df = pd.DataFrame(results)
    return df

# Usage
comparison = compare_models("/Users/user@example.com/my-experiment", "f1_score")
print(comparison.head(10))
```

### Model Performance Monitoring

```python
import mlflow
from datetime import datetime, timedelta

def log_production_metrics(model_name, predictions, actuals):
    """Log production model performance"""
    
    from sklearn.metrics import accuracy_score, f1_score
    
    with mlflow.start_run(run_name=f"production_monitoring_{datetime.now().isoformat()}"):
        # Log model info
        mlflow.log_param("model_name", model_name)
        mlflow.log_param("evaluation_date", datetime.now().isoformat())
        mlflow.log_param("sample_size", len(predictions))
        
        # Calculate metrics
        accuracy = accuracy_score(actuals, predictions)
        f1 = f1_score(actuals, predictions, average='weighted')
        
        mlflow.log_metric("production_accuracy", accuracy)
        mlflow.log_metric("production_f1", f1)
        
        # Log drift metrics if available
        # mlflow.log_metric("feature_drift", drift_score)
        
        return accuracy, f1

# Usage - run daily/hourly
predictions = model.predict(production_data)
actuals = get_ground_truth(production_data)

accuracy, f1 = log_production_metrics("production_model", predictions, actuals)
```

### Experiment Template

```python
import mlflow
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ExperimentConfig:
    """Configuration for ML experiment"""
    experiment_name: str
    model_params: Dict[str, Any]
    data_version: str
    feature_set: str

def run_experiment(config: ExperimentConfig, X_train, y_train, X_test, y_test):
    """Standardized experiment runner"""
    
    mlflow.set_experiment(config.experiment_name)
    
    with mlflow.start_run():
        # Log configuration
        mlflow.log_param("data_version", config.data_version)
        mlflow.log_param("feature_set", config.feature_set)
        
        for param_name, param_value in config.model_params.items():
            mlflow.log_param(param_name, param_value)
        
        # Train model
        model = train_model(X_train, y_train, **config.model_params)
        
        # Evaluate
        predictions = model.predict(X_test)
        metrics = evaluate_model(y_test, predictions)
        
        for metric_name, metric_value in metrics.items():
            mlflow.log_metric(metric_name, metric_value)
        
        # Log model
        mlflow.sklearn.log_model(
            model,
            "model",
            signature=mlflow.models.infer_signature(X_train, predictions)
        )
        
        return model, metrics

# Usage
config = ExperimentConfig(
    experiment_name="/Users/user@example.com/churn-prediction",
    model_params={"n_estimators": 100, "max_depth": 10},
    data_version="v2.1",
    feature_set="standard_features"
)

model, metrics = run_experiment(config, X_train, y_train, X_test, y_test)
```

### Model Retraining Pipeline

```python
import mlflow
from mlflow.tracking import MlflowClient
from datetime import datetime

def automated_retraining(
    model_name: str,
    train_data_path: str,
    performance_threshold: float = 0.85
):
    """Automated model retraining and registration"""
    
    client = MlflowClient()
    
    # Get current production model performance
    current_versions = client.search_model_versions(f"name='{model_name}'")
    production_version = [v for v in current_versions if v.current_stage == "Production"][0]
    
    # Load and evaluate current model
    current_model = mlflow.pyfunc.load_model(
        f"models:/{model_name}/Production"
    )
    
    # Load new training data
    train_df = spark.read.format("delta").load(train_data_path)
    X_train, y_train = prepare_data(train_df)
    
    # Train new model
    with mlflow.start_run(run_name=f"retrain_{datetime.now().strftime('%Y%m%d')}"):
        mlflow.log_param("retrain_date", datetime.now().isoformat())
        mlflow.log_param("data_path", train_data_path)
        mlflow.log_param("previous_version", production_version.version)
        
        # Train
        new_model = train_model(X_train, y_train)
        
        # Evaluate
        X_test, y_test = load_test_data()
        new_accuracy = evaluate_model(new_model, X_test, y_test)
        
        mlflow.log_metric("test_accuracy", new_accuracy)
        
        # Log model
        mlflow.sklearn.log_model(new_model, "model")
        
        # Compare with current production
        current_accuracy = float(production_version.tags.get("accuracy", 0))
        
        if new_accuracy > max(current_accuracy, performance_threshold):
            # Register new version
            model_uri = f"runs:/{mlflow.active_run().info.run_id}/model"
            new_version = mlflow.register_model(model_uri, model_name)
            
            # Tag with performance
            client.set_model_version_tag(
                model_name,
                new_version.version,
                "accuracy",
                str(new_accuracy)
            )
            
            # Transition to Production
            client.transition_model_version_stage(
                model_name,
                new_version.version,
                stage="Production",
                archive_existing_versions=True
            )
            
            print(f"New model v{new_version.version} promoted to Production")
            print(f"Accuracy: {new_accuracy:.4f} (previous: {current_accuracy:.4f})")
        else:
            print(f"New model did not meet threshold ({new_accuracy:.4f} <= {performance_threshold})")

# Usage - run on schedule
automated_retraining(
    model_name="churn_prediction",
    train_data_path="dbfs:/data/training/latest",
    performance_threshold=0.90
)
```

---

## Best Practices

### 1. Experiment Organization

```python
# Use hierarchical naming
mlflow.set_experiment("/Projects/CustomerChurn/ExperimentV1")

# Use descriptive run names
with mlflow.start_run(run_name="rf_100trees_maxdepth10_balanced"):
    pass

# Tag runs for filtering
mlflow.set_tag("model_family", "ensemble")
mlflow.set_tag("feature_version", "v2")
mlflow.set_tag("environment", "development")
```

### 2. Reproducibility

```python
import mlflow
import random
import numpy as np

with mlflow.start_run():
    # Log random seeds
    seed = 42
    mlflow.log_param("random_seed", seed)
    
    random.seed(seed)
    np.random.seed(seed)
    
    # Log data version
    mlflow.log_param("data_version", "2024-01-15")
    mlflow.log_param("data_hash", compute_data_hash(train_data))
    
    # Log code version
    mlflow.log_param("git_commit", get_git_commit())
    
    # Log dependencies
    mlflow.log_artifact("requirements.txt")
```

### 3. Model Signatures

```python
from mlflow.models.signature import infer_signature

with mlflow.start_run():
    model.fit(X_train, y_train)
    predictions = model.predict(X_train)
    
    # Infer signature
    signature = infer_signature(X_train, predictions)
    
    mlflow.sklearn.log_model(
        model,
        "model",
        signature=signature,
        input_example=X_train[:5]
    )
```

---

## Related Documentation

- [Python SDK Guide](./python-sdk.md) - General SDK usage
- [Model Deployment Guide](../examples/model-serving.md) - Deployment patterns
- [Delta Lake Guide](./delta-lake.md) - Data management

---

## Additional Resources

- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Databricks MLflow Guide](https://docs.databricks.com/mlflow/index.html)
- [Model Registry Guide](https://docs.databricks.com/machine-learning/manage-model-lifecycle/index.html)