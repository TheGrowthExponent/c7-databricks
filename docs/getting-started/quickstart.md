# Databricks Quick Start Guide

## Overview

This quick start guide will help you get up and running with Databricks in under 30 minutes. You'll learn how to create a cluster, run your first notebook, work with data, and execute basic analytics.

## Prerequisites

- Access to a Databricks workspace
- Personal Access Token configured (see [Authentication Guide](authentication.md))
- Basic knowledge of Python or SQL

## Step 1: Create Your First Cluster

### Via UI

1. Click **Compute** in the left sidebar
2. Click **Create Cluster**
3. Configure your cluster:
   - **Cluster Name**: `quickstart-cluster`
   - **Cluster Mode**: Single Node (for learning)
   - **Databricks Runtime**: 13.3 LTS (or latest LTS)
   - **Node Type**: Standard_DS3_v2 (Azure) or i3.xlarge (AWS)
   - **Terminate after**: 30 minutes of inactivity
4. Click **Create Cluster**
5. Wait 3-5 minutes for cluster to start

### Via Python SDK

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import compute

client = WorkspaceClient()

# Create cluster
cluster = client.clusters.create(
    cluster_name="quickstart-cluster",
    spark_version="13.3.x-scala2.12",
    node_type_id="i3.xlarge",  # AWS
    # node_type_id="Standard_DS3_v2",  # Azure
    num_workers=0,  # Single node
    autotermination_minutes=30,
    spark_conf={
        "spark.databricks.cluster.profile": "singleNode",
        "spark.master": "local[*]"
    },
    custom_tags={
        "ResourceClass": "SingleNode"
    }
)

print(f"Cluster ID: {cluster.cluster_id}")
print("Cluster starting... This may take a few minutes.")
```

### Via CLI

```bash
# Create cluster configuration file
cat > cluster-config.json << EOF
{
  "cluster_name": "quickstart-cluster",
  "spark_version": "13.3.x-scala2.12",
  "node_type_id": "i3.xlarge",
  "num_workers": 0,
  "autotermination_minutes": 30,
  "spark_conf": {
    "spark.databricks.cluster.profile": "singleNode",
    "spark.master": "local[*]"
  }
}
EOF

# Create cluster
databricks clusters create --json-file cluster-config.json
```

## Step 2: Create Your First Notebook

### Via UI

1. Click **Workspace** in the left sidebar
2. Navigate to your user folder: `/Users/your-email@example.com`
3. Click the dropdown arrow next to your name
4. Select **Create > Notebook**
5. Configure:
   - **Name**: `Quick Start Tutorial`
   - **Language**: Python
   - **Cluster**: Select your `quickstart-cluster`
6. Click **Create**

### Via CLI

```bash
# Create a Python notebook
cat > quickstart.py << 'EOF'
# Databricks notebook source
print("Hello from Databricks!")

# Get cluster information
spark.conf.get("spark.databricks.clusterUsageTags.clusterName")
EOF

# Import notebook to workspace
databricks workspace import quickstart.py \
  /Users/your-email@example.com/quickstart \
  --language PYTHON
```

## Step 3: Run Your First Code

### Hello World Example

In your notebook, create a new cell and run:

```python
# Cell 1: Basic Python
print("Hello, Databricks!")
print(f"Spark Version: {spark.version}")
print(f"Python Version: {spark.conf.get('spark.databricks.pythonVersion')}")
```

**Expected Output:**
```
Hello, Databricks!
Spark Version: 3.4.1
Python Version: 3.10.12
```

### Create a DataFrame

```python
# Cell 2: Create a simple DataFrame
from pyspark.sql import Row

# Create sample data
data = [
    Row(id=1, name="Alice", age=25, city="New York"),
    Row(id=2, name="Bob", age=30, city="San Francisco"),
    Row(id=3, name="Charlie", age=35, city="Seattle"),
    Row(id=4, name="Diana", age=28, city="Boston"),
    Row(id=5, name="Eve", age=32, city="Austin")
]

# Create DataFrame
df = spark.createDataFrame(data)

# Show DataFrame
display(df)
```

### Perform Basic Transformations

```python
# Cell 3: Filter and transform data
from pyspark.sql.functions import col, when

# Filter users over 30
adults = df.filter(col("age") > 30)
display(adults)

# Add a new column
df_with_category = df.withColumn(
    "age_group",
    when(col("age") < 25, "Young")
    .when(col("age") < 35, "Adult")
    .otherwise("Senior")
)

display(df_with_category)
```

### Aggregate Data

```python
# Cell 4: Aggregations
from pyspark.sql.functions import avg, count, max, min

# Calculate statistics
stats = df.agg(
    count("*").alias("total_count"),
    avg("age").alias("average_age"),
    min("age").alias("min_age"),
    max("age").alias("max_age")
)

display(stats)
```

## Step 4: Work with Data Files

### Upload Sample Data

```python
# Cell 5: Create sample CSV data
sample_data = """
product_id,product_name,category,price,stock
1,Laptop,Electronics,999.99,50
2,Mouse,Electronics,29.99,200
3,Keyboard,Electronics,79.99,150
4,Monitor,Electronics,299.99,75
5,Desk,Furniture,399.99,30
6,Chair,Furniture,199.99,45
7,Notebook,Stationery,4.99,500
8,Pen,Stationery,1.99,1000
"""

# Write to DBFS
dbutils.fs.put("/tmp/products.csv", sample_data, overwrite=True)
print("Sample data uploaded to DBFS!")
```

### Read CSV File

```python
# Cell 6: Read CSV into DataFrame
products_df = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load("/tmp/products.csv")

print("Schema:")
products_df.printSchema()

print("\nData:")
display(products_df)
```

### Analyze the Data

```python
# Cell 7: Analyze products data
from pyspark.sql.functions import sum as _sum, round as _round

# Category-wise analysis
category_stats = products_df.groupBy("category").agg(
    count("*").alias("product_count"),
    _round(avg("price"), 2).alias("avg_price"),
    _sum("stock").alias("total_stock"),
    _round(_sum(col("price") * col("stock")), 2).alias("inventory_value")
)

display(category_stats)
```

## Step 5: Create a Delta Table

### Write Data to Delta Format

```python
# Cell 8: Create Delta table
# Write DataFrame to Delta format
products_df.write.format("delta") \
    .mode("overwrite") \
    .save("/tmp/delta/products")

print("Delta table created!")

# Read back from Delta
delta_df = spark.read.format("delta").load("/tmp/delta/products")
display(delta_df)
```

### Create Managed Delta Table

```python
# Cell 9: Create managed table
products_df.write.format("delta") \
    .mode("overwrite") \
    .saveAsTable("products")

print("Managed table 'products' created!")

# Query the table
spark.sql("SELECT * FROM products").show()
```

### Perform MERGE Operation

```python
# Cell 10: Update data with MERGE
from delta.tables import DeltaTable

# Create updates
updates = spark.createDataFrame([
    (1, "Laptop Pro", "Electronics", 1299.99, 45),
    (9, "USB Cable", "Electronics", 9.99, 300)
], ["product_id", "product_name", "category", "price", "stock"])

# Perform MERGE
delta_table = DeltaTable.forPath(spark, "/tmp/delta/products")

delta_table.alias("target").merge(
    updates.alias("source"),
    "target.product_id = source.product_id"
).whenMatchedUpdateAll() \
 .whenNotMatchedInsertAll() \
 .execute()

print("MERGE completed!")

# View results
display(spark.read.format("delta").load("/tmp/delta/products"))
```

## Step 6: SQL Queries

### Switch to SQL

```sql
-- Cell 11: SQL queries
-- Create a temporary view
CREATE OR REPLACE TEMP VIEW product_view AS
SELECT 
    product_id,
    product_name,
    category,
    price,
    stock,
    price * stock AS inventory_value
FROM products;

-- Query the view
SELECT * FROM product_view
ORDER BY inventory_value DESC;
```

### Advanced SQL Analysis

```sql
-- Cell 12: Advanced analytics
-- Category analysis with window functions
SELECT 
    category,
    product_name,
    price,
    RANK() OVER (PARTITION BY category ORDER BY price DESC) AS price_rank,
    ROUND(AVG(price) OVER (PARTITION BY category), 2) AS category_avg_price
FROM products
ORDER BY category, price_rank;
```

## Step 7: Data Visualization

### Create Visualizations

```python
# Cell 13: Prepare data for visualization
viz_data = products_df.groupBy("category").agg(
    count("*").alias("count"),
    _round(avg("price"), 2).alias("avg_price"),
    _sum("stock").alias("total_stock")
)

display(viz_data)
```

**To create a chart:**
1. Click the **+** button below the table
2. Select **Visualization**
3. Choose chart type (Bar, Line, Pie, etc.)
4. Configure axes and keys
5. Save visualization

### Matplotlib Visualization

```python
# Cell 14: Custom visualization with matplotlib
import matplotlib.pyplot as plt
import pandas as pd

# Convert to Pandas for plotting
pandas_df = products_df.toPandas()

# Create bar chart
fig, ax = plt.subplots(figsize=(10, 6))
category_counts = pandas_df.groupby('category').size()
category_counts.plot(kind='bar', ax=ax, color='steelblue')
ax.set_title('Products by Category', fontsize=16)
ax.set_xlabel('Category', fontsize=12)
ax.set_ylabel('Count', fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()

display(fig)
```

## Step 8: Create a Simple Job

### Via UI

1. Click **Workflows** in the sidebar
2. Click **Create Job**
3. Configure:
   - **Task Name**: `quickstart-job`
   - **Type**: Notebook
   - **Notebook Path**: `/Users/your-email/Quick Start Tutorial`
   - **Cluster**: `quickstart-cluster`
4. Click **Create**
5. Click **Run Now** to test

### Via Python SDK

```python
# Cell 15: Create a job programmatically
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs

client = WorkspaceClient()

# Create job
job = client.jobs.create(
    name="quickstart-analysis-job",
    tasks=[
        jobs.Task(
            task_key="analyze_products",
            description="Analyze products data",
            notebook_task=jobs.NotebookTask(
                notebook_path="/Users/your-email@example.com/Quick Start Tutorial",
                base_parameters={}
            ),
            existing_cluster_id=cluster.cluster_id
        )
    ],
    email_notifications=jobs.JobEmailNotifications(
        on_success=["your-email@example.com"],
        on_failure=["your-email@example.com"]
    )
)

print(f"Job created with ID: {job.job_id}")
print(f"View job at: {client.config.host}/#job/{job.job_id}")
```

## Step 9: Working with External Data Sources

### Connect to External Database

```python
# Cell 16: Read from external database (example)
# Note: Update connection details for your database

jdbc_url = "jdbc:postgresql://hostname:5432/database"
properties = {
    "user": dbutils.secrets.get(scope="db-secrets", key="username"),
    "password": dbutils.secrets.get(scope="db-secrets", key="password"),
    "driver": "org.postgresql.Driver"
}

# Read from database
# external_df = spark.read.jdbc(
#     url=jdbc_url,
#     table="public.sales",
#     properties=properties
# )
# display(external_df)

print("Configure your database connection details to use this example")
```

### Read from Cloud Storage

```python
# Cell 17: Read from cloud storage
# AWS S3 example
# s3_df = spark.read.format("csv") \
#     .option("header", "true") \
#     .load("s3://bucket-name/path/to/file.csv")

# Azure Blob Storage example
# azure_df = spark.read.format("csv") \
#     .option("header", "true") \
#     .load("wasbs://container@account.blob.core.windows.net/path/file.csv")

# Google Cloud Storage example
# gcs_df = spark.read.format("csv") \
#     .option("header", "true") \
#     .load("gs://bucket-name/path/to/file.csv")

print("Update paths to read from your cloud storage")
```

## Step 10: Clean Up

### Stop the Cluster

```python
# Cell 18: Stop cluster to save costs
# Note: Only run this when you're done!
# client.clusters.delete(cluster_id=cluster.cluster_id)
print("Remember to stop your cluster when done!")
```

### Via UI
1. Go to **Compute**
2. Find your cluster
3. Click **Terminate**

### Via CLI
```bash
# List clusters to get cluster ID
databricks clusters list

# Terminate cluster
databricks clusters delete --cluster-id <cluster-id>
```

## Common Operations Reference

### DataFrame Operations

```python
# Read data
df = spark.read.format("csv").option("header", "true").load("/path/to/file.csv")
df = spark.read.table("table_name")
df = spark.sql("SELECT * FROM table_name")

# Write data
df.write.format("delta").mode("overwrite").save("/path/to/location")
df.write.saveAsTable("table_name")
df.write.mode("append").saveAsTable("table_name")

# Transformations
df.select("col1", "col2")
df.filter(col("age") > 30)
df.groupBy("category").count()
df.orderBy("price", ascending=False)
df.join(other_df, "key_column", "inner")

# Actions
df.show()
df.count()
df.collect()
df.toPandas()
display(df)
```

### DBFS Commands

```python
# List files
dbutils.fs.ls("/path")

# Copy file
dbutils.fs.cp("/source/path", "/dest/path")

# Move file
dbutils.fs.mv("/source/path", "/dest/path")

# Remove file
dbutils.fs.rm("/path", recurse=True)

# Read file
content = dbutils.fs.head("/path/to/file.txt")

# Write file
dbutils.fs.put("/path/to/file.txt", "content", overwrite=True)
```

## Next Steps

Congratulations! You've completed the quick start guide. Here's what to explore next:

### Beginner Level
1. **[Python SDK Guide](../sdk/python.md)**: Learn more about the Databricks SDK
2. **[SQL Reference](../sql/overview.md)**: Master Databricks SQL
3. **[Examples](../examples/python.md)**: More code examples

### Intermediate Level
4. **[Jobs API](../api/jobs.md)**: Automate workflows
5. **[Delta Lake](../sdk/delta-lake.md)**: Advanced data lake operations
6. **[MLflow](../ml/mlflow.md)**: Machine learning tracking

### Advanced Level
7. **[Best Practices](../best-practices/general.md)**: Production-ready patterns
8. **[Performance Optimization](../best-practices/performance.md)**: Tune your workloads
9. **[Unity Catalog](../api/unity-catalog.md)**: Data governance

## Troubleshooting

### Cluster Won't Start

**Problem:** Cluster stuck in "Pending" state

**Solutions:**
- Check cluster configuration is valid
- Verify you have quota for instance types
- Try a different node type
- Check workspace capacity limits

### Notebook Won't Connect to Cluster

**Problem:** "Cannot attach to cluster" error

**Solutions:**
- Verify cluster is running (green status)
- Check you have permissions to use the cluster
- Try detaching and reattaching notebook
- Restart cluster if necessary

### Import Errors

**Problem:** `ModuleNotFoundError` when importing libraries

**Solutions:**
```python
# Install library on cluster
%pip install package-name

# Or install for current notebook session
%pip install --quiet package-name

# Verify installation
import package_name
print(package_name.__version__)
```

### Out of Memory Errors

**Problem:** `OutOfMemoryError` or `GC overhead limit exceeded`

**Solutions:**
- Use `.limit(n)` to work with smaller data samples
- Increase cluster size or add more workers
- Optimize queries with filters and projections
- Use `df.repartition(n)` to redistribute data
- Cache intermediate results: `df.cache()`

## Helpful Resources

### Documentation
- [Databricks Documentation](https://docs.databricks.com/)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [Delta Lake Documentation](https://docs.delta.io/)

### Learning
- [Databricks Academy](https://academy.databricks.com/)
- [Example Notebooks](https://docs.databricks.com/notebooks/notebook-examples.html)
- [Databricks Blog](https://databricks.com/blog)

### Community
- [Databricks Community Forums](https://community.databricks.com/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/databricks)

## Summary

In this quick start, you learned how to:

✅ Create and configure a Databricks cluster
✅ Create and run notebooks
✅ Work with DataFrames and SQL
✅ Read and write data files
✅ Create Delta tables and perform MERGE operations
✅ Visualize data
✅ Create and run jobs
✅ Clean up resources

You're now ready to start building data pipelines, analytics, and ML workflows on Databricks!

## Related Documentation

- [Introduction to Databricks](introduction.md)
- [Setup Guide](setup.md)
- [Authentication Guide](authentication.md)
- [Clusters API](../api/clusters.md)
- [Jobs API](../api/jobs.md)