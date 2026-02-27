# Delta Lake with Databricks SDK

## Overview

Delta Lake is an open-source storage framework that brings ACID transactions, scalable metadata handling, and time travel to data lakes. This guide covers working with Delta Lake tables using PySpark and the Databricks SDK.

## Table of Contents

1. [Creating Delta Tables](#creating-delta-tables)
2. [Reading Delta Tables](#reading-delta-tables)
3. [Writing to Delta Tables](#writing-to-delta-tables)
4. [ACID Transactions](#acid-transactions)
5. [Time Travel](#time-travel)
6. [Schema Evolution](#schema-evolution)
7. [Optimize and Z-Order](#optimize-and-z-order)
8. [Vacuum](#vacuum)
9. [Change Data Feed](#change-data-feed)
10. [Delta Sharing](#delta-sharing)

---

## Creating Delta Tables

### Create Managed Table

```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType

# Initialize Spark session
spark = SparkSession.builder.appName("DeltaLake").getOrCreate()

# Create schema
schema = StructType([
    StructField("customer_id", IntegerType(), False),
    StructField("name", StringType(), True),
    StructField("email", StringType(), True),
    StructField("created_at", TimestampType(), True)
])

# Create sample data
data = [
    (1, "Alice Smith", "alice@example.com", "2024-01-01 10:00:00"),
    (2, "Bob Jones", "bob@example.com", "2024-01-02 11:00:00"),
    (3, "Carol White", "carol@example.com", "2024-01-03 12:00:00")
]

df = spark.createDataFrame(data, schema)

# Write as Delta table (managed)
df.write.format("delta").mode("overwrite").saveAsTable("catalog.schema.customers")
```

### Create External Table

```python
# Specify external location
external_path = "s3://my-bucket/delta/customers"

df.write.format("delta").mode("overwrite").option("path", external_path).saveAsTable("catalog.schema.customers_external")

# Or save directly to path without catalog
df.write.format("delta").mode("overwrite").save(external_path)
```

### Create Table with Partitioning

```python
from datetime import datetime

# Create partitioned data
data = [
    (1, "Order A", "2026-02-27", 100.0),
    (2, "Order B", "2024-01-16", 200.0),
    (3, "Order C", "2024-02-01", 150.0),
    (4, "Order D", "2024-02-15", 300.0)
]

schema = StructType([
    StructField("order_id", IntegerType(), False),
    StructField("description", StringType(), True),
    StructField("order_date", StringType(), True),
    StructField("amount", DoubleType(), True)
])

df = spark.createDataFrame(data, schema)

# Write with partitioning
df.write.format("delta") \
    .partitionBy("order_date") \
    .mode("overwrite") \
    .saveAsTable("catalog.schema.orders")
```

### Create Table with Table Properties

```python
# Create Delta table with custom properties
df.write.format("delta") \
    .mode("overwrite") \
    .option("delta.dataSkippingNumIndexedCols", "5") \
    .option("delta.logRetentionDuration", "interval 30 days") \
    .option("delta.deletedFileRetentionDuration", "interval 7 days") \
    .saveAsTable("catalog.schema.customers")
```

---

## Reading Delta Tables

### Basic Read

```python
# Read from catalog
df = spark.read.format("delta").table("catalog.schema.customers")
df.show()

# Read from path
df = spark.read.format("delta").load("s3://my-bucket/delta/customers")
df.show()
```

### Read with Filters

```python
# Read with partition filter (efficient)
df = spark.read.format("delta") \
    .table("catalog.schema.orders") \
    .filter("order_date >= '2024-02-01'")

# Read specific columns
df = spark.read.format("delta") \
    .table("catalog.schema.customers") \
    .select("customer_id", "name", "email")

df.show()
```

### Streaming Read

```python
# Read Delta table as streaming source
streaming_df = spark.readStream.format("delta").table("catalog.schema.customers")

# Process and write to another Delta table
query = streaming_df.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", "/tmp/checkpoint") \
    .table("catalog.schema.customers_processed")

query.awaitTermination()
```

---

## Writing to Delta Tables

### Append Mode

```python
# Append new data
new_data = [
    (4, "David Brown", "david@example.com", "2024-01-04 13:00:00"),
    (5, "Eve Wilson", "eve@example.com", "2024-01-05 14:00:00")
]

new_df = spark.createDataFrame(new_data, schema)

new_df.write.format("delta").mode("append").saveAsTable("catalog.schema.customers")
```

### Overwrite Mode

```python
# Overwrite entire table
df.write.format("delta").mode("overwrite").saveAsTable("catalog.schema.customers")

# Overwrite specific partitions
df.write.format("delta") \
    .mode("overwrite") \
    .option("replaceWhere", "order_date = '2024-02-01'") \
    .saveAsTable("catalog.schema.orders")
```

### Merge (Upsert)

```python
from delta.tables import DeltaTable

# Target table
target_table = DeltaTable.forName(spark, "catalog.schema.customers")

# Source data (updates and new records)
updates = [
    (1, "Alice Johnson", "alice.johnson@example.com", "2024-01-01 10:00:00"),  # Update
    (6, "Frank Miller", "frank@example.com", "2024-01-06 15:00:00")  # Insert
]

updates_df = spark.createDataFrame(updates, schema)

# Perform merge (upsert)
target_table.alias("target").merge(
    updates_df.alias("source"),
    "target.customer_id = source.customer_id"
).whenMatchedUpdateAll() \
 .whenNotMatchedInsertAll() \
 .execute()

print("Merge complete")
```

### Advanced Merge with Conditions

```python
from delta.tables import DeltaTable
from pyspark.sql.functions import col, current_timestamp

target_table = DeltaTable.forName(spark, "catalog.schema.customers")

# Merge with conditional logic
target_table.alias("target").merge(
    updates_df.alias("source"),
    "target.customer_id = source.customer_id"
).whenMatchedUpdate(
    condition="source.created_at > target.created_at",
    set={
        "name": col("source.name"),
        "email": col("source.email"),
        "created_at": col("source.created_at")
    }
).whenNotMatchedInsert(
    values={
        "customer_id": col("source.customer_id"),
        "name": col("source.name"),
        "email": col("source.email"),
        "created_at": col("source.created_at")
    }
).execute()
```

### Delete Records

```python
from delta.tables import DeltaTable

# Load Delta table
delta_table = DeltaTable.forName(spark, "catalog.schema.customers")

# Delete records matching condition
delta_table.delete("customer_id = 3")

# Delete with complex condition
delta_table.delete("created_at < '2024-01-02' AND email LIKE '%example.com'")
```

---

## ACID Transactions

### Multiple Operations in Transaction

```python
from delta.tables import DeltaTable
from pyspark.sql.functions import col

# All operations are atomic
target_table = DeltaTable.forName(spark, "catalog.schema.inventory")

# Delete old records
target_table.delete("quantity = 0")

# Update prices
target_table.update(
    condition="product_type = 'electronics'",
    set={"price": col("price") * 1.1}
)

# Each operation is a separate transaction with ACID guarantees
```

### Optimistic Concurrency Control

```python
from delta.tables import DeltaTable
from delta.exceptions import ConcurrentModificationException

try:
    target_table = DeltaTable.forName(spark, "catalog.schema.customers")

    # Perform merge
    target_table.alias("target").merge(
        updates_df.alias("source"),
        "target.customer_id = source.customer_id"
    ).whenMatchedUpdateAll() \
     .whenNotMatchedInsertAll() \
     .execute()

except ConcurrentModificationException:
    print("Concurrent modification detected, retrying...")
    # Implement retry logic
```

---

## Time Travel

### Query Historical Versions

```python
# Read version by number
df_v1 = spark.read.format("delta").option("versionAsOf", 1).table("catalog.schema.customers")

# Read version by timestamp
df_historical = spark.read.format("delta") \
    .option("timestampAsOf", "2026-02-27") \
    .table("catalog.schema.customers")

df_historical.show()
```

### View Table History

```python
from delta.tables import DeltaTable

# Get Delta table
delta_table = DeltaTable.forName(spark, "catalog.schema.customers")

# Show history
history_df = delta_table.history()
history_df.select("version", "timestamp", "operation", "operationMetrics").show(truncate=False)

# Get specific version history
history_df.filter("version >= 5").show()
```

### Restore Table to Previous Version

```python
from delta.tables import DeltaTable

delta_table = DeltaTable.forName(spark, "catalog.schema.customers")

# Restore to specific version
delta_table.restoreToVersion(5)

# Restore to specific timestamp
delta_table.restoreToTimestamp("2026-02-27T10:00:00")

print("Table restored")
```

### Compare Versions

```python
# Read two versions
df_current = spark.read.format("delta").table("catalog.schema.customers")
df_previous = spark.read.format("delta").option("versionAsOf", 5).table("catalog.schema.customers")

# Find differences
added_records = df_current.subtract(df_previous)
removed_records = df_previous.subtract(df_current)

print(f"Added: {added_records.count()}")
print(f"Removed: {removed_records.count()}")

added_records.show()
```

---

## Schema Evolution

### Add Columns

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# New data with additional column
new_schema = StructType([
    StructField("customer_id", IntegerType(), False),
    StructField("name", StringType(), True),
    StructField("email", StringType(), True),
    StructField("phone", StringType(), True),  # New column
    StructField("created_at", TimestampType(), True)
])

new_data = [
    (7, "Grace Lee", "grace@example.com", "555-1234", "2024-01-07 16:00:00")
]

new_df = spark.createDataFrame(new_data, new_schema)

# Write with schema evolution enabled
new_df.write.format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .saveAsTable("catalog.schema.customers")
```

### Modify Column Types

```python
from delta.tables import DeltaTable

# Use SQL for schema changes
spark.sql("""
    ALTER TABLE catalog.schema.customers
    ALTER COLUMN email COMMENT 'Customer email address'
""")

# Change column order (requires rewrite)
spark.sql("""
    ALTER TABLE catalog.schema.customers
    CHANGE COLUMN phone phone STRING AFTER name
""")
```

### Drop Columns

```python
# Drop column using SQL
spark.sql("ALTER TABLE catalog.schema.customers DROP COLUMN phone")

# Or create new table without column
df = spark.read.format("delta").table("catalog.schema.customers")
df_without_phone = df.drop("phone")

df_without_phone.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("catalog.schema.customers")
```

---

## Optimize and Z-Order

### Basic Optimize

```python
from delta.tables import DeltaTable

# Optimize table (compacts small files)
delta_table = DeltaTable.forName(spark, "catalog.schema.customers")
delta_table.optimize().executeCompaction()

print("Optimization complete")
```

### Z-Order Optimization

```python
from delta.tables import DeltaTable

delta_table = DeltaTable.forName(spark, "catalog.schema.orders")

# Z-Order by commonly filtered columns
delta_table.optimize().executeZOrderBy("customer_id", "order_date")

print("Z-Order optimization complete")
```

### Optimize with SQL

```python
# Optimize entire table
spark.sql("OPTIMIZE catalog.schema.customers")

# Optimize specific partition
spark.sql("OPTIMIZE catalog.schema.orders WHERE order_date = '2024-02-01'")

# Z-Order with SQL
spark.sql("OPTIMIZE catalog.schema.orders ZORDER BY (customer_id, product_id)")
```

### Auto-Optimize

```python
# Enable auto-optimize for new writes
spark.sql("""
    ALTER TABLE catalog.schema.customers
    SET TBLPROPERTIES (
        'delta.autoOptimize.optimizeWrite' = 'true',
        'delta.autoOptimize.autoCompact' = 'true'
    )
""")
```

---

## Vacuum

### Remove Old Files

```python
from delta.tables import DeltaTable

delta_table = DeltaTable.forName(spark, "catalog.schema.customers")

# Vacuum files older than retention period (default 7 days)
delta_table.vacuum()

# Vacuum with custom retention (in hours)
delta_table.vacuum(168)  # 7 days

print("Vacuum complete")
```

### Dry Run Vacuum

```python
from delta.tables import DeltaTable

delta_table = DeltaTable.forName(spark, "catalog.schema.customers")

# Preview files to be deleted
files_to_delete = delta_table.vacuum(168, dry_run=True)
files_to_delete.show()
```

### Configure Retention

```python
# Set retention duration
spark.sql("""
    ALTER TABLE catalog.schema.customers
    SET TBLPROPERTIES (
        'delta.logRetentionDuration' = 'interval 30 days',
        'delta.deletedFileRetentionDuration' = 'interval 14 days'
    )
""")
```

---

## Change Data Feed

### Enable Change Data Feed

```python
# Enable CDF on table
spark.sql("""
    ALTER TABLE catalog.schema.customers
    SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")

# Create table with CDF enabled
df.write.format("delta") \
    .mode("overwrite") \
    .option("delta.enableChangeDataFeed", "true") \
    .saveAsTable("catalog.schema.customers_cdf")
```

### Read Change Data

```python
# Read changes between versions
changes_df = spark.read.format("delta") \
    .option("readChangeData", "true") \
    .option("startingVersion", 5) \
    .option("endingVersion", 10) \
    .table("catalog.schema.customers")

changes_df.show()

# Read changes between timestamps
changes_df = spark.read.format("delta") \
    .option("readChangeData", "true") \
    .option("startingTimestamp", "2024-01-01") \
    .option("endingTimestamp", "2026-02-27") \
    .table("catalog.schema.customers")

# Change data columns
# - _change_type: insert, update_preimage, update_postimage, delete
# - _commit_version: version of the change
# - _commit_timestamp: timestamp of the change
```

### Stream Change Data

```python
# Stream changes
changes_stream = spark.readStream.format("delta") \
    .option("readChangeData", "true") \
    .option("startingVersion", 0) \
    .table("catalog.schema.customers")

# Process changes
query = changes_stream.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", "/tmp/cdf_checkpoint") \
    .table("catalog.schema.customer_changes_log")

query.awaitTermination()
```

### Track CDC Patterns

```python
from pyspark.sql.functions import col, when

# Read changes
changes_df = spark.read.format("delta") \
    .option("readChangeData", "true") \
    .option("startingVersion", 0) \
    .table("catalog.schema.customers")

# Separate by operation type
inserts = changes_df.filter(col("_change_type") == "insert")
updates = changes_df.filter(col("_change_type").isin("update_preimage", "update_postimage"))
deletes = changes_df.filter(col("_change_type") == "delete")

print(f"Inserts: {inserts.count()}")
print(f"Updates: {updates.count() / 2}")  # Divide by 2 (pre and post)
print(f"Deletes: {deletes.count()}")
```

---

## Delta Sharing

### Share Delta Table

```python
# Create share
spark.sql("CREATE SHARE IF NOT EXISTS customer_share")

# Add table to share
spark.sql("""
    ALTER SHARE customer_share
    ADD TABLE catalog.schema.customers
""")

# Grant access to recipient
spark.sql("""
    GRANT SELECT ON SHARE customer_share
    TO RECIPIENT external_partner
""")
```

### Read Shared Table

```python
import delta_sharing

# Load shared table profile
profile_file = "/path/to/profile.share"
client = delta_sharing.SharingClient(profile_file)

# List available tables
tables = client.list_all_tables()
for table in tables:
    print(f"{table.share}.{table.schema}.{table.name}")

# Load shared table as pandas DataFrame
pandas_df = delta_sharing.load_as_pandas(
    f"{profile_file}#share.schema.table"
)

# Load as Spark DataFrame
spark_df = delta_sharing.load_as_spark(
    f"{profile_file}#share.schema.table"
)

spark_df.show()
```

---

## Advanced Patterns

### Slowly Changing Dimension Type 2

```python
from pyspark.sql.functions import col, lit, current_timestamp, when
from delta.tables import DeltaTable

def scd_type2_merge(target_table_name, source_df, key_columns, track_columns):
    """
    Implement SCD Type 2 merge pattern

    Args:
        target_table_name: Name of target Delta table
        source_df: Source DataFrame with updates
        key_columns: Business key columns
        track_columns: Columns to track changes
    """

    target = DeltaTable.forName(spark, target_table_name)

    # Add SCD columns to source
    source_with_scd = source_df \
        .withColumn("effective_date", current_timestamp()) \
        .withColumn("end_date", lit(None).cast("timestamp")) \
        .withColumn("is_current", lit(True))

    # Build merge condition
    merge_condition = " AND ".join([f"target.{col} = source.{col}" for col in key_columns])
    merge_condition += " AND target.is_current = true"

    # Build update condition (check if tracked columns changed)
    update_condition = " OR ".join([
        f"target.{col} != source.{col}" for col in track_columns
    ])

    # Perform SCD Type 2 merge
    target.alias("target").merge(
        source_with_scd.alias("source"),
        merge_condition
    ).whenMatchedUpdate(
        condition=update_condition,
        set={
            "end_date": current_timestamp(),
            "is_current": lit(False)
        }
    ).execute()

    # Insert new versions of changed records
    changed_records = target.toDF().alias("target").join(
        source_with_scd.alias("source"),
        on=key_columns,
        how="inner"
    ).where(
        (col("target.is_current") == False) &
        (col("target.end_date") == current_timestamp())
    ).select("source.*")

    changed_records.write.format("delta").mode("append").saveAsTable(target_table_name)

    # Insert completely new records
    target.alias("target").merge(
        source_with_scd.alias("source"),
        " AND ".join([f"target.{col} = source.{col}" for col in key_columns])
    ).whenNotMatchedInsertAll().execute()

# Usage
source_updates = spark.createDataFrame([
    (1, "Alice Johnson", "alice.j@example.com"),
    (4, "David Brown", "david@example.com")
], ["customer_id", "name", "email"])

scd_type2_merge(
    target_table_name="catalog.schema.customers_scd",
    source_df=source_updates,
    key_columns=["customer_id"],
    track_columns=["name", "email"]
)
```

### Incremental ETL Pattern

```python
from pyspark.sql.functions import col, max as spark_max
from delta.tables import DeltaTable

def incremental_load(source_table, target_table, watermark_column):
    """
    Load only new/updated data based on watermark

    Args:
        source_table: Source table name
        target_table: Target Delta table name
        watermark_column: Column to track (e.g., updated_at)
    """

    # Get last watermark from target
    target_df = spark.read.format("delta").table(target_table)
    last_watermark = target_df.agg(spark_max(watermark_column)).collect()[0][0]

    if last_watermark is None:
        # First load
        source_df = spark.read.table(source_table)
    else:
        # Incremental load
        source_df = spark.read.table(source_table) \
            .filter(col(watermark_column) > last_watermark)

    # Merge into target
    if source_df.count() > 0:
        target_delta = DeltaTable.forName(spark, target_table)

        target_delta.alias("target").merge(
            source_df.alias("source"),
            "target.id = source.id"
        ).whenMatchedUpdateAll() \
         .whenNotMatchedInsertAll() \
         .execute()

        print(f"Loaded {source_df.count()} records")
    else:
        print("No new records to load")

# Usage
incremental_load(
    source_table="source_db.transactions",
    target_table="catalog.schema.transactions",
    watermark_column="updated_at"
)
```

### Data Quality Checks

```python
from pyspark.sql.functions import col, count, when, isnull
from delta.tables import DeltaTable

def validate_delta_table(table_name, rules):
    """
    Validate Delta table against quality rules

    Args:
        table_name: Delta table name
        rules: Dict of validation rules

    Returns:
        Dict of validation results
    """

    df = spark.read.format("delta").table(table_name)
    results = {}

    # Check row count
    total_rows = df.count()
    results["total_rows"] = total_rows

    # Check for duplicates on key columns
    if "key_columns" in rules:
        duplicate_count = df.groupBy(rules["key_columns"]) \
            .count() \
            .filter(col("count") > 1) \
            .count()
        results["duplicates"] = duplicate_count

    # Check for nulls in required columns
    if "required_columns" in rules:
        for col_name in rules["required_columns"]:
            null_count = df.filter(isnull(col(col_name))).count()
            results[f"{col_name}_nulls"] = null_count

    # Check value ranges
    if "range_checks" in rules:
        for col_name, (min_val, max_val) in rules["range_checks"].items():
            out_of_range = df.filter(
                (col(col_name) < min_val) | (col(col_name) > max_val)
            ).count()
            results[f"{col_name}_out_of_range"] = out_of_range

    # Check data freshness
    if "freshness_column" in rules:
        from pyspark.sql.functions import max as spark_max, datediff, current_date

        latest_date = df.agg(spark_max(rules["freshness_column"])).collect()[0][0]
        if latest_date:
            days_old = df.select(
                datediff(current_date(), col(rules["freshness_column"]))
            ).agg({"datediff(current_date(), updated_at)": "max"}).collect()[0][0]
            results["days_since_update"] = days_old

    return results

# Usage
validation_rules = {
    "key_columns": ["customer_id"],
    "required_columns": ["name", "email"],
    "range_checks": {
        "customer_id": (1, 1000000)
    },
    "freshness_column": "created_at"
}

results = validate_delta_table("catalog.schema.customers", validation_rules)
print("Validation Results:")
for key, value in results.items():
    print(f"  {key}: {value}")
```

---

## Performance Tips

### 1. Partition Pruning

```python
# Efficient: Uses partition pruning
df = spark.read.format("delta") \
    .table("catalog.schema.orders") \
    .filter("order_date = '2024-02-01'")

# Inefficient: Scans all partitions
df = spark.read.format("delta") \
    .table("catalog.schema.orders") \
    .filter("amount > 1000")
```

### 2. Data Skipping

```python
# Z-Order on commonly filtered columns
from delta.tables import DeltaTable

delta_table = DeltaTable.forName(spark, "catalog.schema.transactions")
delta_table.optimize().executeZOrderBy("customer_id", "transaction_date")

# Queries on these columns will skip irrelevant files
```

### 3. File Sizing

```python
# Configure optimal file size (128MB - 1GB)
spark.conf.set("spark.databricks.delta.targetFileSize", "134217728")  # 128MB

# Enable auto-compaction
spark.sql("""
    ALTER TABLE catalog.schema.large_table
    SET TBLPROPERTIES ('delta.autoOptimize.autoCompact' = 'true')
""")
```

---

## Related Documentation

- [SQL Reference](../sql/README.md) - SQL commands for Delta tables
- [Python SDK Guide](./python-sdk.md) - General SDK usage
- [Streaming Guide](../examples/streaming.md) - Streaming with Delta

---

## Additional Resources

- [Delta Lake Documentation](https://docs.delta.io/)
- [Databricks Delta Lake Guide](https://docs.databricks.com/delta/index.html)
- [Delta Lake Best Practices](https://docs.databricks.com/delta/best-practices.html)
