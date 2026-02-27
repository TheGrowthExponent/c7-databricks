---
title: "Data Engineering Skills"
description: "ETL pipelines, data processing, and workflow orchestration on Databricks"
category: "data-engineering"
tags:
  [
    "data-engineering",
    "etl",
    "pipelines",
    "delta-live-tables",
    "databricks-jobs",
    "workflows",
    "medallion-architecture",
    "data-quality",
    "streaming",
    "batch-processing",
  ]
priority: "medium"
skills_count: 3
last_updated: 2026-02-27
version: "1.0.0"
status: "partial"
---

# Data Engineering Skills

This directory contains skills and patterns for data engineering, ETL pipelines, and data processing on Databricks.

## 📚 Skills Overview

### Well Covered Skills

#### 1. Databricks Jobs

**Status**: ✅ Covered
**Priority**: -
**Description**: Comprehensive guide to creating and managing data pipelines and workflows

**Key Topics**:

- Job creation and configuration
- Task orchestration and dependencies
- Multi-task workflows
- Scheduling and triggers
- Parameterization
- Error handling and retries
- Monitoring and alerts
- Job clusters vs shared clusters

**Use Cases**:

- ETL pipeline orchestration
- Batch data processing
- ML model training pipelines
- Data quality checks
- Incremental data loads
- Multi-stage data transformations

**Related Documentation**:

- [Jobs API](../../api/jobs.md) ✅ (1,382 lines)
- [ETL Patterns](../../examples/etl-patterns.md) ✅
- [Python SDK](../../sdk/python.md) ✅

---

### Medium Priority Skills

#### 2. Databricks Spark Declarative Pipelines (Delta Live Tables)

**Status**: ⚠️ Partially covered (streaming workflows documented)
**Priority**: MEDIUM
**Description**: Build reliable, maintainable data pipelines with declarative syntax

**Key Topics**:

- Delta Live Tables (DLT) basics
- Pipeline declaration with Python and SQL
- Data quality expectations
- Incremental processing patterns
- Pipeline dependencies and DAGs
- Change Data Capture (CDC) with DLT
- Pipeline monitoring and observability
- Cost optimization strategies

**Use Cases**:

- Medallion architecture (Bronze → Silver → Gold)
- Streaming and batch pipelines
- Data quality enforcement
- Complex data transformations
- Real-time analytics pipelines
- CDC processing

**Prerequisites**:

- Delta Lake knowledge
- SQL or Python proficiency
- Understanding of data quality concepts

**Enhancement Needed**:

- Add dedicated DLT guide
- Document pipeline patterns
- Include quality expectation examples
- Show monitoring and troubleshooting

**Related Documentation**:

- [Streaming Workflows](../../examples/streaming-workflows.md) ⚠️ Structured streaming covered
- [Delta Lake Guide](../../sdk/delta-lake.md) ✅
- [ETL Patterns](../../examples/etl-patterns.md) ✅

---

### Low Priority Skills

#### 3. Databricks Synthetic Data Generation

**Status**: ❌ Not covered
**Priority**: LOW
**Description**: Generate synthetic data for testing, development, and demo purposes

**Key Topics**:

- Synthetic data generation libraries
- Realistic data patterns
- Data distribution matching
- PII-safe test data
- Performance data generation
- Schema-based generation
- Data volume scaling

**Use Cases**:

- Development and testing environments
- Demo and training data
- Load testing
- Privacy-compliant testing
- Proof of concepts
- Data science experiments

**Prerequisites**:

- PySpark knowledge
- Understanding of data types
- Schema definition skills

**Related Documentation**:

- [ETL Patterns](../../examples/etl-patterns.md)
- [Delta Lake Guide](../../sdk/delta-lake.md)
- [Python SDK](../../sdk/python.md)

---

## 🎯 Quick Start Examples

### Example 1: Create Multi-Task Job

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs

w = WorkspaceClient()

# Define job with multiple tasks
job = w.jobs.create(
    name="daily_etl_pipeline",
    tasks=[
        # Task 1: Extract raw data
        jobs.Task(
            task_key="extract_raw_data",
            description="Extract data from source systems",
            notebook_task=jobs.NotebookTask(
                notebook_path="/Workspace/pipelines/extract",
                base_parameters={"source": "salesforce", "date": "{{job.start_time}}"}
            ),
            new_cluster=jobs.ClusterSpec(
                spark_version="13.3.x-scala2.12",
                node_type_id="i3.xlarge",
                num_workers=2
            )
        ),
        # Task 2: Transform to silver
        jobs.Task(
            task_key="transform_silver",
            description="Clean and transform to silver layer",
            depends_on=[jobs.TaskDependency(task_key="extract_raw_data")],
            spark_python_task=jobs.SparkPythonTask(
                python_file="dbfs:/pipelines/transform_silver.py",
                parameters=["--layer", "silver"]
            ),
            existing_cluster_id="existing-cluster-id"
        ),
        # Task 3: Aggregate to gold
        jobs.Task(
            task_key="aggregate_gold",
            description="Create gold layer aggregations",
            depends_on=[jobs.TaskDependency(task_key="transform_silver")],
            sql_task=jobs.SqlTask(
                warehouse_id="abc123",
                query=jobs.SqlTaskQuery(
                    query_id="gold_aggregation_query_id"
                )
            )
        ),
        # Task 4: Data quality checks
        jobs.Task(
            task_key="quality_checks",
            description="Run data quality validation",
            depends_on=[jobs.TaskDependency(task_key="aggregate_gold")],
            notebook_task=jobs.NotebookTask(
                notebook_path="/Workspace/quality/validate"
            ),
            new_cluster=jobs.ClusterSpec(
                spark_version="13.3.x-scala2.12",
                node_type_id="i3.xlarge",
                num_workers=1
            )
        )
    ],
    # Schedule daily at 2 AM
    schedule=jobs.CronSchedule(
        quartz_cron_expression="0 0 2 * * ?",
        timezone_id="America/Los_Angeles",
        pause_status=jobs.PauseStatus.UNPAUSED
    ),
    # Email notifications
    email_notifications=jobs.JobEmailNotifications(
        on_failure=["data-eng-team@company.com"],
        on_success=["data-eng-team@company.com"],
        no_alert_for_skipped_runs=True
    ),
    # Retry configuration
    max_concurrent_runs=1,
    timeout_seconds=7200,
    tags={"team": "data-engineering", "environment": "production"}
)

print(f"Created job: {job.job_id}")
```

### Example 2: Delta Live Tables Pipeline (Python)

```python
# DLT Pipeline Definition (Python)
import dlt
from pyspark.sql import functions as F

# Bronze layer - Raw data ingestion
@dlt.table(
    name="bronze_raw_events",
    comment="Raw event data from source systems",
    table_properties={"quality": "bronze"}
)
def bronze_raw_events():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.schemaLocation", "/mnt/schemas/events")
        .load("/mnt/raw/events/")
    )

# Silver layer - Cleaned and validated
@dlt.table(
    name="silver_events",
    comment="Cleaned event data with quality checks",
    table_properties={"quality": "silver"}
)
@dlt.expect_all({
    "valid_timestamp": "event_timestamp IS NOT NULL",
    "valid_user_id": "user_id IS NOT NULL AND LENGTH(user_id) > 0",
    "valid_event_type": "event_type IN ('click', 'view', 'purchase', 'signup')"
})
@dlt.expect_or_drop("valid_amount", "amount >= 0 OR amount IS NULL")
def silver_events():
    return (
        dlt.read_stream("bronze_raw_events")
        .select(
            F.col("event_id"),
            F.col("user_id"),
            F.col("event_type"),
            F.to_timestamp("event_timestamp").alias("event_timestamp"),
            F.col("amount").cast("decimal(10,2)").alias("amount"),
            F.col("metadata")
        )
        .withColumn("processed_timestamp", F.current_timestamp())
        .dropDuplicates(["event_id"])
    )

# Gold layer - Business aggregations
@dlt.table(
    name="gold_daily_user_metrics",
    comment="Daily user engagement metrics",
    table_properties={"quality": "gold"}
)
def gold_daily_user_metrics():
    return (
        dlt.read("silver_events")
        .groupBy(
            F.to_date("event_timestamp").alias("date"),
            "user_id"
        )
        .agg(
            F.count("*").alias("total_events"),
            F.countDistinct("event_type").alias("unique_event_types"),
            F.sum(F.when(F.col("event_type") == "purchase", F.col("amount"))).alias("total_purchase_amount"),
            F.count(F.when(F.col("event_type") == "purchase", 1)).alias("purchase_count")
        )
    )

# CDC processing example
@dlt.table(
    name="silver_customers_cdc",
    comment="Customer data with CDC applied"
)
def silver_customers_cdc():
    return (
        dlt.read_stream("bronze_customers_cdc")
        .select(
            "customer_id",
            "name",
            "email",
            "updated_at",
            "_change_type"  # insert, update, delete
        )
    )

# Apply CDC changes
dlt.apply_changes(
    target="gold_customers",
    source="silver_customers_cdc",
    keys=["customer_id"],
    sequence_by=F.col("updated_at"),
    stored_as_scd_type=2,  # SCD Type 2
    track_history_column_list=["name", "email"]
)
```

### Example 3: Delta Live Tables Pipeline (SQL)

```sql
-- DLT Pipeline Definition (SQL)

-- Bronze layer
CREATE OR REFRESH STREAMING LIVE TABLE bronze_sales_raw
COMMENT "Raw sales data from CSV files"
TBLPROPERTIES ("quality" = "bronze")
AS SELECT * FROM cloud_files(
  "/mnt/raw/sales/",
  "csv",
  map("header", "true", "inferSchema", "true")
)

-- Silver layer with quality checks
CREATE OR REFRESH STREAMING LIVE TABLE silver_sales
COMMENT "Cleaned sales data with validation"
TBLPROPERTIES ("quality" = "silver")
AS SELECT
  sale_id,
  customer_id,
  product_id,
  CAST(sale_date AS DATE) as sale_date,
  CAST(quantity AS INT) as quantity,
  CAST(unit_price AS DECIMAL(10,2)) as unit_price,
  CAST(quantity * unit_price AS DECIMAL(10,2)) as total_amount,
  region,
  current_timestamp() as processed_timestamp
FROM STREAM(LIVE.bronze_sales_raw)
WHERE
  sale_id IS NOT NULL
  AND customer_id IS NOT NULL
  AND quantity > 0
  AND unit_price > 0

-- Data quality expectations
CONSTRAINT valid_sale_id EXPECT (sale_id IS NOT NULL) ON VIOLATION DROP ROW
CONSTRAINT valid_amount EXPECT (total_amount > 0) ON VIOLATION DROP ROW
CONSTRAINT valid_date EXPECT (sale_date >= '2020-01-01') ON VIOLATION FAIL UPDATE

-- Gold layer aggregations
CREATE OR REFRESH LIVE TABLE gold_daily_sales_summary
COMMENT "Daily sales metrics by region"
TBLPROPERTIES ("quality" = "gold")
AS SELECT
  sale_date,
  region,
  COUNT(DISTINCT sale_id) as total_sales,
  COUNT(DISTINCT customer_id) as unique_customers,
  SUM(quantity) as total_units_sold,
  SUM(total_amount) as total_revenue,
  AVG(total_amount) as avg_sale_amount
FROM LIVE.silver_sales
GROUP BY sale_date, region

-- Gold layer for customer analytics
CREATE OR REFRESH LIVE TABLE gold_customer_metrics
COMMENT "Customer lifetime value and behavior"
TBLPROPERTIES ("quality" = "gold")
AS SELECT
  customer_id,
  MIN(sale_date) as first_purchase_date,
  MAX(sale_date) as last_purchase_date,
  COUNT(DISTINCT sale_id) as total_purchases,
  SUM(total_amount) as lifetime_value,
  AVG(total_amount) as avg_purchase_amount,
  DATEDIFF(MAX(sale_date), MIN(sale_date)) as customer_lifetime_days
FROM LIVE.silver_sales
GROUP BY customer_id
```

### Example 4: Synthetic Data Generation

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *
import random

spark = SparkSession.builder.appName("SyntheticData").getOrCreate()

# Generate synthetic customer data
def generate_customers(num_customers=10000):
    """Generate realistic synthetic customer data"""

    # Define schema
    schema = StructType([
        StructField("customer_id", StringType(), False),
        StructField("first_name", StringType(), False),
        StructField("last_name", StringType(), False),
        StructField("email", StringType(), False),
        StructField("phone", StringType(), True),
        StructField("country", StringType(), False),
        StructField("signup_date", DateType(), False),
        StructField("customer_segment", StringType(), False),
        StructField("credit_score", IntegerType(), True)
    ])

    # Sample data pools
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
    countries = ["USA", "Canada", "UK", "Australia", "Germany"]
    segments = ["Premium", "Standard", "Basic"]

    # Generate data
    customers = []
    for i in range(num_customers):
        first = random.choice(first_names)
        last = random.choice(last_names)
        customers.append({
            "customer_id": f"CUST{i:06d}",
            "first_name": first,
            "last_name": last,
            "email": f"{first.lower()}.{last.lower()}{i}@example.com",
            "phone": f"+1-555-{random.randint(1000000, 9999999)}",
            "country": random.choice(countries),
            "signup_date": spark.sql(f"SELECT date_add('2020-01-01', {random.randint(0, 1460)})").first()[0],
            "customer_segment": random.choice(segments),
            "credit_score": random.randint(300, 850) if random.random() > 0.1 else None
        })

    return spark.createDataFrame(customers, schema)

# Generate synthetic transaction data
def generate_transactions(customers_df, num_transactions=50000):
    """Generate realistic transaction data"""

    # Get customer IDs
    customer_ids = [row.customer_id for row in customers_df.select("customer_id").collect()]

    schema = StructType([
        StructField("transaction_id", StringType(), False),
        StructField("customer_id", StringType(), False),
        StructField("transaction_date", TimestampType(), False),
        StructField("amount", DecimalType(10, 2), False),
        StructField("category", StringType(), False),
        StructField("status", StringType(), False)
    ])

    categories = ["Electronics", "Clothing", "Food", "Home", "Sports", "Books"]
    statuses = ["completed", "pending", "cancelled", "refunded"]

    transactions = []
    for i in range(num_transactions):
        transactions.append({
            "transaction_id": f"TXN{i:08d}",
            "customer_id": random.choice(customer_ids),
            "transaction_date": spark.sql(
                f"SELECT timestamp('2023-01-01') + INTERVAL {random.randint(0, 365)} DAYS + INTERVAL {random.randint(0, 86400)} SECONDS"
            ).first()[0],
            "amount": round(random.uniform(10.0, 500.0), 2),
            "category": random.choice(categories),
            "status": random.choices(statuses, weights=[0.85, 0.08, 0.05, 0.02])[0]
        })

    return spark.createDataFrame(transactions, schema)

# Generate data
customers_df = generate_customers(10000)
transactions_df = generate_transactions(customers_df, 50000)

# Save to Delta tables
customers_df.write.format("delta").mode("overwrite").saveAsTable("main.test.synthetic_customers")
transactions_df.write.format("delta").mode("overwrite").saveAsTable("main.test.synthetic_transactions")

print(f"Generated {customers_df.count()} customers")
print(f"Generated {transactions_df.count()} transactions")
```

### Example 5: Incremental ETL Pattern

```python
from delta.tables import DeltaTable
from pyspark.sql import functions as F

def incremental_load(source_path: str, target_table: str, watermark_column: str):
    """
    Incremental data load with watermarking
    """

    # Get last processed watermark
    if spark._jsparkSession.catalog().tableExists(target_table):
        target_df = spark.table(target_table)
        last_watermark = target_df.agg(F.max(watermark_column)).collect()[0][0]
        print(f"Last watermark: {last_watermark}")
    else:
        last_watermark = None
        print("Initial load - no watermark")

    # Read new data
    source_df = spark.read.format("parquet").load(source_path)

    # Filter to new records only
    if last_watermark:
        new_df = source_df.filter(F.col(watermark_column) > last_watermark)
    else:
        new_df = source_df

    new_count = new_df.count()
    print(f"Found {new_count} new records")

    if new_count > 0:
        # Write to target table
        if spark._jsparkSession.catalog().tableExists(target_table):
            # Append to existing table
            new_df.write.format("delta").mode("append").saveAsTable(target_table)
        else:
            # Create new table
            new_df.write.format("delta").mode("overwrite").saveAsTable(target_table)

        print(f"Successfully loaded {new_count} records")
    else:
        print("No new records to load")

# Usage
incremental_load(
    source_path="/mnt/raw/events/",
    target_table="main.silver.events",
    watermark_column="event_timestamp"
)
```

### Example 6: Complex Job with Error Handling

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs
import time

w = WorkspaceClient()

def create_production_pipeline():
    """Create a production ETL pipeline with comprehensive error handling"""

    job = w.jobs.create(
        name="production_daily_etl",
        tasks=[
            # Pre-flight checks
            jobs.Task(
                task_key="preflight_checks",
                description="Validate source data availability",
                notebook_task=jobs.NotebookTask(
                    notebook_path="/Pipelines/preflight_checks",
                    base_parameters={"date": "{{job.start_time}}"}
                ),
                new_cluster=jobs.ClusterSpec(
                    spark_version="13.3.x-scala2.12",
                    node_type_id="i3.xlarge",
                    num_workers=1
                ),
                timeout_seconds=600,
                max_retries=2,
                min_retry_interval_millis=30000
            ),

            # Main ETL task
            jobs.Task(
                task_key="run_etl",
                description="Execute main ETL pipeline",
                depends_on=[jobs.TaskDependency(task_key="preflight_checks")],
                notebook_task=jobs.NotebookTask(
                    notebook_path="/Pipelines/main_etl"
                ),
                new_cluster=jobs.ClusterSpec(
                    spark_version="13.3.x-scala2.12",
                    node_type_id="i3.2xlarge",
                    num_workers=8,
                    autoscale=jobs.AutoScale(min_workers=4, max_workers=8)
                ),
                timeout_seconds=3600,
                max_retries=1
            ),

            # Data quality validation
            jobs.Task(
                task_key="validate_quality",
                description="Run data quality checks",
                depends_on=[jobs.TaskDependency(task_key="run_etl")],
                notebook_task=jobs.NotebookTask(
                    notebook_path="/Quality/validate"
                ),
                existing_cluster_id="shared-cluster-id",
                timeout_seconds=600
            ),

            # Conditional task - only on failure
            jobs.Task(
                task_key="handle_failure",
                description="Execute failure handler",
                depends_on=[
                    jobs.TaskDependency(
                        task_key="validate_quality",
                        outcome=jobs.TaskDependencyOutcome.FAILED
                    )
                ],
                notebook_task=jobs.NotebookTask(
                    notebook_path="/ErrorHandling/failure_handler"
                ),
                new_cluster=jobs.ClusterSpec(
                    spark_version="13.3.x-scala2.12",
                    node_type_id="i3.xlarge",
                    num_workers=1
                )
            ),

            # Post-processing
            jobs.Task(
                task_key="post_process",
                description="Update metadata and send notifications",
                depends_on=[
                    jobs.TaskDependency(
                        task_key="validate_quality",
                        outcome=jobs.TaskDependencyOutcome.SUCCESS
                    )
                ],
                notebook_task=jobs.NotebookTask(
                    notebook_path="/PostProcess/finalize"
                ),
                existing_cluster_id="shared-cluster-id"
            )
        ],

        # Schedule
        schedule=jobs.CronSchedule(
            quartz_cron_expression="0 0 1 * * ?",  # Daily at 1 AM
            timezone_id="UTC",
            pause_status=jobs.PauseStatus.UNPAUSED
        ),

        # Notifications
        email_notifications=jobs.JobEmailNotifications(
            on_start=["data-eng-oncall@company.com"],
            on_success=["data-eng-team@company.com"],
            on_failure=["data-eng-oncall@company.com", "data-eng-lead@company.com"],
            on_duration_warning_threshold_exceeded=["data-eng-oncall@company.com"]
        ),

        # Webhook notifications (e.g., Slack)
        webhook_notifications=jobs.WebhookNotifications(
            on_failure=[
                jobs.Webhook(
                    id="slack-webhook-id"
                )
            ]
        ),

        # Job configuration
        max_concurrent_runs=1,
        timeout_seconds=7200,

        # Tags for organization
        tags={
            "team": "data-engineering",
            "environment": "production",
            "criticality": "high",
            "cost-center": "analytics"
        }
    )

    return job

# Create job
job = create_production_pipeline()
print(f"Created job {job.job_id}")

# Run job immediately
run = w.jobs.run_now(job_id=job.job_id)
print(f"Started run {run.run_id}")

# Monitor run
while True:
    run_info = w.jobs.get_run(run_id=run.run_id)
    state = run_info.state.life_cycle_state

    print(f"Run state: {state}")

    if state in ["TERMINATED", "SKIPPED", "INTERNAL_ERROR"]:
        result_state = run_info.state.result_state
        print(f"Run finished with state: {result_state}")
        break

    time.sleep(30)
```

---

## 🔧 Common Patterns

### Pattern 1: Medallion Architecture

```python
# Bronze → Silver → Gold pattern

# Bronze: Raw data ingestion
bronze_df = (
    spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")
    .load("/mnt/raw/")
    .withColumn("ingestion_timestamp", F.current_timestamp())
)

bronze_df.writeStream \
    .format("delta") \
    .option("checkpointLocation", "/mnt/checkpoints/bronze") \
    .trigger(availableNow=True) \
    .toTable("main.bronze.raw_events")

# Silver: Cleaned and validated
silver_df = (
    spark.readStream
    .format("delta")
    .table("main.bronze.raw_events")
    .filter("event_type IS NOT NULL")
    .dropDuplicates(["event_id"])
    .withColumn("processed_timestamp", F.current_timestamp())
)

silver_df.writeStream \
    .format("delta") \
    .option("checkpointLocation", "/mnt/checkpoints/silver") \
    .trigger(availableNow=True) \
    .toTable("main.silver.events")

# Gold: Business aggregations
gold_df = (
    spark.read
    .format("delta")
    .table("main.silver.events")
    .groupBy("user_id", F.window("event_timestamp", "1 day"))
    .agg(
        F.count("*").alias("event_count"),
        F.countDistinct("event_type").alias("unique_events")
    )
)

gold_df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("main.gold.daily_user_metrics")
```

### Pattern 2: Idempotent ETL

```python
def idempotent_merge(source_df, target_table, merge_keys):
    """
    Idempotent merge that can be safely re-run
    """
    from delta.tables import DeltaTable

    if spark._jsparkSession.catalog().tableExists(target_table):
        target = DeltaTable.forName(spark, target_table)

        # Build merge condition
        merge_condition = " AND ".join([
            f"source.{key} = target.{key}" for key in merge_keys
        ])

        # Merge with upsert logic
        target.alias("target").merge(
            source_df.alias("source"),
            merge_condition
        ).whenMatchedUpdateAll() \
         .whenNotMatchedInsertAll() \
         .execute()
    else:
        # Initial load
        source_df.write.format("delta").saveAsTable(target_table)

# Usage
idempotent_merge(
    source_df=new_data,
    target_table="main.silver.customers",
    merge_keys=["customer_id"]
)
```

### Pattern 3: Parameterized Job Run

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Run job with custom parameters
run = w.jobs.run_now(
    job_id=123,
    notebook_params={
        "start_date": "2026-01-01",
        "end_date": "2026-01-31",
        "environment": "production",
        "batch_size": "10000"
    }
)

print(f"Started run: {run.run_id}")
```

---

## 📊 Best Practices

### Job Design

1. **Task Organization**
   - Keep tasks focused and single-purpose
   - Use task dependencies for orchestration
   - Separate data quality checks into dedicated tasks
   - Implement pre-flight validation tasks

2. **Error Handling**
   - Set appropriate retry counts and intervals
   - Use timeout settings to prevent hanging jobs
   - Implement failure notification webhooks
   - Create conditional tasks for error recovery

3. **Resource Management**
   - Use job clusters for isolation
   - Share clusters for lightweight tasks
   - Configure autoscaling for variable workloads
   - Set appropriate instance types per task

### Delta Live Tables

1. **Pipeline Design**
   - Follow medallion architecture (Bronze/Silver/Gold)
   - Use streaming for continuous processing
   - Implement incremental processing where possible
   - Define clear data quality expectations

2. **Quality Expectations**
   - Use `EXPECT` for monitoring
   - Use `EXPECT_OR_DROP` for filtering
   - Use `EXPECT_OR_FAIL` for critical validations
   - Document all quality rules

3. **Performance**
   - Partition tables appropriately
   - Use Z-ORDER for frequently filtered columns
   - Enable auto-optimization
   - Monitor pipeline execution metrics

### Data Engineering

1. **Incremental Processing**
   - Implement watermarking for efficiency
   - Use Delta Lake change data feed
   - Leverage file-level incremental reads
   - Track processing metadata

2. **Idempotency**
   - Design jobs to be safely re-runnable
   - Use merge operations for upserts
   - Implement exactly-once semantics
   - Handle duplicate data gracefully

3. **Testing**
   - Test with synthetic data
   - Validate schema changes
   - Test error scenarios
   - Implement data quality tests

---

## 🚀 Getting Started Checklist

### For Databricks Jobs

- [ ] Create first notebook or Python script
- [ ] Define job with single task
- [ ] Configure cluster (job cluster or existing)
- [ ] Add scheduling (cron expression)
- [ ] Set up email notifications
- [ ] Test job execution
- [ ] Add multiple tasks with dependencies
- [ ] Implement error handling
- [ ] Configure retries and timeouts
- [ ] Deploy to production

### For Delta Live Tables

- [ ] Install DLT library
- [ ] Create DLT pipeline definition (Python or SQL)
- [ ] Define bronze layer (raw ingestion)
- [ ] Add data quality expectations
- [ ] Create silver layer (cleaned data)
- [ ] Build gold layer (aggregations)
- [ ] Configure pipeline settings
- [ ] Deploy and run pipeline
- [ ] Monitor pipeline execution
- [ ] Review data quality metrics

### For Production Pipelines

- [ ] Design pipeline architecture
- [ ] Implement incremental processing
- [ ] Add comprehensive error handling
- [ ] Set up monitoring and alerting
- [ ] Create runbooks and documentation
- [ ] Implement automated testing
- [ ] Configure CI/CD integration
- [ ] Set up cost tracking
- [ ] Create disaster recovery plan
- [ ] Schedule regular maintenance

---

## 📖 Additional Resources

### Official Documentation

- [Databricks Jobs](https://docs.databricks.com/en/workflows/jobs/index.html)
- [Delta Live Tables](https://docs.databricks.com/en/delta-live-tables/index.html)
- [Workflow Orchestration](https://docs.databricks.com/en/workflows/index.html)
- [Best Practices](https://docs.databricks.com/en/workflows/jobs/jobs-best-practices.html)

### Tutorials

- [Jobs API Guide](../../api/jobs.md)
- [ETL Patterns](../../examples/etl-patterns.md)
- [Streaming Workflows](../../examples/streaming-workflows.md)
- [Delta Lake Guide](../../sdk/delta-lake.md)
- [ETL Pipeline Tutorial](../../getting-started/etl-pipeline-tutorial.md)

### API References

- [Python SDK](../../sdk/python.md)
- [Clusters API](../../api/clusters.md)
- [Workspace API](../../api/workspace.md)

---

## 🏷️ Tags

`data-engineering` `etl` `jobs` `workflows` `delta-live-tables` `dlt` `pipelines` `orchestration` `medallion-architecture` `bronze-silver-gold` `incremental-loading` `cdc` `data-quality`

---

**Last Updated**: 2026-01-15
**Status**: Jobs well documented - DLT needs dedicated guide
**Maintainer**: Context7 Documentation Team
