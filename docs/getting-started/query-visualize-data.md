# Query and Visualize Data in Unity Catalog

## Overview

This tutorial introduces you to querying data stored in Unity Catalog using SQL, Python, Scala, and R, and then visualizing the query results in a Databricks notebook. Unity Catalog provides unified governance for all data and AI assets across clouds.

## Prerequisites

- Access to a Databricks workspace with Unity Catalog enabled
- A running cluster (see [Quick Start Guide](quickstart.md))
- Basic familiarity with SQL and at least one programming language (Python, Scala, or R)

## What You'll Learn

- How to explore Unity Catalog schemas and tables
- How to query data using SQL, Python, Scala, and R
- How to visualize query results in notebooks
- How to work with sample datasets in Unity Catalog

## Step 1: Explore Unity Catalog

### Understanding Unity Catalog Structure

Unity Catalog organizes data in a three-level namespace:

```
Catalog → Schema → Table/View
```

For example: `main.default.sales_data`

### Browse Available Catalogs

```python
# List all catalogs you have access to
catalogs = spark.sql("SHOW CATALOGS")
display(catalogs)
```

### Explore Schemas and Tables

```python
# List schemas in the 'main' catalog
schemas = spark.sql("SHOW SCHEMAS IN main")
display(schemas)

# List tables in a specific schema
tables = spark.sql("SHOW TABLES IN main.default")
display(tables)
```

### Using Data Explorer

1. Click **Data** icon in the left sidebar
2. Browse catalogs, schemas, and tables
3. Click on a table to see:
   - Schema/column information
   - Sample data preview
   - Permissions and ownership
   - Data lineage

## Step 2: Access Sample Data

Databricks provides sample datasets in Unity Catalog for learning and testing.

### Discover Sample Datasets

```python
# List sample datasets
sample_tables = spark.sql("""
    SHOW TABLES IN samples.nyctaxi
""")
display(sample_tables)
```

### Common Sample Datasets

| Dataset | Catalog.Schema | Description |
|---------|---------------|-------------|
| NYC Taxi | `samples.nyctaxi.trips` | New York City taxi trip records |
| Tpch | `samples.tpch` | TPC-H benchmark dataset |
| COVID-19 | `samples.covid19` | COVID-19 related data |

### Preview Sample Data

```python
# Preview NYC taxi data
trips = spark.sql("""
    SELECT * FROM samples.nyctaxi.trips
    LIMIT 10
""")
display(trips)
```

## Step 3: Query Data with SQL

### Basic SELECT Query

```sql
-- View trip data with specific columns
SELECT
    tpep_pickup_datetime,
    tpep_dropoff_datetime,
    passenger_count,
    trip_distance,
    fare_amount,
    pickup_zip,
    dropoff_zip
FROM samples.nyctaxi.trips
LIMIT 100;
```

### Filtering Data

```sql
-- Find trips with multiple passengers and significant distance
SELECT
    tpep_pickup_datetime,
    passenger_count,
    trip_distance,
    fare_amount,
    ROUND(fare_amount / trip_distance, 2) AS fare_per_mile
FROM samples.nyctaxi.trips
WHERE
    passenger_count >= 3
    AND trip_distance > 5.0
    AND fare_amount > 0
ORDER BY fare_amount DESC
LIMIT 50;
```

### Aggregating Data

```sql
-- Calculate daily trip statistics
SELECT
    DATE(tpep_pickup_datetime) AS trip_date,
    COUNT(*) AS total_trips,
    ROUND(AVG(trip_distance), 2) AS avg_distance,
    ROUND(AVG(fare_amount), 2) AS avg_fare,
    ROUND(SUM(fare_amount), 2) AS total_revenue
FROM samples.nyctaxi.trips
WHERE tpep_pickup_datetime >= '2016-01-01'
GROUP BY DATE(tpep_pickup_datetime)
ORDER BY trip_date;
```

### Window Functions

```sql
-- Rank trips by fare amount within each day
SELECT
    DATE(tpep_pickup_datetime) AS trip_date,
    trip_distance,
    fare_amount,
    RANK() OVER (
        PARTITION BY DATE(tpep_pickup_datetime)
        ORDER BY fare_amount DESC
    ) AS fare_rank
FROM samples.nyctaxi.trips
WHERE tpep_pickup_datetime >= '2016-01-01'
QUALIFY fare_rank <= 5
ORDER BY trip_date, fare_rank;
```

## Step 4: Query Data with Python (PySpark)

### Basic DataFrame Operations

```python
from pyspark.sql.functions import col, avg, count, sum, round as spark_round

# Create DataFrame from Unity Catalog table
trips_df = spark.table("samples.nyctaxi.trips")

# Show first few rows
display(trips_df.limit(10))

# Print schema
trips_df.printSchema()
```

### Filter and Select

```python
# Filter trips with multiple passengers
filtered_df = trips_df.filter(
    (col("passenger_count") >= 3) &
    (col("trip_distance") > 5.0) &
    (col("fare_amount") > 0)
).select(
    "tpep_pickup_datetime",
    "passenger_count",
    "trip_distance",
    "fare_amount"
)

display(filtered_df.limit(50))
```

### Aggregations

```python
from pyspark.sql.functions import date_format, to_date

# Daily statistics
daily_stats = trips_df.groupBy(
    to_date("tpep_pickup_datetime").alias("trip_date")
).agg(
    count("*").alias("total_trips"),
    spark_round(avg("trip_distance"), 2).alias("avg_distance"),
    spark_round(avg("fare_amount"), 2).alias("avg_fare"),
    spark_round(sum("fare_amount"), 2).alias("total_revenue")
).orderBy("trip_date")

display(daily_stats)
```

### Complex Transformations

```python
from pyspark.sql.functions import when, hour, dayofweek

# Categorize trips by time of day and calculate metrics
enriched_df = trips_df.withColumn(
    "time_of_day",
    when(hour("tpep_pickup_datetime").between(6, 11), "Morning")
    .when(hour("tpep_pickup_datetime").between(12, 17), "Afternoon")
    .when(hour("tpep_pickup_datetime").between(18, 22), "Evening")
    .otherwise("Night")
).withColumn(
    "day_of_week",
    dayofweek("tpep_pickup_datetime")
).withColumn(
    "is_weekend",
    when(dayofweek("tpep_pickup_datetime").isin([1, 7]), "Weekend")
    .otherwise("Weekday")
)

# Analyze by time of day
time_analysis = enriched_df.groupBy("time_of_day", "is_weekend").agg(
    count("*").alias("trip_count"),
    spark_round(avg("fare_amount"), 2).alias("avg_fare"),
    spark_round(avg("trip_distance"), 2).alias("avg_distance")
).orderBy("is_weekend", "time_of_day")

display(time_analysis)
```

## Step 5: Query Data with Scala

```scala
// Import required functions
import org.apache.spark.sql.functions._

// Load data from Unity Catalog
val tripsDF = spark.table("samples.nyctaxi.trips")

// Basic filtering and selection
val filteredDF = tripsDF
  .filter($"passenger_count" >= 3 && $"trip_distance" > 5.0)
  .select(
    $"tpep_pickup_datetime",
    $"passenger_count",
    $"trip_distance",
    $"fare_amount"
  )

display(filteredDF.limit(50))

// Aggregations
val dailyStats = tripsDF
  .groupBy(to_date($"tpep_pickup_datetime").alias("trip_date"))
  .agg(
    count("*").alias("total_trips"),
    round(avg("trip_distance"), 2).alias("avg_distance"),
    round(avg("fare_amount"), 2).alias("avg_fare"),
    round(sum("fare_amount"), 2).alias("total_revenue")
  )
  .orderBy("trip_date")

display(dailyStats)
```

## Step 6: Query Data with R (SparkR)

```r
# Load SparkR library
library(SparkR)

# Read data from Unity Catalog
trips_df <- sql("SELECT * FROM samples.nyctaxi.trips")

# Show first few rows
display(head(trips_df, 10))

# Filter data
filtered_df <- filter(trips_df,
                      trips_df$passenger_count >= 3 &
                      trips_df$trip_distance > 5.0)

# Select specific columns
selected_df <- select(filtered_df,
                      "tpep_pickup_datetime",
                      "passenger_count",
                      "trip_distance",
                      "fare_amount")

display(head(selected_df, 50))

# Aggregation using SQL
daily_stats <- sql("
  SELECT
    DATE(tpep_pickup_datetime) AS trip_date,
    COUNT(*) AS total_trips,
    ROUND(AVG(trip_distance), 2) AS avg_distance,
    ROUND(AVG(fare_amount), 2) AS avg_fare
  FROM samples.nyctaxi.trips
  GROUP BY DATE(tpep_pickup_datetime)
  ORDER BY trip_date
")

display(daily_stats)
```

## Step 7: Create Visualizations

### Bar Chart - Trip Count by Hour

```python
from pyspark.sql.functions import hour

# Prepare data
hourly_trips = trips_df.groupBy(
    hour("tpep_pickup_datetime").alias("hour")
).agg(
    count("*").alias("trip_count")
).orderBy("hour")

display(hourly_trips)
```

**To create a bar chart:**
1. Run the cell to display the data
2. Click the **+** button below the table
3. Select **Visualization**
4. Choose **Bar** chart type
5. Set **Keys**: `hour`
6. Set **Values**: `trip_count`
7. Click **Save**

### Line Chart - Daily Revenue Trend

```python
# Prepare time series data
daily_revenue = trips_df.groupBy(
    to_date("tpep_pickup_datetime").alias("trip_date")
).agg(
    spark_round(sum("fare_amount"), 2).alias("total_revenue")
).orderBy("trip_date")

display(daily_revenue)
```

**To create a line chart:**
1. Click **+** → **Visualization**
2. Choose **Line** chart type
3. Set **X-axis**: `trip_date`
4. Set **Y-axis**: `total_revenue`
5. Enable **Smooth lines** (optional)
6. Click **Save**

### Histogram - Fare Distribution

```python
# Prepare distribution data
fare_distribution = trips_df.select("fare_amount").filter(
    (col("fare_amount") > 0) & (col("fare_amount") < 100)
)

display(fare_distribution)
```

**To create a histogram:**
1. Click **+** → **Visualization**
2. Choose **Histogram** chart type
3. Set **Value**: `fare_amount`
4. Adjust **Bin count** as needed
5. Click **Save**

### Scatter Plot - Distance vs Fare

```python
# Prepare scatter plot data
scatter_data = trips_df.select(
    "trip_distance",
    "fare_amount"
).filter(
    (col("trip_distance") > 0) & (col("trip_distance") < 30) &
    (col("fare_amount") > 0) & (col("fare_amount") < 100)
).sample(0.01)  # Sample for performance

display(scatter_data)
```

**To create a scatter plot:**
1. Click **+** → **Visualization**
2. Choose **Scatter** chart type
3. Set **X-axis**: `trip_distance`
4. Set **Y-axis**: `fare_amount`
5. Click **Save**

### Heatmap - Trips by Day and Hour

```python
from pyspark.sql.functions import dayofweek

# Prepare heatmap data
heatmap_data = trips_df.groupBy(
    dayofweek("tpep_pickup_datetime").alias("day_of_week"),
    hour("tpep_pickup_datetime").alias("hour")
).agg(
    count("*").alias("trip_count")
).orderBy("day_of_week", "hour")

display(heatmap_data)
```

**To create a heatmap:**
1. Click **+** → **Visualization**
2. Choose **Heatmap** chart type
3. Set **X-axis**: `hour`
4. Set **Y-axis**: `day_of_week`
5. Set **Value**: `trip_count`
6. Adjust color scheme
7. Click **Save**

## Step 8: Advanced Visualizations with Python Libraries

### Matplotlib Visualization

```python
import matplotlib.pyplot as plt
import pandas as pd

# Convert to Pandas for plotting
hourly_pd = hourly_trips.toPandas()

# Create figure
fig, ax = plt.subplots(figsize=(12, 6))

# Create bar plot
ax.bar(hourly_pd['hour'], hourly_pd['trip_count'], color='steelblue', alpha=0.8)

# Customize
ax.set_xlabel('Hour of Day', fontsize=12)
ax.set_ylabel('Number of Trips', fontsize=12)
ax.set_title('NYC Taxi Trips by Hour of Day', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

# Display
plt.tight_layout()
display(fig)
```

### Plotly Interactive Visualization

```python
import plotly.express as px
import pandas as pd

# Prepare data
daily_pd = daily_revenue.toPandas()

# Create interactive line chart
fig = px.line(
    daily_pd,
    x='trip_date',
    y='total_revenue',
    title='Daily Revenue Trend',
    labels={'trip_date': 'Date', 'total_revenue': 'Revenue ($)'},
    template='plotly_white'
)

# Customize
fig.update_traces(line_color='#1f77b4', line_width=2)
fig.update_layout(
    hovermode='x unified',
    xaxis_title='Date',
    yaxis_title='Total Revenue ($)',
    font=dict(size=12)
)

# Display
fig.show()
```

### Seaborn Statistical Visualization

```python
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# Sample data for visualization
sample_data = trips_df.select(
    "trip_distance",
    "fare_amount",
    "passenger_count"
).filter(
    (col("trip_distance") > 0) & (col("trip_distance") < 20) &
    (col("fare_amount") > 0) & (col("fare_amount") < 100)
).sample(0.001).toPandas()

# Create figure with subplots
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Scatter plot with regression line
sns.regplot(
    data=sample_data,
    x='trip_distance',
    y='fare_amount',
    ax=axes[0],
    scatter_kws={'alpha': 0.3},
    line_kws={'color': 'red'}
)
axes[0].set_title('Trip Distance vs Fare Amount')
axes[0].set_xlabel('Distance (miles)')
axes[0].set_ylabel('Fare ($)')

# Box plot by passenger count
sns.boxplot(
    data=sample_data,
    x='passenger_count',
    y='fare_amount',
    ax=axes[1],
    palette='Set2'
)
axes[1].set_title('Fare Distribution by Passenger Count')
axes[1].set_xlabel('Number of Passengers')
axes[1].set_ylabel('Fare ($)')

plt.tight_layout()
display(fig)
```

## Step 9: Save Query Results

### Save as Delta Table

```python
# Save aggregated results as a new Delta table
daily_stats.write.format("delta") \
    .mode("overwrite") \
    .saveAsTable("main.default.nyc_taxi_daily_stats")

print("Results saved to main.default.nyc_taxi_daily_stats")

# Verify
saved_data = spark.table("main.default.nyc_taxi_daily_stats")
display(saved_data)
```

### Save as View

```sql
-- Create a view for easy reuse
CREATE OR REPLACE VIEW main.default.taxi_trip_summary AS
SELECT
    DATE(tpep_pickup_datetime) AS trip_date,
    COUNT(*) AS total_trips,
    ROUND(AVG(trip_distance), 2) AS avg_distance,
    ROUND(AVG(fare_amount), 2) AS avg_fare,
    ROUND(SUM(fare_amount), 2) AS total_revenue
FROM samples.nyctaxi.trips
WHERE tpep_pickup_datetime >= '2016-01-01'
GROUP BY DATE(tpep_pickup_datetime);

-- Query the view
SELECT * FROM main.default.taxi_trip_summary
ORDER BY trip_date DESC
LIMIT 10;
```

### Export to CSV

```python
# Export results to CSV in DBFS
daily_stats.coalesce(1).write.format("csv") \
    .option("header", "true") \
    .mode("overwrite") \
    .save("/tmp/taxi_daily_stats.csv")

print("Results exported to /tmp/taxi_daily_stats.csv")

# List the file
display(dbutils.fs.ls("/tmp/taxi_daily_stats.csv"))
```

## Step 10: Create a Dashboard

### Combine Multiple Visualizations

```python
# Create multiple aggregations for dashboard

# 1. Summary statistics
summary = trips_df.agg(
    count("*").alias("total_trips"),
    spark_round(sum("fare_amount"), 2).alias("total_revenue"),
    spark_round(avg("trip_distance"), 2).alias("avg_distance")
)

print("=== Trip Summary ===")
display(summary)

# 2. Hourly distribution
hourly = trips_df.groupBy(
    hour("tpep_pickup_datetime").alias("hour")
).count().orderBy("hour")

print("=== Trips by Hour ===")
display(hourly)

# 3. Top pickup locations
top_pickups = trips_df.groupBy("pickup_zip") \
    .count() \
    .orderBy(col("count").desc()) \
    .limit(10)

print("=== Top 10 Pickup Locations ===")
display(top_pickups)

# 4. Fare distribution by passenger count
fare_by_passengers = trips_df.groupBy("passenger_count").agg(
    spark_round(avg("fare_amount"), 2).alias("avg_fare"),
    count("*").alias("trip_count")
).filter(col("passenger_count") <= 6).orderBy("passenger_count")

print("=== Average Fare by Passenger Count ===")
display(fare_by_passengers)
```

### Create Databricks Dashboard

1. Click the **Dashboards** icon in the left sidebar
2. Click **Create Dashboard**
3. Add visualizations from your notebook:
   - Click **Add** → **Visualization**
   - Select notebook and specific visualization
   - Position and resize as needed
4. Add filters for interactivity
5. Share with your team

## Best Practices

### Query Optimization

```python
# 1. Use column pruning - select only needed columns
optimized_df = trips_df.select(
    "tpep_pickup_datetime",
    "trip_distance",
    "fare_amount"
).filter(col("fare_amount") > 0)

# 2. Partition filtering for better performance
filtered_by_date = trips_df.filter(
    (col("tpep_pickup_datetime") >= "2016-01-01") &
    (col("tpep_pickup_datetime") < "2016-02-01")
)

# 3. Use limit for exploration
sample = trips_df.limit(1000)
```

### Caching for Repeated Use

```python
# Cache DataFrame for multiple operations
trips_df.cache()

# Run multiple queries
result1 = trips_df.groupBy("passenger_count").count()
result2 = trips_df.groupBy(hour("tpep_pickup_datetime")).count()
result3 = trips_df.agg(avg("fare_amount"))

# Unpersist when done
trips_df.unpersist()
```

### Working with Large Results

```python
# For large result sets, avoid collecting to driver
# Instead, write to storage or use display() with limit

# Good - processes data in Spark
large_result = trips_df.groupBy("pickup_zip").count()
large_result.write.format("delta").save("/tmp/large_result")

# Bad - may cause OOM if result is too large
# large_pandas = large_result.toPandas()  # Avoid without limit
```

## Common Patterns

### Time Series Analysis

```python
from pyspark.sql.functions import window

# Aggregate by time windows
windowed_stats = trips_df.groupBy(
    window("tpep_pickup_datetime", "1 hour")
).agg(
    count("*").alias("trip_count"),
    spark_round(avg("fare_amount"), 2).alias("avg_fare")
).orderBy("window")

display(windowed_stats)
```

### Cohort Analysis

```python
from pyspark.sql.functions import month, year

# Monthly cohort analysis
monthly_cohorts = trips_df.groupBy(
    year("tpep_pickup_datetime").alias("year"),
    month("tpep_pickup_datetime").alias("month")
).agg(
    count("*").alias("trips"),
    spark_round(sum("fare_amount"), 2).alias("revenue"),
    spark_round(avg("trip_distance"), 2).alias("avg_distance")
).orderBy("year", "month")

display(monthly_cohorts)
```

### Percentile Analysis

```python
from pyspark.sql.functions import expr

# Calculate fare percentiles
percentiles = trips_df.selectExpr(
    "percentile_approx(fare_amount, 0.25) as p25",
    "percentile_approx(fare_amount, 0.50) as median",
    "percentile_approx(fare_amount, 0.75) as p75",
    "percentile_approx(fare_amount, 0.95) as p95"
)

display(percentiles)
```

## Troubleshooting

### Table Not Found

**Error:** `Table or view not found: samples.nyctaxi.trips`

**Solutions:**
- Verify Unity Catalog is enabled in your workspace
- Check you have READ permission on the catalog/schema
- Use `SHOW CATALOGS` and `SHOW TABLES` to confirm available data
- Contact workspace admin for access

### Permission Denied

**Error:** `Permission denied: User does not have USE CATALOG on Catalog`

**Solutions:**
- Request permissions from catalog owner
- Use a different catalog you have access to
- Check your workspace role and entitlements

### Out of Memory When Visualizing

**Error:** Visualization fails or notebook crashes

**Solutions:**
```python
# Limit data size before visualization
limited_df = large_df.limit(10000)
display(limited_df)

# Or sample the data
sampled_df = large_df.sample(0.01)  # 1% sample
display(sampled_df)

# Aggregate before visualizing
aggregated = large_df.groupBy("category").count()
display(aggregated)
```

## Next Steps

Now that you can query and visualize Unity Catalog data, explore:

1. **[Import and Visualize CSV Data](csv-import-tutorial.md)**: Load external data
2. **[Create Tables in Unity Catalog](create-table-tutorial.md)**: Build your own tables
3. **[Build ETL Pipelines](etl-pipeline-tutorial.md)**: Automate data workflows
4. **[SQL Reference](../sql/overview.md)**: Learn advanced SQL features
5. **[Python SDK](../sdk/python.md)**: Programmatic data access

## Additional Resources

- [Unity Catalog Documentation](https://docs.databricks.com/data-governance/unity-catalog/index.html)
- [Data Visualization Guide](https://docs.databricks.com/visualizations/index.html)
- [SQL Language Reference](https://docs.databricks.com/sql/language-manual/index.html)
- [PySpark API Reference](https://spark.apache.org/docs/latest/api/python/)

## Summary

In this tutorial, you learned how to:

✅ Explore Unity Catalog structure and browse available data
✅ Access sample datasets for learning and testing
✅ Query data using SQL, Python, Scala, and R
✅ Create visualizations with built-in and custom tools
✅ Save query results as tables and views
✅ Apply best practices for performance and scale

You're now ready to work with data in Unity Catalog and create insightful visualizations!
