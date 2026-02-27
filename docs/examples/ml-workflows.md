# Databricks ML Workflows and Examples

## Overview

This guide provides end-to-end machine learning workflows for Databricks, covering data preparation, model training, hyperparameter tuning, deployment, and monitoring using MLflow, Spark ML, and popular ML libraries.

## Table of Contents

1. [Complete ML Pipeline](#complete-ml-pipeline)
2. [Feature Engineering](#feature-engineering)
3. [Hyperparameter Tuning](#hyperparameter-tuning)
4. [Distributed Training](#distributed-training)
5. [Model Deployment](#model-deployment)
6. [A/B Testing](#ab-testing)
7. [Model Monitoring](#model-monitoring)

---

## Complete ML Pipeline

### End-to-End Classification Pipeline

```python
import mlflow
import mlflow.sklearn
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, avg, count
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import pandas as pd
import numpy as np

# Initialize
spark = SparkSession.builder.appName("MLPipeline").getOrCreate()
mlflow.set_experiment("/Users/user@example.com/churn-prediction")

def complete_ml_pipeline():
    """
    Complete end-to-end ML pipeline from data to deployment
    """

    with mlflow.start_run(run_name="churn_prediction_v1"):

        # 1. DATA LOADING
        print("=== Step 1: Data Loading ===")
        df = spark.read.format("delta").table("catalog.schema.customer_data")

        # Log data info
        mlflow.log_param("total_records", df.count())
        mlflow.log_param("features_count", len(df.columns) - 1)

        # 2. DATA EXPLORATION
        print("=== Step 2: Data Exploration ===")
        churn_rate = df.filter(col("churned") == 1).count() / df.count()
        mlflow.log_metric("baseline_churn_rate", churn_rate)

        # 3. FEATURE ENGINEERING
        print("=== Step 3: Feature Engineering ===")

        # Convert to pandas for sklearn
        pdf = df.toPandas()

        # Separate features and target
        feature_cols = [c for c in pdf.columns if c not in ['customer_id', 'churned']]
        X = pdf[feature_cols]
        y = pdf['churned']

        # Handle missing values
        X = X.fillna(X.mean())

        # Log feature list
        mlflow.log_param("features", ",".join(feature_cols))

        # 4. TRAIN/TEST SPLIT
        print("=== Step 4: Train/Test Split ===")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        mlflow.log_param("train_size", len(X_train))
        mlflow.log_param("test_size", len(X_test))

        # 5. MODEL TRAINING
        print("=== Step 5: Model Training ===")

        # Create pipeline
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            ))
        ])

        # Log model parameters
        mlflow.log_param("model_type", "RandomForestClassifier")
        mlflow.log_param("n_estimators", 100)
        mlflow.log_param("max_depth", 10)

        # Train
        pipeline.fit(X_train, y_train)

        # 6. MODEL EVALUATION
        print("=== Step 6: Model Evaluation ===")

        # Predictions
        y_train_pred = pipeline.predict(X_train)
        y_test_pred = pipeline.predict(X_test)

        # Training metrics
        train_accuracy = accuracy_score(y_train, y_train_pred)
        train_f1 = f1_score(y_train, y_train_pred)

        mlflow.log_metric("train_accuracy", train_accuracy)
        mlflow.log_metric("train_f1", train_f1)

        # Test metrics
        test_accuracy = accuracy_score(y_test, y_test_pred)
        test_precision = precision_score(y_test, y_test_pred)
        test_recall = recall_score(y_test, y_test_pred)
        test_f1 = f1_score(y_test, y_test_pred)

        mlflow.log_metric("test_accuracy", test_accuracy)
        mlflow.log_metric("test_precision", test_precision)
        mlflow.log_metric("test_recall", test_recall)
        mlflow.log_metric("test_f1", test_f1)

        print(f"Test Accuracy: {test_accuracy:.4f}")
        print(f"Test F1 Score: {test_f1:.4f}")

        # 7. FEATURE IMPORTANCE
        print("=== Step 7: Feature Importance ===")

        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': pipeline.named_steps['classifier'].feature_importances_
        }).sort_values('importance', ascending=False)

        # Save and log
        feature_importance.to_csv("feature_importance.csv", index=False)
        mlflow.log_artifact("feature_importance.csv")

        # Log top features
        top_features = feature_importance.head(10)['feature'].tolist()
        mlflow.log_param("top_features", ",".join(top_features))

        # 8. MODEL LOGGING
        print("=== Step 8: Model Logging ===")

        signature = mlflow.models.infer_signature(X_train, y_train_pred)

        mlflow.sklearn.log_model(
            pipeline,
            "model",
            signature=signature,
            input_example=X_train.head(5)
        )

        # 9. MODEL REGISTRATION
        print("=== Step 9: Model Registration ===")

        run_id = mlflow.active_run().info.run_id
        model_uri = f"runs:/{run_id}/model"

        model_version = mlflow.register_model(model_uri, "churn_prediction_model")

        print(f"Model registered: version {model_version.version}")

        return {
            "run_id": run_id,
            "test_accuracy": test_accuracy,
            "test_f1": test_f1,
            "model_version": model_version.version
        }

# Run pipeline
result = complete_ml_pipeline()
print(f"\nPipeline Complete!")
print(f"Run ID: {result['run_id']}")
print(f"Model Version: {result['model_version']}")
```

---

## Feature Engineering

### Advanced Feature Engineering

```python
from pyspark.sql.functions import (
    col, when, datediff, current_date, avg, sum, count, max, min,
    lag, lead, row_number, rank, dense_rank
)
from pyspark.sql.window import Window

def create_customer_features(transactions_df, customers_df):
    """
    Create rich feature set for customer churn prediction
    """

    # 1. TRANSACTION AGGREGATIONS
    customer_stats = transactions_df.groupBy("customer_id").agg(
        count("*").alias("total_transactions"),
        sum("amount").alias("total_spent"),
        avg("amount").alias("avg_transaction_amount"),
        max("amount").alias("max_transaction_amount"),
        min("amount").alias("min_transaction_amount"),
        max("transaction_date").alias("last_transaction_date"),
        min("transaction_date").alias("first_transaction_date")
    )

    # 2. RECENCY FEATURES
    customer_stats = customer_stats.withColumn(
        "days_since_last_transaction",
        datediff(current_date(), col("last_transaction_date"))
    ).withColumn(
        "customer_lifetime_days",
        datediff(col("last_transaction_date"), col("first_transaction_date"))
    )

    # 3. FREQUENCY FEATURES
    customer_stats = customer_stats.withColumn(
        "transactions_per_day",
        col("total_transactions") / col("customer_lifetime_days")
    )

    # 4. MONETARY FEATURES
    customer_stats = customer_stats.withColumn(
        "spending_per_day",
        col("total_spent") / col("customer_lifetime_days")
    )

    # 5. TREND FEATURES
    window_spec = Window.partitionBy("customer_id").orderBy("transaction_date")

    transactions_with_trends = transactions_df.withColumn(
        "transaction_rank",
        row_number().over(window_spec)
    ).withColumn(
        "prev_amount",
        lag("amount", 1).over(window_spec)
    ).withColumn(
        "amount_change",
        col("amount") - col("prev_amount")
    )

    # Calculate trend statistics
    trend_stats = transactions_with_trends.groupBy("customer_id").agg(
        avg("amount_change").alias("avg_amount_change"),
        sum(when(col("amount_change") > 0, 1).otherwise(0)).alias("increasing_transactions"),
        sum(when(col("amount_change") < 0, 1).otherwise(0)).alias("decreasing_transactions")
    )

    # 6. SEGMENTATION FEATURES
    customer_stats = customer_stats.withColumn(
        "customer_segment",
        when(col("total_spent") > 10000, "high_value")
        .when(col("total_spent") > 5000, "medium_value")
        .otherwise("low_value")
    )

    # 7. JOIN ALL FEATURES
    enriched_customers = customers_df \
        .join(customer_stats, "customer_id", "left") \
        .join(trend_stats, "customer_id", "left")

    # 8. FILL MISSING VALUES
    enriched_customers = enriched_customers.fillna({
        "total_transactions": 0,
        "total_spent": 0,
        "avg_transaction_amount": 0,
        "days_since_last_transaction": 9999,
        "transactions_per_day": 0
    })

    return enriched_customers

# Usage
transactions = spark.read.format("delta").table("catalog.schema.transactions")
customers = spark.read.format("delta").table("catalog.schema.customers")

features_df = create_customer_features(transactions, customers)
features_df.write.format("delta").mode("overwrite").saveAsTable("catalog.schema.customer_features")
```

### Time Series Features

```python
from pyspark.sql.functions import col, lag, avg, stddev, window
from pyspark.sql.window import Window

def create_time_series_features(df, id_col, timestamp_col, value_col):
    """
    Create time series features for forecasting
    """

    window_spec = Window.partitionBy(id_col).orderBy(timestamp_col)

    # Lag features
    df = df.withColumn(f"{value_col}_lag_1", lag(value_col, 1).over(window_spec))
    df = df.withColumn(f"{value_col}_lag_7", lag(value_col, 7).over(window_spec))
    df = df.withColumn(f"{value_col}_lag_30", lag(value_col, 30).over(window_spec))

    # Rolling statistics
    rolling_7 = Window.partitionBy(id_col).orderBy(timestamp_col).rowsBetween(-7, -1)
    rolling_30 = Window.partitionBy(id_col).orderBy(timestamp_col).rowsBetween(-30, -1)

    df = df.withColumn(f"{value_col}_rolling_mean_7", avg(value_col).over(rolling_7))
    df = df.withColumn(f"{value_col}_rolling_mean_30", avg(value_col).over(rolling_30))
    df = df.withColumn(f"{value_col}_rolling_std_7", stddev(value_col).over(rolling_7))
    df = df.withColumn(f"{value_col}_rolling_std_30", stddev(value_col).over(rolling_30))

    # Difference features
    df = df.withColumn(
        f"{value_col}_diff_1",
        col(value_col) - col(f"{value_col}_lag_1")
    )

    return df

# Usage
sales_df = spark.read.format("delta").table("catalog.schema.daily_sales")
features_df = create_time_series_features(sales_df, "store_id", "date", "sales")
```

---

## Hyperparameter Tuning

### Grid Search with MLflow

```python
import mlflow
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score
from itertools import product

def grid_search_with_mlflow(X_train, y_train, X_test, y_test):
    """
    Grid search with MLflow tracking
    """

    # Define parameter grid
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [5, 10, 15],
        'min_samples_split': [2, 5, 10]
    }

    # Generate all combinations
    keys = param_grid.keys()
    values = param_grid.values()
    combinations = [dict(zip(keys, v)) for v in product(*values)]

    print(f"Testing {len(combinations)} parameter combinations")

    # Parent run
    with mlflow.start_run(run_name="grid_search"):
        mlflow.log_param("search_type", "grid_search")
        mlflow.log_param("total_combinations", len(combinations))

        best_score = 0
        best_params = None

        # Test each combination
        for i, params in enumerate(combinations):
            with mlflow.start_run(nested=True, run_name=f"config_{i+1}"):
                # Log parameters
                for param_name, param_value in params.items():
                    mlflow.log_param(param_name, param_value)

                # Train model
                model = RandomForestClassifier(**params, random_state=42)
                model.fit(X_train, y_train)

                # Evaluate
                y_pred = model.predict(X_test)
                f1 = f1_score(y_test, y_pred)

                mlflow.log_metric("f1_score", f1)

                # Track best
                if f1 > best_score:
                    best_score = f1
                    best_params = params
                    mlflow.log_param("is_best", True)

                print(f"Config {i+1}/{len(combinations)}: F1={f1:.4f}, Params={params}")

        # Log best results to parent run
        mlflow.log_metric("best_f1_score", best_score)
        mlflow.log_params({f"best_{k}": v for k, v in best_params.items()})

        print(f"\nBest F1 Score: {best_score:.4f}")
        print(f"Best Parameters: {best_params}")

        return best_params, best_score

# Usage
best_params, best_score = grid_search_with_mlflow(X_train, y_train, X_test, y_test)
```

### Hyperopt for Bayesian Optimization

```python
import mlflow
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score

def hyperopt_optimization(X_train, y_train, X_test, y_test, max_evals=50):
    """
    Hyperparameter optimization using Hyperopt with MLflow tracking
    """

    # Define search space
    search_space = {
        'n_estimators': hp.choice('n_estimators', [50, 100, 150, 200]),
        'max_depth': hp.choice('max_depth', [5, 10, 15, 20, None]),
        'min_samples_split': hp.uniform('min_samples_split', 2, 20),
        'min_samples_leaf': hp.uniform('min_samples_leaf', 1, 10),
        'max_features': hp.choice('max_features', ['sqrt', 'log2'])
    }

    def objective(params):
        """Objective function for Hyperopt"""

        with mlflow.start_run(nested=True):
            # Convert parameters
            params['min_samples_split'] = int(params['min_samples_split'])
            params['min_samples_leaf'] = int(params['min_samples_leaf'])

            # Log parameters
            mlflow.log_params(params)

            # Train model
            model = RandomForestClassifier(**params, random_state=42)
            model.fit(X_train, y_train)

            # Evaluate
            y_pred = model.predict(X_test)
            f1 = f1_score(y_test, y_pred)

            mlflow.log_metric("f1_score", f1)

            # Return loss (negative F1 because Hyperopt minimizes)
            return {'loss': -f1, 'status': STATUS_OK}

    # Run optimization
    with mlflow.start_run(run_name="hyperopt_optimization"):
        mlflow.log_param("optimizer", "hyperopt_tpe")
        mlflow.log_param("max_evals", max_evals)

        trials = Trials()

        best = fmin(
            fn=objective,
            space=search_space,
            algo=tpe.suggest,
            max_evals=max_evals,
            trials=trials
        )

        # Log best results
        best_f1 = -min([trial['result']['loss'] for trial in trials.trials])
        mlflow.log_metric("best_f1_score", best_f1)
        mlflow.log_params({f"best_{k}": v for k, v in best.items()})

        print(f"Best F1 Score: {best_f1:.4f}")
        print(f"Best Parameters: {best}")

        return best, best_f1

# Usage
best_params, best_score = hyperopt_optimization(X_train, y_train, X_test, y_test, max_evals=50)
```

---

## Distributed Training

### Spark ML Pipeline

```python
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler, StandardScaler, StringIndexer
from pyspark.ml.classification import RandomForestClassifier, GBTClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator

def spark_ml_pipeline(df, feature_cols, label_col):
    """
    Complete Spark ML pipeline with cross-validation
    """

    # Split data
    train_df, test_df = df.randomSplit([0.8, 0.2], seed=42)

    # Feature engineering stages
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features_raw")
    scaler = StandardScaler(inputCol="features_raw", outputCol="features")

    # Classifier
    rf = RandomForestClassifier(
        featuresCol="features",
        labelCol=label_col,
        predictionCol="prediction"
    )

    # Create pipeline
    pipeline = Pipeline(stages=[assembler, scaler, rf])

    # Parameter grid for tuning
    param_grid = ParamGridBuilder() \
        .addGrid(rf.numTrees, [50, 100, 150]) \
        .addGrid(rf.maxDepth, [5, 10, 15]) \
        .addGrid(rf.minInstancesPerNode, [1, 5]) \
        .build()

    # Evaluator
    evaluator = BinaryClassificationEvaluator(labelCol=label_col)

    # Cross-validation
    cv = CrossValidator(
        estimator=pipeline,
        estimatorParamMaps=param_grid,
        evaluator=evaluator,
        numFolds=5,
        parallelism=4
    )

    # Train
    print("Training model with cross-validation...")
    cv_model = cv.fit(train_df)

    # Best model
    best_model = cv_model.bestModel

    # Evaluate
    predictions = best_model.transform(test_df)

    auc = evaluator.evaluate(predictions)
    print(f"Test AUC: {auc:.4f}")

    # Save model
    best_model.write().overwrite().save("/dbfs/models/spark_ml_model")

    return best_model, predictions

# Usage
df = spark.read.format("delta").table("catalog.schema.training_data")
feature_cols = ["feature1", "feature2", "feature3", "feature4"]
model, predictions = spark_ml_pipeline(df, feature_cols, "label")
```

### Distributed Deep Learning with Horovod

```python
import mlflow
import tensorflow as tf
from tensorflow import keras
import horovod.tensorflow.keras as hvd

def train_with_horovod():
    """
    Distributed training with Horovod
    """

    # Initialize Horovod
    hvd.init()

    # Pin GPU to local rank
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        tf.config.experimental.set_visible_devices(gpus[hvd.local_rank()], 'GPU')

    # Load data (each worker gets a subset)
    (x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()

    # Preprocess
    x_train = x_train.reshape(-1, 784).astype('float32') / 255.0
    x_test = x_test.reshape(-1, 784).astype('float32') / 255.0

    # Build model
    model = keras.Sequential([
        keras.layers.Dense(128, activation='relu', input_shape=(784,)),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(10, activation='softmax')
    ])

    # Horovod optimizer
    optimizer = keras.optimizers.Adam(learning_rate=0.001 * hvd.size())
    optimizer = hvd.DistributedOptimizer(optimizer)

    # Compile
    model.compile(
        optimizer=optimizer,
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    # Callbacks
    callbacks = [
        hvd.callbacks.BroadcastGlobalVariablesCallback(0),
        hvd.callbacks.MetricAverageCallback(),
        hvd.callbacks.LearningRateWarmupCallback(initial_lr=0.001 * hvd.size(), warmup_epochs=3),
    ]

    # Only log metrics on rank 0
    if hvd.rank() == 0:
        callbacks.append(mlflow.tensorflow.autolog())

    # Train
    history = model.fit(
        x_train, y_train,
        batch_size=128,
        epochs=10,
        validation_data=(x_test, y_test),
        callbacks=callbacks,
        verbose=1 if hvd.rank() == 0 else 0
    )

    # Evaluate
    if hvd.rank() == 0:
        test_loss, test_acc = model.evaluate(x_test, y_test)
        print(f"Test Accuracy: {test_acc:.4f}")

        # Save model
        model.save("/dbfs/models/horovod_model")

# Run distributed training
from sparkdl import HorovodRunner

hr = HorovodRunner(np=4)  # 4 workers
hr.run(train_with_horovod)
```

---

## Model Deployment

### Batch Inference Pipeline

```python
import mlflow
from pyspark.sql.functions import struct, col

def batch_inference_pipeline(model_name, model_stage, input_table, output_table):
    """
    Batch inference pipeline using registered model
    """

    print(f"Loading model: {model_name}/{model_stage}")

    # Load model as Spark UDF
    model_uri = f"models:/{model_name}/{model_stage}"
    predict_udf = mlflow.pyfunc.spark_udf(spark, model_uri, result_type="double")

    # Load input data
    print(f"Loading data from {input_table}")
    df = spark.read.format("delta").table(input_table)

    # Get feature columns
    feature_cols = [c for c in df.columns if c not in ['customer_id', 'prediction']]

    # Make predictions
    print("Making predictions...")
    predictions_df = df.withColumn(
        "prediction",
        predict_udf(struct(*[col(c) for c in feature_cols]))
    )

    # Add metadata
    from pyspark.sql.functions import current_timestamp, lit

    predictions_df = predictions_df \
        .withColumn("prediction_timestamp", current_timestamp()) \
        .withColumn("model_name", lit(model_name)) \
        .withColumn("model_version", lit(model_stage))

    # Write predictions
    print(f"Writing predictions to {output_table}")
    predictions_df.write \
        .format("delta") \
        .mode("overwrite") \
        .saveAsTable(output_table)

    prediction_count = predictions_df.count()
    print(f"Generated {prediction_count} predictions")

    return predictions_df

# Usage
predictions = batch_inference_pipeline(
    model_name="churn_prediction_model",
    model_stage="Production",
    input_table="catalog.schema.customer_features",
    output_table="catalog.schema.churn_predictions"
)
```

### Real-time Model Serving

```python
import mlflow
import requests
import json

class ModelServingClient:
    """
    Client for Databricks Model Serving endpoints
    """

    def __init__(self, endpoint_url, token):
        self.endpoint_url = endpoint_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def predict(self, features):
        """
        Make real-time prediction

        Args:
            features: Dict or list of feature values
        """

        # Format input
        if isinstance(features, dict):
            input_data = {
                "dataframe_records": [features]
            }
        else:
            input_data = {
                "dataframe_split": {
                    "columns": list(features[0].keys()),
                    "data": [list(f.values()) for f in features]
                }
            }

        # Make request
        response = requests.post(
            self.endpoint_url,
            headers=self.headers,
            json=input_data
        )

        response.raise_for_status()
        return response.json()

    def predict_batch(self, features_list, batch_size=100):
        """
        Batch predictions with chunking
        """
        predictions = []

        for i in range(0, len(features_list), batch_size):
            batch = features_list[i:i+batch_size]
            result = self.predict(batch)
            predictions.extend(result['predictions'])

        return predictions

# Usage
client = ModelServingClient(
    endpoint_url="https://<instance>/serving-endpoints/churn_model/invocations",
    token="<your-token>"
)

# Single prediction
features = {
    "total_spent": 5000,
    "days_since_last_transaction": 30,
    "total_transactions": 50
}

prediction = client.predict(features)
print(f"Churn probability: {prediction['predictions'][0]}")

# Batch predictions
features_list = [
    {"total_spent": 5000, "days_since_last_transaction": 30, "total_transactions": 50},
    {"total_spent": 10000, "days_since_last_transaction": 5, "total_transactions": 100},
]

predictions = client.predict_batch(features_list)
```

---

## A/B Testing

### A/B Test Framework

```python
import mlflow
import random
from datetime import datetime

class ABTestFramework:
    """
    A/B testing framework for ML models
    """

    def __init__(self, model_a_name, model_b_name, traffic_split=0.5):
        self.model_a = mlflow.pyfunc.load_model(f"models:/{model_a_name}/Production")
        self.model_b = mlflow.pyfunc.load_model(f"models:/{model_b_name}/Staging")
        self.traffic_split = traffic_split
        self.results = []

    def predict(self, features, user_id):
        """
        Route prediction to A or B based on traffic split
        """

        # Consistent routing based on user_id
        random.seed(user_id)
        use_model_b = random.random() < self.traffic_split

        # Make prediction
        if use_model_b:
            prediction = self.model_b.predict(features)
            model_used = "B"
        else:
            prediction = self.model_a.predict(features)
            model_used = "A"

        # Log result
        result = {
            "user_id": user_id,
            "model": model_used,
            "prediction": prediction[0],
            "timestamp": datetime.now()
        }
        self.results.append(result)

        return prediction, model_used

    def log_outcome(self, user_id, actual_outcome):
        """
        Log actual outcome for analysis
        """
        for result in self.results:
            if result['user_id'] == user_id:
                result['actual'] = actual_outcome
                result['correct'] = (result['prediction'] > 0.5) == actual_outcome

    def analyze_results(self):
        """
        Analyze A/B test results
        """
        import pandas as pd

        df = pd.DataFrame(self.results)

        # Filter only results with outcomes
        df = df[df['actual'].notna()]

        # Calculate metrics per model
        metrics = df.groupby('model').agg({
            'correct': 'mean',
            'user_id': 'count'
        }).rename(columns={'correct': 'accuracy', 'user_id': 'count'})

        print("A/B Test Results:")
        print(metrics)

        # Statistical significance test
        from scipy.stats import chi2_contingency

        contingency_table = pd.crosstab(df['model'], df['correct'])
        chi2, p_value, dof, expected = chi2_contingency(contingency_table)

        print(f"\nChi-square test p-value: {p_value:.4f}")

        if p_value < 0.05:
            print("Result is statistically significant!")
        else:
            print("No significant difference between models.")

        return metrics, p_value

# Usage
ab_test = ABTestFramework(
    model_a_name="churn_model_v1",
    model_b_name="churn_model_v2",
    traffic_split=0.3  # 30% to model B
)

# Make predictions
for user_id in range(1000):
    features = get_user_features(user_id)
    prediction, model = ab_test.predict(features, user_id)

    # Later, log actual outcome
    actual = get_actual_churn(user_id)
    ab_test.log_outcome(user_id, actual)

# Analyze results
metrics, p_value = ab_test.analyze_results()
```

---

## Model Monitoring

### Production Monitoring Pipeline

```python
import mlflow
from pyspark.sql.functions import col, current_timestamp, datediff, avg, stddev
from sklearn.metrics import accuracy_score, precision_score, recall_score

def monitor_production_model(
    predictions_table,
    actuals_table,
    model_name,
    monitoring_experiment
):
    """
    Monitor production model performance and data drift
    """

    mlflow.set_experiment(monitoring_experiment)

    with mlflow.start_run(run_name=f"monitoring_{datetime.now().strftime('%Y%m%d')}"):

        # 1. Load predictions and actuals
        predictions_df = spark.read.format("delta").table(predictions_table)
        actuals_df = spark.read.format("delta").table(actuals_table)

        # Join predictions with actuals
        eval_df = predictions_df.join(
            actuals_df,
            on="customer_id",
            how="inner"
        )

        # Convert to pandas for sklearn metrics
        eval_pdf = eval_df.select("prediction", "actual_churn").toPandas()

        # 2. Calculate performance metrics
        predictions = (eval_pdf['prediction'] > 0.5).astype(int)
        actuals = eval_pdf['actual_churn']

        accuracy = accuracy_score(actuals, predictions)
        precision = precision_score(actuals, predictions)
        recall = recall_score(actuals, predictions)

        mlflow.log_metric("production_accuracy", accuracy)
        mlflow.log_metric("production_precision", precision)
        mlflow.log_metric("production_recall", recall)

        print(f"Production Accuracy: {accuracy:.4f}")
        print(f"Production Precision: {precision:.4f}")
        print(f"Production Recall: {recall:.4f}")

        # 3. Data drift detection
        # Compare feature distributions
        training_features = spark.read.format("delta").table("catalog.schema.training_features")
        production_features = predictions_df.select([c for c in predictions_df.columns if c.startswith('feature_')])

        numeric_cols = [c for c in production_features.columns]

        drift_detected = []

        for col_name in numeric_cols:
            # Training statistics
            train_stats = training_features.select(
                avg(col_name).alias("mean"),
                stddev(col_name).alias("std")
            ).collect()[0]

            # Production statistics
            prod_stats = production_features.select(
                avg(col_name).alias("mean"),
                stddev(col_name).alias("std")
            ).collect()[0]

            # Calculate drift (simple threshold-based)
            mean_drift = abs(prod_stats['mean'] - train_stats['mean']) / train_stats['std']

            if mean_drift > 2:  # More than 2 standard deviations
                drift_detected.append(col_name)
                mlflow.log_metric(f"drift_{col_name}", mean_drift)

        if drift_detected:
            print(f"WARNING: Drift detected in features: {drift_detected}")
            mlflow.log_param("drift_features", ",".join(drift_detected))
            mlflow.log_metric("drift_count", len(drift_detected))
        else:
            print("No significant drift detected")

        # 4. Prediction distribution
        positive_rate = (eval_pdf['prediction'] > 0.5).mean()
        mlflow.log_metric("positive_prediction_rate", positive_rate)

        # 5. Alert if performance degrades
        if accuracy < 0.80:  # Threshold
            print("ALERT: Model accuracy below threshold!")
            mlflow.log_param("alert", "accuracy_below_threshold")

        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "drift_features": drift_detected
        }

# Schedule this to run daily
monitoring_results = monitor_production_model(
    predictions_table="catalog.schema.churn_predictions",
    actuals_table="catalog.schema.churn_actuals",
    model_name="churn_prediction_model",
    monitoring_experiment="/monitoring/churn_model"
)
```

---

## Best Practices

### 1. Reproducible ML

```python
import mlflow
import random
import numpy as np
import tensorflow as tf

def set_seeds(seed=42):
    """Set all random seeds for reproducibility"""
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)

with mlflow.start_run():
    # Log everything for reproducibility
    mlflow.log_param("random_seed", 42)
    mlflow.log_param("data_version", "v2024.01")
    mlflow.log_param("python_version", "3.9")

    set_seeds(42)

    # Train model...
```

### 2. Model Versioning

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Tag models with metadata
client.set_model_version_tag(
    name="churn_model",
    version="3",
    key="validation_date",
    value="2026-02-27"
)

client.set_model_version_tag(
    name="churn_model",
    version="3",
    key="training_data_size",
    value="1000000"
)
```

### 3. Feature Store Integration

```python
from databricks.feature_store import FeatureStoreClient

fs = FeatureStoreClient()

# Create feature table
fs.create_table(
    name="catalog.schema.customer_features",
    primary_keys=["customer_id"],
    df=features_df,
    description="Customer features for churn prediction"
)

# Use features in training
training_set = fs.create_training_set(
    df=labels_df,
    feature_lookups=[
        FeatureLookup(
            table_name="catalog.schema.customer_features",
            lookup_key="customer_id"
        )
    ],
    label="churned"
)

training_df = training_set.load_df()
```

---

## Related Documentation

- [MLflow SDK Guide](../sdk/mlflow.md) - MLflow operations
- [Feature Engineering](../best-practices/feature-engineering.md) - Feature best practices
- [Model Serving](../api/model-serving.md) - Deployment patterns

---

## Additional Resources

- [Databricks ML Guide](https://docs.databricks.com/machine-learning/index.html)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Feature Store Guide](https://docs.databricks.com/machine-learning/feature-store/index.html)
