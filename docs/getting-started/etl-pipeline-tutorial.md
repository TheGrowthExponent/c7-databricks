# Build ETL Pipelines on Databricks

## Overview

This tutorial guides you through building Extract, Transform, and Load (ETL) pipelines on Databricks using both Lakeflow Spark Declarative Pipelines and traditional Apache Spark approaches. You'll learn how to ingest data, apply transformations, and create production-ready data pipelines.

## Prerequisites

- Access to a Databricks workspace with Unity Catalog enabled
- A running cluster (see [Quick Start Guide](quickstart.md))
- Basic knowledge of SQL and Python
- Permissions to create tables and workflows

## What You'll Learn

- How to build ETL pipelines with Lakeflow Spark Declarative Pipelines
- How to use Auto Loader for incremental data ingestion
- How to create traditional Spark ETL pipelines
- How to implement medallion architecture (Bronze, Silver, Gold)
- How to schedule and monitor pipeline runs
- ETL best practices and optimization techniques

## Part 1: Lakeflow Spark Declarative Pipelines

### Step 1: Understanding Lakeflow

Lakeflow is Databricks' modern data pipeline framework that simplifies ETL development with:

- **Declarative Syntax**: Define what you want, not how to get it
- **Auto Loader Integration**: Automatically ingest new files
- **Automatic Data Quality**: Built-in expectations and monitoring
- **Simplified Orchestration**: Dependencies managed automatically
- **Delta Live Tables**: Optimized for Delta Lake

### Step 2: Create a Lakeflow Pipeline

#### Define Pipeline Configuration

```python
# Databricks notebook source
# MAGIC %md
# MAGIC # Lakeflow ETL Pipeline
# MAGIC
# MAGIC This notebook defines a Lakeflow pipeline for processing sales data

import dlt
from pyspark.sql.functions import col, current_timestamp, to_date

# Define source path
source_path = "/Volumes/main/default/raw_data/sales"
```

#### Bronze Layer - Raw Data Ingestion

```python
@dlt.table(
    name="bronze_sales_raw",
    comment="Raw sales data ingested from cloud storage",
    table_properties={
        "quality": "bronze",
        "pipelines.autoOptimize.managed": "true"
    }
)
def bronze_sales_raw():
    """
    Ingest raw sales data using Auto Loader
    """
    return (
        spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "csv")
            .option("cloudFiles.schemaLocation", f"{source_path}/_schema")
            .option("cloudFiles.inferColumnTypes", "true")
            .option("header", "true")
            .load(source_path)
            .withColumn("ingestion_timestamp", current_timestamp())
    )
```

#### Silver Layer - Cleaned and Validated Data

```python
@dlt.table(
    name="silver_sales_cleaned",
    comment="Cleaned and validated sales data",
    table_properties={
        "quality": "silver"
    }
)
@dlt.expect_or_drop("valid_amount", "sale_amount > 0")
@dlt.expect_or_drop("valid_date", "sale_date IS NOT NULL")
@dlt.expect_or_fail("valid_customer_id", "customer_id IS NOT NULL")
def silver_sales_cleaned():
    """
    Clean and validate sales data with data quality expectations
    """
    return (
        dlt.read_stream("bronze_sales_raw")
            .select(
                col("transaction_id"),
                col("customer_id"),
                col("product_id"),
                col("sale_amount").cast("decimal(10,2)"),
                to_date(col("sale_date")).alias("sale_date"),
                col("quantity").cast("int"),
                col("store_id"),
                col("ingestion_timestamp")
            )
            .filter(col("sale_amount").isNotNull())
            .filter(col("customer_id").isNotNull())
    )
```

#### Gold Layer - Business Aggregations

```python
@dlt.table(
    name="gold_daily_sales_summary",
    comment="Daily sales summary for analytics",
    table_properties={
        "quality": "gold"
    }
)
def gold_daily_sales_summary():
    """
    Daily sales aggregation for business reporting
    """
    return (
        dlt.read("silver_sales_cleaned")
            .groupBy("sale_date", "store_id")
            .agg(
                count("*").alias("transaction_count"),
                sum("sale_amount").alias("total_revenue"),
                avg("sale_amount").alias("avg_transaction_value"),
                sum("quantity").alias("total_items_sold")
            )
    )

@dlt.table(
    name="gold_customer_purchases",
    comment="Customer purchase history and metrics"
)
def gold_customer_purchases():
    """
    Customer-level purchase aggregations
    """
    return (
        dlt.read("silver_sales_cleaned")
            .groupBy("customer_id")
            .agg(
                count("*").alias("total_purchases"),
                sum("sale_amount").alias("lifetime_value"),
                avg("sale_amount").alias("avg_purchase_value"),
                min("sale_date").alias("first_purchase_date"),
                max("sale_date").alias("last_purchase_date")
            )
    )
```

### Step 3: Create Pipeline via UI

1. Click **Workflows** in the left sidebar
2. Click **Delta Live Tables** tab
3. Click **Create Pipeline**
4. Configure:
   - **Pipeline Name**: `sales_etl_pipeline`
   - **Product Edition**: Advanced (for data quality features)
   - **Source Code**: Select your notebook
   - **Target Catalog**: `main`
   - **Target Schema**: `sales_pipeline`
   - **Storage Location**: (optional) specify location
5. Click **Create**
6. Click **Start** to run the pipeline

### Step 4: Create Pipeline via Python SDK

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import pipelines

client = WorkspaceClient()

# Create pipeline
pipeline = client.pipelines.create(
    name="sales_etl_pipeline",
    catalog="main",
    target="sales_pipeline",
    continuous=False,
    libraries=[
        pipelines.PipelineLibrary(
            notebook=pipelines.NotebookLibrary(
                path="/Users/user@company.com/lakeflow_sales_pipeline"
            )
        )
    ],
    clusters=[
        pipelines.PipelineCluster(
            label="default",
            num_workers=2,
            node_type_id="i3.xlarge"
        )
    ],
    development=False,
    edition="ADVANCED",
    channel="CURRENT"
)

print(f"Pipeline created with ID: {pipeline.pipeline_id}")

# Start pipeline
update = client.pipelines.start_update(
    pipeline_id=pipeline.pipeline_id
)

print(f"Pipeline update started: {update.update_id}")
```

### Step 5: Monitor Pipeline Execution

```python
# Get pipeline details
pipeline_info = client.pipelines.get(pipeline_id=pipeline.pipeline_id)
print(f"Pipeline state: {pipeline_info.state}")

# Get update status
update_info = client.pipelines.get_update(
    pipeline_id=pipeline.pipeline_id,
    update_id=update.update_id
)

print(f"Update state: {update_info.update.state}")

# List all updates
updates = client.pipelines.list_updates(pipeline_id=pipeline.pipeline_id)
for u in updates:
    print(f"Update {u.update_id}: {u.state}")
```

### Step 6: Query Pipeline Results

```sql
-- Query bronze layer
SELECT * FROM main.sales_pipeline.bronze_sales_raw LIMIT 10;

-- Query silver layer
SELECT * FROM main.sales_pipeline.silver_sales_cleaned LIMIT 10;

-- Query gold layer
SELECT
    sale_date,
    SUM(total_revenue) as daily_revenue,
    SUM(transaction_count) as daily_transactions
FROM main.sales_pipeline.gold_daily_sales_summary
GROUP BY sale_date
ORDER BY sale_date DESC;
```

## Part 2: Traditional Apache Spark ETL Pipeline

### Step 1: Create Sample Source Data

```python
# Create sample sales data
from pyspark.sql.types import StructType, StructField, StringType, DecimalType, DateType, IntegerType
import datetime

# Define schema
schema = StructType([
    StructField("transaction_id", StringType(), False),
    StructField("customer_id", StringType(), False),
    StructField("product_id", StringType(), False),
    StructField("sale_amount", DecimalType(10, 2), False),
    StructField("sale_date", DateType(), False),
    StructField("quantity", IntegerType(), False),
    StructField("store_id", StringType(), False)
])

# Create sample data
sales_data = [
    ("TXN001", "CUST001", "PROD001", 99.99, datetime.date(2024, 1, 15), 2, "STORE01"),
    ("TXN002", "CUST002", "PROD002", 149.50, datetime.date(2024, 1, 15), 1, "STORE01"),
    ("TXN003", "CUST001", "PROD003", 75.25, datetime.date(2024, 1, 16), 3, "STORE02"),
    ("TXN004", "CUST003", "PROD001", 99.99, datetime.date(2024, 1, 16), 1, "STORE01"),
    ("TXN005", "CUST004", "PROD004", 299.99, datetime.date(2024, 1, 17), 1, "STORE03")
]

sales_df = spark.createDataFrame(sales_data, schema=schema)

# Write to source location
source_path = "/Volumes/main/default/raw_data/sales_spark"
sales_df.write.format("csv") \
    .option("header", "true") \
    .mode("overwrite") \
    .save(source_path)

print(f"Sample data written to {source_path}")
```

### Step 2: Extract - Read Source Data

```python
from pyspark.sql.functions import col, current_timestamp

# Extract: Read raw data
def extract_sales_data(source_path):
    """
    Extract sales data from source location
    """
    df = spark.read.format("csv") \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .load(source_path) \
        .withColumn("extraction_timestamp", current_timestamp())

    print(f"Extracted {df.count()} records")
    return df

# Run extraction
raw_df = extract_sales_data(source_path)
display(raw_df)
```

### Step 3: Transform - Clean and Enrich Data

```python
from pyspark.sql.functions import col, when, trim, upper, year, month, dayofweek

def transform_sales_data(df):
    """
    Transform and clean sales data
    """
    # Data cleaning
    cleaned_df = df \
        .filter(col("sale_amount") > 0) \
        .filter(col("customer_id").isNotNull()) \
        .filter(col("sale_date").isNotNull()) \
        .withColumn("customer_id", trim(upper(col("customer_id")))) \
        .withColumn("product_id", trim(upper(col("product_id")))) \
        .withColumn("store_id", trim(upper(col("store_id"))))

    # Data enrichment
    enriched_df = cleaned_df \
        .withColumn("sale_year", year(col("sale_date"))) \
        .withColumn("sale_month", month(col("sale_date"))) \
        .withColumn("day_of_week", dayofweek(col("sale_date"))) \
        .withColumn("total_amount", col("sale_amount") * col("quantity")) \
        .withColumn("is_weekend",
                   when(dayofweek(col("sale_date")).isin([1, 7]), True).otherwise(False))

    # Data validation
    validated_df = enriched_df \
        .filter(col("quantity") > 0) \
        .filter(col("total_amount") > 0)

    print(f"Transformed {validated_df.count()} records")
    return validated_df

# Run transformation
transformed_df = transform_sales_data(raw_df)
display(transformed_df)
```

### Step 4: Load - Write to Target Tables

```python
def load_bronze_layer(df, target_table):
    """
    Load raw data to bronze layer
    """
    df.write.format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .saveAsTable(target_table)

    print(f"Loaded bronze layer: {target_table}")

def load_silver_layer(df, target_table):
    """
    Load transformed data to silver layer
    """
    df.write.format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .saveAsTable(target_table)

    print(f"Loaded silver layer: {target_table}")

# Load data
load_bronze_layer(raw_df, "main.default.bronze_sales_spark")
load_silver_layer(transformed_df, "main.default.silver_sales_spark")
```

### Step 5: Create Gold Layer Aggregations

```python
from pyspark.sql.functions import sum, avg, count, min, max, round

def create_gold_daily_summary(silver_table):
    """
    Create daily sales summary
    """
    df = spark.table(silver_table)

    summary_df = df.groupBy("sale_date", "store_id") \
        .agg(
            count("*").alias("transaction_count"),
            round(sum("total_amount"), 2).alias("total_revenue"),
            round(avg("total_amount"), 2).alias("avg_transaction_value"),
            sum("quantity").alias("total_items_sold")
        )

    summary_df.write.format("delta") \
        .mode("overwrite") \
        .saveAsTable("main.default.gold_daily_sales_spark")

    print("Created gold daily summary")
    return summary_df

def create_gold_customer_metrics(silver_table):
    """
    Create customer-level metrics
    """
    df = spark.table(silver_table)

    customer_df = df.groupBy("customer_id") \
        .agg(
            count("*").alias("total_purchases"),
            round(sum("total_amount"), 2).alias("lifetime_value"),
            round(avg("total_amount"), 2).alias("avg_purchase_value"),
            min("sale_date").alias("first_purchase_date"),
            max("sale_date").alias("last_purchase_date")
        )

    customer_df.write.format("delta") \
        .mode("overwrite") \
        .saveAsTable("main.default.gold_customer_metrics_spark")

    print("Created gold customer metrics")
    return customer_df

# Create gold tables
daily_summary = create_gold_daily_summary("main.default.silver_sales_spark")
display(daily_summary)

customer_metrics = create_gold_customer_metrics("main.default.silver_sales_spark")
display(customer_metrics)
```

### Step 6: Implement Incremental Processing

```python
from delta.tables import DeltaTable

def incremental_load_silver(new_data_df, target_table):
    """
    Incrementally load data using MERGE
    """
    if spark.catalog.tableExists(target_table):
        # Table exists - perform MERGE
        target = DeltaTable.forName(spark, target_table)

        target.alias("target").merge(
            new_data_df.alias("source"),
            "target.transaction_id = source.transaction_id"
        ).whenMatchedUpdateAll() \
         .whenNotMatchedInsertAll() \
         .execute()

        print(f"Merged data into {target_table}")
    else:
        # Table doesn't exist - create it
        new_data_df.write.format("delta") \
            .mode("overwrite") \
            .saveAsTable(target_table)

        print(f"Created new table {target_table}")

# Example: Add new transactions
new_sales_data = [
    ("TXN006", "CUST001", "PROD002", 149.50, datetime.date(2024, 1, 18), 1, "STORE01"),
    ("TXN007", "CUST005", "PROD001", 99.99, datetime.date(2024, 1, 18), 2, "STORE02")
]

new_sales_df = spark.createDataFrame(new_sales_data, schema=schema)
transformed_new = transform_sales_data(new_sales_df)

# Incremental load
incremental_load_silver(transformed_new, "main.default.silver_sales_spark")
```

### Step 7: Create Complete ETL Job

```python
def run_etl_pipeline(source_path, target_schema, incremental=False):
    """
    Complete ETL pipeline function
    """
    print(f"Starting ETL pipeline for {source_path}")

    # Extract
    print("Step 1: Extracting data...")
    raw_df = extract_sales_data(source_path)

    # Transform
    print("Step 2: Transforming data...")
    transformed_df = transform_sales_data(raw_df)

    # Load
    print("Step 3: Loading data...")
    bronze_table = f"{target_schema}.bronze_sales"
    silver_table = f"{target_schema}.silver_sales"

    load_bronze_layer(raw_df, bronze_table)

    if incremental:
        incremental_load_silver(transformed_df, silver_table)
    else:
        load_silver_layer(transformed_df, silver_table)

    # Create gold layer
    print("Step 4: Creating gold layer...")
    create_gold_daily_summary(silver_table)
    create_gold_customer_metrics(silver_table)

    print("ETL pipeline completed successfully!")

    # Return summary
    return {
        "bronze_count": raw_df.count(),
        "silver_count": transformed_df.count(),
        "status": "SUCCESS"
    }

# Run the pipeline
result = run_etl_pipeline(
    source_path="/Volumes/main/default/raw_data/sales_spark",
    target_schema="main.default",
    incremental=False
)

print(f"Pipeline result: {result}")
```

## Part 3: Schedule and Orchestrate ETL

### Step 1: Create Workflow Job

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs

client = WorkspaceClient()

# Create ETL job
job = client.jobs.create(
    name="Sales ETL Pipeline",
    tasks=[
        jobs.Task(
            task_key="extract_load_bronze",
            description="Extract raw data and load to bronze",
            notebook_task=jobs.NotebookTask(
                notebook_path="/Users/user@company.com/etl_bronze",
                base_parameters={"source_path": "/Volumes/main/default/raw_data/sales"}
            ),
            new_cluster=jobs.ClusterSpec(
                spark_version="13.3.x-scala2.12",
                node_type_id="i3.xlarge",
                num_workers=2
            )
        ),
        jobs.Task(
            task_key="transform_load_silver",
            description="Transform and load to silver",
            depends_on=[jobs.TaskDependency(task_key="extract_load_bronze")],
            notebook_task=jobs.NotebookTask(
                notebook_path="/Users/user@company.com/etl_silver",
                base_parameters={}
            ),
            new_cluster=jobs.ClusterSpec(
                spark_version="13.3.x-scala2.12",
                node_type_id="i3.xlarge",
                num_workers=2
            )
        ),
        jobs.Task(
            task_key="create_gold_layer",
            description="Create gold layer aggregations",
            depends_on=[jobs.TaskDependency(task_key="transform_load_silver")],
            notebook_task=jobs.NotebookTask(
                notebook_path="/Users/user@company.com/etl_gold",
                base_parameters={}
            ),
            new_cluster=jobs.ClusterSpec(
                spark_version="13.3.x-scala2.12",
                node_type_id="i3.xlarge",
                num_workers=2
            )
        )
    ],
    schedule=jobs.CronSchedule(
        quartz_cron_expression="0 0 2 * * ?",  # Daily at 2 AM
        timezone_id="America/Los_Angeles"
    ),
    email_notifications=jobs.JobEmailNotifications(
        on_success=["data-team@company.com"],
        on_failure=["data-team@company.com"]
    ),
    max_concurrent_runs=1
)

print(f"Job created with ID: {job.job_id}")
```

### Step 2: Monitor Job Execution

```python
# Run job immediately
run = client.jobs.run_now(job_id=job.job_id)
print(f"Job run started: {run.run_id}")

# Get run status
run_info = client.jobs.get_run(run_id=run.run_id)
print(f"Run state: {run_info.state.life_cycle_state}")

# List recent runs
runs = client.jobs.list_runs(job_id=job.job_id, limit=10)
for r in runs:
    print(f"Run {r.run_id}: {r.state.life_cycle_state}")
```

## Part 4: Advanced ETL Patterns

### Error Handling and Retry Logic

```python
from pyspark.sql.utils import AnalysisException
import time

def robust_etl_pipeline(source_path, target_schema, max_retries=3):
    """
    ETL pipeline with error handling and retry logic
    """
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} of {max_retries}")

            # Run ETL
            result = run_etl_pipeline(source_path, target_schema)

            print("Pipeline completed successfully")
            return result

        except AnalysisException as e:
            print(f"Analysis error: {str(e)}")
            if attempt < max_retries - 1:
                print("Retrying...")
                time.sleep(5)
            else:
                raise

        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            # Log error to monitoring system
            raise

    return {"status": "FAILED"}

# Run with error handling
result = robust_etl_pipeline(
    source_path="/Volumes/main/default/raw_data/sales_spark",
    target_schema="main.default"
)
```

### Data Quality Validation

```python
from pyspark.sql.functions import col, count, when

def validate_data_quality(df, table_name):
    """
    Validate data quality metrics
    """
    total_records = df.count()

    validation_results = df.agg(
        count("*").alias("total_records"),
        count(when(col("sale_amount").isNull(), 1)).alias("null_amounts"),
        count(when(col("sale_amount") <= 0, 1)).alias("invalid_amounts"),
        count(when(col("customer_id").isNull(), 1)).alias("null_customers"),
        count(when(col("quantity") <= 0, 1)).alias("invalid_quantities")
    ).collect()[0]

    # Calculate quality score
    null_count = (validation_results["null_amounts"] +
                  validation_results["null_customers"])
    invalid_count = (validation_results["invalid_amounts"] +
                     validation_results["invalid_quantities"])

    quality_score = ((total_records - null_count - invalid_count) / total_records) * 100

    print(f"Data Quality Report for {table_name}:")
    print(f"  Total records: {total_records}")
    print(f"  Null values: {null_count}")
    print(f"  Invalid values: {invalid_count}")
    print(f"  Quality score: {quality_score:.2f}%")

    # Fail if quality is too low
    if quality_score < 95:
        raise ValueError(f"Data quality below threshold: {quality_score:.2f}%")

    return quality_score

# Validate transformed data
quality_score = validate_data_quality(transformed_df, "silver_sales")
```

### Audit Logging

```python
from pyspark.sql.functions import lit, current_timestamp

def log_pipeline_execution(pipeline_name, status, records_processed, execution_time):
    """
    Log pipeline execution details
    """
    log_data = [(
        pipeline_name,
        status,
        records_processed,
        execution_time,
        current_timestamp()
    )]

    log_schema = StructType([
        StructField("pipeline_name", StringType()),
        StructField("status", StringType()),
        StructField("records_processed", IntegerType()),
        StructField("execution_time_seconds", DecimalType(10, 2)),
        StructField("execution_timestamp", TimestampType())
    ])

    log_df = spark.createDataFrame(log_data, schema=log_schema)

    # Append to audit log table
    log_df.write.format("delta") \
        .mode("append") \
        .saveAsTable("main.default.etl_audit_log")

    print(f"Logged execution: {pipeline_name} - {status}")

# Example usage
log_pipeline_execution(
    pipeline_name="sales_etl_pipeline",
    status="SUCCESS",
    records_processed=1000,
    execution_time=45.5
)
```

## Best Practices

### 1. Use Medallion Architecture

```python
# Bronze: Raw data (no transformation)
raw_df.write.format("delta").saveAsTable("bronze.table_name")

# Silver: Cleaned and validated
cleaned_df.write.format("delta").saveAsTable("silver.table_name")

# Gold: Business aggregations
aggregated_df.write.format("delta").saveAsTable("gold.table_name")
```

### 2. Implement Idempotency

```python
# Use MERGE for idempotent operations
def idempotent_load(df, target_table, key_columns):
    if spark.catalog.tableExists(target_table):
        target = DeltaTable.forName(spark, target_table)
        merge_condition = " AND ".join([f"target.{col} = source.{col}" for col in key_columns])

        target.alias("target").merge(
            df.alias("source"),
            merge_condition
        ).whenMatchedUpdateAll() \
         .whenNotMatchedInsertAll() \
         .execute()
    else:
        df.write.format("delta").saveAsTable(target_table)
```

### 3. Optimize Performance

```python
# Partition large tables
df.write.format("delta") \
    .partitionBy("sale_year", "sale_month") \
    .saveAsTable("table_name")

# Optimize and Z-order
spark.sql("OPTIMIZE table_name ZORDER BY (customer_id)")

# Cache intermediate results
df.cache()
```

## Next Steps

- **[Train ML Models](ml-model-tutorial.md)**: Use ETL data for machine learning
- **[Query Data](query-visualize-data.md)**: Analyze pipeline outputs
- **[Jobs API](../api/jobs.md)**: Advanced orchestration
- **[Best Practices](../best-practices/performance.md)**: Optimize pipelines

## Summary

In this tutorial, you learned how to:

✅ Build declarative pipelines with Lakeflow
✅ Create traditional Spark ETL workflows
✅ Implement medallion architecture
✅ Use Auto Loader for incremental ingestion
✅ Schedule and orchestrate pipelines
✅ Implement error handling and data quality checks
✅ Apply ETL best practices

You're now ready to build production-grade ETL pipelines on Databricks!
