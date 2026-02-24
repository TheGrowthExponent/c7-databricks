# Databricks Structured Streaming Workflows

## Overview

This guide provides comprehensive examples for building production-ready streaming workflows in Databricks using Structured Streaming. Learn how to process real-time data from various sources, apply transformations, and write to multiple sinks with exactly-once guarantees.

## Table of Contents

- [Streaming Fundamentals](#streaming-fundamentals)
- [Basic Streaming Patterns](#basic-streaming-patterns)
- [Source Configurations](#source-configurations)
- [Transformation Patterns](#transformation-patterns)
- [Sink Configurations](#sink-configurations)
- [Watermarking & Late Data](#watermarking--late-data)
- [Stateful Operations](#stateful-operations)
- [Streaming Joins](#streaming-joins)
- [Production Patterns](#production-patterns)
- [Monitoring & Troubleshooting](#monitoring--troubleshooting)

---

## Streaming Fundamentals

### Basic Streaming Concepts

Structured Streaming treats real-time data as an unbounded table that continuously grows with new data arriving.

```python
# Basic streaming read
streaming_df = (spark
    .readStream
    .format("delta")
    .table("source_table")
)

# Basic streaming write
(streaming_df
    .writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/mnt/checkpoints/my_stream")
    .table("target_table")
    .awaitTermination()
)
```

### Output Modes

```python
# Append mode - only new rows (default)
.outputMode("append")

# Complete mode - entire result table
.outputMode("complete")

# Update mode - only updated rows
.outputMode("update")
```

---

## Basic Streaming Patterns

### 1. Simple Stream Processing

```python
from pyspark.sql.functions import *

# Read from Delta table
source_stream = (spark
    .readStream
    .format("delta")
    .table("bronze.raw_events")
)

# Apply transformations
processed_stream = (source_stream
    .filter(col("event_type") == "purchase")
    .select(
        col("event_id"),
        col("user_id"),
        col("product_id"),
        col("amount").cast("decimal(10,2)"),
        col("timestamp")
    )
    .withColumn("processing_time", current_timestamp())
)

# Write to silver layer
query = (processed_stream
    .writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/mnt/checkpoints/purchases")
    .option("mergeSchema", "true")
    .table("silver.purchases")
)

query.awaitTermination()
```

### 2. Streaming Aggregation

```python
# Aggregate streaming data
aggregated_stream = (source_stream
    .groupBy(
        window(col("timestamp"), "5 minutes", "1 minute"),
        col("product_category")
    )
    .agg(
        count("*").alias("event_count"),
        sum("amount").alias("total_revenue"),
        avg("amount").alias("avg_order_value"),
        countDistinct("user_id").alias("unique_users")
    )
    .select(
        col("window.start").alias("window_start"),
        col("window.end").alias("window_end"),
        col("product_category"),
        col("event_count"),
        col("total_revenue"),
        col("avg_order_value"),
        col("unique_users")
    )
)

# Write aggregated results
query = (aggregated_stream
    .writeStream
    .format("delta")
    .outputMode("complete")
    .option("checkpointLocation", "/mnt/checkpoints/aggregations")
    .table("gold.product_metrics")
)
```

---

## Source Configurations

### Delta Lake Source

```python
# Read from Delta table with options
delta_stream = (spark
    .readStream
    .format("delta")
    .option("ignoreDeletes", "true")
    .option("ignoreChanges", "true")
    .option("startingVersion", "0")
    .option("maxFilesPerTrigger", "1000")
    .option("maxBytesPerTrigger", "1g")
    .table("my_table")
)

# Read from Delta path
delta_stream = (spark
    .readStream
    .format("delta")
    .load("/mnt/data/delta/events")
)
```

### Kafka Source

```python
# Read from Kafka
kafka_stream = (spark
    .readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "broker1:9092,broker2:9092")
    .option("subscribe", "events-topic")
    .option("startingOffsets", "latest")
    .option("maxOffsetsPerTrigger", "10000")
    .option("kafka.security.protocol", "SASL_SSL")
    .option("kafka.sasl.mechanism", "PLAIN")
    .load()
)

# Parse Kafka messages
parsed_stream = (kafka_stream
    .select(
        col("key").cast("string"),
        from_json(col("value").cast("string"), schema).alias("data"),
        col("topic"),
        col("partition"),
        col("offset"),
        col("timestamp")
    )
    .select("data.*", "topic", "partition", "offset", "timestamp")
)
```

### Event Hubs Source (Azure)

```python
# Connection string
connection_string = "Endpoint=sb://..."

# Read from Event Hubs
eventhubs_stream = (spark
    .readStream
    .format("eventhubs")
    .option("eventhubs.connectionString", connection_string)
    .option("eventhubs.consumerGroup", "$Default")
    .option("maxEventsPerTrigger", "5000")
    .load()
)

# Parse Event Hubs data
parsed_stream = (eventhubs_stream
    .withColumn("body", col("body").cast("string"))
    .withColumn("data", from_json(col("body"), schema))
    .select("data.*", "enqueuedTime", "offset", "sequenceNumber")
)
```

### Auto Loader (Cloud Files)

```python
# Auto Loader for cloud storage
autoloader_stream = (spark
    .readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.schemaLocation", "/mnt/schemas/events")
    .option("cloudFiles.inferColumnTypes", "true")
    .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
    .option("cloudFiles.maxFilesPerTrigger", "100")
    .load("s3://bucket/path/to/files/")
)

# CSV with Auto Loader
csv_stream = (spark
    .readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "csv")
    .option("cloudFiles.schemaLocation", "/mnt/schemas/csv")
    .option("header", "true")
    .option("inferSchema", "true")
    .load("abfss://container@storage.dfs.core.windows.net/data/")
)
```

---

## Transformation Patterns

### 1. Data Cleansing

```python
from pyspark.sql.functions import *

cleansed_stream = (raw_stream
    # Remove nulls
    .filter(col("user_id").isNotNull())
    .filter(col("timestamp").isNotNull())

    # Remove duplicates within 10-minute window
    .withWatermark("timestamp", "10 minutes")
    .dropDuplicates(["event_id", "timestamp"])

    # Standardize formats
    .withColumn("email", lower(trim(col("email"))))
    .withColumn("phone", regexp_replace(col("phone"), "[^0-9]", ""))

    # Data validation
    .withColumn("is_valid",
        (col("amount") > 0) &
        (col("email").rlike("^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$"))
    )
    .filter(col("is_valid"))
    .drop("is_valid")
)
```

### 2. Enrichment with Static Data

```python
# Load dimension table
customers_dim = spark.table("dim.customers")

# Enrich streaming data
enriched_stream = (streaming_events
    .join(customers_dim, "customer_id", "left")
    .select(
        col("event_id"),
        col("customer_id"),
        col("customer_name"),
        col("customer_segment"),
        col("event_type"),
        col("amount"),
        col("timestamp")
    )
)
```

### 3. Complex Transformations

```python
# Multi-step transformation pipeline
transformed_stream = (source_stream
    # Parse JSON
    .withColumn("payload", from_json(col("data"), schema))
    .select("payload.*", "timestamp")

    # Extract nested fields
    .withColumn("user_country", col("user.location.country"))
    .withColumn("user_city", col("user.location.city"))

    # Create derived fields
    .withColumn("hour_of_day", hour(col("timestamp")))
    .withColumn("day_of_week", dayofweek(col("timestamp")))
    .withColumn("is_weekend",
        when(dayofweek(col("timestamp")).isin([1, 7]), True).otherwise(False)
    )

    # Categorize
    .withColumn("amount_category",
        when(col("amount") < 10, "small")
        .when(col("amount") < 100, "medium")
        .when(col("amount") < 1000, "large")
        .otherwise("extra_large")
    )

    # Calculate running metrics
    .withColumn("event_date", to_date(col("timestamp")))
)
```

---

## Sink Configurations

### Delta Lake Sink

```python
# Append to Delta table
query = (streaming_df
    .writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/mnt/checkpoints/my_stream")
    .option("mergeSchema", "true")
    .option("optimizeWrite", "true")
    .option("autoCompact", "true")
    .table("target_table")
)
```

### Streaming Merge (Upsert)

```python
from delta.tables import DeltaTable

def merge_to_delta(microBatchDF, batchId):
    """Perform upsert operation for each micro-batch"""

    # Get target Delta table
    target_table = DeltaTable.forName(spark, "silver.customers")

    # Perform merge
    (target_table.alias("target")
        .merge(
            microBatchDF.alias("source"),
            "target.customer_id = source.customer_id"
        )
        .whenMatchedUpdate(set={
            "customer_name": "source.customer_name",
            "email": "source.email",
            "updated_at": "source.timestamp"
        })
        .whenNotMatchedInsert(values={
            "customer_id": "source.customer_id",
            "customer_name": "source.customer_name",
            "email": "source.email",
            "created_at": "source.timestamp",
            "updated_at": "source.timestamp"
        })
        .execute()
    )

# Apply merge using foreachBatch
query = (streaming_df
    .writeStream
    .foreachBatch(merge_to_delta)
    .option("checkpointLocation", "/mnt/checkpoints/upsert")
    .start()
)
```

### Kafka Sink

```python
# Write to Kafka
kafka_query = (streaming_df
    .selectExpr(
        "customer_id as key",
        "to_json(struct(*)) as value"
    )
    .writeStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "broker1:9092,broker2:9092")
    .option("topic", "processed-events")
    .option("checkpointLocation", "/mnt/checkpoints/kafka_sink")
    .start()
)
```

### Multiple Sinks

```python
# Write to multiple destinations
def write_to_multiple_sinks(microBatchDF, batchId):
    """Write each micro-batch to multiple sinks"""

    # Write to Delta (silver layer)
    (microBatchDF
        .write
        .format("delta")
        .mode("append")
        .saveAsTable("silver.events")
    )

    # Write aggregated data to gold layer
    (microBatchDF
        .groupBy("event_type", "user_segment")
        .agg(
            count("*").alias("event_count"),
            sum("amount").alias("total_amount")
        )
        .write
        .format("delta")
        .mode("append")
        .saveAsTable("gold.event_summary")
    )

    # Write to external system (optional)
    # microBatchDF.write.format("jdbc").save(...)

query = (streaming_df
    .writeStream
    .foreachBatch(write_to_multiple_sinks)
    .option("checkpointLocation", "/mnt/checkpoints/multi_sink")
    .start()
)
```

---

## Watermarking & Late Data

### Event Time Watermarking

```python
from pyspark.sql.functions import *

# Windowed aggregation with watermark
windowed_stream = (streaming_df
    # Define watermark - allow 10 minutes of late data
    .withWatermark("event_time", "10 minutes")

    # Window aggregation
    .groupBy(
        window(col("event_time"), "5 minutes"),
        col("product_id")
    )
    .agg(
        count("*").alias("order_count"),
        sum("amount").alias("total_revenue"),
        avg("amount").alias("avg_order_value")
    )
)

# Write windowed results
query = (windowed_stream
    .writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/mnt/checkpoints/windowed")
    .table("windowed_metrics")
)
```

### Handling Late Events

```python
# Track late events separately
late_events_stream = (streaming_df
    .withWatermark("event_time", "10 minutes")
    .withColumn("processing_time", current_timestamp())
    .withColumn("lateness_seconds",
        unix_timestamp(col("processing_time")) -
        unix_timestamp(col("event_time"))
    )
    .withColumn("is_late", col("lateness_seconds") > 600)  # 10 minutes
)

# Write on-time and late events separately
def process_with_lateness(microBatchDF, batchId):
    # On-time events
    on_time = microBatchDF.filter(~col("is_late"))
    on_time.write.format("delta").mode("append").saveAsTable("events.on_time")

    # Late events
    late = microBatchDF.filter(col("is_late"))
    late.write.format("delta").mode("append").saveAsTable("events.late")

query = (late_events_stream
    .writeStream
    .foreachBatch(process_with_lateness)
    .option("checkpointLocation", "/mnt/checkpoints/lateness")
    .start()
)
```

---

## Stateful Operations

### Session Windows

```python
from pyspark.sql.functions import *

# Track user sessions with gaps
sessions_stream = (events_stream
    .withWatermark("event_time", "30 minutes")
    .groupBy(
        col("user_id"),
        session_window(col("event_time"), "10 minutes")
    )
    .agg(
        count("*").alias("events_in_session"),
        min("event_time").alias("session_start"),
        max("event_time").alias("session_end"),
        sum("amount").alias("session_revenue"),
        collect_list("page_url").alias("pages_visited")
    )
    .select(
        col("user_id"),
        col("session_window.start").alias("session_start"),
        col("session_window.end").alias("session_end"),
        col("events_in_session"),
        col("session_revenue"),
        col("pages_visited")
    )
)
```

### Streaming Deduplication

```python
# Deduplicate within watermark
deduplicated_stream = (events_stream
    .withWatermark("event_time", "1 hour")
    .dropDuplicates(["event_id", "event_time"])
)

# Deduplicate with state timeout
deduplicated_with_state = (events_stream
    .withWatermark("event_time", "2 hours")
    .dropDuplicates(["user_id", "transaction_id", "event_time"])
)
```

### Arbitrary Stateful Processing

```python
from pyspark.sql.types import *

# Define state schema
state_schema = StructType([
    StructField("user_id", StringType()),
    StructField("event_count", IntegerType()),
    StructField("last_event_time", TimestampType())
])

def update_state(key, values, state):
    """Custom stateful logic"""
    if state.exists:
        old_count = state.get[1]
        state.update((key[0], old_count + len(list(values)), current_timestamp()))
    else:
        state.update((key[0], len(list(values)), current_timestamp()))

    return state.get

# Apply stateful transformation
stateful_stream = (events_stream
    .groupByKey(lambda x: x.user_id)
    .mapGroupsWithState(update_state, state_schema, "Update")
)
```

---

## Streaming Joins

### Stream-Static Join

```python
# Load static dimension
customer_dim = spark.table("dim.customers")

# Join streaming data with static dimension
enriched_stream = (streaming_orders
    .join(customer_dim, "customer_id", "left")
    .select(
        col("order_id"),
        col("customer_id"),
        col("customer_name"),
        col("customer_tier"),
        col("order_amount"),
        col("order_time")
    )
)
```

### Stream-Stream Join

```python
# First stream: orders
orders_stream = (spark
    .readStream
    .format("delta")
    .table("orders")
    .withWatermark("order_time", "10 minutes")
)

# Second stream: payments
payments_stream = (spark
    .readStream
    .format("delta")
    .table("payments")
    .withWatermark("payment_time", "10 minutes")
)

# Join two streams
joined_stream = (orders_stream
    .join(
        payments_stream,
        expr("""
            order_id = payment_order_id AND
            payment_time >= order_time AND
            payment_time <= order_time + interval 15 minutes
        """),
        "leftOuter"
    )
    .select(
        col("order_id"),
        col("order_amount"),
        col("order_time"),
        col("payment_id"),
        col("payment_amount"),
        col("payment_time"),
        when(col("payment_id").isNotNull(), "paid")
            .otherwise("pending").alias("payment_status")
    )
)
```

### Inner Stream-Stream Join

```python
# Inner join with time constraint
inner_joined = (impressions_stream
    .withWatermark("impression_time", "5 minutes")
    .join(
        clicks_stream.withWatermark("click_time", "5 minutes"),
        expr("""
            ad_id = clicked_ad_id AND
            user_id = clicked_user_id AND
            click_time >= impression_time AND
            click_time <= impression_time + interval 10 minutes
        """),
        "inner"
    )
    .select(
        col("ad_id"),
        col("user_id"),
        col("impression_time"),
        col("click_time"),
        (unix_timestamp("click_time") - unix_timestamp("impression_time"))
            .alias("time_to_click_seconds")
    )
)
```

---

## Production Patterns

### 1. Complete ETL Pipeline

```python
from pyspark.sql.functions import *
from delta.tables import DeltaTable

# Configuration
checkpoint_base = "/mnt/checkpoints"
bronze_table = "bronze.raw_events"
silver_table = "silver.clean_events"
gold_table = "gold.event_metrics"

# Bronze Layer: Ingest raw data
bronze_query = (spark
    .readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.schemaLocation", f"{checkpoint_base}/bronze/schema")
    .option("cloudFiles.inferColumnTypes", "true")
    .load("s3://raw-data/events/")
    .withColumn("ingestion_time", current_timestamp())
    .withColumn("source_file", input_file_name())
    .writeStream
    .format("delta")
    .option("checkpointLocation", f"{checkpoint_base}/bronze")
    .option("mergeSchema", "true")
    .table(bronze_table)
)

# Silver Layer: Clean and enrich
silver_stream = (spark
    .readStream
    .format("delta")
    .table(bronze_table)
    .filter(col("event_type").isNotNull())
    .withColumn("event_date", to_date(col("event_time")))
    .withColumn("event_hour", hour(col("event_time")))
    .dropDuplicates(["event_id"])
    .join(broadcast(spark.table("dim.customers")), "customer_id", "left")
)

def upsert_silver(microBatchDF, batchId):
    target = DeltaTable.forName(spark, silver_table)
    (target.alias("t")
        .merge(microBatchDF.alias("s"), "t.event_id = s.event_id")
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )

silver_query = (silver_stream
    .writeStream
    .foreachBatch(upsert_silver)
    .option("checkpointLocation", f"{checkpoint_base}/silver")
    .start()
)

# Gold Layer: Aggregated metrics
gold_stream = (spark
    .readStream
    .format("delta")
    .table(silver_table)
    .withWatermark("event_time", "10 minutes")
    .groupBy(
        window(col("event_time"), "5 minutes"),
        col("event_type"),
        col("customer_segment")
    )
    .agg(
        count("*").alias("event_count"),
        countDistinct("customer_id").alias("unique_customers"),
        sum("event_value").alias("total_value"),
        avg("event_value").alias("avg_value")
    )
)

gold_query = (gold_stream
    .writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", f"{checkpoint_base}/gold")
    .table(gold_table)
)
```

### 2. Error Handling Pattern

```python
from pyspark.sql.functions import *

def process_with_error_handling(microBatchDF, batchId):
    """Process micro-batch with comprehensive error handling"""

    try:
        # Separate valid and invalid records
        valid_df = microBatchDF.filter(
            col("event_id").isNotNull() &
            col("event_time").isNotNull() &
            col("event_type").isin(["view", "click", "purchase"])
        )

        invalid_df = microBatchDF.subtract(valid_df)

        # Write valid records
        if valid_df.count() > 0:
            (valid_df
                .write
                .format("delta")
                .mode("append")
                .saveAsTable("silver.valid_events")
            )

        # Write invalid records to quarantine
        if invalid_df.count() > 0:
            (invalid_df
                .withColumn("batch_id", lit(batchId))
                .withColumn("quarantine_time", current_timestamp())
                .write
                .format("delta")
                .mode("append")
                .saveAsTable("quarantine.invalid_events")
            )

        # Log metrics
        print(f"Batch {batchId}: Valid={valid_df.count()}, Invalid={invalid_df.count()}")

    except Exception as e:
        print(f"Error processing batch {batchId}: {str(e)}")
        # Write entire batch to dead letter queue
        (microBatchDF
            .withColumn("batch_id", lit(batchId))
            .withColumn("error", lit(str(e)))
            .withColumn("error_time", current_timestamp())
            .write
            .format("delta")
            .mode("append")
            .saveAsTable("dlq.failed_batches")
        )
        raise

# Apply error handling
query = (streaming_df
    .writeStream
    .foreachBatch(process_with_error_handling)
    .option("checkpointLocation", "/mnt/checkpoints/with_errors")
    .start()
)
```

### 3. Exactly-Once Semantics

```python
from delta.tables import DeltaTable

def idempotent_write(microBatchDF, batchId):
    """Ensure exactly-once processing with idempotent writes"""

    # Check if batch already processed
    processed_batches = spark.table("audit.processed_batches")

    if processed_batches.filter(col("batch_id") == batchId).count() > 0:
        print(f"Batch {batchId} already processed, skipping")
        return

    # Process batch
    target = DeltaTable.forName(spark, "silver.transactions")

    (target.alias("t")
        .merge(
            microBatchDF.alias("s"),
            "t.transaction_id = s.transaction_id"
        )
        .whenMatchedUpdate(set={
            "amount": "s.amount",
            "updated_at": "s.timestamp"
        })
        .whenNotMatchedInsert(values={
            "transaction_id": "s.transaction_id",
            "amount": "s.amount",
            "created_at": "s.timestamp",
            "updated_at": "s.timestamp"
        })
        .execute()
    )

    # Record batch as processed
    (spark.createDataFrame([(batchId, current_timestamp())],
                          ["batch_id", "processed_at"])
        .write
        .format("delta")
        .mode("append")
        .saveAsTable("audit.processed_batches")
    )

query = (streaming_df
    .writeStream
    .foreachBatch(idempotent_write)
    .option("checkpointLocation", "/mnt/checkpoints/exactly_once")
    .start()
)
```

---

## Monitoring & Troubleshooting

### Query Monitoring

```python
# Get active streams
active_streams = spark.streams.active

for stream in active_streams:
    print(f"Stream ID: {stream.id}")
    print(f"Name: {stream.name}")
    print(f"Status: {stream.status}")
    print(f"Recent Progress: {stream.recentProgress}")
    print("---")

# Monitor specific query
query = streaming_df.writeStream.start()

# Get last progress
last_progress = query.lastProgress
print(f"Batch ID: {last_progress['batchId']}")
print(f"Input Rows: {last_progress['numInputRows']}")
print(f"Processing Time: {last_progress['durationMs']}")
```

### Stream Status Tracking

```python
# Monitor query status
def monitor_stream(query, check_interval=30):
    """Monitor streaming query health"""
    import time

    while query.isActive:
        status = query.status
        progress = query.lastProgress

        if progress:
            print(f"""
            Batch: {progress.get('batchId')}
            Input Rows: {progress.get('numInputRows')}
            Processed Rows: {progress.get('processedRowsPerSecond')}
            Duration: {progress.get('durationMs', {}).get('triggerExecution')}ms
            """)

        time.sleep(check_interval)

    # Check why query stopped
    if query.exception():
        print(f"Stream failed with error: {query.exception()}")

# Start monitoring
monitor_stream(query)
```

### Custom Metrics

```python
def write_with_metrics(microBatchDF, batchId):
    """Write data and collect custom metrics"""
    from datetime import datetime

    # Calculate metrics
    row_count = microBatchDF.count()
    start_time = datetime.now()

    # Write data
    (microBatchDF
        .write
        .format("delta")
        .mode("append")
        .saveAsTable("target_table")
    )

    # Calculate duration
    duration = (datetime.now() - start_time).total_seconds()

    # Write metrics
    metrics_df = spark.createDataFrame([
        (batchId, row_count, duration, datetime.now())
    ], ["batch_id", "row_count", "duration_seconds", "timestamp"])

    (metrics_df
        .write
        .format("delta")
        .mode("append")
        .saveAsTable("monitoring.stream_metrics")
    )

query = (streaming_df
    .writeStream
    .foreachBatch(write_with_metrics)
    .option("checkpointLocation", "/mnt/checkpoints/with_metrics")
    .start()
)
```

### Trigger Configurations

```python
# Process available data immediately (default)
.trigger(processingTime="0 seconds")

# Micro-batch every 10 seconds
.trigger(processingTime="10 seconds")

# Continuous processing (experimental)
.trigger(continuous="1 second")

# Process once and stop
.trigger(once=True)

# Available now (process all available data)
.trigger(availableNow=True)
```

### Stream Recovery

```python
# Restart from checkpoint
recovered_query = (spark
    .readStream
    .format("delta")
    .table("source_table")
    .writeStream
    .format("delta")
    .option("checkpointLocation", "/mnt/checkpoints/my_stream")  # Same checkpoint
    .table("target_table")
    .start()
)

# Clear checkpoint to restart from beginning
dbutils.fs.rm("/mnt/checkpoints/my_stream", True)

# Start fresh stream
fresh_query = (spark
    .readStream
    .format("delta")
    .option("startingVersion", "0")  # Process from beginning
    .table("source_table")
    .writeStream
    .format("delta")
    .option("checkpointLocation", "/mnt/checkpoints/my_stream_new")
    .table("target_table")
    .start()
)
```

---

## Performance Best Practices

### 1. Optimize Trigger Intervals

```python
# Balance latency and efficiency
.trigger(processingTime="30 seconds")  # Good for most use cases
.option("maxFilesPerTrigger", "1000")
.option("maxBytesPerTrigger", "1g")
```

### 2. Partition Strategy

```python
# Partition output for better performance
(streaming_df
    .writeStream
    .format("delta")
    .partitionBy("event_date", "event_type")
    .option("checkpointLocation", "/mnt/checkpoints/partitioned")
    .table("partitioned_events")
)
```

### 3. Auto Optimization

```python
# Enable auto-optimization for Delta
(streaming_df
    .writeStream
    .format("delta")
    .option("optimizeWrite", "true")
    .option("autoCompact", "true")
    .option("checkpointLocation", "/mnt/checkpoints/optimized")
    .table("optimized_table")
)
```

### 4. Resource Configuration

```python
# Configure cluster for streaming
spark.conf.set("spark.sql.streaming.schemaInference", "true")
spark.conf.set("spark.sql.streaming.stateStore.providerClass",
               "com.databricks.sql.streaming.state.RocksDBStateStoreProvider")
spark.conf.set("spark.sql.streaming.statefulOperator.checkCorrectness.enabled", "true")
```

---

## Complete Production Example

```python
from pyspark.sql.functions import *
from pyspark.sql.types import *
from delta.tables import DeltaTable

# Define schema
event_schema = StructType([
    StructField("event_id", StringType(), False),
    StructField("user_id", StringType(), False),
    StructField("event_type", StringType(), False),
    StructField("product_id", StringType(), True),
    StructField("amount", DecimalType(10, 2), True),
    StructField("event_time", TimestampType(), False),
    StructField("metadata", StringType(), True)
])

# Read from Auto Loader
raw_stream = (spark
    .readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.schemaLocation", "/mnt/schemas/events")
    .schema(event_schema)
    .load("s3://raw-events/")
)

# Transform and enrich
processed_stream = (raw_stream
    # Add ingestion metadata
    .withColumn("ingestion_time", current_timestamp())
    .withColumn("source_file", input_file_name())

    # Data quality
    .filter(col("event_id").isNotNull())
    .filter(col("event_time") <= current_timestamp())

    # Deduplication
    .withWatermark("event_time", "1 hour")
    .dropDuplicates(["event_id", "event_time"])

    # Enrichment
    .join(broadcast(spark.table("dim.products")), "product_id", "left")

    # Derived fields
    .withColumn("event_date", to_date(col("event_time")))
    .withColumn("event_hour", hour(col("event_time")))
    .withColumn("is_purchase", col("event_type") == "purchase")
)

# Write to Delta with monitoring
def write_processed_data(microBatchDF, batchId):
    """Write with validation and monitoring"""

    # Validate data
    total_rows = microBatchDF.count()

    if total_rows == 0:
        print(f"Batch {batchId}: No data to process")
        return

    # Write to silver layer
    (microBatchDF
        .write
        .format("delta")
        .mode("append")
        .partitionBy("event_date")
        .option("optimizeWrite", "true")
        .saveAsTable("silver.events")
    )

    # Log metrics
    print(f"Batch {batchId}: Processed {total_rows} rows")

# Start streaming query
query = (processed_stream
    .writeStream
    .foreachBatch(write_processed_data)
    .option("checkpointLocation", "/mnt/checkpoints/production")
    .trigger(processingTime="30 seconds")
    .start()
)

# Monitor query
print(f"Query started: {query.id}")
query.awaitTermination()
```

---

## Troubleshooting Guide

### Common Issues

```python
# Issue: Schema mismatch
# Solution: Enable schema evolution
.option("mergeSchema", "true")

# Issue: State store size growing
# Solution: Set watermark appropriately
.withWatermark("event_time", "2 hours")

# Issue: Slow processing
# Solutions:
.option("maxFilesPerTrigger", "1000")
.option("maxBytesPerTrigger", "1g")
.trigger(processingTime="60 seconds")

# Issue: Memory errors in stateful operations
# Solution: Use RocksDB state store
spark.conf.set("spark.sql.streaming.stateStore.providerClass",
               "com.databricks.sql.streaming.state.RocksDBStateStoreProvider")

# Issue: Late data being dropped
# Solution: Increase watermark delay
.withWatermark("event_time", "30 minutes")
```

---

## References

- [Structured Streaming Programming Guide](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html)
- [Databricks Structured Streaming](https://docs.databricks.com/structured-streaming/index.html)
- [Delta Lake Streaming](https://docs.databricks.com/delta/delta-streaming.html)
- [Auto Loader](https://docs.databricks.com/ingestion/auto-loader/index.html)

---

**Best Practices Summary:**
- Always use checkpoints for fault tolerance
- Implement watermarking for stateful operations
- Monitor stream health and metrics
- Handle errors and late data gracefully
- Partition output data appropriately
- Use exactly-once semantics for critical data
- Test with realistic data volumes
- Plan for schema evolution
