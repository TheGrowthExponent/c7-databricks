# Databricks Setup and Configuration Guide

## Overview

This guide walks you through setting up your Databricks environment, from initial workspace access to configuring development tools and connections.

## Prerequisites

- Access to a Databricks workspace (AWS, Azure, or GCP)
- Modern web browser (Chrome, Firefox, Safari, or Edge)
- Administrator permissions (for workspace setup)
- Basic understanding of cloud platforms

## Workspace Setup

### Accessing Your Workspace

#### AWS Databricks
```
URL Format: https://<workspace-id>.cloud.databricks.com
Example: https://dbc-abc12345-6789.cloud.databricks.com
```

#### Azure Databricks
```
URL Format: https://adb-<workspace-id>.<region>.azuredatabricks.net
Example: https://adb-1234567890123456.7.azuredatabricks.net
```

#### Google Cloud Platform Databricks
```
URL Format: https://<workspace-id>.gcp.databricks.com
Example: https://1234567890123456.7.gcp.databricks.com
```

### First-Time Login

1. Navigate to your workspace URL
2. Log in with your credentials:
   - **Email/Password**: For direct authentication
   - **SSO**: For enterprise single sign-on
   - **Azure AD**: For Azure Active Directory
   - **Google OAuth**: For Google authentication

3. Accept terms of service if prompted
4. Complete any required MFA/2FA setup

## User Profile Configuration

### Setting Up Your Profile

1. Click on your username in the top-right corner
2. Select **User Settings**
3. Configure:
   - **Display Name**: Your preferred name
   - **Email**: Contact email
   - **Avatar**: Profile picture
   - **Notification Preferences**: Email alerts

### Generating Access Tokens

Personal Access Tokens are required for API and CLI access:

1. Go to **User Settings**
2. Click **Access Tokens** tab
3. Click **Generate New Token**
4. Configure token:
   - **Comment**: Description (e.g., "Development Token")
   - **Lifetime**: Expiration period (recommend 90 days)
5. Click **Generate**
6. **Copy and save the token immediately**

**Important:** Store tokens securely - you cannot retrieve them later.

```bash
# Store token securely
export DATABRICKS_TOKEN="dapi1234567890abcdef..."
export DATABRICKS_HOST="https://<workspace>.cloud.databricks.com"

# Or add to ~/.bashrc or ~/.zshrc
echo 'export DATABRICKS_TOKEN="dapi..."' >> ~/.bashrc
echo 'export DATABRICKS_HOST="https://..."' >> ~/.bashrc
```

## Development Tools Setup

### 1. Databricks CLI

#### Installation

**Using pip:**
```bash
pip install databricks-cli
```

**Using conda:**
```bash
conda install -c databricks databricks-cli
```

**Verify installation:**
```bash
databricks --version
```

#### Configuration

**Interactive setup:**
```bash
databricks configure --token
```

**Manual configuration:**
Create `~/.databrickscfg`:
```ini
[DEFAULT]
host = https://<workspace>.cloud.databricks.com
token = dapi...

[dev]
host = https://dev-workspace.cloud.databricks.com
token = dapi...

[prod]
host = https://prod-workspace.cloud.databricks.com
token = dapi...
```

**Test CLI:**
```bash
databricks workspace ls /
databricks clusters list
```

### 2. Databricks SDK (Python)

#### Installation

```bash
pip install databricks-sdk
```

**With specific features:**
```bash
# With all optional dependencies
pip install databricks-sdk[all]

# For development
pip install databricks-sdk[dev]
```

#### Configuration

**Using environment variables:**
```python
import os
from databricks.sdk import WorkspaceClient

# Set environment variables first
os.environ["DATABRICKS_HOST"] = "https://<workspace>.cloud.databricks.com"
os.environ["DATABRICKS_TOKEN"] = "dapi..."

# Create client (reads from environment)
client = WorkspaceClient()
```

**Using direct configuration:**
```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient(
    host="https://<workspace>.cloud.databricks.com",
    token="dapi..."
)

# Test connection
print(client.current_user.me())
```

**Using configuration file:**
```python
from databricks.sdk import WorkspaceClient

# Uses ~/.databrickscfg
client = WorkspaceClient(profile="dev")
```

### 3. Databricks Connect

Databricks Connect allows you to connect your IDE to Databricks clusters.

#### Installation

```bash
# Install Databricks Connect (must match cluster version)
pip install databricks-connect==13.3.*
```

#### Configuration

```bash
# Configure Databricks Connect
databricks-connect configure

# You'll be prompted for:
# - Databricks host URL
# - Personal access token
# - Cluster ID
# - Organization ID (for AWS only)
# - Port (default: 15001)
```

**Configuration file location:**
- Linux/Mac: `~/.databricks-connect`
- Windows: `%USERPROFILE%\.databricks-connect`

**Test connection:**
```python
from databricks.connect import DatabricksSession

spark = DatabricksSession.builder.getOrCreate()
df = spark.range(10)
df.show()
```

### 4. Git Integration

#### Connecting to Git Repositories

1. Go to **Repos** in the sidebar
2. Click **Add Repo**
3. Select your Git provider:
   - GitHub
   - GitLab
   - Bitbucket
   - Azure DevOps
4. Authorize Databricks to access your repositories
5. Select repository to clone

#### Git Configuration in Notebooks

```python
# Clone a repository
dbutils.repos.create(
    url="https://github.com/username/repo.git",
    provider="github",
    path="/Repos/<username>/repo"
)

# Update repository
dbutils.repos.update(
    path="/Repos/<username>/repo",
    branch="main"
)
```

### 5. IDE Integration

#### Visual Studio Code

**Install extensions:**
- Databricks extension
- Python extension
- Jupyter extension

**Configure:**
1. Install Databricks extension from VS Code marketplace
2. Open command palette (Ctrl+Shift+P)
3. Select "Databricks: Configure Workspace"
4. Enter workspace URL and token

#### PyCharm

**Setup:**
1. Install Databricks plugin
2. Configure remote interpreter
3. Set up Databricks Connect
4. Configure project SDK

#### Jupyter Notebook

```bash
# Install Jupyter
pip install jupyter

# Install Databricks kernel
pip install databricks-connect

# Start Jupyter
jupyter notebook
```

**In notebook:**
```python
from databricks.connect import DatabricksSession

spark = DatabricksSession.builder.getOrCreate()
```

## Workspace Configuration

### Creating Folders

**Via UI:**
1. Navigate to **Workspace**
2. Right-click in the folder tree
3. Select **Create > Folder**
4. Enter folder name

**Via CLI:**
```bash
databricks workspace mkdirs /Users/<username>/my-project
```

**Via SDK:**
```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()
client.workspace.mkdirs(path="/Users/<username>/my-project")
```

### Setting Up Secret Scopes

Secret scopes store sensitive information like API keys and passwords.

**Via CLI:**
```bash
# Create secret scope
databricks secrets create-scope --scope my-secrets

# Add secret
databricks secrets put --scope my-secrets --key api-key

# List secrets
databricks secrets list --scope my-secrets
```

**Via SDK:**
```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# Create scope (Databricks-managed)
# Note: Must use CLI or API, not available via SDK directly

# Put secret (via CLI or use dbutils in notebook)
```

**In notebooks:**
```python
# Access secrets
api_key = dbutils.secrets.get(scope="my-secrets", key="api-key")
```

### Configuring Cluster Policies

Cluster policies control cluster creation to manage costs and enforce standards.

**Create policy via UI:**
1. Go to **Admin Console**
2. Select **Cluster Policies**
3. Click **Create Cluster Policy**
4. Define policy JSON

**Example policy:**
```json
{
  "spark_version": {
    "type": "fixed",
    "value": "13.3.x-scala2.12"
  },
  "node_type_id": {
    "type": "allowlist",
    "values": ["i3.xlarge", "i3.2xlarge"]
  },
  "autoscale": {
    "type": "fixed",
    "value": {
      "min_workers": 2,
      "max_workers": 8
    }
  },
  "autotermination_minutes": {
    "type": "fixed",
    "value": 30
  }
}
```

## Storage Configuration

### Mounting Cloud Storage

#### AWS S3

```python
# Mount S3 bucket
dbutils.fs.mount(
    source="s3a://bucket-name/path",
    mount_point="/mnt/my-data",
    extra_configs={
        "fs.s3a.access.key": dbutils.secrets.get("aws", "access-key"),
        "fs.s3a.secret.key": dbutils.secrets.get("aws", "secret-key")
    }
)

# Verify mount
display(dbutils.fs.ls("/mnt/my-data"))
```

#### Azure Blob Storage

```python
# Mount Azure Blob Storage
dbutils.fs.mount(
    source="wasbs://container@storageaccount.blob.core.windows.net",
    mount_point="/mnt/azure-data",
    extra_configs={
        "fs.azure.account.key.storageaccount.blob.core.windows.net": 
            dbutils.secrets.get("azure", "storage-key")
    }
)
```

#### Google Cloud Storage

```python
# Mount GCS bucket
dbutils.fs.mount(
    source="gs://bucket-name/path",
    mount_point="/mnt/gcs-data",
    extra_configs={
        "google.cloud.auth.service.account.enable": "true",
        "google.cloud.auth.service.account.json.keyfile": 
            dbutils.secrets.get("gcp", "service-account-key")
    }
)
```

### Using Unity Catalog

Unity Catalog provides centralized data governance.

**Enable Unity Catalog:**
1. Go to **Admin Console**
2. Select **Unity Catalog**
3. Follow setup wizard

**Create catalog and schema:**
```sql
-- Create catalog
CREATE CATALOG IF NOT EXISTS my_catalog;

-- Use catalog
USE CATALOG my_catalog;

-- Create schema
CREATE SCHEMA IF NOT EXISTS my_schema;

-- Use schema
USE SCHEMA my_schema;
```

**Grant permissions:**
```sql
-- Grant catalog access
GRANT USE CATALOG ON CATALOG my_catalog TO `user@example.com`;

-- Grant schema access
GRANT USE SCHEMA ON SCHEMA my_catalog.my_schema TO `user@example.com`;

-- Grant table access
GRANT SELECT ON TABLE my_catalog.my_schema.my_table TO `user@example.com`;
```

## Network Configuration

### IP Access Lists

Restrict workspace access by IP address:

1. Go to **Admin Console**
2. Select **IP Access Lists**
3. Click **Add**
4. Configure:
   - **List Name**: Description
   - **IP Addresses/CIDR**: Allowed ranges
   - **Enabled**: Activate list

**Example:**
```
# Office network
10.0.0.0/8

# VPN gateway
203.0.113.0/24

# Specific IP
198.51.100.42
```

### Private Endpoints

**AWS PrivateLink:**
- Configure VPC endpoints in AWS console
- Link to Databricks workspace
- Update security groups

**Azure Private Link:**
- Enable Private Link in Azure portal
- Create private endpoint
- Configure DNS resolution

## Monitoring and Logging

### Enable Audit Logs

**Via Admin Console:**
1. Go to **Admin Console**
2. Select **Workspace Settings**
3. Enable **Audit Logs**
4. Configure delivery to:
   - AWS S3
   - Azure Blob Storage
   - Google Cloud Storage

### Set Up Cost Attribution Tags

```python
# Add tags to clusters
cluster_config = {
    "cluster_name": "my-cluster",
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "i3.xlarge",
    "custom_tags": {
        "Project": "data-pipeline",
        "Environment": "production",
        "CostCenter": "engineering"
    }
}
```

## Best Practices

### Security
- ✅ Rotate access tokens regularly (every 90 days)
- ✅ Use secret scopes for sensitive data
- ✅ Enable IP access lists for production
- ✅ Use service principals for automated workloads
- ✅ Enable audit logging

### Cost Management
- ✅ Set autotermination on clusters (30 minutes recommended)
- ✅ Use cluster policies to enforce limits
- ✅ Implement cost attribution tags
- ✅ Use spot/preemptible instances for non-critical workloads
- ✅ Right-size clusters based on workload

### Organization
- ✅ Use folders to organize notebooks and files
- ✅ Integrate with Git for version control
- ✅ Establish naming conventions
- ✅ Document workspace structure
- ✅ Use Unity Catalog for data governance

## Verification Checklist

After completing setup, verify:

- [ ] Can access workspace via browser
- [ ] Personal access token generated and stored securely
- [ ] Databricks CLI installed and configured
- [ ] Databricks SDK installed and working
- [ ] Can create and list clusters
- [ ] Can run simple notebook
- [ ] Git integration configured (if needed)
- [ ] Secret scopes created
- [ ] Storage mounted (if needed)
- [ ] Team members have appropriate access

## Troubleshooting

### Cannot Access Workspace

**Problem:** Workspace URL not loading

**Solutions:**
- Verify URL format is correct
- Check network connectivity
- Confirm IP access list settings
- Try incognito/private browsing mode

### CLI Authentication Fails

**Problem:** `databricks clusters list` returns 401 error

**Solutions:**
```bash
# Verify token
echo $DATABRICKS_TOKEN

# Reconfigure CLI
databricks configure --token

# Test with curl
curl -H "Authorization: Bearer $DATABRICKS_TOKEN" \
  $DATABRICKS_HOST/api/2.0/clusters/list
```

### SDK Connection Issues

**Problem:** SDK cannot connect to workspace

**Solutions:**
```python
# Verify configuration
import os
print(f"Host: {os.environ.get('DATABRICKS_HOST')}")
print(f"Token: {os.environ.get('DATABRICKS_TOKEN')[:10]}...")

# Test connection
from databricks.sdk import WorkspaceClient
try:
    client = WorkspaceClient()
    user = client.current_user.me()
    print(f"Connected as: {user.user_name}")
except Exception as e:
    print(f"Connection failed: {e}")
```

## Next Steps

Now that your environment is configured:

1. **[Authentication Guide](authentication.md)**: Understand authentication methods
2. **[Quick Start Guide](quickstart.md)**: Create your first cluster
3. **[Python SDK Guide](../sdk/python.md)**: Learn SDK usage
4. **[API Documentation](../api/overview.md)**: Explore REST APIs

## Related Documentation

- [Introduction](introduction.md)
- [Authentication](authentication.md)
- [Clusters API](../api/clusters.md)
- [Security Best Practices](../best-practices/security.md)

## Additional Resources

- [Databricks Workspace Setup](https://docs.databricks.com/workspace/index.html)
- [Databricks CLI Documentation](https://docs.databricks.com/dev-tools/cli/index.html)
- [Databricks SDK Documentation](https://databricks-sdk-py.readthedocs.io/)
- [Unity Catalog Setup](https://docs.databricks.com/data-governance/unity-catalog/index.html)