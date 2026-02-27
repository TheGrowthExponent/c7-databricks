# Create a Table in Unity Catalog

## Overview

This tutorial guides you through creating tables in Databricks using the Unity Catalog data governance model. You'll learn how to create managed and external tables, define schemas, set properties, grant privileges, and implement best practices for table management.

## Prerequisites

- Access to a Databricks workspace with Unity Catalog enabled
- A running cluster (see [Quick Start Guide](quickstart.md))
- CREATE TABLE permissions in a Unity Catalog schema
- Basic knowledge of SQL and DataFrames

## What You'll Learn

- Unity Catalog three-level namespace structure
- How to create managed and external tables
- How to define table schemas and properties
- How to grant and manage table permissions
- How to work with partitioned and clustered tables
- Best practices for table organization and governance

## Step 1: Understanding Unity Catalog Structure

### Three-Level Namespace

Unity Catalog uses a three-level namespace:

```
Catalog → Schema (Database) → Table
```

Example: `main.sales.customers`

- **Catalog**: Top-level container (e.g., `main`, `dev`, `prod`)
- **Schema**: Logical grouping of tables (e.g., `sales`, `marketing`)
- **Table**: The actual data table

### Explore Existing Structure

```sql
-- List all catalogs
SHOW CATALOGS;

-- List schemas in a catalog
SHOW SCHEMAS IN main;

-- List tables in a schema
SHOW TABLES IN main.default;

-- Describe a catalog
DESCRIBE CATALOG main;

-- Describe a schema
DESCRIBE SCHEMA main.default;
```

## Step 2: Create a Catalog (If Needed)

```sql
-- Create a new catalog (requires account admin privileges)
CREATE CATALOG IF NOT EXISTS my_catalog
COMMENT 'Catalog for tutorial examples';

-- Show catalogs
SHOW CATALOGS;

-- Set default catalog for session
USE CATALOG my_catalog;
```

### Using Python

```python
# Create catalog using SQL
spark.sql("""
    CREATE CATALOG IF NOT EXISTS my_catalog
    COMMENT 'Catalog for tutorial examples'
""")

# Set default catalog
spark.sql("USE CATALOG my_catalog")

# Verify
current_catalog = spark.sql("SELECT current_catalog()").collect()[0][0]
print(f"Current catalog: {current_catalog}")
```

## Step 3: Create a Schema

```sql
-- Create a schema
CREATE SCHEMA IF NOT EXISTS my_catalog.sales
COMMENT 'Schema for sales data'
LOCATION '/mnt/data/sales';  -- Optional: specify external location

-- Create schema with properties
CREATE SCHEMA IF NOT EXISTS my_catalog.analytics
COMMENT 'Schema for analytics tables'
WITH DBPROPERTIES (
    'owner' = 'data-team',
    'department' = 'analytics',
    'project' = 'q1-analysis'
);

-- List schemas
SHOW SCHEMAS IN my_catalog;

-- Describe schema
DESCRIBE SCHEMA EXTENDED my_catalog.sales;
```

### Using Python

```python
# Create schema
spark.sql("""
    CREATE SCHEMA IF NOT EXISTS my_catalog.sales
    COMMENT 'Schema for sales data'
""")

# List schemas
schemas = spark.sql("SHOW SCHEMAS IN my_catalog")
display(schemas)
```

## Step 4: Create a Managed Table

### Create Table from Data

```sql
-- Create a managed table with sample data
CREATE OR REPLACE TABLE my_catalog.sales.customers (
    customer_id BIGINT NOT NULL,
    first_name STRING,
    last_name STRING,
    email STRING,
    phone STRING,
    registration_date DATE,
    country STRING,
    total_purchases DECIMAL(10, 2),
    is_active BOOLEAN
)
COMMENT 'Customer master table'
TBLPROPERTIES (
    'quality' = 'gold',
    'pii' = 'true',
    'owner' = 'sales-team'
);

-- Insert sample data
INSERT INTO my_catalog.sales.customers VALUES
    (1, 'Alice', 'Johnson', 'alice.j@example.com', '+1-555-0101', '2023-01-15', 'USA', 2500.00, true),
    (2, 'Bob', 'Smith', 'bob.smith@example.com', '+1-555-0102', '2023-02-20', 'USA', 1800.50, true),
    (3, 'Charlie', 'Brown', 'charlie.b@example.com', '+44-555-0103', '2023-03-10', 'UK', 3200.75, true),
    (4, 'Diana', 'Martinez', 'diana.m@example.com', '+1-555-0104', '2023-04-05', 'USA', 950.00, false),
    (5, 'Eva', 'Wilson', 'eva.w@example.com', '+61-555-0105', '2023-05-12', 'Australia', 4100.25, true);

-- Verify table creation
SELECT * FROM my_catalog.sales.customers;
```

### Create Table from Query (CTAS)

```sql
-- Create table as select
CREATE OR REPLACE TABLE my_catalog.sales.active_customers
COMMENT 'Active customers only'
AS
SELECT
    customer_id,
    first_name,
    last_name,
    email,
    country,
    total_purchases
FROM my_catalog.sales.customers
WHERE is_active = true;

-- View results
SELECT * FROM my_catalog.sales.active_customers;
```

### Using Python DataFrame

```python
from pyspark.sql.types import StructType, StructField, LongType, StringType, DateType, DecimalType, BooleanType
from pyspark.sql.functions import col
import datetime

# Define schema
schema = StructType([
    StructField("customer_id", LongType(), False),
    StructField("first_name", StringType(), True),
    StructField("last_name", StringType(), True),
    StructField("email", StringType(), True),
    StructField("phone", StringType(), True),
    StructField("registration_date", DateType(), True),
    StructField("country", StringType(), True),
    StructField("total_purchases", DecimalType(10, 2), True),
    StructField("is_active", BooleanType(), True)
])

# Create sample data
data = [
    (1, "Alice", "Johnson", "alice.j@example.com", "+1-555-0101", datetime.date(2023, 1, 15), "USA", 2500.00, True),
    (2, "Bob", "Smith", "bob.smith@example.com", "+1-555-0102", datetime.date(2023, 2, 20), "USA", 1800.50, True),
    (3, "Charlie", "Brown", "charlie.b@example.com", "+44-555-0103", datetime.date(2023, 3, 10), "UK", 3200.75, True),
    (4, "Diana", "Martinez", "diana.m@example.com", "+1-555-0104", datetime.date(2023, 4, 5), "USA", 950.00, False),
    (5, "Eva", "Wilson", "eva.w@example.com", "+61-555-0105", datetime.date(2023, 5, 12), "Australia", 4100.25, True)
]

# Create DataFrame
df = spark.createDataFrame(data, schema=schema)

# Write as managed table
df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("my_catalog.sales.customers_python")

print("Table created successfully!")

# Verify
display(spark.table("my_catalog.sales.customers_python"))
```

## Step 5: Create an External Table

### Create External Table with Specified Location

```sql
-- Create external table (data stored outside default location)
CREATE OR REPLACE TABLE my_catalog.sales.orders_external (
    order_id BIGINT,
    customer_id BIGINT,
    order_date DATE,
    order_amount DECIMAL(10, 2),
    status STRING
)
USING DELTA
LOCATION '/Volumes/my_catalog/sales/orders_data'
COMMENT 'Orders data stored in external location';

-- Insert data
INSERT INTO my_catalog.sales.orders_external VALUES
    (101, 1, '2024-01-10', 150.00, 'completed'),
    (102, 2, '2024-01-11', 220.50, 'completed'),
    (103, 1, '2024-01-12', 89.99, 'pending'),
    (104, 3, '2024-01-13', 450.00, 'completed'),
    (105, 5, '2024-01-14', 310.25, 'shipped');

SELECT * FROM my_catalog.sales.orders_external;
```

### Using Python

```python
from pyspark.sql.types import StructType, StructField, LongType, DateType, DecimalType, StringType
import datetime

# Define external location
external_path = "/Volumes/my_catalog/sales/orders_data"

# Create data
orders_data = [
    (101, 1, datetime.date(2024, 1, 10), 150.00, "completed"),
    (102, 2, datetime.date(2024, 1, 11), 220.50, "completed"),
    (103, 1, datetime.date(2024, 1, 12), 89.99, "pending"),
    (104, 3, datetime.date(2024, 1, 13), 450.00, "completed"),
    (105, 5, datetime.date(2024, 1, 14), 310.25, "shipped")
]

orders_schema = StructType([
    StructField("order_id", LongType(), True),
    StructField("customer_id", LongType(), True),
    StructField("order_date", DateType(), True),
    StructField("order_amount", DecimalType(10, 2), True),
    StructField("status", StringType(), True)
])

orders_df = spark.createDataFrame(orders_data, schema=orders_schema)

# Write to external location
orders_df.write.format("delta") \
    .mode("overwrite") \
    .save(external_path)

# Create external table
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS my_catalog.sales.orders_python
    USING DELTA
    LOCATION '{external_path}'
""")

print("External table created successfully!")
```

## Step 6: Create Partitioned Tables

### Create Partitioned Table

```sql
-- Create partitioned table for better query performance
CREATE OR REPLACE TABLE my_catalog.sales.transactions (
    transaction_id BIGINT,
    customer_id BIGINT,
    product_id STRING,
    quantity INT,
    amount DECIMAL(10, 2),
    transaction_date DATE,
    transaction_year INT,
    transaction_month INT
)
USING DELTA
PARTITIONED BY (transaction_year, transaction_month)
COMMENT 'Partitioned transaction table for performance';

-- Insert sample data
INSERT INTO my_catalog.sales.transactions VALUES
    (1001, 1, 'PROD-001', 2, 100.00, '2026-02-27', 2024, 1),
    (1002, 2, 'PROD-002', 1, 250.50, '2024-01-20', 2024, 1),
    (1003, 3, 'PROD-001', 3, 150.00, '2024-02-10', 2024, 2),
    (1004, 1, 'PROD-003', 1, 500.00, '2024-02-15', 2024, 2),
    (1005, 5, 'PROD-002', 2, 501.00, '2024-03-05', 2024, 3);

-- Query uses partition pruning
SELECT *
FROM my_catalog.sales.transactions
WHERE transaction_year = 2024 AND transaction_month = 1;
```

### Using Python

```python
from pyspark.sql.functions import year, month

# Create data
transactions_data = [
    (1001, 1, "PROD-001", 2, 100.00, datetime.date(2024, 1, 15)),
    (1002, 2, "PROD-002", 1, 250.50, datetime.date(2024, 1, 20)),
    (1003, 3, "PROD-001", 3, 150.00, datetime.date(2024, 2, 10)),
    (1004, 1, "PROD-003", 1, 500.00, datetime.date(2024, 2, 15)),
    (1005, 5, "PROD-002", 2, 501.00, datetime.date(2024, 3, 5))
]

transactions_schema = StructType([
    StructField("transaction_id", LongType(), True),
    StructField("customer_id", LongType(), True),
    StructField("product_id", StringType(), True),
    StructField("quantity", IntegerType(), True),
    StructField("amount", DecimalType(10, 2), True),
    StructField("transaction_date", DateType(), True)
])

trans_df = spark.createDataFrame(transactions_data, schema=transactions_schema)

# Add partition columns
trans_df = trans_df.withColumn("transaction_year", year(col("transaction_date"))) \
                   .withColumn("transaction_month", month(col("transaction_date")))

# Write with partitioning
trans_df.write.format("delta") \
    .mode("overwrite") \
    .partitionBy("transaction_year", "transaction_month") \
    .saveAsTable("my_catalog.sales.transactions_python")

print("Partitioned table created!")
```

## Step 7: Create Tables with Constraints

### Primary Key and Check Constraints

```sql
-- Create table with constraints
CREATE OR REPLACE TABLE my_catalog.sales.products (
    product_id STRING NOT NULL,
    product_name STRING NOT NULL,
    category STRING,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT NOT NULL,
    min_stock_level INT,
    created_at TIMESTAMP,
    CONSTRAINT pk_products PRIMARY KEY (product_id),
    CONSTRAINT chk_price CHECK (price > 0),
    CONSTRAINT chk_stock CHECK (stock_quantity >= 0),
    CONSTRAINT chk_min_stock CHECK (min_stock_level >= 0)
)
COMMENT 'Products table with constraints';

-- Insert valid data
INSERT INTO my_catalog.sales.products VALUES
    ('PROD-001', 'Laptop', 'Electronics', 999.99, 50, 10, current_timestamp()),
    ('PROD-002', 'Mouse', 'Electronics', 29.99, 200, 50, current_timestamp()),
    ('PROD-003', 'Keyboard', 'Electronics', 79.99, 150, 30, current_timestamp());

-- This will fail due to constraint violation
-- INSERT INTO my_catalog.sales.products VALUES
--     ('PROD-004', 'Monitor', 'Electronics', -100.00, 75, 15, current_timestamp());

SELECT * FROM my_catalog.sales.products;
```

### Foreign Key Constraints

```sql
-- Create orders table with foreign key
CREATE OR REPLACE TABLE my_catalog.sales.order_items (
    order_item_id BIGINT NOT NULL,
    order_id BIGINT NOT NULL,
    product_id STRING NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    CONSTRAINT pk_order_items PRIMARY KEY (order_item_id),
    CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES my_catalog.sales.products(product_id),
    CONSTRAINT chk_quantity CHECK (quantity > 0)
)
COMMENT 'Order items with foreign key to products';

-- Insert data
INSERT INTO my_catalog.sales.order_items VALUES
    (1, 101, 'PROD-001', 2, 999.99),
    (2, 101, 'PROD-002', 1, 29.99),
    (3, 102, 'PROD-003', 1, 79.99);

SELECT * FROM my_catalog.sales.order_items;
```

## Step 8: Grant Table Permissions

### Grant SELECT Permission

```sql
-- Grant read access to a user
GRANT SELECT ON TABLE my_catalog.sales.customers TO `user@company.com`;

-- Grant read access to a group
GRANT SELECT ON TABLE my_catalog.sales.customers TO `data-analysts`;

-- Grant multiple privileges
GRANT SELECT, MODIFY ON TABLE my_catalog.sales.orders_external TO `data-engineers`;
```

### Grant All Privileges

```sql
-- Grant all privileges on table
GRANT ALL PRIVILEGES ON TABLE my_catalog.sales.customers TO `admin@company.com`;

-- Grant all privileges on schema
GRANT ALL PRIVILEGES ON SCHEMA my_catalog.sales TO `sales-admins`;
```

### View Grants

```sql
-- Show grants on a table
SHOW GRANTS ON TABLE my_catalog.sales.customers;

-- Show grants for a user
SHOW GRANTS ON TABLE my_catalog.sales.customers FOR `user@company.com`;
```

### Revoke Permissions

```sql
-- Revoke specific privilege
REVOKE SELECT ON TABLE my_catalog.sales.customers FROM `user@company.com`;

-- Revoke all privileges
REVOKE ALL PRIVILEGES ON TABLE my_catalog.sales.customers FROM `user@company.com`;
```

## Step 9: Table Properties and Metadata

### Set Table Properties

```sql
-- Alter table to add properties
ALTER TABLE my_catalog.sales.customers
SET TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'delta.enableChangeDataFeed' = 'true',
    'owner' = 'data-team',
    'version' = '1.0',
    'data_classification' = 'confidential'
);

-- View table properties
DESCRIBE TABLE EXTENDED my_catalog.sales.customers;

-- Show just table properties
SHOW TBLPROPERTIES my_catalog.sales.customers;
```

### Add Comments

```sql
-- Add or modify table comment
COMMENT ON TABLE my_catalog.sales.customers IS 'Customer master table - updated schema';

-- Add column comments
ALTER TABLE my_catalog.sales.customers
ALTER COLUMN email COMMENT 'Customer email address (PII)';

ALTER TABLE my_catalog.sales.customers
ALTER COLUMN phone COMMENT 'Customer phone number (PII)';
```

### Add Table Tags

```sql
-- Apply tags to table
ALTER TABLE my_catalog.sales.customers
SET TAGS ('pii' = 'true', 'department' = 'sales', 'environment' = 'production');

-- Apply tags to columns
ALTER TABLE my_catalog.sales.customers
ALTER COLUMN email SET TAGS ('pii_type' = 'email');

ALTER TABLE my_catalog.sales.customers
ALTER COLUMN phone SET TAGS ('pii_type' = 'phone');
```

## Step 10: Advanced Table Features

### Create Table with Liquid Clustering

```sql
-- Create table with liquid clustering (Databricks feature)
CREATE OR REPLACE TABLE my_catalog.sales.customer_events (
    event_id BIGINT,
    customer_id BIGINT,
    event_type STRING,
    event_timestamp TIMESTAMP,
    event_data STRING
)
USING DELTA
CLUSTER BY (customer_id, event_type)
COMMENT 'Customer events with liquid clustering';

-- Liquid clustering is more flexible than partitioning
-- and handles data skew better
```

### Create Clone Tables

```sql
-- Create shallow clone (metadata only)
CREATE OR REPLACE TABLE my_catalog.sales.customers_clone_shallow
SHALLOW CLONE my_catalog.sales.customers;

-- Create deep clone (full copy)
CREATE OR REPLACE TABLE my_catalog.sales.customers_clone_deep
DEEP CLONE my_catalog.sales.customers;

-- Clone at specific version
CREATE OR REPLACE TABLE my_catalog.sales.customers_clone_v1
SHALLOW CLONE my_catalog.sales.customers VERSION AS OF 1;
```

### Create Temporary Tables

```sql
-- Create temporary view (session-scoped)
CREATE OR REPLACE TEMP VIEW temp_high_value_customers AS
SELECT *
FROM my_catalog.sales.customers
WHERE total_purchases > 3000;

-- Query temporary view
SELECT * FROM temp_high_value_customers;

-- Create global temp view (application-scoped)
CREATE OR REPLACE GLOBAL TEMP VIEW global_temp.customer_summary AS
SELECT
    country,
    COUNT(*) as customer_count,
    SUM(total_purchases) as total_revenue
FROM my_catalog.sales.customers
GROUP BY country;

-- Query global temp view
SELECT * FROM global_temp.customer_summary;
```

## Step 11: Table Maintenance Operations

### Optimize Tables

```sql
-- Optimize table (compact small files)
OPTIMIZE my_catalog.sales.customers;

-- Optimize with Z-Ordering
OPTIMIZE my_catalog.sales.customers
ZORDER BY (country, registration_date);

-- Optimize specific partition
OPTIMIZE my_catalog.sales.transactions
WHERE transaction_year = 2024 AND transaction_month = 1;
```

### Vacuum Tables

```sql
-- Remove old files (default: 7 days retention)
VACUUM my_catalog.sales.customers;

-- Vacuum with specific retention
VACUUM my_catalog.sales.customers RETAIN 168 HOURS;  -- 7 days

-- Dry run to see what would be deleted
VACUUM my_catalog.sales.customers DRY RUN;
```

### Analyze Tables

```sql
-- Compute statistics for query optimization
ANALYZE TABLE my_catalog.sales.customers COMPUTE STATISTICS;

-- Compute column statistics
ANALYZE TABLE my_catalog.sales.customers COMPUTE STATISTICS FOR COLUMNS
    customer_id, country, total_purchases;

-- View statistics
DESCRIBE EXTENDED my_catalog.sales.customers;
```

## Step 12: Query Table History and Time Travel

### View Table History

```sql
-- Show table history
DESCRIBE HISTORY my_catalog.sales.customers;

-- Show specific number of versions
DESCRIBE HISTORY my_catalog.sales.customers LIMIT 5;
```

### Time Travel Queries

```sql
-- Query table at specific version
SELECT * FROM my_catalog.sales.customers VERSION AS OF 1;

-- Query table at specific timestamp
SELECT * FROM my_catalog.sales.customers TIMESTAMP AS OF '2026-02-27T10:00:00';

-- Compare versions
SELECT
    current.customer_id,
    current.total_purchases as current_purchases,
    previous.total_purchases as previous_purchases,
    current.total_purchases - previous.total_purchases as change
FROM my_catalog.sales.customers AS current
INNER JOIN my_catalog.sales.customers VERSION AS OF 0 AS previous
    ON current.customer_id = previous.customer_id
WHERE current.total_purchases != previous.total_purchases;
```

## Best Practices

### Table Naming Conventions

```sql
-- Use clear, descriptive names
-- Good examples:
-- - customer_orders
-- - product_inventory
-- - sales_transactions_daily

-- Bad examples:
-- - tbl1
-- - data
-- - temp

-- Include layer in medallion architecture
CREATE TABLE my_catalog.bronze.raw_customer_data (...);
CREATE TABLE my_catalog.silver.cleaned_customers (...);
CREATE TABLE my_catalog.gold.customer_metrics (...);
```

### Schema Design

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType

# Define schemas explicitly for production tables
production_schema = StructType([
    StructField("id", StringType(), False),  # NOT NULL
    StructField("name", StringType(), False),
    StructField("created_at", TimestampType(), False),
    StructField("updated_at", TimestampType(), True)  # Nullable
])

# Add meaningful comments
df.write.format("delta") \
    .option("comment", "Production customer data") \
    .option("delta.columnMapping.mode", "name") \
    .saveAsTable("my_catalog.prod.customers")
```

### Use Appropriate Data Types

```sql
-- Choose optimal data types
CREATE TABLE my_catalog.sales.optimized_table (
    -- Use BIGINT for large IDs
    id BIGINT NOT NULL,

    -- Use DECIMAL for monetary values
    amount DECIMAL(10, 2) NOT NULL,

    -- Use appropriate string length
    code STRING NOT NULL,  -- or VARCHAR(50) if known

    -- Use DATE/TIMESTAMP appropriately
    created_date DATE,
    updated_timestamp TIMESTAMP,

    -- Use BOOLEAN for flags
    is_active BOOLEAN DEFAULT true
);
```

### Implement Data Quality Checks

```sql
-- Add constraints
CREATE TABLE my_catalog.sales.quality_controlled (
    record_id BIGINT NOT NULL,
    email STRING NOT NULL,
    age INT,
    created_at TIMESTAMP NOT NULL,
    CONSTRAINT pk_record PRIMARY KEY (record_id),
    CONSTRAINT chk_email CHECK (email LIKE '%@%.%'),
    CONSTRAINT chk_age CHECK (age >= 0 AND age <= 150),
    CONSTRAINT chk_created CHECK (created_at <= current_timestamp())
);
```

### Enable Change Data Feed

```sql
-- Enable CDC for tracking changes
ALTER TABLE my_catalog.sales.customers
SET TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true');

-- Query changes
SELECT *
FROM table_changes('my_catalog.sales.customers', 0, 5);
```

## Troubleshooting

### Permission Denied Error

**Error:** `Permission denied: User does not have CREATE TABLE on Schema`

**Solutions:**

```sql
-- Request permissions from schema owner
-- GRANT CREATE TABLE ON SCHEMA my_catalog.sales TO `user@company.com`;

-- Or use a schema where you have permissions
SHOW SCHEMAS IN my_catalog;
```

### Table Already Exists

**Error:** `Table my_catalog.sales.customers already exists`

**Solutions:**

```sql
-- Use CREATE OR REPLACE
CREATE OR REPLACE TABLE my_catalog.sales.customers (...);

-- Or use IF NOT EXISTS
CREATE TABLE IF NOT EXISTS my_catalog.sales.customers (...);

-- Or drop existing table first
DROP TABLE IF EXISTS my_catalog.sales.customers;
CREATE TABLE my_catalog.sales.customers (...);
```

### Schema Evolution Issues

**Error:** Schema mismatch when writing data

**Solutions:**

```python
# Enable schema evolution
df.write.format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .saveAsTable("my_catalog.sales.customers")

# Or overwrite with new schema
df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("my_catalog.sales.customers")
```

## Next Steps

Now that you know how to create and manage tables in Unity Catalog:

1. **[Build ETL Pipelines](etl-pipeline-tutorial.md)**: Create data workflows
2. **[Query and Visualize Data](query-visualize-data.md)**: Analyze your tables
3. **[Delta Lake Advanced Features](../sdk/delta-lake.md)**: Learn advanced Delta operations
4. **[Unity Catalog API](../api/unity-catalog.md)**: Programmatic table management

## Additional Resources

- [Unity Catalog Tables Documentation](https://docs.databricks.com/data-governance/unity-catalog/create-tables.html)
- [Delta Lake Table Features](https://docs.delta.io/latest/delta-intro.html)
- [SQL Language Reference](https://docs.databricks.com/sql/language-manual/index.html)
- [Table ACLs and Governance](https://docs.databricks.com/data-governance/table-acls/index.html)

## Summary

In this tutorial, you learned how to:

✅ Understand Unity Catalog's three-level namespace
✅ Create catalogs and schemas
✅ Create managed and external tables
✅ Define partitioned and clustered tables
✅ Add constraints for data quality
✅ Grant and manage table permissions
✅ Set table properties and metadata
✅ Use advanced features like cloning and time travel
✅ Maintain tables with OPTIMIZE and VACUUM
✅ Implement best practices for production tables

You're now ready to create well-governed, high-performance tables in Unity Catalog!
