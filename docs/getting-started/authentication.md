# Authentication Guide for Databricks

## Overview

Authentication is the process of verifying your identity when accessing Databricks resources. This guide covers all authentication methods available for Databricks APIs, CLI, SDK, and notebooks.

## Authentication Methods

### 1. Personal Access Tokens (PAT)

Personal Access Tokens are the most common authentication method for programmatic access to Databricks.

#### Creating a Personal Access Token

**Steps:**
1. Log in to your Databricks workspace
2. Click on your username in the top right corner
3. Select **User Settings**
4. Go to the **Access Tokens** tab
5. Click **Generate New Token**
6. Enter a comment (description) and optionally set an expiration
7. Click **Generate**
8. **Copy and save the token immediately** (you won't see it again)

#### Using Personal Access Tokens

**In Python:**
```python
import requests

DATABRICKS_INSTANCE = "https://<workspace-url>.cloud.databricks.com"
DATABRICKS_TOKEN = "dapi..."  # Your token

headers = {
    "Authorization": f"Bearer {DATABRICKS_TOKEN}"
}

response = requests.get(
    f"{DATABRICKS_INSTANCE}/api/2.0/clusters/list",
    headers=headers
)

print(response.json())
```

**With Databricks SDK:**
```python
from databricks.sdk import WorkspaceClient

# Method 1: Direct token
client = WorkspaceClient(
    host="https://<workspace-url>.cloud.databricks.com",
    token="dapi..."
)

# Method 2: Environment variables
# Set DATABRICKS_HOST and DATABRICKS_TOKEN environment variables
client = WorkspaceClient()

# List clusters
for cluster in client.clusters.list():
    print(f"Cluster: {cluster.cluster_name}")
```

**With cURL:**
```bash
curl -X GET \
  https://<workspace-url>.cloud.databricks.com/api/2.0/clusters/list \
  -H "Authorization: Bearer dapi..."
```

#### Best Practices for PATs

- **Never hardcode tokens** in source code
- **Use environment variables** or secure vaults
- **Set expiration dates** for tokens
- **Use different tokens** for different applications
- **Rotate tokens regularly**
- **Revoke unused tokens** immediately
- **Use service principals** for production workloads

### 2. OAuth 2.0 (OAuth Machine-to-Machine)

OAuth provides more secure, temporary credentials for applications.

#### OAuth for Applications

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.oauth import ClientCredentials

# OAuth M2M authentication
credentials = ClientCredentials(
    client_id="your-client-id",
    client_secret="your-client-secret",
    token_url="https://<workspace-url>.cloud.databricks.com/oidc/v1/token"
)

client = WorkspaceClient(
    host="https://<workspace-url>.cloud.databricks.com",
    credentials_provider=credentials
)

# Use the client
clusters = client.clusters.list()
```

#### OAuth User Flow

For interactive applications:

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.oauth import OAuthClient

# Initiate OAuth flow
oauth_client = OAuthClient(
    host="https://<workspace-url>.cloud.databricks.com",
    client_id="your-client-id",
    redirect_url="http://localhost:8020"
)

# This will open a browser for user consent
client = WorkspaceClient(
    host="https://<workspace-url>.cloud.databricks.com",
    oauth_client=oauth_client
)
```

### 3. Azure Active Directory (Azure AD)

For Azure Databricks workspaces, you can use Azure AD authentication.

#### Using Azure AD Tokens

```python
from azure.identity import DefaultAzureCredential
from databricks.sdk import WorkspaceClient

# Azure AD authentication
credential = DefaultAzureCredential()
token = credential.get_token("2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default")

client = WorkspaceClient(
    host="https://<workspace-url>.azuredatabricks.net",
    azure_workspace_resource_id="/subscriptions/.../resourceGroups/.../providers/Microsoft.Databricks/workspaces/...",
    azure_client_id="your-client-id",
    azure_client_secret="your-client-secret",
    azure_tenant_id="your-tenant-id"
)
```

#### Using Managed Identity (Azure)

```python
from databricks.sdk import WorkspaceClient

# System-assigned managed identity
client = WorkspaceClient(
    host="https://<workspace-url>.azuredatabricks.net",
    azure_use_msi=True
)

# User-assigned managed identity
client = WorkspaceClient(
    host="https://<workspace-url>.azuredatabricks.net",
    azure_use_msi=True,
    azure_client_id="managed-identity-client-id"
)
```

### 4. AWS IAM Roles

For AWS Databricks deployments, use IAM roles.

#### Using IAM Instance Profiles

```python
from databricks.sdk import WorkspaceClient

# Automatically uses IAM role from EC2 instance
client = WorkspaceClient(
    host="https://<workspace-url>.cloud.databricks.com",
    aws_profile="your-aws-profile"  # Optional
)
```

#### Cross-Account IAM Roles

```python
import boto3
from databricks.sdk import WorkspaceClient

# Assume role for Databricks access
sts = boto3.client('sts')
assumed_role = sts.assume_role(
    RoleArn='arn:aws:iam::account-id:role/databricks-role',
    RoleSessionName='databricks-session'
)

credentials = assumed_role['Credentials']

# Use temporary credentials
client = WorkspaceClient(
    host="https://<workspace-url>.cloud.databricks.com",
    # Use the temporary credentials appropriately
)
```

### 5. Service Principals

Service principals are recommended for automated workloads and CI/CD pipelines.

#### Creating a Service Principal

**Via Databricks UI:**
1. Go to **Admin Console**
2. Select **Service Principals**
3. Click **Add Service Principal**
4. Enter application ID and display name
5. Generate a secret for the service principal

**Via API:**
```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# Create service principal
sp = client.service_principals.create(
    display_name="my-app-service-principal",
    active=True
)

print(f"Service Principal ID: {sp.id}")
```

#### Using Service Principals

```python
from databricks.sdk import WorkspaceClient

# Authenticate as service principal
client = WorkspaceClient(
    host="https://<workspace-url>.cloud.databricks.com",
    client_id="service-principal-app-id",
    client_secret="service-principal-secret"
)

# Service principal operations
clusters = client.clusters.list()
```

## Environment Variables

### Standard Environment Variables

Set these environment variables to avoid hardcoding credentials:

```bash
# Host
export DATABRICKS_HOST="https://<workspace-url>.cloud.databricks.com"

# Personal Access Token
export DATABRICKS_TOKEN="dapi..."

# OAuth Client Credentials
export DATABRICKS_CLIENT_ID="your-client-id"
export DATABRICKS_CLIENT_SECRET="your-client-secret"

# Azure AD
export DATABRICKS_AZURE_TENANT_ID="your-tenant-id"
export DATABRICKS_AZURE_CLIENT_ID="your-client-id"
export DATABRICKS_AZURE_CLIENT_SECRET="your-client-secret"

# AWS Profile
export AWS_PROFILE="your-aws-profile"
```

### Using Environment Variables in Code

```python
import os
from databricks.sdk import WorkspaceClient

# Automatically reads from environment variables
client = WorkspaceClient()

# Or explicitly
client = WorkspaceClient(
    host=os.environ.get("DATABRICKS_HOST"),
    token=os.environ.get("DATABRICKS_TOKEN")
)
```

## Configuration Files

### Databricks CLI Configuration

The Databricks CLI uses a configuration file located at `~/.databrickscfg`:

```ini
[DEFAULT]
host = https://<workspace-url>.cloud.databricks.com
token = dapi...

[production]
host = https://prod-workspace.cloud.databricks.com
token = dapi...

[development]
host = https://dev-workspace.cloud.databricks.com
token = dapi...
```

#### Using Configuration Profiles

```bash
# Use default profile
databricks clusters list

# Use specific profile
databricks clusters list --profile production

# Set default profile
export DATABRICKS_CONFIG_PROFILE=production
```

#### Creating Configuration via CLI

```bash
# Interactive configuration
databricks configure --token

# Non-interactive
databricks configure --token --host https://<workspace>.cloud.databricks.com
```

### SDK Configuration File

```python
from databricks.sdk import WorkspaceClient

# Use specific profile from config file
client = WorkspaceClient(profile="production")

# Config file location: ~/.databrickscfg
```

## Authentication in Notebooks

### Accessing Current User Token

Inside a Databricks notebook, you can access credentials:

```python
# Get current user's context
dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

# Get workspace URL
dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()
```

### Using Secrets in Notebooks

```python
# Store token in secret scope
token = dbutils.secrets.get(scope="my-scope", key="databricks-token")

# Use in API calls
import requests

response = requests.get(
    f"https://<workspace>.cloud.databricks.com/api/2.0/clusters/list",
    headers={"Authorization": f"Bearer {token}"}
)
```

## Security Best Practices

### Token Management

1. **Use Secret Scopes**
   ```python
   # Store tokens in Databricks secrets
   token = dbutils.secrets.get(scope="tokens", key="api-token")
   
   from databricks.sdk import WorkspaceClient
   client = WorkspaceClient(
       host="https://<workspace>.cloud.databricks.com",
       token=token
   )
   ```

2. **Rotate Tokens Regularly**
   ```python
   # Generate new token and update secrets
   # Revoke old token after transition period
   ```

3. **Use Least Privilege**
   - Grant minimum necessary permissions
   - Use workspace access control
   - Implement fine-grained Unity Catalog permissions

### Secrets Management

#### Azure Key Vault Integration

```python
# Create secret scope backed by Azure Key Vault
# Via Databricks UI: User Settings > Secret Scopes

# Access secrets
password = dbutils.secrets.get(scope="azure-keyvault", key="db-password")
```

#### AWS Secrets Manager Integration

```python
# Create secret scope backed by AWS Secrets Manager
# Via Databricks API or UI

# Access secrets
api_key = dbutils.secrets.get(scope="aws-secrets", key="api-key")
```

#### Databricks-Managed Secrets

```bash
# Create secret scope
databricks secrets create-scope --scope my-secrets

# Add secret
databricks secrets put --scope my-secrets --key my-token

# List secrets
databricks secrets list --scope my-secrets

# Delete secret
databricks secrets delete --scope my-secrets --key my-token
```

### Network Security

```python
# Use private endpoints (Azure Private Link, AWS PrivateLink)
# Configure IP access lists in workspace settings
# Enable secure cluster connectivity
```

## Troubleshooting

### Common Authentication Errors

#### 401 Unauthorized

**Problem:** Invalid or expired token

**Solution:**
```python
# Verify token is correct
# Check token hasn't expired
# Regenerate token if needed

# Test authentication
from databricks.sdk import WorkspaceClient

try:
    client = WorkspaceClient()
    client.current_user.me()
    print("Authentication successful!")
except Exception as e:
    print(f"Authentication failed: {e}")
```

#### 403 Forbidden

**Problem:** Insufficient permissions

**Solution:**
- Check user/service principal has necessary permissions
- Verify cluster access control settings
- Ensure workspace access is granted

```python
# Check current user permissions
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()
user = client.current_user.me()
print(f"Current user: {user.user_name}")
print(f"Active: {user.active}")
```

#### Connection Errors

**Problem:** Cannot reach Databricks workspace

**Solution:**
```python
import socket

# Verify DNS resolution
hostname = "<workspace>.cloud.databricks.com"
try:
    ip = socket.gethostbyname(hostname)
    print(f"Resolved {hostname} to {ip}")
except socket.gaierror as e:
    print(f"DNS resolution failed: {e}")

# Check network connectivity
# Verify firewall rules
# Confirm VPN connection if required
```

### Token Validation

```python
from databricks.sdk import WorkspaceClient

def validate_token(host, token):
    """Validate Databricks token"""
    try:
        client = WorkspaceClient(host=host, token=token)
        user = client.current_user.me()
        print(f"✓ Token valid for user: {user.user_name}")
        return True
    except Exception as e:
        print(f"✗ Token validation failed: {e}")
        return False

# Usage
validate_token(
    host="https://<workspace>.cloud.databricks.com",
    token="dapi..."
)
```

## Authentication Flow Diagram

```
User/Application
    |
    ├──> Personal Access Token ──────────────> Databricks API
    |
    ├──> OAuth 2.0
    |      ├──> Client Credentials ──────────> Token Endpoint
    |      └──> Authorization Code ──────────> Browser Flow
    |
    ├──> Azure AD
    |      ├──> Service Principal ────────────> Azure Token
    |      └──> Managed Identity ─────────────> Azure Token
    |
    └──> AWS IAM
           ├──> Instance Profile ─────────────> AWS STS
           └──> Cross-Account Role ───────────> AWS STS
                                                   |
                                                   v
                                         Databricks Workspace
```

## Code Examples

### Complete Authentication Example

```python
import os
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config

class DatabricksAuthenticator:
    """Handle multiple authentication methods"""
    
    @staticmethod
    def from_token(host: str, token: str) -> WorkspaceClient:
        """Authenticate with personal access token"""
        return WorkspaceClient(host=host, token=token)
    
    @staticmethod
    def from_env() -> WorkspaceClient:
        """Authenticate using environment variables"""
        return WorkspaceClient()
    
    @staticmethod
    def from_profile(profile: str) -> WorkspaceClient:
        """Authenticate using configuration profile"""
        return WorkspaceClient(profile=profile)
    
    @staticmethod
    def from_service_principal(
        host: str,
        client_id: str,
        client_secret: str
    ) -> WorkspaceClient:
        """Authenticate as service principal"""
        return WorkspaceClient(
            host=host,
            client_id=client_id,
            client_secret=client_secret
        )

# Usage examples
if __name__ == "__main__":
    # Method 1: Direct token
    client1 = DatabricksAuthenticator.from_token(
        host="https://<workspace>.cloud.databricks.com",
        token=os.environ.get("DATABRICKS_TOKEN")
    )
    
    # Method 2: Environment variables
    client2 = DatabricksAuthenticator.from_env()
    
    # Method 3: Configuration profile
    client3 = DatabricksAuthenticator.from_profile("production")
    
    # Method 4: Service principal
    client4 = DatabricksAuthenticator.from_service_principal(
        host=os.environ.get("DATABRICKS_HOST"),
        client_id=os.environ.get("DATABRICKS_CLIENT_ID"),
        client_secret=os.environ.get("DATABRICKS_CLIENT_SECRET")
    )
    
    # Test connection
    try:
        user = client1.current_user.me()
        print(f"✓ Authenticated as: {user.user_name}")
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
```

## Next Steps

After configuring authentication:

1. **[Quick Start Guide](quickstart.md)**: Create your first cluster
2. **[API Overview](../api/overview.md)**: Learn about REST APIs
3. **[Python SDK Guide](../sdk/python.md)**: Use the SDK effectively
4. **[Security Best Practices](../best-practices/security.md)**: Secure your deployments

## Related Documentation

- [Setup Guide](setup.md)
- [Secrets Management](../api/secrets.md)
- [Unity Catalog Security](../api/unity-catalog.md)
- [Best Practices: Security](../best-practices/security.md)

## Additional Resources

- [Databricks Authentication Documentation](https://docs.databricks.com/dev-tools/auth.html)
- [Databricks SDK Python](https://github.com/databricks/databricks-sdk-py)
- [OAuth 2.0 Specification](https://oauth.net/2/)
- [Azure AD Integration](https://docs.databricks.com/administration-guide/users-groups/single-sign-on/azure-ad.html)