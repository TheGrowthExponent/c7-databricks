# MLflow Skills

This directory contains skills and patterns for MLflow experiment tracking, model management, and tracing on Databricks.

## 📚 Skills Overview

### Well Covered Skills

#### 1. MLflow Onboarding
**Status**: ✅ Covered
**Priority**: -
**Description**: Comprehensive guide to getting started with MLflow on Databricks

**Key Topics**:
- MLflow setup and configuration
- Experiment tracking basics
- Model logging and registration
- Tracking server integration
- Authentication and permissions

**Related Documentation**:
- [MLflow Guide](../../sdk/mlflow.md) ✅
- [ML Workflows](../../examples/ml-workflows.md) ✅
- [Authentication](../../getting-started/authentication.md) ✅

---

#### 2. Querying MLflow Metrics
**Status**: ✅ Covered
**Priority**: -
**Description**: Search and analyze experiment metrics programmatically

**Key Topics**:
- Metric query APIs
- Run comparison
- Hyperparameter analysis
- Best run selection
- Metric visualization

**Related Documentation**:
- [MLflow Guide](../../sdk/mlflow.md) ✅
- [ML Workflows](../../examples/ml-workflows.md) ✅

---

### Medium Priority Skills

#### 3. Instrumenting with MLflow Tracing
**Status**: ⚠️ Partially documented
**Priority**: MEDIUM
**Description**: Add observability and debugging to LLM applications and agents

**Key Topics**:
- Trace creation and management
- Span instrumentation
- LLM call tracking
- Agent execution tracing
- Performance profiling
- Debugging complex workflows

**Use Cases**:
- LLM application observability
- Agent debugging
- Latency optimization
- Cost tracking
- Error analysis

**Prerequisites**:
- MLflow 2.9.0+
- LLM or agent application
- Understanding of spans and traces

**Enhancement Needed**:
- Add dedicated tracing examples
- Document span context propagation
- Include agent tracing patterns
- Show integration with Model Serving

**Related Documentation**:
- [MLflow Guide](../../sdk/mlflow.md) ⚠️ Basic coverage only

---

#### 4. Agent Evaluation
**Status**: ❌ Not covered
**Priority**: MEDIUM
**Description**: Evaluate and compare AI agent performance systematically

**Key Topics**:
- Agent evaluation metrics
- Test case creation
- Automated evaluation pipelines
- Human feedback integration
- A/B testing agents
- Performance benchmarking

**Use Cases**:
- Agent quality assurance
- Comparing agent versions
- Production readiness validation
- Continuous evaluation
- Regression detection

**Prerequisites**:
- Deployed agents
- Evaluation datasets
- MLflow experiment tracking

**Related Documentation**:
- [ML Workflows](../../examples/ml-workflows.md)
- [AI Playground Tutorial](../../getting-started/ai-playground-tutorial.md)

---

### Low Priority Skills

#### 5. Analyze MLflow Chat Session
**Status**: ❌ Not covered
**Priority**: LOW
**Description**: Analyze chat interactions and conversation patterns

**Key Topics**:
- Session replay and analysis
- Conversation flow visualization
- User interaction patterns
- Response quality metrics
- Session duration analysis

**Use Cases**:
- Chatbot improvement
- User experience optimization
- Conversation debugging
- Quality monitoring

**Prerequisites**:
- MLflow tracking enabled
- Chat application logs
- Session data stored

---

#### 6. Analyze MLflow Trace
**Status**: ⚠️ Partially documented
**Priority**: LOW
**Description**: Deep dive into trace data for debugging and optimization

**Key Topics**:
- Trace visualization
- Span analysis
- Latency breakdown
- Cost attribution
- Error investigation

**Use Cases**:
- Performance bottleneck identification
- Cost optimization
- Error root cause analysis
- Workflow optimization

**Prerequisites**:
- MLflow tracing enabled
- Trace data collected
- Understanding of distributed tracing

---

#### 7. Retrieving MLflow Traces
**Status**: ⚠️ Partially documented
**Priority**: LOW
**Description**: Query and retrieve trace data programmatically

**Key Topics**:
- Trace search APIs
- Filtering by tags and attributes
- Bulk trace retrieval
- Export and analysis
- Integration with monitoring tools

**Use Cases**:
- Custom trace analysis
- Monitoring dashboard creation
- Trace data export
- Anomaly detection

**Prerequisites**:
- MLflow Python client
- Trace data available
- API authentication

---

## 🎯 Quick Start Examples

### Example 1: Basic MLflow Tracking

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

# Start MLflow run
with mlflow.start_run(run_name="rf-classifier-v1"):
    # Log parameters
    n_estimators = 100
    max_depth = 10
    mlflow.log_param("n_estimators", n_estimators)
    mlflow.log_param("max_depth", max_depth)
    mlflow.log_param("model_type", "random_forest")

    # Train model
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth)
    model.fit(X_train, y_train)

    # Make predictions
    y_pred = model.predict(X_test)

    # Log metrics
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("f1_score", f1)

    # Log model
    mlflow.sklearn.log_model(
        model,
        "model",
        registered_model_name="rf_classifier"
    )

    # Log artifacts
    import matplotlib.pyplot as plt
    from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot()
    plt.savefig("confusion_matrix.png")
    mlflow.log_artifact("confusion_matrix.png")

    print(f"Run ID: {mlflow.active_run().info.run_id}")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"F1 Score: {f1:.4f}")
```

### Example 2: Querying Experiments and Runs

```python
import mlflow
from mlflow.tracking import MlflowClient

# Initialize client
client = MlflowClient()

# Search for best runs
experiment_name = "customer-churn-prediction"
experiment = client.get_experiment_by_name(experiment_name)

# Query runs with filters
runs = client.search_runs(
    experiment_ids=[experiment.experiment_id],
    filter_string="metrics.accuracy > 0.85",
    order_by=["metrics.f1_score DESC"],
    max_results=10
)

print(f"Found {len(runs)} runs with accuracy > 0.85")

# Analyze top runs
for run in runs[:3]:
    print(f"\nRun ID: {run.info.run_id}")
    print(f"  Accuracy: {run.data.metrics.get('accuracy', 'N/A'):.4f}")
    print(f"  F1 Score: {run.data.metrics.get('f1_score', 'N/A'):.4f}")
    print(f"  Parameters:")
    for param, value in run.data.params.items():
        print(f"    {param}: {value}")

# Get best run
best_run = runs[0]
print(f"\nBest Run: {best_run.info.run_id}")

# Load best model
best_model_uri = f"runs:/{best_run.info.run_id}/model"
model = mlflow.sklearn.load_model(best_model_uri)
```

### Example 3: MLflow Tracing for LLM Applications

```python
import mlflow
from mlflow.tracing import trace

@trace(name="rag_query", span_type="CHAIN")
def rag_query(question: str, context_docs: list) -> str:
    """RAG query with tracing"""

    # Retrieve context (traced automatically)
    with mlflow.start_span(name="retrieve_context", span_type="RETRIEVER") as span:
        context = retrieve_relevant_docs(question, context_docs)
        span.set_attribute("num_docs_retrieved", len(context))
        span.set_attribute("retrieval_score", context[0].get("score", 0))

    # Build prompt (traced)
    with mlflow.start_span(name="build_prompt", span_type="PARSER") as span:
        prompt = build_rag_prompt(question, context)
        span.set_attribute("prompt_length", len(prompt))

    # Call LLM (traced)
    with mlflow.start_span(name="llm_call", span_type="LLM") as span:
        response = call_llm(prompt)
        span.set_attribute("model", "llama-3-70b")
        span.set_attribute("response_length", len(response))
        span.set_attribute("estimated_tokens", len(response.split()) * 1.3)

    return response

# Use with automatic tracing
mlflow.tracing.enable()
answer = rag_query("What is Delta Lake?", documents)
mlflow.tracing.disable()

# View traces in MLflow UI or retrieve programmatically
traces = mlflow.search_traces(
    experiment_ids=[experiment_id],
    filter_string="attributes.span_type = 'CHAIN'"
)
```

### Example 4: Agent Tracing

```python
import mlflow
from mlflow.tracing import trace

class TracedAgent:
    @trace(name="agent_execution", span_type="AGENT")
    def execute(self, user_query: str) -> str:
        """Execute agent with full tracing"""

        # Plan actions
        with mlflow.start_span(name="plan", span_type="TOOL") as span:
            plan = self.create_plan(user_query)
            span.set_attribute("plan_steps", len(plan))

        # Execute tools
        results = []
        for i, step in enumerate(plan):
            with mlflow.start_span(name=f"tool_{step.tool_name}", span_type="TOOL") as span:
                result = self.execute_tool(step)
                span.set_attribute("tool_name", step.tool_name)
                span.set_attribute("tool_input", str(step.inputs)[:200])
                span.set_attribute("success", result.get("success", False))
                results.append(result)

        # Synthesize response
        with mlflow.start_span(name="synthesize", span_type="LLM") as span:
            response = self.synthesize_response(user_query, results)
            span.set_attribute("num_tool_results", len(results))

        return response

# Use traced agent
agent = TracedAgent()
mlflow.tracing.enable()
response = agent.execute("Analyze sales data for last quarter")
mlflow.tracing.disable()
```

### Example 5: Hyperparameter Tuning with MLflow

```python
import mlflow
from hyperopt import fmin, tpe, hp, Trials, STATUS_OK
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

# Define search space
search_space = {
    'n_estimators': hp.quniform('n_estimators', 50, 500, 50),
    'max_depth': hp.quniform('max_depth', 5, 50, 5),
    'min_samples_split': hp.quniform('min_samples_split', 2, 20, 2),
    'min_samples_leaf': hp.quniform('min_samples_leaf', 1, 10, 1)
}

def objective(params):
    """Objective function for hyperparameter tuning"""
    with mlflow.start_run(nested=True):
        # Convert params to integers
        params = {k: int(v) for k, v in params.items()}

        # Log parameters
        mlflow.log_params(params)

        # Train and evaluate
        model = RandomForestClassifier(**params, random_state=42)
        scores = cross_val_score(model, X_train, y_train, cv=5, scoring='f1_weighted')

        mean_score = scores.mean()
        std_score = scores.std()

        # Log metrics
        mlflow.log_metric("mean_f1_score", mean_score)
        mlflow.log_metric("std_f1_score", std_score)

        # Return loss (negative score for minimization)
        return {'loss': -mean_score, 'status': STATUS_OK}

# Run hyperparameter optimization
with mlflow.start_run(run_name="hyperparameter_tuning"):
    trials = Trials()
    best_params = fmin(
        fn=objective,
        space=search_space,
        algo=tpe.suggest,
        max_evals=50,
        trials=trials
    )

    # Log best parameters
    mlflow.log_params({f"best_{k}": v for k, v in best_params.items()})

    print("Best parameters:", best_params)
```

### Example 6: Model Registry and Deployment

```python
import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Register model
model_name = "customer_churn_classifier"
run_id = "abc123..."

model_uri = f"runs:/{run_id}/model"
model_version = mlflow.register_model(model_uri, model_name)

print(f"Registered model version: {model_version.version}")

# Add model description
client.update_model_version(
    name=model_name,
    version=model_version.version,
    description="Random Forest classifier with hyperparameter tuning. F1 Score: 0.89"
)

# Transition to staging
client.transition_model_version_stage(
    name=model_name,
    version=model_version.version,
    stage="Staging",
    archive_existing_versions=False
)

# Add tags
client.set_model_version_tag(
    name=model_name,
    version=model_version.version,
    key="validation_status",
    value="passed"
)

# Get production model
production_versions = client.get_latest_versions(model_name, stages=["Production"])
if production_versions:
    prod_model = mlflow.pyfunc.load_model(
        f"models:/{model_name}/Production"
    )

# Promote to production after validation
client.transition_model_version_stage(
    name=model_name,
    version=model_version.version,
    stage="Production",
    archive_existing_versions=True
)

print(f"Model {model_name} v{model_version.version} promoted to Production")
```

---

## 🔧 Common Patterns

### Pattern 1: Autologging for Common Frameworks

```python
import mlflow

# Enable autologging for scikit-learn
mlflow.sklearn.autolog()

# Enable autologging for PyTorch
mlflow.pytorch.autolog()

# Enable autologging for TensorFlow
mlflow.tensorflow.autolog()

# Train model - parameters, metrics, and model logged automatically
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)
```

### Pattern 2: Nested Runs for Complex Workflows

```python
# Parent run for overall experiment
with mlflow.start_run(run_name="ensemble_experiment"):
    mlflow.log_param("ensemble_type", "voting")

    models = []

    # Child runs for individual models
    for model_type in ['rf', 'xgb', 'lgb']:
        with mlflow.start_run(run_name=f"{model_type}_model", nested=True):
            model = train_model(model_type, X_train, y_train)
            score = evaluate_model(model, X_test, y_test)
            mlflow.log_metric("accuracy", score)
            models.append(model)

    # Log ensemble performance
    ensemble_score = evaluate_ensemble(models, X_test, y_test)
    mlflow.log_metric("ensemble_accuracy", ensemble_score)
```

### Pattern 3: Custom Metrics and Artifacts

```python
import mlflow
import json

with mlflow.start_run():
    # Log custom metrics
    mlflow.log_metrics({
        "precision": 0.85,
        "recall": 0.82,
        "auc": 0.91,
        "training_time_seconds": 123.45
    })

    # Log text files
    with open("model_summary.txt", "w") as f:
        f.write("Model Summary\n")
        f.write(f"Features: {X_train.shape[1]}\n")
    mlflow.log_artifact("model_summary.txt")

    # Log JSON config
    config = {"preprocessing": "standard", "features": list(X_train.columns)}
    with open("config.json", "w") as f:
        json.dump(config, f)
    mlflow.log_artifact("config.json")

    # Log entire directory
    mlflow.log_artifacts("analysis_results/", artifact_path="analysis")
```

### Pattern 4: MLflow with Databricks Jobs

```python
# In your training script
import mlflow
import sys

# Get job parameters
learning_rate = float(sys.argv[1])
batch_size = int(sys.argv[2])

# Set experiment
mlflow.set_experiment("/Users/username/production-training")

with mlflow.start_run():
    # Log job parameters
    mlflow.log_params({
        "learning_rate": learning_rate,
        "batch_size": batch_size,
        "job_id": dbutils.notebook.entry_point.getDbutils().notebook().getContext().jobId().get(),
        "run_id": dbutils.notebook.entry_point.getDbutils().notebook().getContext().currentRunId().get()
    })

    # Train model
    model = train_model(learning_rate, batch_size)

    # Log model and metrics
    mlflow.log_metric("final_loss", final_loss)
    mlflow.sklearn.log_model(model, "model")
```

---

## 📊 Best Practices

### Experiment Organization
1. **Naming Conventions**
   - Use descriptive experiment names: `/team/project/model-type`
   - Include version numbers in run names
   - Tag runs with metadata (data_version, environment)

2. **Parameter Tracking**
   - Log all hyperparameters
   - Include data preprocessing parameters
   - Track feature engineering decisions
   - Record random seeds for reproducibility

3. **Metric Selection**
   - Log multiple evaluation metrics
   - Include training and validation metrics
   - Track computation time and resource usage
   - Log business metrics when applicable

### Model Management
1. **Model Registry**
   - Use semantic versioning
   - Add comprehensive descriptions
   - Tag models with validation results
   - Document model dependencies

2. **Stage Transitions**
   - Validate before promoting to staging
   - Require approval for production deployment
   - Archive old versions systematically
   - Document transition reasons

3. **Model Packaging**
   - Include preprocessing code
   - Bundle feature definitions
   - Package prediction utilities
   - Document input/output schemas

### Tracing Best Practices
1. **Span Organization**
   - Use meaningful span names
   - Set appropriate span types
   - Add relevant attributes
   - Keep span granularity balanced

2. **Performance**
   - Avoid excessive span creation
   - Sample traces in high-volume scenarios
   - Set trace retention policies
   - Monitor tracing overhead

3. **Debugging**
   - Add error information to spans
   - Include input/output samples
   - Track resource consumption
   - Log decision points

---

## 🚀 Getting Started Checklist

### Basic MLflow Setup
- [ ] Install MLflow SDK: `pip install mlflow`
- [ ] Configure tracking URI (Databricks managed automatically)
- [ ] Create experiment: `mlflow.create_experiment()`
- [ ] Start first run: `mlflow.start_run()`
- [ ] Log parameters, metrics, and model
- [ ] View results in MLflow UI

### Model Registry
- [ ] Register trained model: `mlflow.register_model()`
- [ ] Add model description and tags
- [ ] Transition through stages (Staging → Production)
- [ ] Load model from registry: `mlflow.pyfunc.load_model()`
- [ ] Set up model approval process
- [ ] Configure model serving endpoint

### MLflow Tracing
- [ ] Enable tracing: `mlflow.tracing.enable()`
- [ ] Add `@trace` decorators to functions
- [ ] Create spans for key operations
- [ ] Add attributes to spans
- [ ] View traces in MLflow UI
- [ ] Set up trace retention and sampling

### Production Deployment
- [ ] Set up CI/CD integration with MLflow
- [ ] Configure automated model validation
- [ ] Implement model monitoring
- [ ] Set up alerting for metric degradation
- [ ] Document deployment procedures
- [ ] Create rollback procedures

---

## 🔍 Advanced Topics

### Custom MLflow Plugins

```python
import mlflow
from mlflow.tracking import MlflowClient

class CustomMetricLogger:
    """Custom plugin for domain-specific metrics"""

    def __init__(self):
        self.client = MlflowClient()

    def log_business_metrics(self, run_id: str, metrics: dict):
        """Log business-specific metrics"""
        for key, value in metrics.items():
            self.client.log_metric(run_id, f"business.{key}", value)

    def log_data_quality(self, run_id: str, dataset_stats: dict):
        """Log data quality metrics"""
        self.client.log_metric(run_id, "data.missing_rate", dataset_stats["missing_rate"])
        self.client.log_metric(run_id, "data.outlier_rate", dataset_stats["outlier_rate"])
        self.client.log_metric(run_id, "data.row_count", dataset_stats["row_count"])
```

### Distributed Training with MLflow

```python
import mlflow
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

# Spark MLlib with MLflow
with mlflow.start_run():
    # Create pipeline
    rf = RandomForestClassifier(numTrees=100, maxDepth=10)

    # Log parameters
    mlflow.log_param("num_trees", 100)
    mlflow.log_param("max_depth", 10)

    # Train on distributed data
    model = rf.fit(train_df)

    # Evaluate
    predictions = model.transform(test_df)
    evaluator = MulticlassClassificationEvaluator(metricName="f1")
    f1_score = evaluator.evaluate(predictions)

    mlflow.log_metric("f1_score", f1_score)
    mlflow.spark.log_model(model, "spark-model")
```

---

## 📖 Additional Resources

### Official Documentation
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Databricks MLflow Guide](https://docs.databricks.com/en/mlflow/index.html)
- [MLflow Model Registry](https://docs.databricks.com/en/mlflow/model-registry.html)
- [MLflow Tracing](https://docs.databricks.com/en/mlflow/tracing.html)

### Tutorials
- [ML Workflows Tutorial](../../examples/ml-workflows.md)
- [ML Model Tutorial](../../getting-started/ml-model-tutorial.md)
- [Python SDK Guide](../../sdk/python.md)

### API References
- [MLflow Python API](../../sdk/mlflow.md)
- [Jobs API](../../api/jobs.md)
- [Unity Catalog API](../../api/unity-catalog.md)

---

## 🏷️ Tags

`mlflow` `experiment-tracking` `model-registry` `tracing` `observability` `hyperparameter-tuning` `model-deployment` `ml-ops` `model-management`

---

**Last Updated**: 2026-01-15
**Status**: Core skills well documented - Tracing and agent evaluation need expansion
**Maintainer**: Context7 Documentation Team
