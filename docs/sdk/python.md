# Databricks SDK for Python

## Overview

The Databricks SDK for Python provides a high-level, Pythonic interface to interact with Databricks REST APIs. It simplifies common operations like cluster management, job scheduling, workspace operations, and more.

## Installation

### Using pip

```bash
pip install databricks-sdk
```

### Using conda

```bash
conda install -c databricks databricks-sdk
```

### With Optional Dependencies

```bash
# Install with all optional dependencies
pip install databricks-sdk[all]

# Install for development
pip install databricks-sdk[dev]
```

### Verify Installation

```python
import databricks.sdk
print(databricks.sdk.__version__)
```

## Quick Start

### Basic Usage

```python
from databricks.sdk import WorkspaceClient

# Initialize client (uses environment variables or config file)
client = WorkspaceClient()

# List clusters
for cluster in client.clusters.list():
    print(f"Cluster: {cluster.cluster_name} ({cluster.state})")
```

### With Explicit Configuration

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient(
    host="https://<workspace>.cloud.databricks.com",
    token="dapi..."
)

# Get current user
user = client.current_user.me()
print(f"Logged in as: {user.user_name}")
```

## Configuration

### Environment Variables

The SDK automatically reads from environment variables:

```bash
export DATABRICKS_HOST="https://<workspace>.cloud.databricks.com"
export DATABRICKS_TOKEN="dapi..."
```

```python
from databricks.sdk import WorkspaceClient

# Automatically uses environment variables
client = WorkspaceClient()
```

### Configuration File

Create `~/.databrickscfg`:

```ini
[DEFAULT]
host = https://<workspace>.cloud.databricks.com
token = dapi...

[production]
host = https://prod-workspace.cloud.databricks.com
token = dapi...

[development]
host = https://dev-workspace.cloud.databricks.com
token = dapi...
```

```python
from databricks.sdk import WorkspaceClient

# Use default profile
client = WorkspaceClient()

# Use specific profile
client = WorkspaceClient(profile="production")
```

### Direct Configuration

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient(
    host="https://<workspace>.cloud.databricks.com",
    token="dapi...",
    # Optional parameters
    cluster_id="1234-567890-abc123",
    warehouse_id="abc123def456"
)
```

## Authentication Methods

### Personal Access Token

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient(
    host="https://<workspace>.cloud.databricks.com",
    token="dapi..."
)
```

### OAuth 2.0

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient(
    host="https://<workspace>.cloud.databricks.com",
    client_id="your-client-id",
    client_secret="your-client-secret"
)
```

### Azure Active Directory

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient(
    host="https://<workspace>.azuredatabricks.net",
    azure_tenant_id="your-tenant-id",
    azure_client_id="your-client-id",
    azure_client_secret="your-client-secret"
)
```

### Azure Managed Identity

```python
from databricks.sdk import WorkspaceClient

# System-assigned managed identity
client = WorkspaceClient(
    host="https://<workspace>.azuredatabricks.net",
    azure_use_msi=True
)

# User-assigned managed identity
client = WorkspaceClient(
    host="https://<workspace>.azuredatabricks.net",
    azure_use_msi=True,
    azure_client_id="managed-identity-client-id"
)
```

### AWS IAM

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient(
    host="https://<workspace>.cloud.databricks.com",
    aws_profile="your-aws-profile"
)
```

## Core Clients

### WorkspaceClient

Main client for workspace-level operations.

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# Access services
client.clusters        # Cluster management
client.jobs            # Job operations
client.workspace       # Workspace operations
client.dbfs            # DBFS operations
client.secrets         # Secrets management
client.repos           # Git repo integration
client.pipelines       # Delta Live Tables
client.catalogs        # Unity Catalog
client.schemas         # Schema management
client.tables          # Table operations
```

### AccountClient

Client for account-level operations (admin only).

```python
from databricks.sdk import AccountClient

client = AccountClient(
    host="https://accounts.cloud.databricks.com",
    account_id="your-account-id",
    client_id="your-client-id",
    client_secret="your-client-secret"
)

# Access account services
client.workspaces      # Workspace management
client.users           # User management
client.service_principals  # Service principal management
```

## Service Modules

### Clusters

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import compute

client = WorkspaceClient()

# Create cluster
cluster = client.clusters.create(
    cluster_name="my-cluster",
    spark_version="13.3.x-scala2.12",
    node_type_id="i3.xlarge",
    num_workers=2,
    autotermination_minutes=30
)

print(f"Cluster ID: {cluster.cluster_id}")

# Get cluster
cluster_info = client.clusters.get(cluster_id=cluster.cluster_id)
print(f"State: {cluster_info.state}")

# List clusters
for cluster in client.clusters.list():
    print(f"{cluster.cluster_name}: {cluster.state}")

# Start cluster
client.clusters.start(cluster_id=cluster.cluster_id)

# Wait for cluster to be running
client.clusters.wait_get_cluster_running(cluster_id=cluster.cluster_id)

# Terminate cluster
client.clusters.delete(cluster_id=cluster.cluster_id)
```

### Jobs

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs, compute

client = WorkspaceClient()

# Create job
job = client.jobs.create(
    name="My ETL Job",
    tasks=[
        jobs.Task(
            task_key="etl_task",
            description="Run ETL process",
            notebook_task=jobs.NotebookTask(
                notebook_path="/Users/user@example.com/etl"
            ),
            new_cluster=compute.ClusterSpec(
                spark_version="13.3.x-scala2.12",
                node_type_id="i3.xlarge",
                num_workers=2
            )
        )
    ],
    email_notifications=jobs.JobEmailNotifications(
        on_failure=["user@example.com"]
    )
)

print(f"Job ID: {job.job_id}")

# Run job
run = client.jobs.run_now(job_id=job.job_id)
print(f"Run ID: {run.run_id}")

# Wait for completion
client.jobs.wait_get_run_job_terminated_or_skipped(run_id=run.run_id)

# Get run details
run_info = client.jobs.get_run(run_id=run.run_id)
print(f"Result: {run_info.state.result_state}")

# List jobs
for job in client.jobs.list():
    print(f"{job.settings.name}: Job ID {job.job_id}")

# Delete job
client.jobs.delete(job_id=job.job_id)
```

### Workspace

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import workspace

client = WorkspaceClient()

# List workspace objects
for obj in client.workspace.list(path="/Users"):
    print(f"{obj.path} ({obj.object_type})")

# Create directory
client.workspace.mkdirs(path="/Users/user@example.com/my-project")

# Import notebook
with open("notebook.py", "rb") as f:
    content = f.read()

client.workspace.import_notebook(
    path="/Users/user@example.com/my-project/notebook",
    format=workspace.ImportFormat.SOURCE,
    language=workspace.Language.PYTHON,
    content=content
)

# Export notebook
exported = client.workspace.export(
    path="/Users/user@example.com/my-project/notebook",
    format=workspace.ExportFormat.SOURCE
)
print(exported.content)

# Delete object
client.workspace.delete(
    path="/Users/user@example.com/my-project/notebook",
    recursive=False
)
```

### DBFS

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# List files
for file in client.dbfs.list(path="/FileStore"):
    print(f"{file.path} ({file.file_size} bytes)")

# Create directory
client.dbfs.mkdirs(path="/FileStore/my-data")

# Upload file
with open("data.csv", "rb") as f:
    content = f.read()

client.dbfs.put(path="/FileStore/my-data/data.csv", contents=content)

# Read file
file_info = client.dbfs.read(path="/FileStore/my-data/data.csv")
print(file_info.data)

# Download file
with open("downloaded.csv", "wb") as f:
    f.write(file_info.data)

# Delete file
client.dbfs.delete(path="/FileStore/my-data/data.csv")
```

### Secrets

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import workspace as ws

client = WorkspaceClient()

# Create secret scope
client.secrets.create_scope(
    scope="my-secrets",
    scope_backend_type=ws.ScopeBackendType.DATABRICKS
)

# Put secret (requires CLI or notebook)
# Cannot set secret value via API for security reasons
# Use: databricks secrets put --scope my-secrets --key api-key

# List secret scopes
for scope in client.secrets.list_scopes():
    print(f"Scope: {scope.name}")

# List secrets in scope
for secret in client.secrets.list_secrets(scope="my-secrets"):
    print(f"Secret: {secret.key}")

# Delete secret
client.secrets.delete_secret(scope="my-secrets", key="api-key")

# Delete scope
client.secrets.delete_scope(scope="my-secrets")
```

### Repos (Git Integration)

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# Create repo
repo = client.repos.create(
    url="https://github.com/username/repo.git",
    provider="github",
    path="/Repos/user@example.com/repo"
)

print(f"Repo ID: {repo.id}")

# List repos
for repo in client.repos.list():
    print(f"{repo.path}: {repo.url}")

# Update repo (pull latest)
client.repos.update(
    repo_id=repo.id,
    branch="main"
)

# Get repo info
repo_info = client.repos.get(repo_id=repo.id)
print(f"Current branch: {repo_info.branch}")

# Delete repo
client.repos.delete(repo_id=repo.id)
```

### Delta Live Tables

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import pipelines

client = WorkspaceClient()

# Create pipeline
pipeline = client.pipelines.create(
    name="My DLT Pipeline",
    storage="/mnt/dlt/storage",
    configuration={
        "spark.master": "local[*]"
    },
    clusters=[
        pipelines.PipelineCluster(
            label="default",
            num_workers=2,
            node_type_id="i3.xlarge"
        )
    ],
    libraries=[
        pipelines.PipelineLibrary(
            notebook=pipelines.NotebookLibrary(
                path="/Users/user@example.com/dlt_notebook"
            )
        )
    ],
    continuous=False
)

print(f"Pipeline ID: {pipeline.pipeline_id}")

# Start pipeline
client.pipelines.start_update(pipeline_id=pipeline.pipeline_id)

# Get pipeline status
pipeline_info = client.pipelines.get(pipeline_id=pipeline.pipeline_id)
print(f"State: {pipeline_info.state}")

# List pipelines
for p in client.pipelines.list_pipelines():
    print(f"{p.name}: {p.state}")

# Delete pipeline
client.pipelines.delete(pipeline_id=pipeline.pipeline_id)
```

### Unity Catalog

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# List catalogs
for catalog in client.catalogs.list():
    print(f"Catalog: {catalog.name}")

# Create catalog
catalog = client.catalogs.create(
    name="my_catalog",
    comment="My catalog"
)

# List schemas
for schema in client.schemas.list(catalog_name="my_catalog"):
    print(f"Schema: {schema.name}")

# Create schema
schema = client.schemas.create(
    catalog_name="my_catalog",
    name="my_schema",
    comment="My schema"
)

# List tables
for table in client.tables.list(
    catalog_name="my_catalog",
    schema_name="my_schema"
):
    print(f"Table: {table.name}")

# Get table info
table_info = client.tables.get(
    full_name="my_catalog.my_schema.my_table"
)
print(f"Table type: {table_info.table_type}")

# Delete schema
client.schemas.delete(full_name="my_catalog.my_schema")

# Delete catalog
client.catalogs.delete(name="my_catalog")
```

### SQL Warehouses

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import sql

client = WorkspaceClient()

# List warehouses
for warehouse in client.warehouses.list():
    print(f"Warehouse: {warehouse.name} ({warehouse.state})")

# Create warehouse
warehouse = client.warehouses.create(
    name="my-warehouse",
    cluster_size="Small",
    max_num_clusters=1,
    auto_stop_mins=10
)

print(f"Warehouse ID: {warehouse.id}")

# Start warehouse
client.warehouses.start(id=warehouse.id)

# Wait for warehouse to start
client.warehouses.wait_get_warehouse_running(id=warehouse.id)

# Execute SQL statement
statement = client.statement_execution.execute_statement(
    warehouse_id=warehouse.id,
    statement="SELECT * FROM samples.nyctaxi.trips LIMIT 10"
)

# Get statement result
result = client.statement_execution.get_statement(
    statement_id=statement.statement_id
)
print(f"Result: {result.result}")

# Stop warehouse
client.warehouses.stop(id=warehouse.id)

# Delete warehouse
client.warehouses.delete(id=warehouse.id)
```

## Advanced Usage

### Error Handling

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import DatabricksError

client = WorkspaceClient()

try:
    cluster = client.clusters.get(cluster_id="invalid-id")
except DatabricksError as e:
    print(f"Error code: {e.error_code}")
    print(f"Message: {e.message}")
    print(f"Status code: {e.status_code}")

# Specific error handling
try:
    client.clusters.create(
        cluster_name="test",
        spark_version="invalid-version",
        node_type_id="invalid-type"
    )
except DatabricksError as e:
    if e.error_code == "INVALID_PARAMETER_VALUE":
        print("Invalid parameter provided")
    elif e.error_code == "RESOURCE_DOES_NOT_EXIST":
        print("Resource not found")
    else:
        print(f"Unexpected error: {e}")
```

### Retry Logic

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config
from databricks.sdk.retries import retried

client = WorkspaceClient()

# SDK has built-in retry logic for transient errors
# Customize retry behavior
config = Config(
    host="https://<workspace>.cloud.databricks.com",
    token="dapi...",
    retry_timeout_seconds=300,  # 5 minutes
    max_retries=3
)

client = WorkspaceClient(config=config)
```

### Pagination

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# SDK handles pagination automatically
all_jobs = list(client.jobs.list())
print(f"Total jobs: {len(all_jobs)}")

# Or iterate without loading all into memory
for job in client.jobs.list():
    print(f"Job: {job.settings.name}")
    # Process one at a time

# Manual pagination with limit
jobs_page = client.jobs.list(limit=25)
for job in jobs_page:
    print(job.settings.name)
```

### Async Operations

```python
from databricks.sdk import WorkspaceClient
import time

client = WorkspaceClient()

# Start cluster (returns immediately)
cluster_id = "1234-567890-abc123"
client.clusters.start(cluster_id=cluster_id)

# Wait for cluster to be ready
client.clusters.wait_get_cluster_running(
    cluster_id=cluster_id,
    timeout=timedelta(minutes=10)
)

print("Cluster is ready!")

# Or poll manually
while True:
    cluster = client.clusters.get(cluster_id=cluster_id)
    if cluster.state == "RUNNING":
        break
    elif cluster.state in ["TERMINATING", "TERMINATED", "ERROR"]:
        raise Exception(f"Cluster failed: {cluster.state}")
    print(f"Waiting... Current state: {cluster.state}")
    time.sleep(10)
```

### Batch Operations

```python
from databricks.sdk import WorkspaceClient
from concurrent.futures import ThreadPoolExecutor

client = WorkspaceClient()

# Get all clusters
clusters = list(client.clusters.list())

# Terminate multiple clusters in parallel
def terminate_cluster(cluster):
    try:
        client.clusters.delete(cluster_id=cluster.cluster_id)
        return f"Terminated: {cluster.cluster_name}"
    except Exception as e:
        return f"Failed: {cluster.cluster_name} - {e}"

with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(terminate_cluster, clusters)
    for result in results:
        print(result)
```

## Complete Examples

### Cluster Lifecycle Management

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import compute
from datetime import timedelta

def manage_cluster_lifecycle():
    """Complete cluster lifecycle example"""
    client = WorkspaceClient()
    
    # 1. Create cluster
    print("Creating cluster...")
    cluster = client.clusters.create(
        cluster_name="lifecycle-demo",
        spark_version="13.3.x-scala2.12",
        node_type_id="i3.xlarge",
        autoscale=compute.AutoScale(
            min_workers=2,
            max_workers=8
        ),
        autotermination_minutes=30,
        spark_conf={
            "spark.speculation": "true"
        },
        custom_tags={
            "project": "demo",
            "environment": "development"
        }
    )
    
    cluster_id = cluster.cluster_id
    print(f"Cluster created: {cluster_id}")
    
    # 2. Wait for cluster to start
    print("Waiting for cluster to start...")
    client.clusters.wait_get_cluster_running(
        cluster_id=cluster_id,
        timeout=timedelta(minutes=10)
    )
    print("Cluster is running!")
    
    # 3. Get cluster details
    cluster_info = client.clusters.get(cluster_id=cluster_id)
    print(f"Workers: {cluster_info.num_workers}")
    print(f"Spark version: {cluster_info.spark_version}")
    
    # 4. Resize cluster
    print("Resizing cluster...")
    client.clusters.resize(
        cluster_id=cluster_id,
        autoscale=compute.AutoScale(
            min_workers=4,
            max_workers=16
        )
    )
    
    # 5. Restart cluster
    print("Restarting cluster...")
    client.clusters.restart(cluster_id=cluster_id)
    client.clusters.wait_get_cluster_running(cluster_id=cluster_id)
    
    # 6. Terminate cluster
    print("Terminating cluster...")
    client.clusters.delete(cluster_id=cluster_id)
    client.clusters.wait_get_cluster_terminated(cluster_id=cluster_id)
    print("Cluster terminated!")

# Run example
manage_cluster_lifecycle()
```

### Job Creation and Monitoring

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs, compute

def create_and_monitor_job():
    """Create and monitor a job execution"""
    client = WorkspaceClient()
    
    # Create job with multiple tasks
    print("Creating job...")
    job = client.jobs.create(
        name="Data Processing Pipeline",
        tasks=[
            # Task 1: Extract
            jobs.Task(
                task_key="extract",
                description="Extract data from source",
                notebook_task=jobs.NotebookTask(
                    notebook_path="/Pipelines/extract",
                    base_parameters={"date": "{{job.start_time.iso_date}}"}
                ),
                new_cluster=compute.ClusterSpec(
                    spark_version="13.3.x-scala2.12",
                    node_type_id="i3.xlarge",
                    num_workers=2
                ),
                timeout_seconds=3600,
                max_retries=2
            ),
            
            # Task 2: Transform
            jobs.Task(
                task_key="transform",
                description="Transform data",
                depends_on=[jobs.TaskDependency(task_key="extract")],
                notebook_task=jobs.NotebookTask(
                    notebook_path="/Pipelines/transform"
                ),
                existing_cluster_id="1234-567890-abc123"
            ),
            
            # Task 3: Load
            jobs.Task(
                task_key="load",
                description="Load data to warehouse",
                depends_on=[jobs.TaskDependency(task_key="transform")],
                notebook_task=jobs.NotebookTask(
                    notebook_path="/Pipelines/load"
                ),
                existing_cluster_id="1234-567890-abc123"
            )
        ],
        email_notifications=jobs.JobEmailNotifications(
            on_success=["team@example.com"],
            on_failure=["team@example.com"]
        ),
        schedule=jobs.CronSchedule(
            quartz_cron_expression="0 0 2 * * ?",
            timezone_id="America/Los_Angeles"
        ),
        max_concurrent_runs=1,
        tags={"pipeline": "etl", "version": "1.0"}
    )
    
    job_id = job.job_id
    print(f"Job created: {job_id}")
    
    # Run job
    print("Triggering job run...")
    run = client.jobs.run_now(
        job_id=job_id,
        notebook_params={"environment": "production"}
    )
    
    run_id = run.run_id
    print(f"Run started: {run_id}")
    
    # Monitor run
    print("Monitoring run...")
    import time
    while True:
        run_info = client.jobs.get_run(run_id=run_id)
        state = run_info.state.life_cycle_state
        
        print(f"State: {state}")
        
        if state in ["TERMINATED", "SKIPPED", "INTERNAL_ERROR"]:
            result = run_info.state.result_state
            print(f"Run completed: {result}")
            
            if result == "SUCCESS":
                print("✓ Job completed successfully!")
                
                # Get output
                output = client.jobs.get_run_output(run_id=run_id)
                print(f"Output: {output}")
            else:
                print(f"✗ Job failed: {run_info.state.state_message}")
            
            break
        
        time.sleep(10)
    
    return job_id, run_id

# Run example
job_id, run_id = create_and_monitor_job()
```

### Workspace Operations

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import workspace

def manage_workspace_content():
    """Manage notebooks and workspace content"""
    client = WorkspaceClient()
    
    base_path = "/Users/user@example.com/project"
    
    # Create directory structure
    print("Creating directories...")
    client.workspace.mkdirs(path=f"{base_path}/notebooks")
    client.workspace.mkdirs(path=f"{base_path}/data")
    
    # Import notebook
    print("Importing notebook...")
    notebook_content = """
# Databricks notebook source
print("Hello from imported notebook!")

# COMMAND ----------

from pyspark.sql import SparkSession
spark = SparkSession.builder.getOrCreate()
df = spark.range(100)
display(df)
    """.strip()
    
    client.workspace.import_notebook(
        path=f"{base_path}/notebooks/demo",
        format=workspace.ImportFormat.SOURCE,
        language=workspace.Language.PYTHON,
        content=notebook_content.encode()
    )
    
    # List workspace contents
    print("Listing workspace contents...")
    for item in client.workspace.list(path=base_path):
        obj_type = "DIR" if item.object_type == workspace.ObjectType.DIRECTORY else "FILE"
        print(f"  [{obj_type}] {item.path}")
    
    # Export notebook
    print("Exporting notebook...")
    exported = client.workspace.export(
        path=f"{base_path}/notebooks/demo",
        format=workspace.ExportFormat.SOURCE
    )
    
    with open("exported_notebook.py", "wb") as f:
        f.write(exported.content)
    
    print("Notebook exported to: exported_notebook.py")
    
    # Get workspace object info
    info = client.workspace.get_status(path=f"{base_path}/notebooks/demo")
    print(f"Object type: {info.object_type}")
    print(f"Language: {info.language}")
    
    # Clean up
    print("Cleaning up...")
    client.workspace.delete(path=base_path, recursive=True)
    print("Workspace cleaned!")

# Run example
manage_workspace_content()
```

## Best Practices

### Configuration Management

```python
import os
from databricks.sdk import WorkspaceClient

# Good: Use environment variables
client = WorkspaceClient()

# Good: Use configuration profiles
client = WorkspaceClient(profile="production")

# Good: Validate configuration
try:
    user = client.current_user.me()
    print(f"✓ Connected as: {user.user_name}")
except Exception as e:
    print(f"✗ Connection failed: {e}")
```

### Error Handling

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import DatabricksError

client = WorkspaceClient()

# Good: Specific error handling
try:
    cluster = client.clusters.get(cluster_id="invalid-id")
except DatabricksError as e:
    if e.error_code == "RESOURCE_DOES_NOT_EXIST":
        print("Cluster not found - create a new one")
    elif e.error_code == "INVALID_PARAMETER_VALUE":
        print("Invalid parameter - check configuration")
    else:
        print(f"Unexpected error: {e}")
        raise

# Good: Graceful degradation
def get_cluster_safely(cluster_id):
    try:
        return client.clusters.get(cluster_id=cluster_id)
    except DatabricksError:
        return None

cluster = get_cluster_safely("1234-567890-abc123")
if cluster:
    print(f"Found cluster: {cluster.cluster_name}")
else:
    print("Cluster not found")
```

### Resource Management

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# Good: Clean up resources
def process_data_with_temp_cluster():
    # Create temporary cluster
    cluster = client.clusters.create(
        cluster_name="temp-cluster",
        spark_version="13.3.x-scala2.12",
        node_type_id="i3.xlarge",
        num_workers=2,
        autotermination_minutes=10
    )
    
    try:
        # Wait for cluster
        client.clusters.wait_get_cluster_running(
            cluster_id=cluster.cluster_id
        )
        
        # Do work
        print(f"Processing data on cluster {cluster.cluster_id}")
        
    finally:
        # Always clean up
        print("Terminating cluster...")
        client.clusters.delete(cluster_id=cluster.cluster_id)
```

### Performance Optimization

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# Good: Reuse client instances
# Bad: Creating new client for each operation
# client = WorkspaceClient()  # Don't do this repeatedly

# Good: Batch operations
cluster_ids = ["id1", "id2", "id3"]
clusters = [client.clusters.get(cluster_id=cid) for cid in cluster_ids]

# Good: Use generators for large result sets
for job in client.jobs.list():
    # Process one at a time without loading all into memory
    print(job.settings.name)
```

## Troubleshooting

### Connection Issues

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import DatabricksError

def diagnose_connection():
    """Diagnose connection issues"""
    try:
        client = WorkspaceClient()
        user = client.current_user.me()
        print(f"✓ Connected successfully as: {user.user_name}")
        return True
    except DatabricksError as e:
        print(f"✗ Connection failed")
        print(f"Error code: {e.error_code}")
        print(f"Message: {e.message}")
        print(f"Status code: {e.status_code}")
        
        if e.status_code == 401:
            print("→ Check your authentication token")
        elif e.status_code == 403:
            print("→ Check your permissions")
        elif e.status_code == 404:
            print("→ Check your workspace URL")
        
        return False

diagnose_connection()
```

### SDK Version Check

```python
import databricks.sdk

print(f"SDK Version: {databricks.sdk.__version__}")

# Check if version is compatible
required_version = "0.12.0"
current_version = databricks.sdk.__version__

if current_version < required_version:
    print(f"Please upgrade: pip install --upgrade databricks-sdk")
```

## Related Documentation

- [Getting Started: Authentication](../getting-started/authentication.md)
- [API Overview](../api/overview.md)
- [Clusters API](../api/clusters.md)
- [Jobs API](../api/jobs.md)
- [Quick Start Guide](../getting-started/quickstart.md)

## Additional Resources

- [Official Databricks SDK Documentation](https://databricks-sdk-py.readthedocs.io/)
- [GitHub Repository](https://github.com/databricks/databricks-sdk-py)
- [PyPI Package](https://pypi.org/project/databricks-sdk/)
- [API Reference](https://databricks-sdk-py.readthedocs.io/en/latest/workspace/index.html)
- [Examples](https://github.com/databricks/databricks-sdk-py/tree/main/examples)