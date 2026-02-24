# Databricks REST API Overview

## Introduction

The Databricks REST API provides programmatic access to all Databricks platform capabilities. Use these APIs to automate cluster management, job scheduling, workspace operations, and data management tasks.

## API Endpoint Structure

### Base URL Format

**AWS:**
```
https://<workspace-id>.cloud.databricks.com/api/<version>/<endpoint>
```

**Azure:**
```
https://<workspace-id>.<region>.azuredatabricks.net/api/<version>/<endpoint>
```

**GCP:**
```
https://<workspace-id>.gcp.databricks.com/api/<version>/<endpoint>
```

### API Versions

- **2.0**: Most common APIs (Clusters, Jobs, Workspace, DBFS, Secrets)
- **2.1**: Enhanced APIs (Jobs 2.1, Unity Catalog)
- **1.2**: Legacy APIs (being deprecated)

## Authentication

All API requests require authentication using one of these methods:

### Personal Access Token (Recommended)

```bash
curl -X GET \
  https://<workspace>.cloud.databricks.com/api/2.0/clusters/list \
  -H "Authorization: Bearer dapi..."
```

### Basic Authentication (Legacy)

```bash
curl -X GET \
  https://<workspace>.cloud.databricks.com/api/2.0/clusters/list \
  -u token:dapi...
```

### OAuth 2.0

```python
import requests
from requests_oauthlib import OAuth2Session

oauth = OAuth2Session(client_id, token=token)
response = oauth.get(f"{host}/api/2.0/clusters/list")
```

## Making API Requests

### Using cURL

```bash
# GET request
curl -X GET \
  https://<workspace>.cloud.databricks.com/api/2.0/clusters/list \
  -H "Authorization: Bearer ${DATABRICKS_TOKEN}"

# POST request with JSON body
curl -X POST \
  https://<workspace>.cloud.databricks.com/api/2.0/clusters/create \
  -H "Authorization: Bearer ${DATABRICKS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "cluster_name": "my-cluster",
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "i3.xlarge",
    "num_workers": 2
  }'
```

### Using Python Requests

```python
import requests
import json

# Configuration
DATABRICKS_HOST = "https://<workspace>.cloud.databricks.com"
DATABRICKS_TOKEN = "dapi..."

headers = {
    "Authorization": f"Bearer {DATABRICKS_TOKEN}",
    "Content-Type": "application/json"
}

# GET request
response = requests.get(
    f"{DATABRICKS_HOST}/api/2.0/clusters/list",
    headers=headers
)

if response.status_code == 200:
    clusters = response.json()
    print(json.dumps(clusters, indent=2))
else:
    print(f"Error: {response.status_code} - {response.text}")

# POST request
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
    print(f"Cluster ID: {result['cluster_id']}")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

### Using Databricks SDK

```python
from databricks.sdk import WorkspaceClient

# Initialize client
client = WorkspaceClient(
    host="https://<workspace>.cloud.databricks.com",
    token="dapi..."
)

# List clusters
for cluster in client.clusters.list():
    print(f"Cluster: {cluster.cluster_name} ({cluster.state})")

# Create cluster
from databricks.sdk.service.compute import CreateCluster

new_cluster = client.clusters.create(
    cluster_name="sdk-cluster",
    spark_version="13.3.x-scala2.12",
    node_type_id="i3.xlarge",
    num_workers=2,
    autotermination_minutes=30
)

print(f"Created cluster: {new_cluster.cluster_id}")
```

## Core API Categories

### Workspace Management

Manage notebooks, folders, and workspace objects.

**Endpoints:**
- `GET /api/2.0/workspace/list` - List workspace objects
- `GET /api/2.0/workspace/export` - Export notebook/file
- `POST /api/2.0/workspace/import` - Import notebook/file
- `POST /api/2.0/workspace/delete` - Delete object
- `POST /api/2.0/workspace/mkdirs` - Create directory

**Example:**
```python
# List workspace contents
response = requests.get(
    f"{DATABRICKS_HOST}/api/2.0/workspace/list",
    headers=headers,
    params={"path": "/Users"}
)
```

[Full Documentation](workspace.md)

### Clusters API

Create, manage, and monitor Spark clusters.

**Endpoints:**
- `POST /api/2.0/clusters/create` - Create cluster
- `POST /api/2.0/clusters/start` - Start cluster
- `POST /api/2.0/clusters/delete` - Terminate cluster
- `GET /api/2.0/clusters/get` - Get cluster info
- `GET /api/2.0/clusters/list` - List all clusters

**Example:**
```python
# Get cluster status
response = requests.get(
    f"{DATABRICKS_HOST}/api/2.0/clusters/get",
    headers=headers,
    params={"cluster_id": "1234-567890-abc123"}
)

cluster_info = response.json()
print(f"State: {cluster_info['state']}")
```

[Full Documentation](clusters.md)

### Jobs API

Schedule and manage automated workflows.

**Endpoints:**
- `POST /api/2.1/jobs/create` - Create job
- `POST /api/2.1/jobs/run-now` - Trigger job run
- `GET /api/2.1/jobs/list` - List all jobs
- `GET /api/2.1/jobs/runs/get` - Get run details
- `POST /api/2.1/jobs/runs/cancel` - Cancel run

**Example:**
```python
# Create a simple job
job_config = {
    "name": "Daily ETL",
    "tasks": [{
        "task_key": "etl_task",
        "notebook_task": {
            "notebook_path": "/Users/me/etl_notebook"
        },
        "existing_cluster_id": "1234-567890-abc123"
    }],
    "schedule": {
        "quartz_cron_expression": "0 0 0 * * ?",
        "timezone_id": "America/Los_Angeles"
    }
}

response = requests.post(
    f"{DATABRICKS_HOST}/api/2.1/jobs/create",
    headers=headers,
    json=job_config
)
```

[Full Documentation](jobs.md)

### DBFS API

Interact with Databricks File System.

**Endpoints:**
- `GET /api/2.0/dbfs/list` - List directory contents
- `POST /api/2.0/dbfs/put` - Upload file
- `GET /api/2.0/dbfs/read` - Download file
- `POST /api/2.0/dbfs/delete` - Delete file
- `POST /api/2.0/dbfs/mkdirs` - Create directory

**Example:**
```python
# List files
response = requests.get(
    f"{DATABRICKS_HOST}/api/2.0/dbfs/list",
    headers=headers,
    params={"path": "/FileStore"}
)

for file in response.json().get("files", []):
    print(f"{file['path']} ({file['file_size']} bytes)")
```

[Full Documentation](dbfs.md)

### Secrets API

Manage sensitive credentials and API keys.

**Endpoints:**
- `POST /api/2.0/secrets/scopes/create` - Create secret scope
- `POST /api/2.0/secrets/put` - Store secret
- `GET /api/2.0/secrets/list` - List secrets
- `POST /api/2.0/secrets/delete` - Delete secret

**Example:**
```python
# Create secret scope
response = requests.post(
    f"{DATABRICKS_HOST}/api/2.0/secrets/scopes/create",
    headers=headers,
    json={"scope": "my-secrets"}
)

# Put secret (requires interactive input via CLI)
# databricks secrets put --scope my-secrets --key api-key
```

[Full Documentation](secrets.md)

### SQL API

Execute SQL queries and manage SQL warehouses.

**Endpoints:**
- `POST /api/2.0/sql/statements` - Execute SQL
- `GET /api/2.0/sql/statements/{id}` - Get statement status
- `GET /api/2.0/sql/warehouses` - List warehouses
- `POST /api/2.0/sql/warehouses/{id}/start` - Start warehouse

**Example:**
```python
# Execute SQL statement
sql_request = {
    "warehouse_id": "abc123def456",
    "statement": "SELECT * FROM sales LIMIT 10"
}

response = requests.post(
    f"{DATABRICKS_HOST}/api/2.0/sql/statements",
    headers=headers,
    json=sql_request
)

statement_id = response.json()["statement_id"]
```

[Full Documentation](sql.md)

### Unity Catalog API

Manage data governance and metadata.

**Endpoints:**
- `GET /api/2.1/unity-catalog/catalogs` - List catalogs
- `POST /api/2.1/unity-catalog/catalogs` - Create catalog
- `GET /api/2.1/unity-catalog/schemas` - List schemas
- `GET /api/2.1/unity-catalog/tables` - List tables

**Example:**
```python
# List catalogs
response = requests.get(
    f"{DATABRICKS_HOST}/api/2.1/unity-catalog/catalogs",
    headers=headers
)

for catalog in response.json().get("catalogs", []):
    print(f"Catalog: {catalog['name']}")
```

[Full Documentation](unity-catalog.md)

## Response Format

### Success Response

```json
{
  "cluster_id": "1234-567890-abc123",
  "cluster_name": "my-cluster",
  "state": "RUNNING"
}
```

### Error Response

```json
{
  "error_code": "INVALID_PARAMETER_VALUE",
  "message": "Cluster size must be at least 1 worker"
}
```

## Common HTTP Status Codes

| Status Code | Meaning | Description |
|-------------|---------|-------------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication failed |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

## Error Handling

### Python Example

```python
import requests
from requests.exceptions import RequestException

def make_api_request(method, endpoint, **kwargs):
    """Make API request with error handling"""
    url = f"{DATABRICKS_HOST}{endpoint}"
    
    try:
        response = requests.request(
            method,
            url,
            headers=headers,
            **kwargs
        )
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("Authentication failed. Check your token.")
        elif e.response.status_code == 403:
            print("Insufficient permissions.")
        elif e.response.status_code == 404:
            print("Resource not found.")
        elif e.response.status_code == 429:
            print("Rate limit exceeded. Wait and retry.")
        else:
            print(f"HTTP Error: {e}")
        return None
        
    except RequestException as e:
        print(f"Request failed: {e}")
        return None

# Usage
result = make_api_request(
    "GET",
    "/api/2.0/clusters/list"
)

if result:
    print(f"Found {len(result.get('clusters', []))} clusters")
```

## Rate Limiting

Databricks APIs have rate limits to ensure fair usage:

- **Default limit**: 30 requests per second per user
- **Burst limit**: Short bursts above limit allowed
- **429 status code**: Indicates rate limit exceeded

### Handling Rate Limits

```python
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def create_session_with_retry():
    """Create session with automatic retry logic"""
    session = requests.Session()
    
    retry_strategy = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    return session

# Usage
session = create_session_with_retry()
response = session.get(
    f"{DATABRICKS_HOST}/api/2.0/clusters/list",
    headers=headers
)
```

## Pagination

Some APIs return paginated results.

### Example: Paginated Listing

```python
def list_all_jobs():
    """List all jobs with pagination"""
    all_jobs = []
    has_more = True
    offset = 0
    limit = 25
    
    while has_more:
        response = requests.get(
            f"{DATABRICKS_HOST}/api/2.1/jobs/list",
            headers=headers,
            params={
                "limit": limit,
                "offset": offset
            }
        )
        
        data = response.json()
        jobs = data.get("jobs", [])
        all_jobs.extend(jobs)
        
        has_more = data.get("has_more", False)
        offset += limit
    
    return all_jobs

# Usage
all_jobs = list_all_jobs()
print(f"Total jobs: {len(all_jobs)}")
```

## Asynchronous Operations

Some operations are asynchronous and return immediately with a handle to check status.

### Example: Cluster Operations

```python
import time

def wait_for_cluster_ready(cluster_id, timeout=600):
    """Wait for cluster to reach RUNNING state"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        response = requests.get(
            f"{DATABRICKS_HOST}/api/2.0/clusters/get",
            headers=headers,
            params={"cluster_id": cluster_id}
        )
        
        cluster = response.json()
        state = cluster.get("state")
        
        if state == "RUNNING":
            print(f"Cluster {cluster_id} is ready!")
            return True
        elif state in ["TERMINATING", "TERMINATED", "ERROR"]:
            print(f"Cluster failed with state: {state}")
            return False
        
        print(f"Current state: {state}. Waiting...")
        time.sleep(10)
    
    print("Timeout waiting for cluster")
    return False

# Create and wait for cluster
create_response = requests.post(
    f"{DATABRICKS_HOST}/api/2.0/clusters/create",
    headers=headers,
    json=cluster_config
)

cluster_id = create_response.json()["cluster_id"]
wait_for_cluster_ready(cluster_id)
```

## Best Practices

### Security

- **Store tokens securely**: Use environment variables or secret management
- **Rotate tokens regularly**: Set expiration dates
- **Use service principals**: For production automation
- **Principle of least privilege**: Grant minimum necessary permissions

### Performance

- **Batch operations**: Combine multiple API calls when possible
- **Cache results**: Avoid redundant API calls
- **Use async operations**: Don't block on long-running tasks
- **Implement retry logic**: Handle transient failures

### Error Handling

- **Check response status**: Always verify status codes
- **Parse error messages**: Extract meaningful error information
- **Log API interactions**: For debugging and auditing
- **Handle rate limits**: Implement exponential backoff

### Code Organization

```python
class DatabricksAPIClient:
    """Wrapper for Databricks REST API"""
    
    def __init__(self, host, token):
        self.host = host
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.session = create_session_with_retry()
    
    def _request(self, method, endpoint, **kwargs):
        """Make API request with error handling"""
        url = f"{self.host}{endpoint}"
        response = self.session.request(
            method, url, headers=self.headers, **kwargs
        )
        response.raise_for_status()
        return response.json()
    
    def list_clusters(self):
        """List all clusters"""
        return self._request("GET", "/api/2.0/clusters/list")
    
    def create_cluster(self, config):
        """Create a new cluster"""
        return self._request(
            "POST", "/api/2.0/clusters/create", json=config
        )
    
    def get_cluster(self, cluster_id):
        """Get cluster information"""
        return self._request(
            "GET", "/api/2.0/clusters/get",
            params={"cluster_id": cluster_id}
        )

# Usage
client = DatabricksAPIClient(
    host="https://<workspace>.cloud.databricks.com",
    token="dapi..."
)

clusters = client.list_clusters()
```

## API Reference Documentation

Explore detailed documentation for each API:

### Workspace & Compute
- [Workspace API](workspace.md) - Manage notebooks and folders
- [Clusters API](clusters.md) - Create and manage clusters
- [Instance Pools API](instance-pools.md) - Manage instance pools

### Jobs & Workflows
- [Jobs API](jobs.md) - Schedule and run workflows
- [Runs API](jobs.md#runs) - Monitor job executions

### Data Management
- [DBFS API](dbfs.md) - File system operations
- [Unity Catalog API](unity-catalog.md) - Data governance
- [SQL API](sql.md) - Query execution

### Security
- [Secrets API](secrets.md) - Manage secrets
- [Tokens API](tokens.md) - Token management
- [Permissions API](permissions.md) - Access control

### Integration
- [Repos API](repos.md) - Git integration
- [Libraries API](libraries.md) - Package management

## Testing APIs

### Using Postman

1. Import Databricks API collection
2. Set environment variables:
   - `DATABRICKS_HOST`
   - `DATABRICKS_TOKEN`
3. Use collection to test endpoints

### Using Python unittest

```python
import unittest
from databricks_api_client import DatabricksAPIClient

class TestDatabricksAPI(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.client = DatabricksAPIClient(
            host=os.environ["DATABRICKS_HOST"],
            token=os.environ["DATABRICKS_TOKEN"]
        )
    
    def test_list_clusters(self):
        """Test listing clusters"""
        result = self.client.list_clusters()
        self.assertIn("clusters", result)
        self.assertIsInstance(result["clusters"], list)
    
    def test_cluster_lifecycle(self):
        """Test creating and deleting cluster"""
        # Create cluster
        config = {
            "cluster_name": "test-cluster",
            "spark_version": "13.3.x-scala2.12",
            "node_type_id": "i3.xlarge",
            "num_workers": 0
        }
        
        result = self.client.create_cluster(config)
        cluster_id = result["cluster_id"]
        
        # Verify cluster exists
        cluster = self.client.get_cluster(cluster_id)
        self.assertEqual(cluster["cluster_name"], "test-cluster")
        
        # Cleanup
        self.client.delete_cluster(cluster_id)

if __name__ == "__main__":
    unittest.main()
```

## Additional Resources

- [Databricks REST API Reference](https://docs.databricks.com/api/workspace/introduction)
- [Databricks SDK for Python](https://github.com/databricks/databricks-sdk-py)
- [API Examples Repository](https://github.com/databricks/databricks-rest-api-examples)
- [Postman Collection](https://www.postman.com/databricks)

## Next Steps

- [Clusters API Documentation](clusters.md)
- [Jobs API Documentation](jobs.md)
- [Python SDK Guide](../sdk/python.md)
- [Authentication Guide](../getting-started/authentication.md)

## Related Documentation

- [Setup Guide](../getting-started/setup.md)
- [Quick Start](../getting-started/quickstart.md)
- [Best Practices](../best-practices/general.md)
- [Security Best Practices](../best-practices/security.md)