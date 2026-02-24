# Databricks Connect Setup Guide

## Overview

Databricks Connect is a client library that allows you to connect your favorite IDE (PyCharm, VS Code, IntelliJ, etc.), notebook server (Zeppelin, Jupyter), and other custom applications to Databricks clusters. This enables you to write and execute Spark code locally while leveraging the power of Databricks compute resources.

## Table of Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [IDE Integration](#ide-integration)
- [Testing Strategies](#testing-strategies)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Architecture

### How Databricks Connect Works

```
┌─────────────────────────────────────────────────────────────┐
│                    Local Development Environment            │
│                                                             │
│  ┌──────────────┐      ┌─────────────────────────────┐   │
│  │   IDE/Editor │──────│  Databricks Connect Client  │   │
│  │   (VS Code)  │      │    (Python Library)         │   │
│  └──────────────┘      └─────────────┬───────────────┘   │
│                                       │                     │
└───────────────────────────────────────┼─────────────────────┘
                                        │ HTTPS/gRPC
                                        │
┌───────────────────────────────────────▼─────────────────────┐
│                    Databricks Workspace                     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            Databricks Cluster                        │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │  │
│  │  │  Executor  │  │  Executor  │  │  Executor  │    │  │
│  │  └────────────┘  └────────────┘  └────────────┘    │  │
│  │                                                      │  │
│  │  Data Processing, Execution, and Storage            │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### Key Features

- **Local Development** - Write and debug Spark code in your IDE
- **Remote Execution** - Code executes on Databricks clusters
- **IDE Integration** - Works with PyCharm, VS Code, IntelliJ, Jupyter
- **Testing Support** - Unit test Spark code locally
- **Library Management** - Use local Python libraries with remote execution

---

## Prerequisites

### System Requirements

- **Python Version**: 3.8, 3.9, 3.10, or 3.11
- **Operating System**: Windows, macOS, or Linux
- **Databricks Runtime**: DBR 13.0+ recommended
- **Cluster Access**: Permissions to create and use clusters

### Databricks Requirements

```python
# Cluster configuration for Databricks Connect
cluster_config = {
    "spark_version": "13.3.x-scala2.12",  # DBR 13.0+
    "node_type_id": "i3.xlarge",
    "num_workers": 2,
    "spark_conf": {
        "spark.databricks.service.server.enabled": "true",
        "spark.databricks.repl.allowedLanguages": "python,sql"
    }
}
```

### Important Limitations

- Cannot use Databricks utilities (`dbutils`) - most features unavailable
- No support for streaming jobs (use Databricks notebooks instead)
- Limited support for Scala and R (Python only for v13.0+)
- Cannot run shell commands or access local file systems from cluster

---

## Installation

### Step 1: Install Databricks Connect

```bash
# Install Databricks Connect for DBR 13.0+
pip install databricks-connect

# Or install for specific Databricks Runtime version
pip install databricks-connect==13.3.*

# Verify installation
databricks-connect --version
```

### Step 2: Configure Environment Variables

**Option 1: Environment Variables**

```bash
# Linux/macOS
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="dapiXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
export DATABRICKS_CLUSTER_ID="1234-567890-abc123"

# Windows (PowerShell)
$env:DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
$env:DATABRICKS_TOKEN="dapiXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
$env:DATABRICKS_CLUSTER_ID="1234-567890-abc123"

# Windows (CMD)
set DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
set DATABRICKS_TOKEN=dapiXXXXXXXXXXXXXXXXXXXXXXXXXXXX
set DATABRICKS_CLUSTER_ID=1234-567890-abc123
```

**Option 2: Configuration File**

Create `~/.databrickscfg`:

```ini
[DEFAULT]
host = https://your-workspace.cloud.databricks.com
token = dapiXXXXXXXXXXXXXXXXXXXXXXXXXXXX
cluster_id = 1234-567890-abc123

[dev]
host = https://dev-workspace.cloud.databricks.com
token = dapiYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
cluster_id = 5678-901234-def456

[prod]
host = https://prod-workspace.cloud.databricks.com
token = dapiZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
cluster_id = 9012-345678-ghi789
```

### Step 3: Verify Connection

```python
# test_connection.py
from databricks.connect import DatabricksSession

# Create session
spark = DatabricksSession.builder.getOrCreate()

# Test connection
df = spark.range(10)
print(f"Row count: {df.count()}")
print("Connection successful!")
```

Run the test:

```bash
python test_connection.py
```

---

## Configuration

### Basic Configuration

```python
# basic_config.py
from databricks.connect import DatabricksSession
from pyspark.sql import SparkSession

# Option 1: Using environment variables (recommended)
spark = DatabricksSession.builder.getOrCreate()

# Option 2: Explicit configuration
spark = (DatabricksSession.builder
    .remote(
        host="https://your-workspace.cloud.databricks.com",
        token="dapiXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        cluster_id="1234-567890-abc123"
    )
    .getOrCreate()
)

# Option 3: Using profile from .databrickscfg
spark = (DatabricksSession.builder
    .profile("dev")  # Uses [dev] section from config file
    .getOrCreate()
)
```

### Advanced Configuration

```python
# advanced_config.py
from databricks.connect import DatabricksSession

spark = (DatabricksSession.builder
    .remote(
        host="https://your-workspace.cloud.databricks.com",
        token="dapiXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        cluster_id="1234-567890-abc123"
    )
    # Set Spark configurations
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
    .config("spark.databricks.delta.optimizeWrite.enabled", "true")
    .appName("MyLocalApp")
    .getOrCreate()
)

# View current configuration
print(spark.sparkContext.getConf().getAll())
```

### Using Different Profiles

```python
# multi_environment.py
import os
from databricks.connect import DatabricksSession

def get_spark_session(environment="dev"):
    """Get Spark session for different environments"""

    # Set profile based on environment
    spark = (DatabricksSession.builder
        .profile(environment)
        .getOrCreate()
    )

    print(f"Connected to {environment} environment")
    return spark

# Use in development
spark_dev = get_spark_session("dev")

# Use in production
spark_prod = get_spark_session("prod")
```

---

## Usage Examples

### Basic Data Operations

```python
# basic_operations.py
from databricks.connect import DatabricksSession
from pyspark.sql.functions import *

spark = DatabricksSession.builder.getOrCreate()

# Create DataFrame
data = [
    ("Alice", 34, "Engineering"),
    ("Bob", 45, "Sales"),
    ("Charlie", 28, "Marketing"),
    ("Diana", 32, "Engineering")
]

df = spark.createDataFrame(data, ["name", "age", "department"])

# Basic operations
print("Count:", df.count())
df.show()

# Aggregations
dept_stats = (df
    .groupBy("department")
    .agg(
        count("*").alias("employee_count"),
        avg("age").alias("avg_age")
    )
)

dept_stats.show()
```

### Reading from Delta Lake

```python
# read_delta.py
from databricks.connect import DatabricksSession

spark = DatabricksSession.builder.getOrCreate()

# Read Delta table
customers_df = spark.table("main.sales.customers")

# Or read from path
orders_df = (spark
    .read
    .format("delta")
    .load("/mnt/data/orders")
)

# Query data
high_value_customers = (customers_df
    .filter(col("lifetime_value") > 10000)
    .orderBy(col("lifetime_value").desc())
)

high_value_customers.show()
```

### Writing to Delta Lake

```python
# write_delta.py
from databricks.connect import DatabricksSession
from pyspark.sql.functions import *

spark = DatabricksSession.builder.getOrCreate()

# Create sample data
data = [
    (1, "Product A", 100.0, "2024-01-15"),
    (2, "Product B", 150.0, "2024-01-15"),
    (3, "Product C", 200.0, "2024-01-16")
]

df = spark.createDataFrame(data, ["id", "product", "price", "date"])

# Write to Delta table
(df
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("main.sales.products")
)

print("Data written successfully!")
```

### SQL Queries

```python
# sql_queries.py
from databricks.connect import DatabricksSession

spark = DatabricksSession.builder.getOrCreate()

# Execute SQL query
result = spark.sql("""
    SELECT
        department,
        COUNT(*) as employee_count,
        AVG(salary) as avg_salary
    FROM main.hr.employees
    WHERE active = true
    GROUP BY department
    ORDER BY avg_salary DESC
""")

result.show()

# Use SQL with temp views
df = spark.table("main.sales.orders")
df.createOrReplaceTempView("orders_temp")

monthly_sales = spark.sql("""
    SELECT
        DATE_TRUNC('month', order_date) as month,
        SUM(order_amount) as total_sales
    FROM orders_temp
    GROUP BY month
    ORDER BY month
""")

monthly_sales.show()
```

### Complex Transformations

```python
# complex_transformations.py
from databricks.connect import DatabricksSession
from pyspark.sql.functions import *
from pyspark.sql.window import Window

spark = DatabricksSession.builder.getOrCreate()

# Read data
sales_df = spark.table("main.sales.transactions")

# Complex transformation pipeline
result = (sales_df
    # Add derived columns
    .withColumn("sale_month", date_trunc("month", col("sale_date")))
    .withColumn("sale_year", year(col("sale_date")))

    # Window function for running total
    .withColumn("running_total",
        sum("amount").over(
            Window.partitionBy("customer_id")
            .orderBy("sale_date")
            .rowsBetween(Window.unboundedPreceding, Window.currentRow)
        )
    )

    # Rank by sales within each month
    .withColumn("monthly_rank",
        dense_rank().over(
            Window.partitionBy("sale_month")
            .orderBy(col("amount").desc())
        )
    )

    # Filter top performers
    .filter(col("monthly_rank") <= 10)
)

result.show()
```

### Working with UDFs

```python
# udfs.py
from databricks.connect import DatabricksSession
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType, IntegerType

spark = DatabricksSession.builder.getOrCreate()

# Define UDF
@udf(returnType=StringType())
def categorize_amount(amount):
    """Categorize transaction amounts"""
    if amount < 100:
        return "Small"
    elif amount < 1000:
        return "Medium"
    elif amount < 10000:
        return "Large"
    else:
        return "Extra Large"

# Register UDF
spark.udf.register("categorize_amount", categorize_amount)

# Use UDF in DataFrame
df = spark.table("main.sales.transactions")
result = df.withColumn("category", categorize_amount(col("amount")))
result.show()

# Use UDF in SQL
spark.sql("""
    SELECT
        transaction_id,
        amount,
        categorize_amount(amount) as category
    FROM main.sales.transactions
""").show()
```

---

## IDE Integration

### VS Code Setup

**1. Install Python Extension**
```bash
# Install VS Code Python extension
code --install-extension ms-python.python
```

**2. Configure Python Environment**

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.envFile": "${workspaceFolder}/.env",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests"
    ]
}
```

**3. Create Environment File**

Create `.env`:

```bash
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapiXXXXXXXXXXXXXXXXXXXXXXXXXXXX
DATABRICKS_CLUSTER_ID=1234-567890-abc123
```

**4. Create Launch Configuration**

Create `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "envFile": "${workspaceFolder}/.env"
        }
    ]
}
```

### PyCharm Setup

**1. Configure Python Interpreter**

1. Go to `File` → `Settings` → `Project` → `Python Interpreter`
2. Add new environment or select existing
3. Install `databricks-connect` package

**2. Set Environment Variables**

1. Go to `Run` → `Edit Configurations`
2. Add environment variables:
   - `DATABRICKS_HOST`
   - `DATABRICKS_TOKEN`
   - `DATABRICKS_CLUSTER_ID`

**3. Configure Run Configuration**

```python
# Create run configuration with environment variables
# File → Settings → Build, Execution, Deployment → Console → Python Console
```

### Jupyter Notebook Setup

```python
# notebook_setup.ipynb

# Cell 1: Install and import
!pip install databricks-connect

from databricks.connect import DatabricksSession
from pyspark.sql.functions import *

# Cell 2: Create session
spark = DatabricksSession.builder.getOrCreate()

# Cell 3: Test connection
print(f"Spark version: {spark.version}")
spark.range(10).show()

# Cell 4: Your analysis
df = spark.table("main.sales.customers")
df.show()
```

---

## Testing Strategies

### Unit Testing

```python
# tests/test_transformations.py
import pytest
from databricks.connect import DatabricksSession
from pyspark.sql.functions import col

@pytest.fixture(scope="session")
def spark():
    """Create Spark session for tests"""
    return DatabricksSession.builder.getOrCreate()

def test_data_transformation(spark):
    """Test data transformation logic"""
    # Create test data
    test_data = [
        (1, "Alice", 1000),
        (2, "Bob", 2000),
        (3, "Charlie", 3000)
    ]

    df = spark.createDataFrame(test_data, ["id", "name", "amount"])

    # Apply transformation
    result = df.filter(col("amount") > 1500)

    # Assert results
    assert result.count() == 2
    assert result.filter(col("name") == "Bob").count() == 1

def test_aggregation(spark):
    """Test aggregation logic"""
    test_data = [
        ("Engineering", 100),
        ("Engineering", 200),
        ("Sales", 150),
        ("Sales", 250)
    ]

    df = spark.createDataFrame(test_data, ["department", "amount"])

    # Aggregate
    result = (df
        .groupBy("department")
        .sum("amount")
        .withColumnRenamed("sum(amount)", "total")
    )

    # Verify
    eng_total = result.filter(col("department") == "Engineering").first()["total"]
    assert eng_total == 300
```

### Integration Testing

```python
# tests/test_integration.py
import pytest
from databricks.connect import DatabricksSession
from datetime import datetime

@pytest.fixture(scope="module")
def spark():
    return DatabricksSession.builder.getOrCreate()

def test_read_write_delta(spark):
    """Test reading and writing to Delta Lake"""

    # Create test table
    test_table = f"test.integration.test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Write data
    data = [(1, "test"), (2, "data")]
    df = spark.createDataFrame(data, ["id", "value"])
    df.write.format("delta").mode("overwrite").saveAsTable(test_table)

    # Read data back
    result = spark.table(test_table)

    # Verify
    assert result.count() == 2
    assert result.filter(col("id") == 1).first()["value"] == "test"

    # Cleanup
    spark.sql(f"DROP TABLE {test_table}")

def test_sql_query(spark):
    """Test SQL query execution"""

    result = spark.sql("SELECT 1 + 1 as result")
    assert result.first()["result"] == 2
```

### Running Tests

```bash
# Install pytest
pip install pytest

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_transformations.py

# Run with coverage
pip install pytest-cov
pytest --cov=src tests/

# Run with verbose output
pytest -v tests/
```

---

## Best Practices

### 1. Connection Management

```python
# connection_manager.py
from databricks.connect import DatabricksSession
from functools import lru_cache

@lru_cache(maxsize=1)
def get_spark_session(profile="dev"):
    """Get or create cached Spark session"""
    return (DatabricksSession.builder
        .profile(profile)
        .getOrCreate()
    )

# Use in your code
spark = get_spark_session("dev")
```

### 2. Configuration Management

```python
# config.py
import os
from dataclasses import dataclass

@dataclass
class DatabricksConfig:
    """Databricks configuration"""
    host: str
    token: str
    cluster_id: str

    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        return cls(
            host=os.getenv("DATABRICKS_HOST"),
            token=os.getenv("DATABRICKS_TOKEN"),
            cluster_id=os.getenv("DATABRICKS_CLUSTER_ID")
        )

    def validate(self):
        """Validate configuration"""
        if not all([self.host, self.token, self.cluster_id]):
            raise ValueError("Missing required configuration")
        return True

# Usage
config = DatabricksConfig.from_env()
config.validate()
```

### 3. Error Handling

```python
# error_handling.py
from databricks.connect import DatabricksSession
from pyspark.sql.utils import AnalysisException
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_table_read(spark, table_name):
    """Safely read table with error handling"""
    try:
        df = spark.table(table_name)
        logger.info(f"Successfully read table: {table_name}")
        return df
    except AnalysisException as e:
        logger.error(f"Table not found: {table_name}")
        logger.error(str(e))
        return None
    except Exception as e:
        logger.error(f"Unexpected error reading {table_name}: {str(e)}")
        raise

# Usage
spark = DatabricksSession.builder.getOrCreate()
df = safe_table_read(spark, "main.sales.orders")
```

### 4. Reusable Transformations

```python
# transformations.py
from pyspark.sql import DataFrame
from pyspark.sql.functions import *

def add_audit_columns(df: DataFrame) -> DataFrame:
    """Add standard audit columns"""
    return (df
        .withColumn("created_at", current_timestamp())
        .withColumn("created_by", lit("databricks-connect"))
    )

def clean_string_columns(df: DataFrame, columns: list) -> DataFrame:
    """Clean and standardize string columns"""
    result = df
    for col_name in columns:
        result = result.withColumn(
            col_name,
            trim(lower(col(col_name)))
        )
    return result

# Usage
from transformations import add_audit_columns, clean_string_columns

df = spark.table("raw.customers")
df = clean_string_columns(df, ["email", "phone"])
df = add_audit_columns(df)
```

### 5. Logging and Monitoring

```python
# logging_setup.py
import logging
from datetime import datetime

def setup_logging(log_file="app.log"):
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

# Use in your application
setup_logging()
logger = logging.getLogger(__name__)

def process_data(spark, table_name):
    """Process data with logging"""
    logger.info(f"Starting data processing for {table_name}")
    start_time = datetime.now()

    try:
        df = spark.table(table_name)
        row_count = df.count()
        logger.info(f"Loaded {row_count} rows from {table_name}")

        # Process data...

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Processing completed in {duration:.2f} seconds")

    except Exception as e:
        logger.error(f"Error processing {table_name}: {str(e)}", exc_info=True)
        raise
```

---

## Troubleshooting

### Common Issues

#### 1. Connection Refused

```bash
# Error: Connection refused
# Solution: Check cluster is running and cluster ID is correct

# Verify cluster status
databricks clusters get --cluster-id 1234-567890-abc123

# Check cluster is RUNNING state
# Restart cluster if needed
databricks clusters start --cluster-id 1234-567890-abc123
```

#### 2. Authentication Errors

```python
# Error: Invalid token
# Solution: Generate new token and update configuration

# Verify token in .databrickscfg
cat ~/.databrickscfg

# Or check environment variable
echo $DATABRICKS_TOKEN

# Generate new token from Databricks UI:
# User Settings → Access Tokens → Generate New Token
```

#### 3. Version Mismatch

```bash
# Error: Version mismatch between client and cluster
# Solution: Install matching version

# Check cluster Spark version
databricks clusters get --cluster-id 1234-567890-abc123 | grep spark_version

# Install matching Databricks Connect version
pip install databricks-connect==13.3.*
```

#### 4. Module Import Errors

```python
# Error: No module named 'databricks.connect'
# Solution: Install in correct Python environment

# Check Python path
python -c "import sys; print(sys.executable)"

# Install in correct environment
/path/to/python -m pip install databricks-connect

# Verify installation
python -c "from databricks.connect import DatabricksSession; print('OK')"
```

#### 5. Performance Issues

```python
# Issue: Slow query execution
# Solution: Optimize configuration

spark = (DatabricksSession.builder
    # Increase parallelism
    .config("spark.sql.shuffle.partitions", "200")

    # Enable adaptive query execution
    .config("spark.sql.adaptive.enabled", "true")

    # Enable optimization
    .config("spark.databricks.delta.optimizeWrite.enabled", "true")
    .config("spark.databricks.delta.autoCompact.enabled", "true")

    .getOrCreate()
)
```

### Debug Mode

```python
# enable_debug.py
import logging
from databricks.connect import DatabricksSession

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("databricks.connect")
logger.setLevel(logging.DEBUG)

# Create session with debug info
spark = DatabricksSession.builder.getOrCreate()

# View configuration
print("Spark Configuration:")
for conf in spark.sparkContext.getConf().getAll():
    print(f"  {conf[0]}: {conf[1]}")
```

### Connectivity Test Script

```python
# test_connectivity.py
import sys
from databricks.connect import DatabricksSession

def test_connection():
    """Comprehensive connection test"""

    print("Testing Databricks Connect...")

    try:
        # Create session
        print("1. Creating Spark session...")
        spark = DatabricksSession.builder.getOrCreate()
        print("   ✓ Session created")

        # Test basic operation
        print("2. Testing basic operation...")
        result = spark.range(10).count()
        assert result == 10
        print(f"   ✓ Basic operation successful (count={result})")

        # Test SQL
        print("3. Testing SQL execution...")
        df = spark.sql("SELECT 1 + 1 as result")
        assert df.first()["result"] == 2
        print("   ✓ SQL execution successful")

        # Test table access
        print("4. Testing table access...")
        databases = spark.sql("SHOW DATABASES")
        db_count = databases.count()
        print(f"   ✓ Table access successful (found {db_count} databases)")

        print("\n✓ All tests passed!")
        return True

    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
```

---

## Security Best Practices

### 1. Token Management

```python
# Never hardcode tokens
# BAD
spark = DatabricksSession.builder.remote(
    host="https://...",
    token="dapi12345..."  # Never do this!
)

# GOOD - Use environment variables
import os
spark = DatabricksSession.builder.remote(
    host=os.getenv("DATABRICKS_HOST"),
    token=os.getenv("DATABRICKS_TOKEN"),
    cluster_id=os.getenv("DATABRICKS_CLUSTER_ID")
)
```

### 2. Credential Storage

```bash
# Store credentials securely
# Use .databrickscfg with restrictive permissions
chmod 600 ~/.databrickscfg

# Add .databrickscfg and .env to .gitignore
echo ".databrickscfg" >> .gitignore
echo ".env" >> .gitignore
```

### 3. Token Rotation

```python
# token_rotation.py
from datetime import datetime, timedelta
import os

def check_token_expiry(token_created_date):
    """Check if token should be rotated"""

    # Rotate tokens every 90 days
    expiry_days = 90
    days_old = (datetime.now() - token_created_date).days

    if days_old >= expiry_days:
        print(f"⚠ Token is {days_old} days old. Consider rotating.")
        return True

    return False
```

---

## Performance Optimization

### 1. Caching Strategy

```python
# Use caching for frequently accessed data
df = spark.table("large_table")
df.cache()

# Use data
result1 = df.filter(col("status") == "active").count()
result2 = df.groupBy("category").count()

# Unpersist when done
df.unpersist()
```

### 2. Broadcast Joins

```python
# Broadcast small dimension tables
from pyspark.sql.functions import broadcast

large_df = spark.table("fact.sales")
small_df = spark.table("dim.products")

# Broadcast the small table
result = large_df.join(broadcast(small_df), "product_id")
```

### 3. Partition Pruning

```python
# Use partition filters to reduce data scanned
df = (spark.table("partitioned_table")
    .filter(col("year") == 2024)
    .filter(col("month") == 1)
)
```

---

## References

- [Databricks Connect Documentation](https://docs.databricks.com/dev-tools/databricks-connect.html)
- [Databricks Connect Python API](https://docs.databricks.com/dev-tools/databricks-connect-ref.html)
- [PySpark API Reference](https://spark.apache.org/docs/latest/api/python/)
- [Delta Lake Documentation](https://docs.delta.io/)

---

**Quick Start Checklist:**
- [ ] Install `databricks-connect`
- [ ] Configure `.databrickscfg` or environment variables
- [ ] Verify cluster is running
- [ ] Test connection with sample script
- [ ] Configure IDE integration
- [ ] Set up version control (.gitignore)
- [ ] Implement error handling
- [ ] Add logging
- [ ] Create unit tests
- [ ] Document your setup
