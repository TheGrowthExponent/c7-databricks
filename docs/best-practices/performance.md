# Databricks Performance Optimization Best Practices

## Overview

This guide provides comprehensive best practices for optimizing performance in Databricks, covering cluster configuration, Spark optimization, Delta Lake tuning, and query performance.

## Table of Contents

1. [Cluster Configuration](#cluster-configuration)
2. [Spark Optimization](#spark-optimization)
3. [Delta Lake Performance](#delta-lake-performance)
4. [Query Optimization](#query-optimization)
5. [Data Skew Solutions](#data-skew-solutions)
6. [Caching Strategies](#caching-strategies)
7. [Monitoring and Debugging](#monitoring-and-debugging)

---

## Cluster Configuration

### Right-Sizing Clusters

```python
# Assess your workload first
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("WorkloadAnalysis").getOrCreate()

# Check current resources
print(f"Executors: {spark.sparkContext.defaultParallelism}")
print(f"Executor Memory: {spark.conf.get('spark.executor.memory')}")
print(f"Executor Cores: {spark.conf.get('spark.executor.cores')}")
```

**Guidelines:**

1. **Driver Node**
   - Use Standard_DS3_v2 or similar for typical workloads
   - Scale up for collect() operations or large broadcast variables
   - Driver memory should be ~10% of total cluster memory

2. **Worker Nodes**
   - Memory-optimized: For large datasets and aggregations
   - Compute-optimized: For CPU-intensive transformations
   - General-purpose: Balanced workloads

3. **Autoscaling**
   ```python
   # Enable autoscaling for variable workloads
   # Min workers: 2, Max workers: 8
   # Automatically scales based on pending tasks
   ```

### Cluster Configuration Best Practices

```python
# Optimal Spark configurations
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")

# Memory management
spark.conf.set("spark.executor.memory", "8g")
spark.conf.set("spark.executor.memoryOverhead", "1g")
spark.conf.set("spark.memory.fraction", "0.8")
spark.conf.set("spark.memory.storageFraction", "0.3")

# Parallelism
spark.conf.set("spark.sql.shuffle.partitions", "200")  # Adjust based on data size
spark.conf.set("spark.default.parallelism", "200")

# Network
spark.conf.set("spark.network.timeout", "800s")
spark.conf.set("spark.executor.heartbeatInterval", "60s")
```

---

## Spark Optimization

### Partitioning Strategy

```python
from pyspark.sql.functions import col

# GOOD: Appropriate partition count
df = spark.read.format("delta").table("large_table")

# Rule of thumb: Each partition should be 128MB - 1GB
data_size_gb = 100
ideal_partitions = data_size_gb / 0.5  # 200 partitions

df = df.repartition(int(ideal_partitions))

# BETTER: Partition by commonly filtered columns
df = df.repartition(200, "date", "region")

# BEST: Adaptive Query Execution (AQE) handles this automatically
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
```

### Avoid Common Anti-Patterns

```python
# ❌ BAD: Collecting large datasets
large_df = spark.read.format("delta").table("billion_rows")
data = large_df.collect()  # Will crash!

# ✅ GOOD: Process in distributed manner
large_df.write.format("delta").mode("overwrite").saveAsTable("processed")

# ❌ BAD: Using UDFs when built-in functions exist
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

@udf(returnType=StringType())
def upper_case(s):
    return s.upper()

df = df.withColumn("upper", upper_case(col("name")))

# ✅ GOOD: Use built-in functions
from pyspark.sql.functions import upper
df = df.withColumn("upper", upper(col("name")))

# ❌ BAD: Excessive shuffles
df = df.groupBy("col1").count()
df = df.groupBy("col2").count()  # Two shuffles!

# ✅ GOOD: Combine operations
df = df.groupBy("col1", "col2").count()
```

### Broadcast Joins

```python
from pyspark.sql.functions import broadcast

# Small dimension table
dim_table = spark.read.format("delta").table("small_dimension")  # < 10MB

# Large fact table
fact_table = spark.read.format("delta").table("large_fact")

# ❌ BAD: Regular join (shuffle both sides)
result = fact_table.join(dim_table, "key")

# ✅ GOOD: Broadcast join (no shuffle of large table)
result = fact_table.join(broadcast(dim_table), "key")

# Automatic broadcast threshold
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "10485760")  # 10MB
```

### Predicate Pushdown

```python
# ✅ GOOD: Filter early (predicate pushdown)
df = spark.read.format("delta") \
    .table("large_table") \
    .filter(col("date") == "2024-01-01") \
    .filter(col("status") == "active")

# ❌ BAD: Filter late
df = spark.read.format("delta").table("large_table")
df = df.join(other_df, "key")
df = df.filter(col("date") == "2024-01-01")  # Too late!

# ✅ GOOD: Filter before join
df = spark.read.format("delta").table("large_table")
df = df.filter(col("date") == "2024-01-01")
df = df.join(other_df, "key")
```

### Column Pruning

```python
# ❌ BAD: Reading all columns
df = spark.read.format("delta").table("wide_table")
result = df.select("col1", "col2")  # Wasted I/O!

# ✅ GOOD: Select only needed columns early
df = spark.read.format("delta").table("wide_table")
df = spark.read.format("delta").table("wide_table").select("col1", "col2", "col3")
result = df.select("col1", "col2")

# ✅ BEST: Automatic column pruning
result = spark.read.format("delta").table("wide_table").select("col1", "col2")
```

---

## Delta Lake Performance

### Optimize and Z-Order

```python
from delta.tables import DeltaTable

# Regular optimization (compact small files)
delta_table = DeltaTable.forName(spark, "catalog.schema.table")
delta_table.optimize().executeCompaction()

# Z-Order for better data skipping
delta_table.optimize().executeZOrderBy("customer_id", "date")

# Schedule regular optimization
spark.sql("""
    OPTIMIZE catalog.schema.table
    ZORDER BY (customer_id, date)
""")
```

**Z-Order Guidelines:**
- Choose 2-4 columns most frequently used in WHERE clauses
- Order columns by cardinality (highest first)
- Re-run Z-Order after significant data changes

### Auto-Optimize

```python
# Enable auto-optimize for new tables
spark.sql("""
    CREATE TABLE catalog.schema.auto_optimized (
        id INT,
        name STRING,
        date DATE
    ) USING DELTA
    TBLPROPERTIES (
        'delta.autoOptimize.optimizeWrite' = 'true',
        'delta.autoOptimize.autoCompact' = 'true'
    )
""")

# Enable for existing tables
spark.sql("""
    ALTER TABLE catalog.schema.existing_table
    SET TBLPROPERTIES (
        'delta.autoOptimize.optimizeWrite' = 'true',
        'delta.autoOptimize.autoCompact' = 'true'
    )
""")
```

### Partition Pruning

```python
# ✅ GOOD: Partitioned table with filter on partition column
df = spark.read.format("delta") \
    .table("catalog.schema.partitioned_table") \
    .filter("date = '2024-01-01'")  # Only reads one partition!

# ❌ BAD: Filter on non-partition column
df = spark.read.format("delta") \
    .table("catalog.schema.partitioned_table") \
    .filter("amount > 1000")  # Scans all partitions

# ✅ GOOD: Combine partition and data filters
df = spark.read.format("delta") \
    .table("catalog.schema.partitioned_table") \
    .filter("date = '2024-01-01' AND amount > 1000")
```

### Vacuum Strategy

```python
from delta.tables import DeltaTable

# Don't vacuum too frequently
# Rule: Vacuum after major updates/deletes, not after every write

# Configure retention
spark.sql("""
    ALTER TABLE catalog.schema.table
    SET TBLPROPERTIES (
        'delta.deletedFileRetentionDuration' = 'interval 7 days',
        'delta.logRetentionDuration' = 'interval 30 days'
    )
""")

# Vacuum old files
delta_table = DeltaTable.forName(spark, "catalog.schema.table")
delta_table.vacuum(168)  # 7 days in hours
```

---

## Query Optimization

### Use Explain Plan

```python
df = spark.read.format("delta").table("catalog.schema.table") \
    .filter(col("date") == "2024-01-01") \
    .groupBy("customer_id") \
    .agg({"amount": "sum"})

# View physical plan
df.explain(mode="formatted")

# Look for:
# - Number of shuffle exchanges (minimize)
# - Broadcast joins vs sort-merge joins
# - Predicate pushdown effectiveness
# - Column pruning
```

### Optimize Aggregations

```python
from pyspark.sql.functions import sum, avg, count, col

# ❌ BAD: Multiple passes over data
total = df.agg(sum("amount")).collect()[0][0]
average = df.agg(avg("amount")).collect()[0][0]
cnt = df.count()

# ✅ GOOD: Single pass
stats = df.agg(
    sum("amount").alias("total"),
    avg("amount").alias("average"),
    count("*").alias("count")
).collect()[0]

# ✅ GOOD: Approximate aggregations for large datasets
approx_count = df.agg(
    approx_count_distinct("customer_id").alias("unique_customers")
)
```

### Window Functions Optimization

```python
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, rank, dense_rank

# ❌ BAD: Multiple window specifications
window1 = Window.partitionBy("customer_id").orderBy("date")
window2 = Window.partitionBy("customer_id").orderBy("date")

df = df.withColumn("row_num", row_number().over(window1))
df = df.withColumn("rank", rank().over(window2))

# ✅ GOOD: Reuse window specification
window = Window.partitionBy("customer_id").orderBy("date")

df = df.withColumn("row_num", row_number().over(window)) \
       .withColumn("rank", rank().over(window))

# ✅ GOOD: Limit window frame size when possible
window_limited = Window.partitionBy("customer_id") \
    .orderBy("date") \
    .rowsBetween(-7, 0)  # Only last 7 rows
```

---

## Data Skew Solutions

### Detect Data Skew

```python
from pyspark.sql.functions import col, count

# Check for skew in key columns
skew_check = df.groupBy("customer_id").count() \
    .orderBy(col("count").desc())

skew_check.show(20)

# Calculate skew statistics
stats = skew_check.agg(
    avg("count").alias("avg"),
    max("count").alias("max"),
    stddev("count").alias("stddev")
).collect()[0]

skew_ratio = stats['max'] / stats['avg']
if skew_ratio > 10:
    print(f"Significant skew detected! Ratio: {skew_ratio}")
```

### Salting Technique

```python
from pyspark.sql.functions import col, concat, lit, monotonically_increasing_id

# Add salt to skewed keys
num_salts = 10

df_salted = df.withColumn(
    "salt",
    (col("customer_id") % num_salts).cast("string")
).withColumn(
    "salted_key",
    concat(col("customer_id"), lit("_"), col("salt"))
)

# Perform operation on salted keys
result = df_salted.groupBy("salted_key").agg(sum("amount"))

# Remove salt from results
final = result.withColumn(
    "customer_id",
    split(col("salted_key"), "_")[0].cast("int")
).groupBy("customer_id").agg(sum("sum(amount)"))
```

### Adaptive Query Execution (AQE)

```python
# Enable AQE to handle skew automatically
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "5")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256MB")

# AQE will automatically detect and handle skewed joins
result = large_df.join(skewed_df, "key")
```

---

## Caching Strategies

### When to Cache

```python
from pyspark.sql.functions import col

# ✅ GOOD: Cache for reuse
df = spark.read.format("delta").table("large_table") \
    .filter(col("date") >= "2024-01-01")

df.cache()  # or df.persist()

# Use multiple times
result1 = df.groupBy("category").count()
result2 = df.groupBy("region").agg({"amount": "sum"})
result3 = df.filter(col("status") == "active").count()

# Don't forget to unpersist when done
df.unpersist()
```

### Cache Levels

```python
from pyspark import StorageLevel

# Memory only (fastest, but can evict)
df.persist(StorageLevel.MEMORY_ONLY)

# Memory and disk (safer)
df.persist(StorageLevel.MEMORY_AND_DISK)

# Serialized (saves memory)
df.persist(StorageLevel.MEMORY_ONLY_SER)

# Replicated (fault tolerance)
df.persist(StorageLevel.MEMORY_AND_DISK_2)
```

### Delta Caching

```python
# Enable Delta cache (automatic for SQL queries)
spark.conf.set("spark.databricks.io.cache.enabled", "true")

# Use CACHE SELECT for explicit caching
spark.sql("""
    CACHE SELECT * FROM catalog.schema.table
    WHERE date >= '2024-01-01'
""")

# Check what's cached
spark.sql("SHOW TABLES IN cache_db").show()

# Clear cache
spark.sql("CLEAR CACHE")
```

---

## Monitoring and Debugging

### Spark UI Metrics

```python
# Access Spark UI to monitor:
# 1. Stages: Look for long-running stages
# 2. Storage: Check cached DataFrames
# 3. Executors: Monitor resource utilization
# 4. SQL: View query plans

# Get stage metrics programmatically
sc = spark.sparkContext
stage_ids = sc.statusTracker().getActiveStageIds()
print(f"Active stages: {stage_ids}")
```

### Query Profiling

```python
import time

def profile_query(query_name, df):
    """Profile query execution time"""
    start = time.time()
    
    # Force execution
    count = df.count()
    
    end = time.time()
    duration = end - start
    
    print(f"{query_name}: {duration:.2f}s, Rows: {count}")
    return duration

# Usage
df = spark.read.format("delta").table("catalog.schema.table")

profile_query("Full scan", df)
profile_query("Filtered", df.filter(col("date") == "2024-01-01"))
profile_query("Aggregated", df.groupBy("category").count())
```

### Memory Analysis

```python
# Check memory usage
spark.sparkContext.getConf().get("spark.executor.memory")
spark.sparkContext.getConf().get("spark.driver.memory")

# Monitor storage
storage_status = spark.sparkContext._jsc.sc().getExecutorStorageStatus()

for executor in storage_status:
    print(f"Executor: {executor.blockManagerId().host()}")
    print(f"  Memory Used: {executor.memUsed() / 1024 / 1024:.2f} MB")
    print(f"  Memory Free: {executor.memRemaining() / 1024 / 1024:.2f} MB")
```

### Performance Logging

```python
import logging
from functools import wraps
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_performance(func):
    """Decorator to log function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        logger.info(f"Starting {func.__name__}")
        
        result = func(*args, **kwargs)
        
        duration = time.time() - start
        logger.info(f"Completed {func.__name__} in {duration:.2f}s")
        
        return result
    return wrapper

@log_performance
def load_and_process():
    df = spark.read.format("delta").table("large_table")
    result = df.groupBy("category").count()
    return result.count()
```

---

## Optimization Checklist

### Pre-Production Checklist

- [ ] Enable Adaptive Query Execution
- [ ] Configure appropriate shuffle partitions
- [ ] Use broadcast joins for small tables
- [ ] Enable Delta auto-optimize
- [ ] Set up regular OPTIMIZE jobs
- [ ] Configure proper retention periods
- [ ] Use Z-Order on frequently filtered columns
- [ ] Partition large tables appropriately
- [ ] Avoid collecting large datasets
- [ ] Use built-in functions instead of UDFs
- [ ] Cache reused DataFrames
- [ ] Monitor for data skew
- [ ] Review Spark UI for bottlenecks
- [ ] Set appropriate cluster size
- [ ] Enable autoscaling for variable workloads

### Performance Testing Template

```python
from datetime import datetime
import json

def performance_test_suite():
    """Run comprehensive performance tests"""
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": []
    }
    
    # Test 1: Read performance
    start = time.time()
    df = spark.read.format("delta").table("catalog.schema.table")
    count = df.count()
    duration = time.time() - start
    
    results["tests"].append({
        "test": "read_performance",
        "duration": duration,
        "rows": count
    })
    
    # Test 2: Filter performance
    start = time.time()
    filtered = df.filter(col("date") == "2024-01-01")
    count = filtered.count()
    duration = time.time() - start
    
    results["tests"].append({
        "test": "filter_performance",
        "duration": duration,
        "rows": count
    })
    
    # Test 3: Aggregation performance
    start = time.time()
    agg = df.groupBy("category").agg(sum("amount"))
    count = agg.count()
    duration = time.time() - start
    
    results["tests"].append({
        "test": "aggregation_performance",
        "duration": duration,
        "rows": count
    })
    
    # Save results
    with open("performance_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(json.dumps(results, indent=2))
    return results

# Run tests
performance_test_suite()
```

---

## Related Documentation

- [Cluster Configuration Guide](./cluster-config.md)
- [Delta Lake Optimization](../sdk/delta-lake.md#optimize-and-z-order)
- [SQL Performance](../sql/optimization.md)
- [ETL Best Practices](../examples/etl-patterns.md)

---

## Additional Resources

- [Databricks Performance Tuning](https://docs.databricks.com/optimizations/index.html)
- [Spark Performance Tuning](https://spark.apache.org/docs/latest/tuning.html)
- [Delta Lake Optimization Guide](https://docs.delta.io/latest/optimizations-oss.html)
- [Adaptive Query Execution](https://databricks.com/blog/2020/05/29/adaptive-query-execution-speeding-up-spark-sql-at-runtime.html)