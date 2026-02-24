# Databricks Secrets API

## Overview

The Secrets API allows you to securely store and manage sensitive information such as passwords, API keys, tokens, and certificates. Secrets are stored in secret scopes and can be accessed from notebooks, jobs, and applications without exposing the actual values in code.

## Base Endpoint

```
/api/2.0/secrets
```

## Why Use Secrets?

- **Security**: Keep credentials out of notebooks and code
- **Access Control**: Fine-grained permissions on secret scopes
- **Audit Trail**: Track secret access and modifications
- **Integration**: Works with external secret managers (Azure Key Vault, AWS Secrets Manager)
- **Best Practice**: Industry-standard secret management

## Secret Scope Types

### Databricks-Managed Scopes

Secrets stored and managed by Databricks.

**Pros**:
- Simple to set up and use
- No additional infrastructure needed
- Integrated access control

**Cons**:
- Limited to Databricks platform
- Cannot be shared with external systems

### Azure Key Vault-Backed Scopes

Secrets stored in Azure Key Vault, accessible from Databricks.

**Pros**:
- Centralized secret management
- Enterprise-grade security
- Cross-platform access
- Existing key vault integration

**Cons**:
- Azure-specific
- Requires Azure Key Vault setup

### AWS Secrets Manager-Backed Scopes

Secrets stored in AWS Secrets Manager, accessible from Databricks.

**Pros**:
- Centralized AWS secret management
- Automatic rotation support
- Cross-service access

**Cons**:
- AWS-specific
- Requires AWS Secrets Manager setup

## Authentication

All requests require authentication. See [Authentication Guide](../getting-started/authentication.md).

```python
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
```

---

## Create Secret Scope

Create a new secret scope to store secrets.

### Endpoint

```
POST /api/2.0/secrets/scopes/create
```

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| scope | string | Yes | Name of the secret scope |
| scope_backend_type | string | No | DATABRICKS (default) or AZURE_KEYVAULT |
| backend_azure_keyvault | object | No | Azure Key Vault configuration |
| initial_manage_principal | string | No | Principal with MANAGE permission |

### Databricks-Managed Scope

```json
{
  "scope": "my-secrets",
  "scope_backend_type": "DATABRICKS",
  "initial_manage_principal": "users"
}
```

### Azure Key Vault-Backed Scope

```json
{
  "scope": "azure-keyvault-secrets",
  "scope_backend_type": "AZURE_KEYVAULT",
  "backend_azure_keyvault": {
    "resource_id": "/subscriptions/{subscription-id}/resourceGroups/{rg-name}/providers/Microsoft.KeyVault/vaults/{vault-name}",
    "dns_name": "https://{vault-name}.vault.azure.net/"
  }
}
```

### Example (CLI Required)

**Note**: Creating scopes with the REST API requires admin privileges. Most users will use the CLI:

```bash
# Create Databricks-managed scope
databricks secrets create-scope --scope my-secrets

# Create Azure Key Vault-backed scope
databricks secrets create-scope \
  --scope azure-secrets \
  --scope-backend-type AZURE_KEYVAULT \
  --resource-id "/subscriptions/.../providers/Microsoft.KeyVault/vaults/my-vault" \
  --dns-name "https://my-vault.vault.azure.net/"
```

### SDK Example

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import workspace

client = WorkspaceClient()

# Create Databricks-managed scope
client.secrets.create_scope(
    scope="my-secrets",
    scope_backend_type=workspace.ScopeBackendType.DATABRICKS
)

print("Secret scope created!")
```

---

## List Secret Scopes

List all secret scopes available in the workspace.

### Endpoint

```
GET /api/2.0/secrets/scopes/list
```

### Example

```python
import requests

DATABRICKS_HOST = "https://<workspace>.cloud.databricks.com"
DATABRICKS_TOKEN = "dapi..."

headers = {
    "Authorization": f"Bearer {DATABRICKS_TOKEN}",
    "Content-Type": "application/json"
}

response = requests.get(
    f"{DATABRICKS_HOST}/api/2.0/secrets/scopes/list",
    headers=headers
)

scopes = response.json().get("scopes", [])

for scope in scopes:
    print(f"Scope: {scope['name']}")
    print(f"  Backend Type: {scope['backend_type']}")
```

### SDK Example

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# List all secret scopes
for scope in client.secrets.list_scopes():
    print(f"Scope: {scope.name}")
    print(f"  Backend Type: {scope.backend_type}")
```

### CLI Example

```bash
databricks secrets list-scopes
```

### Response

```json
{
  "scopes": [
    {
      "name": "my-secrets",
      "backend_type": "DATABRICKS"
    },
    {
      "name": "azure-keyvault-secrets",
      "backend_type": "AZURE_KEYVAULT"
    }
  ]
}
```

---

## Delete Secret Scope

Delete a secret scope and all secrets within it.

### Endpoint

```
POST /api/2.0/secrets/scopes/delete
```

### Request Body

```json
{
  "scope": "my-secrets"
}
```

### Example

```bash
# CLI (Recommended)
databricks secrets delete-scope --scope my-secrets
```

### SDK Example

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# Delete scope
client.secrets.delete_scope(scope="my-secrets")

print("Scope deleted!")
```

**Warning**: This permanently deletes the scope and all secrets within it.

---

## Put Secret

Store a secret value in a secret scope.

### Endpoint

```
POST /api/2.0/secrets/put
```

### Important Notes

- **Cannot set secret values via REST API** for security reasons
- **Must use CLI or notebook interface** to set secret values
- Secret values are never returned in API responses

### CLI Example (Recommended)

```bash
# Interactive (prompts for secret value)
databricks secrets put --scope my-secrets --key api-key

# From file
databricks secrets put --scope my-secrets --key api-key --string-value "secret-value"

# From stdin
echo "secret-value" | databricks secrets put --scope my-secrets --key api-key
```

### Notebook Example

```python
# In a Databricks notebook, you can use dbutils
dbutils.secrets.help()

# Note: You still need to use CLI to put secrets
# This is intentional for security
```

---

## List Secrets

List all secret keys in a scope (without values).

### Endpoint

```
GET /api/2.0/secrets/list
```

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| scope | string | Yes | The secret scope name |

### Example

```python
import requests

response = requests.get(
    f"{DATABRICKS_HOST}/api/2.0/secrets/list",
    headers=headers,
    params={"scope": "my-secrets"}
)

secrets = response.json().get("secrets", [])

for secret in secrets:
    print(f"Key: {secret['key']}")
    print(f"  Last Updated: {secret['last_updated_timestamp']}")
```

### SDK Example

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# List secrets in scope
for secret in client.secrets.list_secrets(scope="my-secrets"):
    print(f"Key: {secret.key}")
    print(f"  Last Updated: {secret.last_updated_timestamp}")
```

### CLI Example

```bash
databricks secrets list --scope my-secrets
```

### Response

```json
{
  "secrets": [
    {
      "key": "api-key",
      "last_updated_timestamp": 1699564800000
    },
    {
      "key": "database-password",
      "last_updated_timestamp": 1699564900000
    }
  ]
}
```

---

## Delete Secret

Delete a secret from a scope.

### Endpoint

```
POST /api/2.0/secrets/delete
```

### Request Body

```json
{
  "scope": "my-secrets",
  "key": "api-key"
}
```

### Example

```bash
# CLI (Recommended)
databricks secrets delete --scope my-secrets --key api-key
```

### SDK Example

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# Delete secret
client.secrets.delete_secret(scope="my-secrets", key="api-key")

print("Secret deleted!")
```

---

## Access Control (ACLs)

Manage permissions for secret scopes.

### Permission Levels

| Permission | Description |
|------------|-------------|
| READ | Can read secret values |
| WRITE | Can write secret values |
| MANAGE | Can manage scope and ACLs |

### Put ACL

Grant permission to a principal (user or group).

#### Endpoint

```
POST /api/2.0/secrets/acls/put
```

#### Request Body

```json
{
  "scope": "my-secrets",
  "principal": "user@example.com",
  "permission": "READ"
}
```

#### Example

```bash
# Grant READ permission
databricks secrets put-acl \
  --scope my-secrets \
  --principal user@example.com \
  --permission READ

# Grant MANAGE permission
databricks secrets put-acl \
  --scope my-secrets \
  --principal admins \
  --permission MANAGE
```

### Get ACL

Get permissions for a specific principal.

#### Endpoint

```
GET /api/2.0/secrets/acls/get
```

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| scope | string | Yes | The secret scope name |
| principal | string | Yes | User or group name |

#### Example

```bash
databricks secrets get-acl \
  --scope my-secrets \
  --principal user@example.com
```

### List ACLs

List all ACLs for a scope.

#### Endpoint

```
GET /api/2.0/secrets/acls/list
```

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| scope | string | Yes | The secret scope name |

#### Example

```python
import requests

response = requests.get(
    f"{DATABRICKS_HOST}/api/2.0/secrets/acls/list",
    headers=headers,
    params={"scope": "my-secrets"}
)

acls = response.json().get("items", [])

for acl in acls:
    print(f"Principal: {acl['principal']}")
    print(f"  Permission: {acl['permission']}")
```

#### CLI Example

```bash
databricks secrets list-acls --scope my-secrets
```

### Delete ACL

Remove permissions for a principal.

#### Endpoint

```
POST /api/2.0/secrets/acls/delete
```

#### Request Body

```json
{
  "scope": "my-secrets",
  "principal": "user@example.com"
}
```

#### Example

```bash
databricks secrets delete-acl \
  --scope my-secrets \
  --principal user@example.com
```

---

## Using Secrets in Notebooks

### Access Secrets with dbutils

```python
# Get secret value
api_key = dbutils.secrets.get(scope="my-secrets", key="api-key")

# Secret values are redacted in output
print(api_key)  # Output: [REDACTED]

# Use secret in code
import requests

response = requests.get(
    "https://api.example.com/data",
    headers={"Authorization": f"Bearer {api_key}"}
)
```

### Access Secrets in Spark Config

```python
# Set Spark configuration with secrets
spark.conf.set(
    "fs.s3a.access.key",
    dbutils.secrets.get(scope="aws-secrets", key="access-key")
)

spark.conf.set(
    "fs.s3a.secret.key",
    dbutils.secrets.get(scope="aws-secrets", key="secret-key")
)

# Read from S3
df = spark.read.csv("s3a://my-bucket/data.csv")
```

### Environment Variables

```python
import os

# Set environment variable with secret
os.environ["API_KEY"] = dbutils.secrets.get(scope="my-secrets", key="api-key")

# Use in subprocess or external libraries
import subprocess
result = subprocess.run(["some-command"], env=os.environ)
```

---

## Complete Examples

### Secrets Management Class

```python
from databricks.sdk import WorkspaceClient
from typing import List, Dict

class SecretsManager:
    """Manage Databricks secrets"""
    
    def __init__(self):
        self.client = WorkspaceClient()
    
    def create_scope(self, scope_name: str):
        """Create a secret scope"""
        try:
            self.client.secrets.create_scope(scope=scope_name)
            print(f"✓ Created scope: {scope_name}")
        except Exception as e:
            print(f"✗ Error creating scope: {e}")
    
    def list_scopes(self) -> List[Dict]:
        """List all secret scopes"""
        scopes = []
        for scope in self.client.secrets.list_scopes():
            scopes.append({
                "name": scope.name,
                "backend_type": scope.backend_type
            })
        return scopes
    
    def list_secrets(self, scope: str) -> List[str]:
        """List secret keys in a scope"""
        keys = []
        try:
            for secret in self.client.secrets.list_secrets(scope=scope):
                keys.append(secret.key)
        except Exception as e:
            print(f"✗ Error listing secrets: {e}")
        return keys
    
    def delete_secret(self, scope: str, key: str):
        """Delete a secret"""
        try:
            self.client.secrets.delete_secret(scope=scope, key=key)
            print(f"✓ Deleted secret: {scope}/{key}")
        except Exception as e:
            print(f"✗ Error deleting secret: {e}")
    
    def grant_access(self, scope: str, principal: str, permission: str = "READ"):
        """Grant access to a scope"""
        # Note: ACL management typically requires CLI
        print(f"Use CLI: databricks secrets put-acl --scope {scope} --principal {principal} --permission {permission}")
    
    def audit_secrets(self):
        """Audit all secrets in workspace"""
        print("Secret Scope Audit")
        print("=" * 60)
        
        for scope in self.list_scopes():
            print(f"\nScope: {scope['name']} ({scope['backend_type']})")
            secrets = self.list_secrets(scope['name'])
            print(f"  Secrets: {len(secrets)}")
            for key in secrets:
                print(f"    - {key}")

# Usage
manager = SecretsManager()

# List all scopes
scopes = manager.list_scopes()
for scope in scopes:
    print(f"Scope: {scope['name']}")

# List secrets in a scope
secrets = manager.list_secrets("my-secrets")
print(f"Found {len(secrets)} secrets")

# Audit all secrets
manager.audit_secrets()
```

### Database Connection with Secrets

```python
import psycopg2
from databricks.sdk import WorkspaceClient

def connect_to_database():
    """Connect to PostgreSQL using secrets"""
    
    # Get credentials from secrets
    host = dbutils.secrets.get(scope="db-secrets", key="host")
    port = dbutils.secrets.get(scope="db-secrets", key="port")
    database = dbutils.secrets.get(scope="db-secrets", key="database")
    username = dbutils.secrets.get(scope="db-secrets", key="username")
    password = dbutils.secrets.get(scope="db-secrets", key="password")
    
    # Connect to database
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=username,
        password=password
    )
    
    return conn

# Use connection
conn = connect_to_database()
cursor = conn.cursor()
cursor.execute("SELECT * FROM users LIMIT 10")
results = cursor.fetchall()

conn.close()
```

### API Integration with Secrets

```python
import requests

class APIClient:
    """API client using secrets for authentication"""
    
    def __init__(self, scope: str):
        self.api_key = dbutils.secrets.get(scope=scope, key="api-key")
        self.api_url = dbutils.secrets.get(scope=scope, key="api-url")
    
    def make_request(self, endpoint: str, method: str = "GET", **kwargs):
        """Make authenticated API request"""
        url = f"{self.api_url}/{endpoint}"
        
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.api_key}"
        
        response = requests.request(
            method,
            url,
            headers=headers,
            **kwargs
        )
        
        response.raise_for_status()
        return response.json()
    
    def get_data(self, resource_id: str):
        """Get data from API"""
        return self.make_request(f"data/{resource_id}")
    
    def post_data(self, data: dict):
        """Post data to API"""
        return self.make_request(
            "data",
            method="POST",
            json=data
        )

# Usage
client = APIClient(scope="api-secrets")
data = client.get_data("12345")
print(data)
```

### S3 Access with Secrets

```python
# Mount S3 bucket using secrets
def mount_s3_bucket():
    """Mount S3 bucket with credentials from secrets"""
    
    bucket_name = "my-data-bucket"
    mount_point = f"/mnt/{bucket_name}"
    
    # Get AWS credentials from secrets
    access_key = dbutils.secrets.get(scope="aws-secrets", key="access-key")
    secret_key = dbutils.secrets.get(scope="aws-secrets", key="secret-key")
    
    # Check if already mounted
    if any(mount.mountPoint == mount_point for mount in dbutils.fs.mounts()):
        print(f"Already mounted: {mount_point}")
        return
    
    # Mount S3 bucket
    dbutils.fs.mount(
        source=f"s3a://{bucket_name}",
        mount_point=mount_point,
        extra_configs={
            "fs.s3a.access.key": access_key,
            "fs.s3a.secret.key": secret_key
        }
    )
    
    print(f"✓ Mounted {bucket_name} to {mount_point}")

# Mount bucket
mount_s3_bucket()

# Access data
df = spark.read.csv("/mnt/my-data-bucket/data.csv")
display(df)
```

---

## Best Practices

### Secret Management

```python
# Good: Use descriptive secret names
dbutils.secrets.get(scope="production-db", key="postgres-password")

# Good: Organize secrets by environment
# - dev-secrets
# - staging-secrets  
# - production-secrets

# Good: Rotate secrets regularly
# Implement automated secret rotation

# Bad: Hardcoding secrets
# api_key = "abc123"  # Don't do this!
```

### Scope Organization

```bash
# Good: Organize by purpose
my-app-dev-secrets
my-app-prod-secrets
shared-api-keys
database-credentials

# Good: Use consistent naming
{project}-{environment}-secrets
```

### Access Control

```bash
# Good: Principle of least privilege
# Grant only READ to most users
databricks secrets put-acl --scope prod-secrets --principal developers --permission READ

# Grant MANAGE only to admins
databricks secrets put-acl --scope prod-secrets --principal admins --permission MANAGE
```

### Security

```python
# Good: Never print or log secret values
api_key = dbutils.secrets.get(scope="api", key="key")
# Don't: print(api_key)
# Don't: logger.info(f"API Key: {api_key}")

# Good: Use secrets in configuration only
spark.conf.set("api.key", dbutils.secrets.get(scope="api", key="key"))

# Good: Delete secrets when no longer needed
client.secrets.delete_secret(scope="temp-secrets", key="old-key")
```

---

## Troubleshooting

### Cannot Create Scope

**Problem**: Permission denied when creating scope

**Solution**:
```python
# Only workspace admins can create scopes
# Contact your workspace administrator
# Or use CLI with proper authentication
```

### Cannot Access Secret

**Problem**: Secret not found or access denied

**Solution**:
```python
# Check if scope exists
scopes = [s.name for s in client.secrets.list_scopes()]
print(f"Available scopes: {scopes}")

# Check if you have permission
# Ask admin to grant READ permission:
# databricks secrets put-acl --scope <scope> --principal <user> --permission READ
```

### Secret Value Not Working

**Problem**: Secret value seems incorrect

**Solution**:
```python
# Verify secret was set correctly
# Use CLI to update:
# databricks secrets put --scope my-secrets --key api-key

# Check for whitespace or encoding issues
api_key = dbutils.secrets.get(scope="my-secrets", key="api-key").strip()
```

### Azure Key Vault Issues

**Problem**: Cannot access Azure Key Vault-backed scope

**Solution**:
```bash
# Verify Azure Key Vault configuration
# Check resource ID and DNS name are correct
# Ensure Databricks service principal has access to Key Vault
# Grant "Get" and "List" permissions in Key Vault access policies
```

---

## Related Documentation

- [API Overview](overview.md)
- [Authentication Guide](../getting-started/authentication.md)
- [Python SDK Guide](../sdk/python.md)
- [Security Best Practices](../best-practices/security.md)

## Additional Resources

- [Official Secrets Documentation](https://docs.databricks.com/security/secrets/index.html)
- [Secrets API Reference](https://docs.databricks.com/api/workspace/secrets)
- [Azure Key Vault Integration](https://docs.databricks.com/security/secrets/secret-scopes.html#azure-key-vault-backed-scopes)
- [AWS Secrets Manager Integration](https://docs.databricks.com/security/secrets/secret-scopes.html#aws-secrets-manager-backed-scopes)