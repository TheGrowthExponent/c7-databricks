# Databricks SQL Examples

## Overview

This guide provides practical SQL examples for common operations in Databricks. All examples use Delta Lake format and follow best practices for performance and reliability.

## Table of Contents

- [Data Definition Language (DDL)](#data-definition-language-ddl)
- [Data Manipulation Language (DML)](#data-manipulation-language-dml)
- [Delta Lake Operations](#delta-lake-operations)
- [Unity Catalog](#unity-catalog)
- [Common Query Patterns](#common-query-patterns)
- [Window Functions](#window-functions)
- [Aggregations](#aggregations)
- [Joins](#joins)
- [Performance Optimization](#performance-optimization)

---

## Data Definition Language (DDL)

### Create Database

```sql
-- Create database
CREATE DATABASE IF NOT EXISTS my_database
COMMENT 'Database for analytics'
LOCATION '/mnt/data/my_database';

-- Use database
USE my_database;

-- Show databases
SHOW DATABASES;
```

### Create Tables

#### Managed Table

```sql
-- Create managed Delta table
CREATE TABLE IF NOT EXISTS customers (
    customer_id BIGINT,
    first_name STRING,
    last_name STRING,
    email STRING,
    phone STRING,
    registration_date DATE,
    country STRING,
    is_active BOOLEAN
)
USING DELTA
COMMENT 'Customer information table'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true'
);
```

#### External Table

```sql
-- Create external table pointing to existing data
CREATE EXTERNAL TABLE IF NOT EXISTS sales_raw (
    transaction_id STRING,
    customer_id BIGINT,
    product_id BIGINT,
    quantity INT,
    amount DECIMAL(10, 2),
    transaction_date DATE
)
USING DELTA
LOCATION '/mnt/data/sales_raw';
```

#### Table with Partitioning

```sql
-- Create partitioned table
CREATE TABLE IF NOT EXISTS sales (
    transaction_id STRING,
    customer_id BIGINT,
    product_id BIGINT,
    quantity INT,
    amount DECIMAL(10, 2),
    transaction_date DATE,
    year INT,
    month INT
)
USING DELTA
PARTITIONED BY (year, month)
LOCATION '/mnt/data/sales'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);
```

#### Create Table As Select (CTAS)

```sql
-- Create table from query results
CREATE TABLE customer_summary
USING DELTA
AS
SELECT
    customer_id,
    COUNT(*) as order_count,
    SUM(amount) as total_spent,
    AVG(amount) as avg_order_value,
    MAX(transaction_date) as last_order_date
FROM sales
GROUP BY customer_id;
```

### Alter Tables

```sql
-- Add column
ALTER TABLE customers
ADD COLUMN loyalty_points INT;

-- Rename column
ALTER TABLE customers
RENAME COLUMN phone TO phone_number;

-- Change column type
ALTER TABLE customers
ALTER COLUMN loyalty_points TYPE BIGINT;

-- Add comment to column
ALTER TABLE customers
ALTER COLUMN email COMMENT 'Customer email address';

-- Set table properties
ALTER TABLE customers
SET TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true'
);
```

### Drop Tables

```sql
-- Drop table
DROP TABLE IF EXISTS temp_table;

-- Drop table and delete data
DROP TABLE IF EXISTS old_data PURGE;
```

### Describe Tables

```sql
-- Show table schema
DESCRIBE TABLE customers;

-- Show detailed table information
DESCRIBE EXTENDED customers;

-- Show table properties
SHOW TBLPROPERTIES customers;

-- Show create table statement
SHOW CREATE TABLE customers;
```

---

## Data Manipulation Language (DML)

### Insert Data

```sql
-- Insert single row
INSERT INTO customers VALUES (
    1,
    'John',
    'Doe',
    'john.doe@example.com',
    '555-0100',
    '2026-02-27',
    'USA',
    true
);

-- Insert multiple rows
INSERT INTO customers VALUES
    (2, 'Jane', 'Smith', 'jane.smith@example.com', '555-0101', '2024-01-16', 'USA', true),
    (3, 'Bob', 'Johnson', 'bob.j@example.com', '555-0102', '2024-01-17', 'Canada', true);

-- Insert from select
INSERT INTO customer_summary
SELECT
    customer_id,
    COUNT(*) as order_count,
    SUM(amount) as total_spent,
    AVG(amount) as avg_order_value,
    MAX(transaction_date) as last_order_date
FROM sales
GROUP BY customer_id;

-- Insert overwrite
INSERT OVERWRITE TABLE customer_summary
SELECT
    customer_id,
    COUNT(*) as order_count,
    SUM(amount) as total_spent
FROM sales
WHERE transaction_date >= '2024-01-01'
GROUP BY customer_id;
```

### Update Data

```sql
-- Simple update
UPDATE customers
SET is_active = false
WHERE registration_date < '2020-01-01';

-- Update with calculation
UPDATE customers
SET loyalty_points = loyalty_points + 100
WHERE customer_id IN (
    SELECT customer_id
    FROM sales
    WHERE transaction_date >= CURRENT_DATE - INTERVAL 30 DAYS
);

-- Update with join
UPDATE customers c
SET c.loyalty_points = s.points
FROM (
    SELECT customer_id, SUM(amount) / 10 as points
    FROM sales
    GROUP BY customer_id
) s
WHERE c.customer_id = s.customer_id;
```

### Delete Data

```sql
-- Delete with condition
DELETE FROM customers
WHERE is_active = false
  AND registration_date < '2020-01-01';

-- Delete with subquery
DELETE FROM sales
WHERE customer_id IN (
    SELECT customer_id
    FROM customers
    WHERE is_active = false
);
```

### Merge (Upsert)

```sql
-- Merge data (upsert)
MERGE INTO customers target
USING customer_updates source
ON target.customer_id = source.customer_id
WHEN MATCHED THEN
    UPDATE SET
        target.first_name = source.first_name,
        target.last_name = source.last_name,
        target.email = source.email,
        target.phone_number = source.phone_number
WHEN NOT MATCHED THEN
    INSERT (
        customer_id,
        first_name,
        last_name,
        email,
        phone_number,
        registration_date,
        country,
        is_active
    )
    VALUES (
        source.customer_id,
        source.first_name,
        source.last_name,
        source.email,
        source.phone_number,
        CURRENT_DATE,
        source.country,
        true
    );
```

### Complex Merge with Delete

```sql
-- Merge with delete for inactive records
MERGE INTO customers target
USING customer_updates source
ON target.customer_id = source.customer_id
WHEN MATCHED AND source.status = 'deleted' THEN
    DELETE
WHEN MATCHED AND source.status = 'updated' THEN
    UPDATE SET *
WHEN NOT MATCHED AND source.status = 'new' THEN
    INSERT *;
```

---

## Delta Lake Operations

### Optimize Tables

```sql
-- Optimize table (compact small files)
OPTIMIZE customers;

-- Optimize with Z-ordering
OPTIMIZE customers
ZORDER BY (country, registration_date);

-- Optimize specific partition
OPTIMIZE sales
WHERE year = 2024 AND month = 1;
```

### Vacuum Tables

```sql
-- Remove old versions (default 7 days retention)
VACUUM customers;

-- Vacuum with custom retention period
VACUUM customers RETAIN 168 HOURS;

-- Dry run to see what would be deleted
VACUUM customers DRY RUN;
```

### Time Travel

```sql
-- Query table as of specific timestamp
SELECT * FROM customers
TIMESTAMP AS OF '2026-02-27 10:00:00';

-- Query table as of specific version
SELECT * FROM customers
VERSION AS OF 42;

-- See table history
DESCRIBE HISTORY customers;

-- Restore table to previous version
RESTORE TABLE customers TO VERSION AS OF 42;

-- Restore table to timestamp
RESTORE TABLE customers TO TIMESTAMP AS OF '2026-02-27';
```

### Clone Tables

```sql
-- Deep clone (copies data)
CREATE TABLE customers_backup
DEEP CLONE customers;

-- Shallow clone (references data)
CREATE TABLE customers_dev
SHALLOW CLONE customers;

-- Clone specific version
CREATE TABLE customers_snapshot
SHALLOW CLONE customers VERSION AS OF 42;
```

### Convert to Delta

```sql
-- Convert Parquet table to Delta
CONVERT TO DELTA parquet.`/mnt/data/old_table`;

-- Convert with partitioning info
CONVERT TO DELTA parquet.`/mnt/data/partitioned_table`
PARTITIONED BY (year INT, month INT);
```

---

## Unity Catalog

### Catalog Operations

```sql
-- Create catalog
CREATE CATALOG IF NOT EXISTS production
COMMENT 'Production data catalog';

-- Use catalog
USE CATALOG production;

-- Show catalogs
SHOW CATALOGS;

-- Grant access
GRANT USE CATALOG ON CATALOG production TO `data_analysts`;
```

### Schema Operations

```sql
-- Create schema
CREATE SCHEMA IF NOT EXISTS production.sales
COMMENT 'Sales data schema';

-- Use schema
USE production.sales;

-- Show schemas
SHOW SCHEMAS IN production;

-- Grant access
GRANT USE SCHEMA ON SCHEMA production.sales TO `data_analysts`;
GRANT SELECT ON SCHEMA production.sales TO `data_analysts`;
```

### Three-Level Namespace

```sql
-- Query with full three-level namespace
SELECT * FROM production.sales.transactions
WHERE transaction_date = CURRENT_DATE;

-- Create table in specific catalog/schema
CREATE TABLE production.sales.daily_summary
AS SELECT
    transaction_date,
    COUNT(*) as transaction_count,
    SUM(amount) as total_amount
FROM production.sales.transactions
GROUP BY transaction_date;
```

### Row and Column Level Security

```sql
-- Create view with row-level filtering
CREATE VIEW sales.customer_sales_filtered AS
SELECT *
FROM sales.transactions
WHERE country = current_user_country();

-- Column masking
CREATE FUNCTION mask_email(email STRING)
RETURNS STRING
RETURN CONCAT(SUBSTRING(email, 1, 3), '***@', SPLIT(email, '@')[1]);

-- Use in view
CREATE VIEW customers_masked AS
SELECT
    customer_id,
    first_name,
    last_name,
    mask_email(email) as email
FROM customers;
```

---

## Common Query Patterns

### Basic Queries

```sql
-- Select with filtering
SELECT
    customer_id,
    first_name,
    last_name,
    email
FROM customers
WHERE country = 'USA'
  AND is_active = true
  AND registration_date >= '2023-01-01';

-- Select with sorting
SELECT *
FROM sales
ORDER BY transaction_date DESC, amount DESC
LIMIT 100;

-- Select distinct values
SELECT DISTINCT country
FROM customers
ORDER BY country;

-- Count records
SELECT COUNT(*) as total_customers
FROM customers
WHERE is_active = true;
```

### Filtering with IN and NOT IN

```sql
-- Using IN
SELECT *
FROM sales
WHERE customer_id IN (1, 2, 3, 4, 5);

-- Using IN with subquery
SELECT *
FROM sales
WHERE customer_id IN (
    SELECT customer_id
    FROM customers
    WHERE country = 'USA'
);

-- Using NOT IN
SELECT *
FROM customers
WHERE customer_id NOT IN (
    SELECT DISTINCT customer_id
    FROM sales
);
```

### CASE Statements

```sql
-- Simple CASE
SELECT
    customer_id,
    first_name,
    last_name,
    CASE
        WHEN loyalty_points >= 1000 THEN 'Gold'
        WHEN loyalty_points >= 500 THEN 'Silver'
        WHEN loyalty_points >= 100 THEN 'Bronze'
        ELSE 'Standard'
    END as loyalty_tier
FROM customers;

-- CASE in aggregation
SELECT
    country,
    COUNT(*) as total_customers,
    COUNT(CASE WHEN is_active = true THEN 1 END) as active_customers,
    COUNT(CASE WHEN is_active = false THEN 1 END) as inactive_customers
FROM customers
GROUP BY country;
```

### Subqueries

```sql
-- Subquery in WHERE
SELECT *
FROM customers
WHERE customer_id IN (
    SELECT customer_id
    FROM sales
    GROUP BY customer_id
    HAVING SUM(amount) > 10000
);

-- Correlated subquery
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    (
        SELECT SUM(amount)
        FROM sales s
        WHERE s.customer_id = c.customer_id
    ) as total_spent
FROM customers c;

-- Subquery in FROM
SELECT
    country,
    AVG(order_count) as avg_orders_per_customer
FROM (
    SELECT
        c.country,
        c.customer_id,
        COUNT(s.transaction_id) as order_count
    FROM customers c
    LEFT JOIN sales s ON c.customer_id = s.customer_id
    GROUP BY c.country, c.customer_id
)
GROUP BY country;
```

### Common Table Expressions (CTEs)

```sql
-- Single CTE
WITH active_customers AS (
    SELECT customer_id, first_name, last_name, country
    FROM customers
    WHERE is_active = true
)
SELECT
    country,
    COUNT(*) as customer_count
FROM active_customers
GROUP BY country;

-- Multiple CTEs
WITH
customer_orders AS (
    SELECT
        customer_id,
        COUNT(*) as order_count,
        SUM(amount) as total_spent
    FROM sales
    GROUP BY customer_id
),
customer_segments AS (
    SELECT
        customer_id,
        CASE
            WHEN total_spent >= 10000 THEN 'High Value'
            WHEN total_spent >= 5000 THEN 'Medium Value'
            ELSE 'Low Value'
        END as segment
    FROM customer_orders
)
SELECT
    c.first_name,
    c.last_name,
    co.order_count,
    co.total_spent,
    cs.segment
FROM customers c
JOIN customer_orders co ON c.customer_id = co.customer_id
JOIN customer_segments cs ON c.customer_id = cs.customer_id
ORDER BY co.total_spent DESC;
```

---

## Window Functions

### Row Number

```sql
-- Assign row numbers within partition
SELECT
    customer_id,
    transaction_date,
    amount,
    ROW_NUMBER() OVER (
        PARTITION BY customer_id
        ORDER BY transaction_date DESC
    ) as transaction_rank
FROM sales;

-- Get most recent transaction per customer
WITH ranked_transactions AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY transaction_date DESC
        ) as rn
    FROM sales
)
SELECT *
FROM ranked_transactions
WHERE rn = 1;
```

### Rank and Dense Rank

```sql
-- Rank customers by total spending
SELECT
    customer_id,
    SUM(amount) as total_spent,
    RANK() OVER (ORDER BY SUM(amount) DESC) as rank,
    DENSE_RANK() OVER (ORDER BY SUM(amount) DESC) as dense_rank
FROM sales
GROUP BY customer_id;
```

### Running Totals

```sql
-- Calculate running total
SELECT
    transaction_date,
    amount,
    SUM(amount) OVER (
        ORDER BY transaction_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) as running_total
FROM sales
ORDER BY transaction_date;

-- Running total by customer
SELECT
    customer_id,
    transaction_date,
    amount,
    SUM(amount) OVER (
        PARTITION BY customer_id
        ORDER BY transaction_date
    ) as customer_running_total
FROM sales;
```

### Moving Averages

```sql
-- 7-day moving average
SELECT
    transaction_date,
    SUM(amount) as daily_total,
    AVG(SUM(amount)) OVER (
        ORDER BY transaction_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as moving_avg_7day
FROM sales
GROUP BY transaction_date
ORDER BY transaction_date;
```

### Lag and Lead

```sql
-- Compare with previous period
SELECT
    transaction_date,
    SUM(amount) as daily_total,
    LAG(SUM(amount), 1) OVER (ORDER BY transaction_date) as previous_day,
    SUM(amount) - LAG(SUM(amount), 1) OVER (ORDER BY transaction_date) as day_over_day_change
FROM sales
GROUP BY transaction_date
ORDER BY transaction_date;

-- Look ahead to next value
SELECT
    customer_id,
    transaction_date,
    amount,
    LEAD(transaction_date, 1) OVER (
        PARTITION BY customer_id
        ORDER BY transaction_date
    ) as next_transaction_date
FROM sales;
```

---

## Aggregations

### Basic Aggregations

```sql
-- Multiple aggregations
SELECT
    COUNT(*) as total_transactions,
    COUNT(DISTINCT customer_id) as unique_customers,
    SUM(amount) as total_revenue,
    AVG(amount) as average_transaction,
    MIN(amount) as min_transaction,
    MAX(amount) as max_transaction,
    STDDEV(amount) as stddev_transaction
FROM sales;
```

### GROUP BY with Multiple Dimensions

```sql
-- Group by multiple columns
SELECT
    country,
    year,
    month,
    COUNT(*) as transaction_count,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_transaction
FROM sales s
JOIN customers c ON s.customer_id = c.customer_id
GROUP BY country, year, month
ORDER BY country, year, month;
```

### HAVING Clause

```sql
-- Filter aggregated results
SELECT
    customer_id,
    COUNT(*) as order_count,
    SUM(amount) as total_spent
FROM sales
GROUP BY customer_id
HAVING SUM(amount) > 10000
ORDER BY total_spent DESC;
```

### ROLLUP and CUBE

```sql
-- ROLLUP for hierarchical totals
SELECT
    country,
    year,
    month,
    SUM(amount) as total_revenue
FROM sales s
JOIN customers c ON s.customer_id = c.customer_id
GROUP BY ROLLUP (country, year, month)
ORDER BY country, year, month;

-- CUBE for all combinations
SELECT
    country,
    year,
    SUM(amount) as total_revenue
FROM sales s
JOIN customers c ON s.customer_id = c.customer_id
GROUP BY CUBE (country, year)
ORDER BY country, year;
```

### GROUPING SETS

```sql
-- Specific grouping combinations
SELECT
    country,
    year,
    month,
    SUM(amount) as total_revenue
FROM sales s
JOIN customers c ON s.customer_id = c.customer_id
GROUP BY GROUPING SETS (
    (country, year, month),
    (country, year),
    (country),
    ()
)
ORDER BY country, year, month;
```

---

## Joins

### Inner Join

```sql
-- Basic inner join
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    s.transaction_id,
    s.amount,
    s.transaction_date
FROM customers c
INNER JOIN sales s ON c.customer_id = s.customer_id;
```

### Left Join

```sql
-- Left join to include all customers
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    COUNT(s.transaction_id) as order_count,
    COALESCE(SUM(s.amount), 0) as total_spent
FROM customers c
LEFT JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name;
```

### Multiple Joins

```sql
-- Join multiple tables
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    s.transaction_id,
    s.amount,
    p.product_name,
    p.category
FROM customers c
INNER JOIN sales s ON c.customer_id = s.customer_id
INNER JOIN products p ON s.product_id = p.product_id
WHERE s.transaction_date >= '2024-01-01';
```

### Self Join

```sql
-- Find customers from same country
SELECT
    c1.customer_id as customer1_id,
    c1.first_name as customer1_name,
    c2.customer_id as customer2_id,
    c2.first_name as customer2_name,
    c1.country
FROM customers c1
INNER JOIN customers c2
    ON c1.country = c2.country
    AND c1.customer_id < c2.customer_id;
```

### Cross Join

```sql
-- Generate all combinations
SELECT
    d.date,
    p.product_id,
    p.product_name
FROM date_dimension d
CROSS JOIN products p
WHERE d.date BETWEEN '2024-01-01' AND '2024-12-31';
```

---

## Performance Optimization

### Partition Pruning

```sql
-- Query with partition filters (fast)
SELECT *
FROM sales
WHERE year = 2024
  AND month = 1
  AND amount > 100;

-- Avoid functions on partition columns
-- Bad: WHERE YEAR(transaction_date) = 2024
-- Good: WHERE transaction_date >= '2024-01-01' AND transaction_date < '2025-01-01'
```

### Predicate Pushdown

```sql
-- Filter early for better performance
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    s.total_spent
FROM customers c
INNER JOIN (
    SELECT
        customer_id,
        SUM(amount) as total_spent
    FROM sales
    WHERE transaction_date >= '2024-01-01'  -- Filter early
    GROUP BY customer_id
) s ON c.customer_id = s.customer_id
WHERE c.is_active = true;  -- Filter early
```

### Broadcast Joins

```sql
-- Hint for small dimension tables
SELECT /*+ BROADCAST(c) */
    c.customer_id,
    c.first_name,
    s.transaction_id,
    s.amount
FROM customers c
INNER JOIN sales s ON c.customer_id = s.customer_id;
```

### Caching

```sql
-- Cache frequently accessed table
CACHE TABLE customers;

-- Lazy cache (cache on first access)
CACHE LAZY TABLE sales;

-- Remove from cache
UNCACHE TABLE customers;

-- Clear all caches
CLEAR CACHE;
```

### Statistics

```sql
-- Compute table statistics
ANALYZE TABLE sales COMPUTE STATISTICS;

-- Compute column statistics
ANALYZE TABLE sales COMPUTE STATISTICS FOR COLUMNS customer_id, amount;

-- Show table statistics
DESCRIBE EXTENDED sales;
```

---

## Related Documentation

- [SQL Reference Overview](../sql/overview.md)
- [Delta Lake SDK](../sdk/delta-lake.md)
- [Quick Start Guide](../getting-started/quickstart.md)
- [Performance Best Practices](../best-practices/performance.md)

## Additional Resources

- [Databricks SQL Reference](https://docs.databricks.com/sql/language-manual/index.html)
- [Delta Lake SQL Commands](https://docs.delta.io/latest/delta-batch.html)
- [SQL Performance Tuning](https://docs.databricks.com/optimizations/index.html)
