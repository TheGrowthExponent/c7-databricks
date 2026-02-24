# Databricks ETL Patterns and Examples

## Overview

This guide provides production-ready ETL (Extract, Transform, Load) patterns for Databricks, covering common data engineering scenarios with Delta Lake, Spark, and best practices.

## Table of Contents

1. [Basic ETL Patterns](#basic-etl-patterns)
2. [Incremental Loading](#incremental-loading)
3. [Change Data Capture (CDC)](#change-data-capture-cdc)
4. [Slowly Changing Dimensions](#slowly-changing-dimensions)
5. [Data Quality Patterns](#data-quality-patterns)
6. [Orchestration Patterns](#orchestration-patterns)

---

## Basic ETL Patterns

### Simple Extract-Transform-Load

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, to_date

spark = SparkSession.builder.appName("BasicETL").getOrCreate()

# EXTRACT: Read from source
raw_df = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load("s3://source-bucket/data/*.csv")

# TRANSFORM: Clean and transform
transformed_df = raw_df \
    .filter(col("amount").isNotNull()) \
    .withColumn("load_date", current_timestamp()) \
    .withColumn("transaction_date", to_date(col("transaction_date"), "yyyy-MM-dd")) \
    .select(
        "transaction_id",
        "customer_id",
        "amount",
        "transaction_date",
        "load_date"
    )

# LOAD: Write to Delta table
transformed_df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("mergeSchema", "true") \
    .saveAsTable("catalog.schema.transactions")

print(f"Loaded {transformed_df.count()} records")
```

### Multi-Source Join Pattern

```python
from pyspark.sql.functions import col, coalesce, lit

# Extract from multiple sources
customers_df = spark.read.format("delta").table("catalog.schema.customers")
orders_df = spark.read.format("delta").table("catalog.schema.orders")
products_df = spark.read.format("delta").table("catalog.schema.products")

# Transform: Join and aggregate
enriched_orders = orders_df \
    .join(customers_df, "customer_id", "left") \
    .join(products_df, "product_id", "left") \
    .select(
        col("order_id"),
        col("customer_id"),
        coalesce(col("customer_name"), lit("Unknown")).alias("customer_name"),
        col("product_id"),
        coalesce(col("product_name"), lit("Unknown")).alias("product_name"),
        col("quantity"),
        col("unit_price"),
        (col("quantity") * col("unit_price")).alias("total_amount"),
        col("order_date")
    )

# Load to target
enriched_orders.write \
    .format("delta") \
    .mode("overwrite") \
    .partitionBy("order_date") \
    .saveAsTable("catalog.schema.enriched_orders")
```

### Batch Processing with Error Handling

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lit
from delta.tables import DeltaTable
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_batch(source_path, target_table, error_table):
    """
    Process batch with error handling and logging
    """
    try:
        # Extract
        logger.info(f"Reading data from {source_path}")
        df = spark.read.format("parquet").load(source_path)
        
        # Add validation column
        validated_df = df.withColumn(
            "is_valid",
            when(
                (col("customer_id").isNotNull()) & 
                (col("amount") > 0) &
                (col("transaction_date").isNotNull()),
                lit(True)
            ).otherwise(lit(False))
        )
        
        # Split valid and invalid records
        valid_df = validated_df.filter(col("is_valid") == True).drop("is_valid")
        invalid_df = validated_df.filter(col("is_valid") == False)
        
        # Load valid records
        if valid_df.count() > 0:
            valid_df.write \
                .format("delta") \
                .mode("append") \
                .saveAsTable(target_table)
            logger.info(f"Loaded {valid_df.count()} valid records")
        
        # Log invalid records
        if invalid_df.count() > 0:
            invalid_df \
                .withColumn("error_timestamp", current_timestamp()) \
                .withColumn("source_file", lit(source_path)) \
                .write \
                .format("delta") \
                .mode("append") \
                .saveAsTable(error_table)
            logger.warning(f"Found {invalid_df.count()} invalid records")
        
        return True
        
    except Exception as e:
        logger.error(f"Error processing batch: {str(e)}")
        raise

# Usage
process_batch(
    source_path="s3://source/batch_20240115/",
    target_table="catalog.schema.transactions",
    error_table="catalog.schema.transaction_errors"
)
```

---

## Incremental Loading

### Watermark-Based Incremental Load

```python
from pyspark.sql.functions import col, max as spark_max, lit
from delta.tables import DeltaTable

def incremental_load(source_table, target_table, watermark_column):
    """
    Load only new/changed records based on watermark
    """
    
    # Get last watermark from target
    try:
        target_df = spark.read.format("delta").table(target_table)
        last_watermark = target_df.agg(spark_max(watermark_column)).collect()[0][0]
    except:
        # First load - no watermark exists
        last_watermark = None
    
    # Read source data
    source_df = spark.read.table(source_table)
    
    # Filter for new records
    if last_watermark:
        new_records = source_df.filter(col(watermark_column) > last_watermark)
        print(f"Loading records where {watermark_column} > {last_watermark}")
    else:
        new_records = source_df
        print("Performing initial full load")
    
    # Add processing metadata
    new_records = new_records \
        .withColumn("processed_timestamp", current_timestamp()) \
        .withColumn("load_type", lit("incremental" if last_watermark else "full"))
    
    # Merge into target
    if new_records.count() > 0:
        target_delta = DeltaTable.forName(spark, target_table)
        
        target_delta.alias("target").merge(
            new_records.alias("source"),
            "target.id = source.id"
        ).whenMatchedUpdateAll() \
         .whenNotMatchedInsertAll() \
         .execute()
        
        print(f"Processed {new_records.count()} records")
        return new_records.count()
    else:
        print("No new records to process")
        return 0

# Usage
records_processed = incremental_load(
    source_table="source_db.customer_events",
    target_table="catalog.schema.customer_events",
    watermark_column="event_timestamp"
)
```

### Append-Only Incremental Pattern

```python
from pyspark.sql.functions import col, current_timestamp
import os

def append_only_load(source_path, target_table, checkpoint_path):
    """
    Append-only incremental load with checkpoint tracking
    """
    
    # Get list of already processed files
    try:
        processed_files = spark.read.text(checkpoint_path).rdd.map(lambda r: r[0]).collect()
    except:
        processed_files = []
    
    # List all source files
    all_files = dbutils.fs.ls(source_path)
    new_files = [f.path for f in all_files if f.path not in processed_files]
    
    if not new_files:
        print("No new files to process")
        return 0
    
    print(f"Processing {len(new_files)} new files")
    
    # Process each file
    total_records = 0
    for file_path in new_files:
        try:
            # Read file
            df = spark.read.format("json").load(file_path)
            
            # Add metadata
            df = df.withColumn("source_file", lit(file_path)) \
                   .withColumn("load_timestamp", current_timestamp())
            
            # Append to target
            df.write.format("delta").mode("append").saveAsTable(target_table)
            
            # Update checkpoint
            spark.createDataFrame([(file_path,)], ["file_path"]) \
                .write.mode("append").text(checkpoint_path)
            
            record_count = df.count()
            total_records += record_count
            print(f"Processed {file_path}: {record_count} records")
            
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            continue
    
    print(f"Total records loaded: {total_records}")
    return total_records

# Usage
append_only_load(
    source_path="s3://source-bucket/daily-exports/",
    target_table="catalog.schema.daily_data",
    checkpoint_path="s3://checkpoint-bucket/processed_files/"
)
```

---

## Change Data Capture (CDC)

### CDC with Delta Lake Change Data Feed

```python
from pyspark.sql.functions import col, when, lit
from delta.tables import DeltaTable

def process_cdc_changes(source_table, target_table, start_version, end_version):
    """
    Process CDC changes from Delta table change data feed
    """
    
    # Read changes
    changes_df = spark.read.format("delta") \
        .option("readChangeData", "true") \
        .option("startingVersion", start_version) \
        .option("endingVersion", end_version) \
        .table(source_table)
    
    # Process by change type
    inserts = changes_df.filter(col("_change_type") == "insert")
    updates = changes_df.filter(col("_change_type") == "update_postimage")
    deletes = changes_df.filter(col("_change_type") == "delete")
    
    print(f"Changes: {inserts.count()} inserts, {updates.count()} updates, {deletes.count()} deletes")
    
    # Apply changes to target
    target_delta = DeltaTable.forName(spark, target_table)
    
    # Process deletes
    if deletes.count() > 0:
        delete_ids = deletes.select("id").rdd.flatMap(lambda x: x).collect()
        target_delta.delete(col("id").isin(delete_ids))
    
    # Process inserts and updates
    upsert_df = inserts.union(updates).drop("_change_type", "_commit_version", "_commit_timestamp")
    
    if upsert_df.count() > 0:
        target_delta.alias("target").merge(
            upsert_df.alias("source"),
            "target.id = source.id"
        ).whenMatchedUpdateAll() \
         .whenNotMatchedInsertAll() \
         .execute()
    
    print("CDC processing complete")

# Enable CDF on source table first
spark.sql("""
    ALTER TABLE catalog.schema.source_table
    SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")

# Process changes
process_cdc_changes(
    source_table="catalog.schema.source_table",
    target_table="catalog.schema.target_table",
    start_version=0,
    end_version=10
)
```

### CDC from External System

```python
from pyspark.sql.functions import col, when, lit, current_timestamp

def process_external_cdc(cdc_file_path, target_table):
    """
    Process CDC file from external system (e.g., Debezium, Oracle GoldenGate)
    """
    
    # Read CDC file
    cdc_df = spark.read.format("json").load(cdc_file_path)
    
    # Parse CDC operation
    parsed_cdc = cdc_df \
        .withColumn("operation", col("op")) \
        .withColumn("data", 
            when(col("op").isin("c", "r", "u"), col("after"))
            .when(col("op") == "d", col("before"))
        )
    
    # Expand nested data
    flattened = parsed_cdc.select(
        col("operation"),
        col("data.*"),
        current_timestamp().alias("cdc_processed_at")
    )
    
    # Separate by operation
    inserts = flattened.filter(col("operation").isin("c", "r"))  # create, read
    updates = flattened.filter(col("operation") == "u")  # update
    deletes = flattened.filter(col("operation") == "d")  # delete
    
    target_delta = DeltaTable.forName(spark, target_table)
    
    # Apply deletes
    if deletes.count() > 0:
        delete_keys = deletes.select("id").rdd.flatMap(lambda x: x).collect()
        target_delta.delete(col("id").isin(delete_keys))
        print(f"Deleted {len(delete_keys)} records")
    
    # Apply inserts and updates
    upserts = inserts.union(updates).drop("operation")
    
    if upserts.count() > 0:
        target_delta.alias("target").merge(
            upserts.alias("source"),
            "target.id = source.id"
        ).whenMatchedUpdateAll() \
         .whenNotMatchedInsertAll() \
         .execute()
        print(f"Upserted {upserts.count()} records")

# Usage
process_external_cdc(
    cdc_file_path="s3://cdc-bucket/changes/*.json",
    target_table="catalog.schema.customers"
)
```

---

## Slowly Changing Dimensions

### SCD Type 1 (Overwrite)

```python
from delta.tables import DeltaTable
from pyspark.sql.functions import col, current_timestamp

def scd_type1_merge(target_table, source_df, key_columns):
    """
    SCD Type 1: Overwrite changed records
    """
    
    target_delta = DeltaTable.forName(spark, target_table)
    
    # Add update timestamp
    source_with_timestamp = source_df.withColumn("updated_at", current_timestamp())
    
    # Build merge condition
    merge_condition = " AND ".join([f"target.{col} = source.{col}" for col in key_columns])
    
    # Merge (overwrite on match)
    target_delta.alias("target").merge(
        source_with_timestamp.alias("source"),
        merge_condition
    ).whenMatchedUpdateAll() \
     .whenNotMatchedInsertAll() \
     .execute()
    
    print("SCD Type 1 merge complete")

# Usage
source_updates = spark.createDataFrame([
    (1, "Alice Johnson", "alice.j@example.com", "555-0001"),
    (2, "Bob Smith", "bob.s@example.com", "555-0002")
], ["customer_id", "name", "email", "phone"])

scd_type1_merge(
    target_table="catalog.schema.customers",
    source_df=source_updates,
    key_columns=["customer_id"]
)
```

### SCD Type 2 (Historical Tracking)

```python
from pyspark.sql.functions import col, lit, current_timestamp, when, coalesce
from pyspark.sql.types import TimestampType
from delta.tables import DeltaTable

def scd_type2_merge(target_table, source_df, key_columns, track_columns):
    """
    SCD Type 2: Maintain history of changes
    """
    
    target = DeltaTable.forName(spark, target_table)
    
    # Add SCD columns to source
    source_with_scd = source_df \
        .withColumn("effective_start_date", current_timestamp()) \
        .withColumn("effective_end_date", lit(None).cast(TimestampType())) \
        .withColumn("is_current", lit(True))
    
    # Build merge condition (match on key and current flag)
    key_condition = " AND ".join([f"target.{col} = source.{col}" for col in key_columns])
    merge_condition = f"{key_condition} AND target.is_current = true"
    
    # Build change detection condition
    change_condition = " OR ".join([f"target.{col} != source.{col}" for col in track_columns])
    
    # Expire old records (set end date and is_current flag)
    target.alias("target").merge(
        source_with_scd.alias("source"),
        merge_condition
    ).whenMatchedUpdate(
        condition=change_condition,
        set={
            "effective_end_date": current_timestamp(),
            "is_current": lit(False)
        }
    ).execute()
    
    # Insert new versions for changed records
    target_df = target.toDF()
    
    changed_keys = target_df \
        .filter(
            (col("is_current") == False) &
            (col("effective_end_date").isNotNull())
        ) \
        .select(*key_columns) \
        .distinct()
    
    new_versions = source_with_scd.join(
        changed_keys,
        on=key_columns,
        how="inner"
    )
    
    if new_versions.count() > 0:
        new_versions.write.format("delta").mode("append").saveAsTable(target_table)
        print(f"Inserted {new_versions.count()} new versions")
    
    # Insert completely new records
    target.alias("target").merge(
        source_with_scd.alias("source"),
        " AND ".join([f"target.{col} = source.{col}" for col in key_columns])
    ).whenNotMatchedInsertAll().execute()
    
    print("SCD Type 2 merge complete")

# Create SCD Type 2 table
spark.sql("""
    CREATE TABLE IF NOT EXISTS catalog.schema.customers_scd (
        customer_id INT,
        name STRING,
        email STRING,
        phone STRING,
        effective_start_date TIMESTAMP,
        effective_end_date TIMESTAMP,
        is_current BOOLEAN
    ) USING DELTA
""")

# Usage
source_updates = spark.createDataFrame([
    (1, "Alice Johnson", "alice.j@example.com", "555-0001"),
    (2, "Bob Smith", "bob.smith@example.com", "555-0002")
], ["customer_id", "name", "email", "phone"])

scd_type2_merge(
    target_table="catalog.schema.customers_scd",
    source_df=source_updates,
    key_columns=["customer_id"],
    track_columns=["name", "email", "phone"]
)
```

---

## Data Quality Patterns

### Schema Validation

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
from pyspark.sql.functions import col

def validate_schema(df, expected_schema):
    """
    Validate DataFrame against expected schema
    """
    
    # Check all expected columns exist
    expected_cols = set(expected_schema.fieldNames())
    actual_cols = set(df.columns)
    
    missing_cols = expected_cols - actual_cols
    extra_cols = actual_cols - expected_cols
    
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    if extra_cols:
        print(f"Warning: Extra columns found: {extra_cols}")
    
    # Check data types
    for field in expected_schema.fields:
        actual_type = df.schema[field.name].dataType
        expected_type = field.dataType
        
        if actual_type != expected_type:
            raise TypeError(
                f"Column '{field.name}' has type {actual_type}, expected {expected_type}"
            )
    
    print("Schema validation passed")
    return True

# Define expected schema
expected_schema = StructType([
    StructField("customer_id", IntegerType(), False),
    StructField("name", StringType(), False),
    StructField("email", StringType(), True),
    StructField("total_spent", DoubleType(), True)
])

# Validate
df = spark.read.format("csv").option("header", "true").load("input.csv")
validate_schema(df, expected_schema)
```

### Data Quality Checks

```python
from pyspark.sql.functions import col, count, when, isnull, isnan, sum as spark_sum

def data_quality_report(df, rules):
    """
    Generate comprehensive data quality report
    """
    
    results = {
        "total_rows": df.count(),
        "checks": []
    }
    
    # Null checks
    for col_name in rules.get("not_null_columns", []):
        null_count = df.filter(col(col_name).isNull()).count()
        null_pct = (null_count / results["total_rows"]) * 100 if results["total_rows"] > 0 else 0
        
        results["checks"].append({
            "check": f"{col_name}_not_null",
            "passed": null_count == 0,
            "null_count": null_count,
            "null_percentage": null_pct
        })
    
    # Duplicate checks
    if "unique_columns" in rules:
        duplicate_count = df.groupBy(rules["unique_columns"]) \
            .count() \
            .filter(col("count") > 1) \
            .count()
        
        results["checks"].append({
            "check": "unique_key",
            "passed": duplicate_count == 0,
            "duplicate_count": duplicate_count
        })
    
    # Range checks
    for col_name, (min_val, max_val) in rules.get("range_checks", {}).items():
        out_of_range = df.filter(
            (col(col_name) < min_val) | (col(col_name) > max_val)
        ).count()
        
        results["checks"].append({
            "check": f"{col_name}_range",
            "passed": out_of_range == 0,
            "out_of_range_count": out_of_range,
            "expected_range": f"[{min_val}, {max_val}]"
        })
    
    # Pattern checks (regex)
    for col_name, pattern in rules.get("pattern_checks", {}).items():
        invalid_count = df.filter(~col(col_name).rlike(pattern)).count()
        
        results["checks"].append({
            "check": f"{col_name}_pattern",
            "passed": invalid_count == 0,
            "invalid_count": invalid_count,
            "pattern": pattern
        })
    
    # Calculate pass rate
    passed_checks = sum(1 for c in results["checks"] if c["passed"])
    results["pass_rate"] = (passed_checks / len(results["checks"])) * 100 if results["checks"] else 0
    
    return results

# Define quality rules
quality_rules = {
    "not_null_columns": ["customer_id", "order_id", "amount"],
    "unique_columns": ["order_id"],
    "range_checks": {
        "amount": (0, 1000000),
        "quantity": (1, 1000)
    },
    "pattern_checks": {
        "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "phone": r"^\d{3}-\d{4}$"
    }
}

# Run quality checks
df = spark.read.format("delta").table("catalog.schema.orders")
report = data_quality_report(df, quality_rules)

# Print report
print(f"Total Rows: {report['total_rows']}")
print(f"Pass Rate: {report['pass_rate']:.2f}%")
print("\nCheck Results:")
for check in report["checks"]:
    status = "✓ PASS" if check["passed"] else "✗ FAIL"
    print(f"  {status}: {check['check']}")
```

---

## Orchestration Patterns

### Parameterized ETL Job

```python
import sys
from datetime import datetime
from pyspark.sql import SparkSession

# Get parameters
dbutils.widgets.text("source_path", "", "Source Path")
dbutils.widgets.text("target_table", "", "Target Table")
dbutils.widgets.text("processing_date", "", "Processing Date")
dbutils.widgets.dropdown("mode", "append", ["append", "overwrite"], "Write Mode")

source_path = dbutils.widgets.get("source_path")
target_table = dbutils.widgets.get("target_table")
processing_date = dbutils.widgets.get("processing_date")
mode = dbutils.widgets.get("mode")

def run_etl_job(source_path, target_table, processing_date, mode):
    """
    Parameterized ETL job
    """
    
    print(f"Starting ETL job at {datetime.now()}")
    print(f"Source: {source_path}")
    print(f"Target: {target_table}")
    print(f"Processing Date: {processing_date}")
    print(f"Mode: {mode}")
    
    try:
        # Extract
        df = spark.read.format("parquet").load(source_path)
        
        # Transform
        transformed_df = df \
            .filter(col("date") == processing_date) \
            .withColumn("processed_at", current_timestamp())
        
        # Load
        transformed_df.write \
            .format("delta") \
            .mode(mode) \
            .saveAsTable(target_table)
        
        record_count = transformed_df.count()
        print(f"Successfully processed {record_count} records")
        
        return {
            "status": "SUCCESS",
            "records_processed": record_count,
            "processing_date": processing_date
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "status": "FAILED",
            "error": str(e),
            "processing_date": processing_date
        }

# Run job
result = run_etl_job(source_path, target_table, processing_date, mode)

# Return result for job orchestration
dbutils.notebook.exit(str(result))
```

### Multi-Stage Pipeline

```python
from pyspark.sql.functions import col, current_timestamp

def stage1_bronze_load(source_path, bronze_table):
    """Stage 1: Raw data ingestion"""
    print("=== Stage 1: Bronze Layer ===")
    
    raw_df = spark.read.format("json").load(source_path)
    
    bronze_df = raw_df \
        .withColumn("ingestion_timestamp", current_timestamp()) \
        .withColumn("source_file", lit(source_path))
    
    bronze_df.write.format("delta").mode("append").saveAsTable(bronze_table)
    
    print(f"Bronze: Loaded {bronze_df.count()} raw records")
    return bronze_df.count()

def stage2_silver_transform(bronze_table, silver_table):
    """Stage 2: Cleaned and validated data"""
    print("=== Stage 2: Silver Layer ===")
    
    bronze_df = spark.read.format("delta").table(bronze_table)
    
    silver_df = bronze_df \
        .filter(col("amount").isNotNull()) \
        .filter(col("customer_id").isNotNull()) \
        .dropDuplicates(["transaction_id"]) \
        .withColumn("processing_timestamp", current_timestamp())
    
    silver_df.write.format("delta").mode("overwrite").saveAsTable(silver_table)
    
    print(f"Silver: Processed {silver_df.count()} clean records")
    return silver_df.count()

def stage3_gold_aggregate(silver_table, gold_table):
    """Stage 3: Business-level aggregations"""
    print("=== Stage 3: Gold Layer ===")
    
    silver_df = spark.read.format("delta").table(silver_table)
    
    gold_df = silver_df \
        .groupBy("customer_id", "date") \
        .agg(
            count("*").alias("transaction_count"),
            sum("amount").alias("total_amount"),
            avg("amount").alias("avg_amount")
        ) \
        .withColumn("calculation_timestamp", current_timestamp())
    
    gold_df.write.format("delta").mode("overwrite").saveAsTable(gold_table)
    
    print(f"Gold: Generated {gold_df.count()} aggregated records")
    return gold_df.count()

# Execute pipeline
try:
    bronze_count = stage1_bronze_load(
        "s3://source/data/*.json",
        "catalog.bronze.transactions"
    )
    
    silver_count = stage2_silver_transform(
        "catalog.bronze.transactions",
        "catalog.silver.transactions"
    )
    
    gold_count = stage3_gold_aggregate(
        "catalog.silver.transactions",
        "catalog.gold.customer_daily_metrics"
    )
    
    print("\n=== Pipeline Complete ===")
    print(f"Bronze: {bronze_count} records")
    print(f"Silver: {silver_count} records")
    print(f"Gold: {gold_count} records")
    
except Exception as e:
    print(f"Pipeline failed: {str(e)}")
    raise
```

---

## Best Practices

### 1. Idempotent ETL

```python
from pyspark.sql.functions import col, md5, concat_ws

def idempotent_etl(source_path, target_table, partition_col):
    """
    ETL that can safely be re-run without duplicating data
    """
    
    # Read source
    df = spark.read.format("json").load(source_path)
    
    # Add deterministic hash for deduplication
    df_with_hash = df.withColumn(
        "row_hash",
        md5(concat_ws("|", *df.columns))
    )
    
    # Remove duplicates within source
    deduped = df_with_hash.dropDuplicates(["row_hash"])
    
    # Merge into target (prevents duplicates across runs)
    from delta.tables import DeltaTable
    
    target = DeltaTable.forName(spark, target_table)
    
    target.alias("target").merge(
        deduped.alias("source"),
        "target.row_hash = source.row_hash"
    ).whenNotMatchedInsertAll().execute()
    
    print("Idempotent load complete")
```

### 2. Partitioning Strategy

```python
# Date partitioning for time-series data
df.write \
    .format("delta") \
    .partitionBy("year", "month", "day") \
    .saveAsTable("catalog.schema.events")

# Avoid over-partitioning (target 1GB per partition)
df.repartition(10).write.format("delta").saveAsTable("catalog.schema.data")

# Use coalesce for small files
df.coalesce(1).write.format("delta").saveAsTable("catalog.schema.small_data")
```

### 3. Error Handling and Logging

```python
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def etl_with_logging(source, target):
    """ETL with comprehensive logging"""
    
    job_id = f"etl_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        logger.info(f"Job {job_id} started")
        
        # Extract
        logger.info(f"Reading from {source}")
        df = spark.read.format("delta").load(source)
        logger.info(f"Extracted {df.count()} records")
        
        # Transform
        logger.info("Applying transformations")
        transformed = df.filter(col("amount") > 0)
        logger.info(f"After filtering: {transformed.count()} records")
        
        # Load
        logger.info(f"Writing to {target}")
        transformed.write.format("delta").mode("append").saveAsTable(target)
        
        logger.info(f"Job {job_id} completed successfully")
        return {"status": "SUCCESS", "job_id": job_id}
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {str(e)}", exc_info=True)
        return {"status": "FAILED", "job_id": job_id, "error": str(e)}
```

---

## Related Documentation

- [Delta Lake Guide](../sdk/delta-lake.md) - Delta Lake operations
- [SQL Reference](../sql/README.md) - SQL-based ETL
- [Best Practices](../best-practices/performance.md) - Performance optimization

---

## Additional Resources

- [Databricks ETL Best Practices](https://docs.databricks.com/data-engineering/index.html)
- [Delta Lake Performance Tuning](https://docs.databricks.com/delta/optimizations/index.html)
- [Data Quality Framework](https://docs.databricks.com/data-governance/index.html)