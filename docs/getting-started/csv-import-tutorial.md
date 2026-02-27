# Import and Visualize CSV Data from a Notebook

## Overview

This tutorial guides you through importing data from a CSV file into Databricks, storing it in Unity Catalog volumes, modifying the data, visualizing it, and saving it as a table. You'll work with real-world baby name data from the New York State Department of Health.

## Prerequisites

- Access to a Databricks workspace with Unity Catalog enabled
- A running cluster (see [Quick Start Guide](quickstart.md))
- Basic knowledge of Python, Scala, or R
- Write permissions to a Unity Catalog volume

## What You'll Learn

- How to download and upload CSV files to Unity Catalog volumes
- How to read CSV files into DataFrames
- How to transform and clean data
- How to modify column names
- How to visualize data in notebooks
- How to save data as managed tables in Unity Catalog

## Step 1: Understanding Unity Catalog Volumes

### What are Volumes?

Unity Catalog Volumes provide a way to store and access non-tabular data (files) with governance:

```
Catalog → Schema → Volume → Files
```

For example: `main.default.my_volume/data.csv`

### Create a Volume

```sql
-- Create a volume for your data files
CREATE VOLUME IF NOT EXISTS main.default.csv_data
COMMENT 'Volume for CSV data files';

-- List volumes
SHOW VOLUMES IN main.default;
```

### Using Python SDK

```python
# Check if volume exists
volumes = spark.sql("SHOW VOLUMES IN main.default")
display(volumes)

# Volume path
volume_path = "/Volumes/main/default/csv_data"
print(f"Volume path: {volume_path}")
```

## Step 2: Download Sample CSV Data

### Using Python (urllib)

```python
import urllib.request
import os

# Data source: NY State Health Department Baby Names
url = "https://health.data.ny.gov/api/views/jxy9-yhdk/rows.csv?accessType=DOWNLOAD"

# Download to local temp
local_file = "/tmp/baby_names.csv"
urllib.request.urlretrieve(url, local_file)

print(f"Downloaded CSV to {local_file}")

# Preview first few lines
with open(local_file, 'r') as f:
    for i, line in enumerate(f):
        if i < 5:
            print(line.strip())
        else:
            break
```

### Alternative: Using Requests

```python
import requests

url = "https://health.data.ny.gov/api/views/jxy9-yhdk/rows.csv?accessType=DOWNLOAD"

response = requests.get(url)
if response.status_code == 200:
    # Save to local file
    with open("/tmp/baby_names.csv", "wb") as f:
        f.write(response.content)
    print("Download successful!")
else:
    print(f"Download failed with status code: {response.status_code}")
```

## Step 3: Upload CSV to Unity Catalog Volume

### Using Python

```python
# Define paths
local_path = "/tmp/baby_names.csv"
volume_path = "/Volumes/main/default/csv_data/baby_names.csv"

# Read local file and write to volume
with open(local_path, 'rb') as f:
    data = f.read()

# Write to volume using dbutils
dbutils.fs.put(volume_path, data.decode('utf-8'), overwrite=True)

print(f"Uploaded to {volume_path}")

# Verify upload
files = dbutils.fs.ls("/Volumes/main/default/csv_data")
display(spark.createDataFrame(files))
```

### Alternative: Direct Download to Volume

```python
import requests

url = "https://health.data.ny.gov/api/views/jxy9-yhdk/rows.csv?accessType=DOWNLOAD"
volume_path = "/Volumes/main/default/csv_data/baby_names.csv"

# Download directly to volume
response = requests.get(url)
if response.status_code == 200:
    dbutils.fs.put(volume_path, response.text, overwrite=True)
    print(f"CSV uploaded to {volume_path}")
```

## Step 4: Read CSV File into DataFrame (Python)

### Basic CSV Read

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# Read CSV with header inference
df = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load("/Volumes/main/default/csv_data/baby_names.csv")

# Display first few rows
display(df.limit(10))

# Show schema
df.printSchema()

# Show record count
print(f"Total records: {df.count()}")
```

### Read with Explicit Schema

```python
# Define schema for better performance and type control
schema = StructType([
    StructField("Year", IntegerType(), True),
    StructField("First Name", StringType(), True),
    StructField("County", StringType(), True),
    StructField("Sex", StringType(), True),
    StructField("Count", IntegerType(), True)
])

# Read with explicit schema
df = spark.read.format("csv") \
    .option("header", "true") \
    .schema(schema) \
    .load("/Volumes/main/default/csv_data/baby_names.csv")

display(df.limit(10))
```

### Handle CSV Options

```python
# Read with additional CSV options
df = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .option("mode", "DROPMALFORMED") \
    .option("encoding", "UTF-8") \
    .option("quote", '"') \
    .option("escape", "\\") \
    .load("/Volumes/main/default/csv_data/baby_names.csv")

print(f"Records loaded: {df.count()}")
```

## Step 5: Read CSV File (Scala)

```scala
// Import required libraries
import org.apache.spark.sql.types._

// Read CSV file
val df = spark.read
  .format("csv")
  .option("header", "true")
  .option("inferSchema", "true")
  .load("/Volumes/main/default/csv_data/baby_names.csv")

// Display data
display(df.limit(10))

// Show schema
df.printSchema()

// With explicit schema
val schema = StructType(Array(
  StructField("Year", IntegerType, true),
  StructField("First Name", StringType, true),
  StructField("County", StringType, true),
  StructField("Sex", StringType, true),
  StructField("Count", IntegerType, true)
))

val dfWithSchema = spark.read
  .format("csv")
  .option("header", "true")
  .schema(schema)
  .load("/Volumes/main/default/csv_data/baby_names.csv")

display(dfWithSchema.limit(10))
```

## Step 6: Read CSV File (R)

```r
# Load SparkR library
library(SparkR)

# Read CSV file
df <- read.df(
  "/Volumes/main/default/csv_data/baby_names.csv",
  source = "csv",
  header = "true",
  inferSchema = "true"
)

# Display first rows
display(head(df, 10))

# Show schema
printSchema(df)

# Show count
cat("Total records:", count(df), "\n")
```

## Step 7: Modify Column Names

### Using Python

```python
from pyspark.sql.functions import col

# Current column names
print("Original columns:", df.columns)

# Rename columns to snake_case
df_renamed = df \
    .withColumnRenamed("First Name", "first_name") \
    .withColumnRenamed("Year", "year") \
    .withColumnRenamed("County", "county") \
    .withColumnRenamed("Sex", "sex") \
    .withColumnRenamed("Count", "count")

print("New columns:", df_renamed.columns)
display(df_renamed.limit(10))

# Alternative: Rename all columns at once
new_column_names = ["year", "first_name", "county", "sex", "count"]
df_renamed = df.toDF(*new_column_names)

display(df_renamed.limit(10))
```

### Using Scala

```scala
// Rename columns
val dfRenamed = df
  .withColumnRenamed("First Name", "first_name")
  .withColumnRenamed("Year", "year")
  .withColumnRenamed("County", "county")
  .withColumnRenamed("Sex", "sex")
  .withColumnRenamed("Count", "count")

println("New columns: " + dfRenamed.columns.mkString(", "))
display(dfRenamed.limit(10))
```

### Using R

```r
# Rename columns
df_renamed <- withColumnRenamed(df, "First Name", "first_name")
df_renamed <- withColumnRenamed(df_renamed, "Year", "year")
df_renamed <- withColumnRenamed(df_renamed, "County", "county")
df_renamed <- withColumnRenamed(df_renamed, "Sex", "sex")
df_renamed <- withColumnRenamed(df_renamed, "Count", "count")

display(head(df_renamed, 10))
```

## Step 8: Transform and Clean Data

### Data Exploration

```python
# Check for null values
from pyspark.sql.functions import col, count, when, isnan

null_counts = df_renamed.select([
    count(when(col(c).isNull(), c)).alias(c)
    for c in df_renamed.columns
])
display(null_counts)

# Get distinct values
print("Years range:", df_renamed.select("year").distinct().count())
print("Unique names:", df_renamed.select("first_name").distinct().count())
print("Counties:", df_renamed.select("county").distinct().count())

# Show sex distribution
display(df_renamed.groupBy("sex").count().orderBy("sex"))
```

### Clean and Filter Data

```python
from pyspark.sql.functions import trim, upper, lower

# Clean data
df_clean = df_renamed \
    .filter(col("count").isNotNull()) \
    .filter(col("year") >= 2000) \
    .withColumn("first_name", trim(col("first_name"))) \
    .withColumn("county", trim(upper(col("county")))) \
    .withColumn("first_name_lower", lower(col("first_name")))

print(f"Records after cleaning: {df_clean.count()}")
display(df_clean.limit(10))
```

### Add Derived Columns

```python
from pyspark.sql.functions import length, concat, lit

# Add computed columns
df_enriched = df_clean \
    .withColumn("name_length", length(col("first_name"))) \
    .withColumn("decade", (col("year") / 10).cast("int") * 10) \
    .withColumn("full_description",
                concat(col("first_name"), lit(" ("), col("sex"), lit(")"))
    )

display(df_enriched.limit(10))
```

## Step 9: Visualize the Data

### Most Popular Names by Year

```python
from pyspark.sql.functions import sum as _sum, rank
from pyspark.sql.window import Window

# Top 10 names overall
top_names = df_clean.groupBy("first_name") \
    .agg(_sum("count").alias("total_count")) \
    .orderBy(col("total_count").desc()) \
    .limit(10)

print("=== Top 10 Baby Names (2000+) ===")
display(top_names)
```

**Create a bar chart:**
1. Run the cell above
2. Click **+** → **Visualization**
3. Choose **Bar** chart
4. Set **Keys**: `first_name`
5. Set **Values**: `total_count`
6. Click **Save**

### Trend Over Time

```python
# Popular names trend by year
yearly_trend = df_clean.groupBy("year") \
    .agg(_sum("count").alias("total_births")) \
    .orderBy("year")

print("=== Total Births by Year ===")
display(yearly_trend)
```

**Create a line chart:**
1. Click **+** → **Visualization**
2. Choose **Line** chart
3. Set **X-axis**: `year`
4. Set **Y-axis**: `total_births`

### Gender Distribution

```python
# Gender distribution by year
gender_trend = df_clean.groupBy("year", "sex") \
    .agg(_sum("count").alias("total_count")) \
    .orderBy("year", "sex")

print("=== Gender Distribution by Year ===")
display(gender_trend)
```

**Create a stacked area chart:**
1. Click **+** → **Visualization**
2. Choose **Area** chart
3. Set **X-axis**: `year`
4. Set **Y-axis**: `total_count`
5. Set **Group by**: `sex`

### Top Names by Decade

```python
# Top 5 names per decade
window_spec = Window.partitionBy("decade", "sex").orderBy(col("total_count").desc())

decade_top_names = df_enriched.groupBy("decade", "sex", "first_name") \
    .agg(_sum("count").alias("total_count")) \
    .withColumn("rank", rank().over(window_spec)) \
    .filter(col("rank") <= 5) \
    .orderBy("decade", "sex", "rank")

print("=== Top 5 Names by Decade and Gender ===")
display(decade_top_names)
```

### County Analysis

```python
# Top counties by birth count
county_stats = df_clean.groupBy("county") \
    .agg(_sum("count").alias("total_births")) \
    .orderBy(col("total_births").desc()) \
    .limit(15)

print("=== Top 15 Counties by Birth Count ===")
display(county_stats)
```

## Step 10: Advanced Visualizations

### Using Matplotlib

```python
import matplotlib.pyplot as plt
import pandas as pd

# Convert to Pandas
top_names_pd = top_names.toPandas()

# Create figure
fig, ax = plt.subplots(figsize=(12, 6))

# Horizontal bar chart
ax.barh(top_names_pd['first_name'], top_names_pd['total_count'], color='steelblue')
ax.set_xlabel('Total Count', fontsize=12)
ax.set_ylabel('Name', fontsize=12)
ax.set_title('Top 10 Baby Names in NY (2000+)', fontsize=14, fontweight='bold')
ax.invert_yaxis()  # Highest at top

# Add value labels
for i, v in enumerate(top_names_pd['total_count']):
    ax.text(v + 100, i, f'{v:,}', va='center')

plt.tight_layout()
display(fig)
```

### Using Plotly

```python
import plotly.express as px
import pandas as pd

# Prepare data
yearly_trend_pd = yearly_trend.toPandas()

# Create interactive line chart
fig = px.line(
    yearly_trend_pd,
    x='year',
    y='total_births',
    title='Total Births Trend Over Time',
    labels={'year': 'Year', 'total_births': 'Total Births'},
    template='plotly_white'
)

fig.update_traces(line_color='#1f77b4', line_width=3)
fig.update_layout(
    hovermode='x unified',
    font=dict(size=12)
)

fig.show()
```

### Gender Comparison Visualization

```python
import plotly.graph_objects as go
import pandas as pd

# Prepare data by gender
gender_data = df_clean.groupBy("year", "sex") \
    .agg(_sum("count").alias("count")) \
    .orderBy("year") \
    .toPandas()

# Separate by gender
male_data = gender_data[gender_data['sex'] == 'M']
female_data = gender_data[gender_data['sex'] == 'F']

# Create figure
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=male_data['year'],
    y=male_data['count'],
    mode='lines',
    name='Male',
    line=dict(color='blue', width=2)
))

fig.add_trace(go.Scatter(
    x=female_data['year'],
    y=female_data['count'],
    mode='lines',
    name='Female',
    line=dict(color='pink', width=2)
))

fig.update_layout(
    title='Baby Names by Gender Over Time',
    xaxis_title='Year',
    yaxis_title='Number of Births',
    hovermode='x unified',
    template='plotly_white'
)

fig.show()
```

## Step 11: Save Data as Table

### Create Managed Delta Table

```python
# Write to managed table
df_clean.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("main.default.baby_names")

print("Table created: main.default.baby_names")

# Verify table creation
display(spark.sql("DESCRIBE TABLE EXTENDED main.default.baby_names"))
```

### Create External Table

```python
# Write to external location with table reference
external_path = "/Volumes/main/default/csv_data/baby_names_delta"

df_clean.write.format("delta") \
    .mode("overwrite") \
    .save(external_path)

# Create external table
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS main.default.baby_names_external
    USING DELTA
    LOCATION '{external_path}'
""")

print("External table created: main.default.baby_names_external")
```

### Create Partitioned Table

```python
# Write partitioned table for better query performance
df_clean.write.format("delta") \
    .mode("overwrite") \
    .partitionBy("year", "sex") \
    .saveAsTable("main.default.baby_names_partitioned")

print("Partitioned table created: main.default.baby_names_partitioned")
```

### Using SQL

```sql
-- Create table from DataFrame
CREATE OR REPLACE TABLE main.default.baby_names_sql AS
SELECT
    year,
    first_name,
    county,
    sex,
    count
FROM main.default.baby_names
WHERE count > 5;

-- Verify creation
SELECT COUNT(*) as total_rows FROM main.default.baby_names_sql;
```

## Step 12: Query the Saved Table

### Basic Queries

```sql
-- View table data
SELECT * FROM main.default.baby_names
LIMIT 10;

-- Count records
SELECT COUNT(*) as total_records
FROM main.default.baby_names;

-- Top names by year
SELECT
    year,
    first_name,
    sex,
    SUM(count) as total_count
FROM main.default.baby_names
WHERE year = 2020
GROUP BY year, first_name, sex
ORDER BY total_count DESC
LIMIT 10;
```

### Advanced Analytics

```sql
-- Year-over-year growth
WITH yearly_totals AS (
    SELECT
        year,
        SUM(count) as total_births
    FROM main.default.baby_names
    GROUP BY year
)
SELECT
    year,
    total_births,
    LAG(total_births) OVER (ORDER BY year) as prev_year_births,
    ROUND(
        (total_births - LAG(total_births) OVER (ORDER BY year)) * 100.0 /
        LAG(total_births) OVER (ORDER BY year),
        2
    ) as yoy_growth_pct
FROM yearly_totals
ORDER BY year;
```

## Step 13: Grant Table Permissions

### Grant Read Access

```sql
-- Grant SELECT permission to users
GRANT SELECT ON TABLE main.default.baby_names TO `user@company.com`;

-- Grant to group
GRANT SELECT ON TABLE main.default.baby_names TO `data-analysts`;

-- Show grants
SHOW GRANTS ON TABLE main.default.baby_names;
```

### Using Python SDK

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# Grant permissions (requires account admin)
# Note: Actual implementation depends on your Unity Catalog setup
print("Use SQL GRANT statements or Unity Catalog UI to manage permissions")
```

## Best Practices

### CSV Reading Optimization

```python
# 1. Use explicit schema for large files
from pyspark.sql.types import *

schema = StructType([
    StructField("year", IntegerType(), True),
    StructField("first_name", StringType(), True),
    StructField("county", StringType(), True),
    StructField("sex", StringType(), True),
    StructField("count", IntegerType(), True)
])

df = spark.read.format("csv") \
    .option("header", "true") \
    .schema(schema) \
    .load(volume_path)

# 2. Handle malformed records
df = spark.read.format("csv") \
    .option("header", "true") \
    .option("mode", "PERMISSIVE") \
    .option("columnNameOfCorruptRecord", "_corrupt_record") \
    .load(volume_path)

# Check for corrupt records
corrupt = df.filter(col("_corrupt_record").isNotNull())
if corrupt.count() > 0:
    print(f"Found {corrupt.count()} corrupt records")
    display(corrupt)
```

### Data Validation

```python
from pyspark.sql.functions import col, count, when

# Validate data quality
validation_results = df_clean.agg(
    count("*").alias("total_rows"),
    count(when(col("year").isNull(), 1)).alias("null_years"),
    count(when(col("first_name").isNull(), 1)).alias("null_names"),
    count(when(col("count") < 0, 1)).alias("negative_counts"),
    count(when(col("year") < 1900, 1)).alias("invalid_years")
)

display(validation_results)
```

### Memory Management

```python
# For large CSV files
# 1. Use sampling for exploration
sample_df = df.sample(0.1)  # 10% sample
display(sample_df)

# 2. Use repartition for better distribution
df_repartitioned = df.repartition(8)

# 3. Cache intermediate results
df_clean.cache()
result1 = df_clean.groupBy("year").count()
result2 = df_clean.groupBy("sex").count()
df_clean.unpersist()
```

## Troubleshooting

### File Not Found Error

**Error:** `Path does not exist: /Volumes/main/default/csv_data/baby_names.csv`

**Solutions:**
```python
# Verify volume exists
spark.sql("SHOW VOLUMES IN main.default").show()

# List files in volume
dbutils.fs.ls("/Volumes/main/default/csv_data/")

# Check file path spelling
volume_path = "/Volumes/main/default/csv_data/baby_names.csv"
print(f"Checking path: {volume_path}")
```

### Schema Mismatch

**Error:** CSV columns don't match expected schema

**Solutions:**
```python
# Let Spark infer schema first
df_infer = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load(volume_path)

df_infer.printSchema()

# Then create explicit schema based on inference
```

### Encoding Issues

**Error:** Special characters not displaying correctly

**Solutions:**
```python
# Specify encoding explicitly
df = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .option("encoding", "UTF-8") \
    .option("charset", "UTF-8") \
    .load(volume_path)
```

## Next Steps

Now that you can import and visualize CSV data:

1. **[Create Tables Tutorial](create-table-tutorial.md)**: Learn more about Unity Catalog tables
2. **[Build ETL Pipelines](etl-pipeline-tutorial.md)**: Automate data processing
3. **[Query and Visualize Data](query-visualize-data.md)**: Advanced querying techniques
4. **[Machine Learning](../ml/mlflow.md)**: Use data for ML models

## Additional Resources

- [Unity Catalog Volumes Documentation](https://docs.databricks.com/data-governance/unity-catalog/volumes.html)
- [CSV Data Source Documentation](https://spark.apache.org/docs/latest/sql-data-sources-csv.html)
- [Data Visualization Guide](https://docs.databricks.com/visualizations/index.html)
- [Delta Lake Documentation](https://docs.delta.io/)

## Summary

In this tutorial, you learned how to:

✅ Create and use Unity Catalog Volumes for file storage
✅ Download and upload CSV files to volumes
✅ Read CSV data using Python, Scala, and R
✅ Modify column names and transform data
✅ Clean and validate data quality
✅ Create visualizations with multiple tools
✅ Save data as managed Delta tables in Unity Catalog
✅ Query and grant permissions on tables

You're now equipped to work with external CSV data in Databricks!
