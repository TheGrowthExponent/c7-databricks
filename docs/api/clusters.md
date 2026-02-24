# Databricks Clusters API

## Overview

The Clusters API allows you to programmatically create, configure, start, stop, and manage Databricks clusters. Clusters are sets of computation resources and configurations on which you run data engineering, data science, and analytics workloads.

## Base Endpoint

```
/api/2.0/clusters
```

## Cluster Types

### All-Purpose Clusters
- Interactive development and exploration
- Shared among multiple users
- Persist until manually terminated
- Best for notebooks and ad-hoc analysis

### Job Clusters
- Created for specific job runs
- Automatically terminated after job completion
- Cannot be restarted
- Cost-effective for automated workloads

## Authentication

All requests require authentication. See [Authentication Guide](../getting-started/authentication.md).

```python
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
```

---

## Create Cluster

Create a new Spark cluster.

### Endpoint

```
POST /api/2.0/clusters/create
```

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| cluster_name | string | Yes | Name for the cluster |
| spark_version | string | Yes | Spark runtime version |
| node_type_id | string | Yes | Instance type for driver and workers |
| num_workers | integer | Conditional | Number of worker nodes (0 for single node) |
| autoscale | object | Conditional | Autoscaling configuration |
| autotermination_minutes | integer | No | Auto-terminate after inactivity (default: 120) |
| spark_conf | object | No | Spark configuration properties |
| aws_attributes | object | No | AWS-specific attributes |
| azure_attributes | object | No | Azure-specific attributes |
| gcp_attributes | object | No | GCP-specific attributes |
| custom_tags | object | No | Custom tags for cost tracking |
| init_scripts | array | No | Initialization scripts |
| spark_env_vars | object | No | Environment variables |
| enable_elastic_disk | boolean | No | Enable elastic disk scaling |
| driver_node_type_id | string | No | Instance type for driver (if different) |
| instance_pool_id | string | No | Instance pool to use |
| policy_id | string | No | Cluster policy to apply |

### Request Body Examples

#### Single Node Cluster

```json
{
  "cluster_name": "single-node-cluster",
  "spark_version": "13.3.x-scala2.12",
  "node_type_id": "i3.xlarge",
  "num_workers": 0,
  "autotermination_minutes": 30,
  "spark_conf": {
    "spark.databricks.cluster.profile": "singleNode",
    "spark.master": "local[*]"
  },
  "custom_tags": {
    "ResourceClass": "SingleNode"
  }
}
```

#### Standard Multi-Node Cluster

```json
{
  "cluster_name": "multi-node-cluster",
  "spark_version": "13.3.x-scala2.12",
  "node_type_id": "i3.xlarge",
  "num_workers": 4,
  "autotermination_minutes": 60,
  "spark_conf": {
    "spark.speculation": "true"
  },
  "custom_tags": {
    "Project": "data-engineering",
    "Environment": "production"
  }
}
```

#### Autoscaling Cluster

```json
{
  "cluster_name": "autoscaling-cluster",
  "spark_version": "13.3.x-scala2.12",
  "node_type_id": "i3.xlarge",
  "autoscale": {
    "min_workers": 2,
    "max_workers": 8
  },
  "autotermination_minutes": 30,
  "enable_elastic_disk": true
}
```

### Python SDK Example

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import compute

client = WorkspaceClient()

# Create single node cluster
cluster = client.clusters.create(
    cluster_name="my-cluster",
    spark_version="13.3.x-scala2.12",
    node_type_id="i3.xlarge",
    num_workers=0,
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
print(f"State: {cluster.state}")
```

### Python Requests Example

```python
import requests
import json

DATABRICKS_HOST = "https://<workspace>.cloud.databricks.com"
DATABRICKS_TOKEN = "dapi..."

headers = {
    "Authorization": f"Bearer {DATABRICKS_TOKEN}",
    "Content-Type": "application/json"
}

cluster_config = {
    "cluster_name": "api-cluster",
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "i3.xlarge",
    "num_workers": 2,
    "autotermination_minutes": 30
}

response = requests.post(
    f"{DATABRICKS_HOST}/api/2.0/clusters/create",
    headers=headers,
    json=cluster_config
)

if response.status_code == 200:
    result = response.json()
    print(f"Cluster created: {result['cluster_id']}")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

### Response

```json
{
  "cluster_id": "1234-567890-abc123"
}
```

### Error Responses

```json
{
  "error_code": "INVALID_PARAMETER_VALUE",
  "message": "Cluster size must be at least 1 worker"
}
```

---

## Get Cluster

Retrieve information about a cluster.

### Endpoint

```
GET /api/2.0/clusters/get
```

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| cluster_id | string | Yes | The cluster ID |

### Example

```python
import requests

response = requests.get(
    f"{DATABRICKS_HOST}/api/2.0/clusters/get",
    headers=headers,
    params={"cluster_id": "1234-567890-abc123"}
)

cluster = response.json()
print(f"Name: {cluster['cluster_name']}")
print(f"State: {cluster['state']}")
print(f"Workers: {cluster.get('num_workers', 'Single Node')}")
```

### SDK Example

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

cluster = client.clusters.get(cluster_id="1234-567890-abc123")

print(f"Cluster Name: {cluster.cluster_name}")
print(f"State: {cluster.state}")
print(f"Spark Version: {cluster.spark_version}")
print(f"Node Type: {cluster.node_type_id}")
```

### Response

```json
{
  "cluster_id": "1234-567890-abc123",
  "cluster_name": "my-cluster",
  "spark_version": "13.3.x-scala2.12",
  "node_type_id": "i3.xlarge",
  "driver_node_type_id": "i3.xlarge",
  "num_workers": 2,
  "autotermination_minutes": 30,
  "state": "RUNNING",
  "state_message": "",
  "start_time": 1699564800000,
  "creator_user_name": "user@example.com",
  "spark_conf": {},
  "aws_attributes": {
    "zone_id": "us-west-2a",
    "availability": "SPOT_WITH_FALLBACK"
  },
  "custom_tags": {
    "Project": "data-engineering"
  }
}
```

---

## List Clusters

List all clusters in the workspace.

### Endpoint

```
GET /api/2.0/clusters/list
```

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| can_use_client | string | No | Filter clusters user can attach to |

### Example

```python
import requests

response = requests.get(
    f"{DATABRICKS_HOST}/api/2.0/clusters/list",
    headers=headers
)

clusters = response.json().get("clusters", [])

for cluster in clusters:
    print(f"ID: {cluster['cluster_id']}")
    print(f"Name: {cluster['cluster_name']}")
    print(f"State: {cluster['state']}")
    print("-" * 40)
```

### SDK Example

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# List all clusters
for cluster in client.clusters.list():
    print(f"Cluster: {cluster.cluster_name}")
    print(f"  ID: {cluster.cluster_id}")
    print(f"  State: {cluster.state}")
    print(f"  Workers: {cluster.num_workers or 'Single Node'}")
    print()
```

### Response

```json
{
  "clusters": [
    {
      "cluster_id": "1234-567890-abc123",
      "cluster_name": "my-cluster",
      "state": "RUNNING",
      "num_workers": 2
    },
    {
      "cluster_id": "5678-123456-def789",
      "cluster_name": "another-cluster",
      "state": "TERMINATED",
      "num_workers": 4
    }
  ]
}
```

---

## Start Cluster

Start a terminated cluster.

### Endpoint

```
POST /api/2.0/clusters/start
```

### Request Body

```json
{
  "cluster_id": "1234-567890-abc123"
}
```

### Example

```python
import requests

response = requests.post(
    f"{DATABRICKS_HOST}/api/2.0/clusters/start",
    headers=headers,
    json={"cluster_id": "1234-567890-abc123"}
)

if response.status_code == 200:
    print("Cluster starting...")
```

### SDK Example

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# Start cluster
client.clusters.start(cluster_id="1234-567890-abc123")

# Wait for cluster to be ready
client.clusters.wait_get_cluster_running(cluster_id="1234-567890-abc123")

print("Cluster is running!")
```

---

## Restart Cluster

Restart a running cluster.

### Endpoint

```
POST /api/2.0/clusters/restart
```

### Request Body

```json
{
  "cluster_id": "1234-567890-abc123"
}
```

### Example

```python
import requests

response = requests.post(
    f"{DATABRICKS_HOST}/api/2.0/clusters/restart",
    headers=headers,
    json={"cluster_id": "1234-567890-abc123"}
)

if response.status_code == 200:
    print("Cluster restarting...")
```

### SDK Example

```python
client = WorkspaceClient()

# Restart cluster
client.clusters.restart(cluster_id="1234-567890-abc123")

# Wait for restart to complete
client.clusters.wait_get_cluster_running(cluster_id="1234-567890-abc123")

print("Cluster restarted successfully!")
```

---

## Terminate Cluster

Terminate (stop) a running cluster.

### Endpoint

```
POST /api/2.0/clusters/delete
```

### Request Body

```json
{
  "cluster_id": "1234-567890-abc123"
}
```

### Example

```python
import requests

response = requests.post(
    f"{DATABRICKS_HOST}/api/2.0/clusters/delete",
    headers=headers,
    json={"cluster_id": "1234-567890-abc123"}
)

if response.status_code == 200:
    print("Cluster terminating...")
```

### SDK Example

```python
client = WorkspaceClient()

# Terminate cluster
client.clusters.delete(cluster_id="1234-567890-abc123")

# Wait for termination
client.clusters.wait_get_cluster_terminated(cluster_id="1234-567890-abc123")

print("Cluster terminated successfully!")
```

---

## Edit Cluster

Edit configuration of a terminated cluster.

### Endpoint

```
POST /api/2.0/clusters/edit
```

### Request Body

Include all required cluster configuration parameters (same as create).

```json
{
  "cluster_id": "1234-567890-abc123",
  "cluster_name": "updated-cluster-name",
  "spark_version": "13.3.x-scala2.12",
  "node_type_id": "i3.xlarge",
  "num_workers": 4,
  "autotermination_minutes": 60
}
```

### Example

```python
import requests

cluster_config = {
    "cluster_id": "1234-567890-abc123",
    "cluster_name": "updated-cluster",
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "i3.2xlarge",
    "num_workers": 4,
    "autotermination_minutes": 60
}

response = requests.post(
    f"{DATABRICKS_HOST}/api/2.0/clusters/edit",
    headers=headers,
    json=cluster_config
)

if response.status_code == 200:
    print("Cluster configuration updated!")
```

### SDK Example

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# Edit cluster
client.clusters.edit(
    cluster_id="1234-567890-abc123",
    cluster_name="updated-cluster",
    spark_version="13.3.x-scala2.12",
    node_type_id="i3.2xlarge",
    num_workers=4,
    autotermination_minutes=60
)

print("Cluster updated!")
```

---

## Resize Cluster

Change the number of workers for a running cluster.

### Endpoint

```
POST /api/2.0/clusters/resize
```

### Request Body

```json
{
  "cluster_id": "1234-567890-abc123",
  "num_workers": 8
}
```

Or for autoscaling:

```json
{
  "cluster_id": "1234-567890-abc123",
  "autoscale": {
    "min_workers": 4,
    "max_workers": 16
  }
}
```

### Example

```python
import requests

resize_config = {
    "cluster_id": "1234-567890-abc123",
    "num_workers": 8
}

response = requests.post(
    f"{DATABRICKS_HOST}/api/2.0/clusters/resize",
    headers=headers,
    json=resize_config
)

if response.status_code == 200:
    print("Cluster resizing...")
```

### SDK Example

```python
client = WorkspaceClient()

# Resize to fixed number of workers
client.clusters.resize(
    cluster_id="1234-567890-abc123",
    num_workers=8
)

# Or enable autoscaling
client.clusters.resize(
    cluster_id="1234-567890-abc123",
    autoscale=compute.AutoScale(
        min_workers=4,
        max_workers=16
    )
)

print("Cluster resized!")
```

---

## Pin Cluster

Pin a cluster to prevent it from being deleted automatically.

### Endpoint

```
POST /api/2.0/clusters/pin
```

### Request Body

```json
{
  "cluster_id": "1234-567890-abc123"
}
```

### Example

```python
client = WorkspaceClient()

# Pin cluster
client.clusters.pin(cluster_id="1234-567890-abc123")

print("Cluster pinned!")
```

---

## Unpin Cluster

Unpin a cluster to allow automatic deletion.

### Endpoint

```
POST /api/2.0/clusters/unpin
```

### Request Body

```json
{
  "cluster_id": "1234-567890-abc123"
}
```

### Example

```python
client = WorkspaceClient()

# Unpin cluster
client.clusters.unpin(cluster_id="1234-567890-abc123")

print("Cluster unpinned!")
```

---

## List Node Types

List available node types for clusters.

### Endpoint

```
GET /api/2.0/clusters/list-node-types
```

### Example

```python
import requests

response = requests.get(
    f"{DATABRICKS_HOST}/api/2.0/clusters/list-node-types",
    headers=headers
)

node_types = response.json().get("node_types", [])

for node_type in node_types:
    print(f"ID: {node_type['node_type_id']}")
    print(f"Memory: {node_type['memory_mb']} MB")
    print(f"Cores: {node_type['num_cores']}")
    print("-" * 40)
```

### SDK Example

```python
client = WorkspaceClient()

# List node types
for node_type in client.clusters.list_node_types():
    print(f"Node Type: {node_type.node_type_id}")
    print(f"  Memory: {node_type.memory_mb} MB")
    print(f"  Cores: {node_type.num_cores}")
    print(f"  Category: {node_type.category}")
    print()
```

---

## List Spark Versions

List available Spark runtime versions.

### Endpoint

```
GET /api/2.0/clusters/spark-versions
```

### Example

```python
import requests

response = requests.get(
    f"{DATABRICKS_HOST}/api/2.0/clusters/spark-versions",
    headers=headers
)

versions = response.json().get("versions", [])

for version in versions:
    print(f"Key: {version['key']}")
    print(f"Name: {version['name']}")
    print("-" * 40)
```

### SDK Example

```python
client = WorkspaceClient()

# List Spark versions
for version in client.clusters.spark_versions():
    print(f"Version: {version.key}")
    print(f"Name: {version.name}")
```

---

## Get Cluster Events

Retrieve events for a cluster.

### Endpoint

```
POST /api/2.0/clusters/events
```

### Request Body

```json
{
  "cluster_id": "1234-567890-abc123",
  "start_time": 1699564800000,
  "end_time": 1699651200000,
  "event_types": ["STARTING", "TERMINATING", "RUNNING"],
  "limit": 50
}
```

### Example

```python
import requests
import time

# Get events from last 24 hours
end_time = int(time.time() * 1000)
start_time = end_time - (24 * 60 * 60 * 1000)

request_body = {
    "cluster_id": "1234-567890-abc123",
    "start_time": start_time,
    "end_time": end_time,
    "limit": 50
}

response = requests.post(
    f"{DATABRICKS_HOST}/api/2.0/clusters/events",
    headers=headers,
    json=request_body
)

events = response.json().get("events", [])

for event in events:
    print(f"Type: {event['type']}")
    print(f"Time: {event['timestamp']}")
    print(f"Details: {event.get('details', {})}")
    print("-" * 40)
```

### SDK Example

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.compute import ClusterEventType
import time

client = WorkspaceClient()

# Get recent events
end_time = int(time.time() * 1000)
start_time = end_time - (24 * 60 * 60 * 1000)

events = client.clusters.events(
    cluster_id="1234-567890-abc123",
    start_time=start_time,
    end_time=end_time,
    event_types=[
        ClusterEventType.STARTING,
        ClusterEventType.RUNNING,
        ClusterEventType.TERMINATING
    ]
)

for event in events.events:
    print(f"Event: {event.type} at {event.timestamp}")
```

---

## Cluster States

| State | Description |
|-------|-------------|
| PENDING | Cluster is being created |
| RUNNING | Cluster is running and ready |
| RESTARTING | Cluster is restarting |
| RESIZING | Cluster is being resized |
| TERMINATING | Cluster is being terminated |
| TERMINATED | Cluster has been stopped |
| ERROR | Cluster encountered an error |
| UNKNOWN | Cluster state is unknown |

---

## Advanced Examples

### Complete Cluster Lifecycle Management

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import compute
import time

def manage_cluster_lifecycle():
    """Complete cluster lifecycle example"""
    client = WorkspaceClient()
    
    # 1. Create cluster
    print("Creating cluster...")
    cluster = client.clusters.create(
        cluster_name="lifecycle-cluster",
        spark_version="13.3.x-scala2.12",
        node_type_id="i3.xlarge",
        num_workers=2,
        autotermination_minutes=30,
        custom_tags={
            "Project": "demo",
            "Environment": "test"
        }
    )
    
    cluster_id = cluster.cluster_id
    print(f"Cluster created: {cluster_id}")
    
    # 2. Wait for cluster to be ready
    print("Waiting for cluster to start...")
    client.clusters.wait_get_cluster_running(cluster_id=cluster_id)
    print("Cluster is running!")
    
    # 3. Get cluster info
    cluster_info = client.clusters.get(cluster_id=cluster_id)
    print(f"Cluster name: {cluster_info.cluster_name}")
    print(f"Spark version: {cluster_info.spark_version}")
    
    # 4. Resize cluster
    print("Resizing cluster to 4 workers...")
    client.clusters.resize(cluster_id=cluster_id, num_workers=4)
    time.sleep(30)  # Wait for resize
    
    # 5. Pin cluster
    print("Pinning cluster...")
    client.clusters.pin(cluster_id=cluster_id)
    
    # 6. Get cluster events
    end_time = int(time.time() * 1000)
    start_time = end_time - (60 * 60 * 1000)  # Last hour
    
    events = client.clusters.events(
        cluster_id=cluster_id,
        start_time=start_time,
        end_time=end_time
    )
    
    print(f"Recent events: {len(events.events or [])}")
    
    # 7. Terminate cluster
    print("Terminating cluster...")
    client.clusters.delete(cluster_id=cluster_id)
    
    # Wait for termination
    client.clusters.wait_get_cluster_terminated(cluster_id=cluster_id)
    print("Cluster terminated!")

# Run example
manage_cluster_lifecycle()
```

### Cluster with Custom Configuration

```python
def create_production_cluster():
    """Create production-ready cluster"""
    client = WorkspaceClient()
    
    cluster = client.clusters.create(
        cluster_name="production-cluster",
        spark_version="13.3.x-scala2.12",
        node_type_id="i3.2xlarge",
        driver_node_type_id="i3.4xlarge",  # Larger driver
        autoscale=compute.AutoScale(
            min_workers=4,
            max_workers=16
        ),
        autotermination_minutes=60,
        enable_elastic_disk=True,
        
        # Spark configuration
        spark_conf={
            "spark.speculation": "true",
            "spark.sql.adaptive.enabled": "true",
            "spark.databricks.delta.preview.enabled": "true"
        },
        
        # Environment variables
        spark_env_vars={
            "ENVIRONMENT": "production",
            "LOG_LEVEL": "INFO"
        },
        
        # AWS attributes
        aws_attributes=compute.AwsAttributes(
            zone_id="us-west-2a",
            availability=compute.AwsAvailability.SPOT_WITH_FALLBACK,
            spot_bid_price_percent=50
        ),
        
        # Custom tags for cost tracking
        custom_tags={
            "Project": "data-pipeline",
            "Environment": "production",
            "CostCenter": "engineering",
            "Owner": "data-team"
        },
        
        # Init script
        init_scripts=[
            compute.InitScriptInfo(
                dbfs=compute.DbfsStorageInfo(
                    destination="dbfs:/init-scripts/setup.sh"
                )
            )
        ]
    )
    
    print(f"Production cluster created: {cluster.cluster_id}")
    return cluster

# Create cluster
prod_cluster = create_production_cluster()
```

### Monitor Cluster Health

```python
def monitor_cluster_health(cluster_id, duration_seconds=300):
    """Monitor cluster health over time"""
    client = WorkspaceClient()
    start_time = time.time()
    
    print(f"Monitoring cluster {cluster_id} for {duration_seconds} seconds...")
    
    while time.time() - start_time < duration_seconds:
        try:
            cluster = client.clusters.get(cluster_id=cluster_id)
            
            print(f"\nTime: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"State: {cluster.state}")
            print(f"Workers: {cluster.num_workers or 'Single Node'}")
            
            if cluster.state == "RUNNING":
                # Cluster is healthy
                print("✓ Cluster is healthy")
            elif cluster.state == "ERROR":
                print("✗ Cluster in ERROR state!")
                print(f"Message: {cluster.state_message}")
                break
            else:
                print(f"⚠ Cluster is {cluster.state}")
            
            time.sleep(30)  # Check every 30 seconds
            
        except Exception as e:
            print(f"Error checking cluster: {e}")
            break
    
    print("\nMonitoring complete!")

# Monitor cluster
monitor_cluster_health("1234-567890-abc123", duration_seconds=300)
```

### Batch Operations

```python
def batch_cluster_operations():
    """Perform batch operations on multiple clusters"""
    client = WorkspaceClient()
    
    # Get all running clusters
    running_clusters = [
        c for c in client.clusters.list()
        if c.state == "RUNNING"
    ]
    
    print(f"Found {len(running_clusters)} running clusters")
    
    # Terminate idle clusters (example logic)
    for cluster in running_clusters:
        if should_terminate(cluster):
            print(f"Terminating cluster: {cluster.cluster_name}")
            client.clusters.delete(cluster_id=cluster.cluster_id)
    
    # List all terminated clusters
    terminated_clusters = [
        c for c in client.clusters.list()
        if c.state == "TERMINATED"
    ]
    
    print(f"Found {len(terminated_clusters)} terminated clusters")
    
    # Clean up old terminated clusters
    for cluster in terminated_clusters:
        # Add logic to permanently delete old clusters
        pass

def should_terminate(cluster):
    """Determine if cluster should be terminated"""
    # Example: Terminate if no activity in last 2 hours
    # Add your logic here
    return False

# Run batch operations
batch_cluster_operations()
```

---

## Best Practices

### Cluster Configuration

1. **Use Autotermination**: Always set `autotermination_minutes` to avoid unnecessary costs
2. **Right-size Clusters**: Start small and scale up based on actual needs
3. **Use Autoscaling**: Enable autoscaling for variable workloads
4. **Tag Clusters**: Use custom tags for cost attribution and tracking
5. **Separate Dev/Prod**: Use different clusters for development and production

### Cost Optimization

```python
# Good: Autoscaling with reasonable limits
autoscale=compute.AutoScale(
    min_workers=2,
    max_workers=8
)

# Good: Short autotermination for dev clusters
autotermination_minutes=30

# Good: Use spot instances for fault-tolerant workloads
aws_attributes=compute.AwsAttributes(
    availability=compute.AwsAvailability.SPOT_WITH_FALLBACK,
    spot_bid_price_percent=50
)
```

### Performance Optimization

```python
# Enable adaptive query execution
spark_conf={
    "spark.sql.adaptive.enabled": "true",
    "spark.sql.adaptive.coalescePartitions.enabled": "true"
}

# Use larger driver for memory-intensive operations
driver_node_type_id="i3.4xlarge"  # Larger than workers

# Enable elastic disk for storage-intensive workloads
enable_elastic_disk=True
```

### Security

```python
# Use cluster policies to enforce standards
policy_id="ABC123DEF456"

# Use instance pools for network isolation
instance_pool_id="pool-abc-123"

# Set appropriate tags for governance
custom_tags={
    "DataClassification": "confidential",
    "ComplianceScope": "GDPR"
}
```

---

## Troubleshooting

### Cluster Won't Start

**Problem**: Cluster stuck in PENDING state

**Solutions**:
- Check instance type availability in region
- Verify account has sufficient quota
- Review cluster configuration for errors
- Check cluster policies aren't too restrictive

### Out of Memory Errors

**Problem**: Cluster running out of memory

**Solutions**:
```python
# Increase driver memory
driver_node_type_id="i3.4xlarge"

# Add more workers
num_workers=8

# Or enable autoscaling
autoscale=compute.AutoScale(min_workers=4, max_workers=16)
```

### Slow Cluster Startup

**Problem**: Clusters taking too long to start

**Solutions**:
- Use instance pools for faster startup
- Avoid large init scripts
- Pre-install commonly used libraries
- Consider using cluster policies

---

## Related Documentation

- [API Overview](overview.md)
- [Jobs API](jobs.md)
- [Instance Pools API](instance-pools.md)
- [Libraries API](libraries.md)
- [Python SDK Guide](../sdk/python.md)
- [Best Practices: Performance](../best-practices/performance.md)
- [Best Practices: Cost Optimization](../best-practices/cost.md)

## Additional Resources

- [Official Clusters API Documentation](https://docs.databricks.com/api/workspace/clusters)
- [Cluster Configuration Best Practices](https://docs.databricks.com/clusters/configure.html)
- [Autoscaling Guide](https://docs.databricks.com/clusters/configure.html#autoscaling)