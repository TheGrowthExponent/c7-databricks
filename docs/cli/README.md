# Databricks CLI Reference

## Overview

The Databricks CLI (Command Line Interface) provides a convenient way to interact with Databricks workspaces, manage resources, and automate workflows. This guide covers installation, configuration, and common commands.

## Table of Contents

1. [Installation](#installation)
2. [Authentication](#authentication)
3. [Workspace Commands](#workspace-commands)
4. [Cluster Commands](#cluster-commands)
5. [Jobs Commands](#jobs-commands)
6. [DBFS Commands](#dbfs-commands)
7. [Secrets Commands](#secrets-commands)
8. [Repos Commands](#repos-commands)
9. [Unity Catalog Commands](#unity-catalog-commands)
10. [Advanced Usage](#advanced-usage)

---

## Installation

### Install via pip

```bash
# Install latest version
pip install databricks-cli

# Install specific version
pip install databricks-cli==0.18.0

# Upgrade existing installation
pip install --upgrade databricks-cli

# Verify installation
databricks --version
```

### Install via Homebrew (macOS)

```bash
brew tap databricks/tap
brew install databricks
```

### Install via Download

```bash
# Download binary for your platform
# https://github.com/databricks/databricks-cli/releases

# Make executable (Unix/Linux)
chmod +x databricks
sudo mv databricks /usr/local/bin/
```

---

## Authentication

### Configure with Token

```bash
# Interactive configuration
databricks configure --token

# You'll be prompted for:
# - Databricks Host: https://<your-workspace>.cloud.databricks.com
# - Token: dapi1234567890abcdef

# Non-interactive configuration
export DATABRICKS_HOST="https://<workspace>.cloud.databricks.com"
export DATABRICKS_TOKEN="dapi1234567890abcdef"

# Or use config file
databricks configure --token <<EOF
https://<workspace>.cloud.databricks.com
dapi1234567890abcdef
EOF
```

### Multiple Profiles

```bash
# Create named profiles
databricks configure --token --profile prod
databricks configure --token --profile dev

# Use specific profile
databricks clusters list --profile prod
databricks workspace ls / --profile dev

# Set default profile
export DATABRICKS_CONFIG_PROFILE=prod
```

### Configuration File Location

```bash
# Default location
~/.databrickscfg

# Example config file content
[DEFAULT]
host = https://workspace1.cloud.databricks.com
token = dapi1234567890abcdef

[prod]
host = https://prod-workspace.cloud.databricks.com
token = dapi_prod_token

[dev]
host = https://dev-workspace.cloud.databricks.com
token = dapi_dev_token
```

### Azure AD Authentication

```bash
# Configure with Azure AD
databricks configure --aad-token

# Set Azure-specific environment variables
export DATABRICKS_HOST="https://adb-1234567890.azuredatabricks.net"
export DATABRICKS_AAD_TOKEN="<azure-ad-token>"
```

---

## Workspace Commands

### List Workspace Objects

```bash
# List root directory
databricks workspace ls /

# List user directory
databricks workspace ls /Users/user@example.com

# List with details
databricks workspace ls / -l

# Recursive listing
databricks workspace ls / -r
```

### Export Notebooks

```bash
# Export single notebook (SOURCE format)
databricks workspace export /Users/user@example.com/notebook.py ./notebook.py

# Export as Jupyter notebook
databricks workspace export /Users/user@example.com/notebook \
  ./notebook.ipynb --format JUPYTER

# Export as HTML
databricks workspace export /Users/user@example.com/notebook \
  ./notebook.html --format HTML

# Export as DBC archive
databricks workspace export /Users/user@example.com/notebook \
  ./notebook.dbc --format DBC
```

### Import Notebooks

```bash
# Import notebook
databricks workspace import ./notebook.py \
  /Users/user@example.com/notebook.py --language PYTHON

# Import with overwrite
databricks workspace import ./notebook.py \
  /Users/user@example.com/notebook.py \
  --language PYTHON --overwrite

# Import Jupyter notebook
databricks workspace import ./notebook.ipynb \
  /Users/user@example.com/notebook --format JUPYTER
```

### Export/Import Directories

```bash
# Export directory recursively
databricks workspace export_dir /Users/user@example.com/project ./project

# Import directory
databricks workspace import_dir ./project /Users/user@example.com/project

# Import with overwrite
databricks workspace import_dir ./project \
  /Users/user@example.com/project --overwrite
```

### Create and Delete

```bash
# Create directory
databricks workspace mkdirs /Users/user@example.com/new_folder

# Delete object
databricks workspace rm /Users/user@example.com/old_notebook

# Delete directory recursively
databricks workspace rm -r /Users/user@example.com/old_folder
```

---

## Cluster Commands

### List Clusters

```bash
# List all clusters
databricks clusters list

# Output as JSON
databricks clusters list --output JSON

# List specific cluster
databricks clusters get --cluster-id 1234-567890-abc123
```

### Create Cluster

```bash
# Create cluster from JSON config
cat <<EOF > cluster-config.json
{
  "cluster_name": "my-cluster",
  "spark_version": "13.3.x-scala2.12",
  "node_type_id": "Standard_DS3_v2",
  "num_workers": 2,
  "autoscale": {
    "min_workers": 2,
    "max_workers": 8
  }
}
EOF

databricks clusters create --json-file cluster-config.json

# Create with inline JSON
databricks clusters create --json '{
  "cluster_name": "test-cluster",
  "spark_version": "13.3.x-scala2.12",
  "node_type_id": "Standard_DS3_v2",
  "num_workers": 1
}'
```

### Start and Stop Clusters

```bash
# Start cluster
databricks clusters start --cluster-id 1234-567890-abc123

# Stop cluster
databricks clusters stop --cluster-id 1234-567890-abc123

# Restart cluster
databricks clusters restart --cluster-id 1234-567890-abc123
```

### Delete Cluster

```bash
# Permanent delete
databricks clusters permanent-delete --cluster-id 1234-567890-abc123

# Terminate (can be restarted)
databricks clusters delete --cluster-id 1234-567890-abc123
```

### Cluster Events

```bash
# List cluster events
databricks clusters events --cluster-id 1234-567890-abc123

# Get specific event types
databricks clusters events --cluster-id 1234-567890-abc123 \
  --event-types STARTING,RUNNING,TERMINATING
```

---

## Jobs Commands

### List Jobs

```bash
# List all jobs
databricks jobs list

# List with details
databricks jobs list --output JSON

# Get specific job
databricks jobs get --job-id 123
```

### Create Job

```bash
# Create job from JSON
cat <<EOF > job-config.json
{
  "name": "Daily ETL Job",
  "tasks": [
    {
      "task_key": "etl_task",
      "notebook_task": {
        "notebook_path": "/Users/user@example.com/etl_notebook",
        "base_parameters": {
          "date": "{{job.start_time.date}}"
        }
      },
      "existing_cluster_id": "1234-567890-abc123"
    }
  ],
  "schedule": {
    "quartz_cron_expression": "0 0 2 * * ?",
    "timezone_id": "America/Los_Angeles"
  }
}
EOF

databricks jobs create --json-file job-config.json
```

### Run Job

```bash
# Run job now
databricks jobs run-now --job-id 123

# Run with parameters
databricks jobs run-now --job-id 123 \
  --notebook-params '{"date": "2026-02-27", "env": "prod"}'

# Run and wait for completion
databricks jobs run-now --job-id 123 --wait
```

### Monitor Runs

```bash
# List runs for a job
databricks jobs runs list --job-id 123

# Get run details
databricks jobs runs get --run-id 456

# Get run output
databricks jobs runs get-output --run-id 456

# Cancel run
databricks jobs runs cancel --run-id 456
```

### Update and Delete Jobs

```bash
# Update job settings
databricks jobs reset --job-id 123 --json-file updated-job-config.json

# Delete job
databricks jobs delete --job-id 123
```

---

## DBFS Commands

### List Files

```bash
# List DBFS root
databricks fs ls dbfs:/

# List specific directory
databricks fs ls dbfs:/FileStore/

# Recursive listing
databricks fs ls -r dbfs:/data/
```

### Upload and Download

```bash
# Upload file
databricks fs cp local-file.csv dbfs:/FileStore/data/file.csv

# Upload with overwrite
databricks fs cp local-file.csv dbfs:/FileStore/data/file.csv --overwrite

# Download file
databricks fs cp dbfs:/FileStore/data/file.csv ./downloaded-file.csv

# Upload directory
databricks fs cp -r ./local-dir/ dbfs:/FileStore/data/

# Download directory
databricks fs cp -r dbfs:/FileStore/data/ ./local-dir/
```

### Create and Delete

```bash
# Create directory
databricks fs mkdirs dbfs:/FileStore/new-folder

# Delete file
databricks fs rm dbfs:/FileStore/data/old-file.csv

# Delete directory recursively
databricks fs rm -r dbfs:/FileStore/old-folder
```

### Move and Copy

```bash
# Move file
databricks fs mv dbfs:/source/file.csv dbfs:/destination/file.csv

# Copy file (within DBFS)
databricks fs cp dbfs:/source/file.csv dbfs:/destination/file.csv
```

### Cat and Head

```bash
# Display file contents
databricks fs cat dbfs:/FileStore/data/file.txt

# Display first N bytes
databricks fs cat dbfs:/FileStore/data/file.txt --head 1000
```

---

## Secrets Commands

### List Scopes

```bash
# List all secret scopes
databricks secrets list-scopes

# Example output:
# Scope           Backend Type
# prod-secrets    DATABRICKS
# dev-secrets     DATABRICKS
```

### Create Scope

```bash
# Create Databricks-backed scope
databricks secrets create-scope --scope my-secrets

# Create with ACLs (premium tier)
databricks secrets create-scope --scope my-secrets \
  --initial-manage-principal users
```

### Manage Secrets

```bash
# Add secret (interactive)
databricks secrets put --scope my-secrets --key api-key

# Add secret (from file)
databricks secrets put --scope my-secrets --key db-password \
  --string-value "$(cat password.txt)"

# List secrets in scope
databricks secrets list --scope my-secrets

# Delete secret
databricks secrets delete --scope my-secrets --key old-key

# Delete scope
databricks secrets delete-scope --scope old-scope
```

### Manage ACLs

```bash
# Grant permissions
databricks secrets put-acl --scope my-secrets \
  --principal user@example.com --permission READ

# List ACLs
databricks secrets list-acls --scope my-secrets

# Get ACL for principal
databricks secrets get-acl --scope my-secrets \
  --principal user@example.com

# Delete ACL
databricks secrets delete-acl --scope my-secrets \
  --principal user@example.com
```

---

## Repos Commands

### List Repos

```bash
# List all repos
databricks repos list

# Get specific repo
databricks repos get --repo-id 123
```

### Create Repo

```bash
# Create from Git URL
databricks repos create --url https://github.com/user/repo.git \
  --provider gitHub --path /Repos/user@example.com/my-repo
```

### Update Repo

```bash
# Pull latest changes
databricks repos update --repo-id 123 --branch main

# Switch branch
databricks repos update --repo-id 123 --branch feature-branch

# Update to specific tag
databricks repos update --repo-id 123 --tag v1.0.0

# Update to specific commit
databricks repos update --repo-id 123 \
  --commit 1234567890abcdef
```

### Delete Repo

```bash
databricks repos delete --repo-id 123
```

---

## Unity Catalog Commands

### Catalogs

```bash
# List catalogs
databricks unity-catalog catalogs list

# Create catalog
databricks unity-catalog catalogs create --name my_catalog \
  --comment "My data catalog"

# Get catalog details
databricks unity-catalog catalogs get --name my_catalog

# Delete catalog
databricks unity-catalog catalogs delete --name old_catalog
```

### Schemas

```bash
# List schemas in catalog
databricks unity-catalog schemas list --catalog-name my_catalog

# Create schema
databricks unity-catalog schemas create --catalog-name my_catalog \
  --name my_schema --comment "My schema"

# Get schema details
databricks unity-catalog schemas get --full-name my_catalog.my_schema

# Delete schema
databricks unity-catalog schemas delete --full-name my_catalog.old_schema
```

### Tables

```bash
# List tables in schema
databricks unity-catalog tables list \
  --catalog-name my_catalog --schema-name my_schema

# Get table details
databricks unity-catalog tables get \
  --full-name my_catalog.my_schema.my_table

# Delete table
databricks unity-catalog tables delete \
  --full-name my_catalog.my_schema.old_table
```

### Grants

```bash
# Grant permissions
databricks unity-catalog grants update \
  --securable-type catalog \
  --full-name my_catalog \
  --principal data-engineers \
  --add '["USE_CATALOG", "CREATE_SCHEMA"]'

# List grants
databricks unity-catalog grants list \
  --securable-type catalog --full-name my_catalog

# Revoke permissions
databricks unity-catalog grants update \
  --securable-type catalog \
  --full-name my_catalog \
  --principal data-viewers \
  --remove '["CREATE_SCHEMA"]'
```

---

## Advanced Usage

### Scripting with CLI

```bash
#!/bin/bash
# Automated deployment script

set -e

WORKSPACE_HOST="https://workspace.cloud.databricks.com"
PROFILE="prod"

echo "Deploying notebooks..."

# Export from dev
databricks workspace export_dir /Users/dev@example.com/project \
  ./project --profile dev

# Import to prod
databricks workspace import_dir ./project \
  /Users/prod@example.com/project --overwrite --profile prod

echo "Creating job..."

# Create production job
JOB_ID=$(databricks jobs create --json-file job-config.json --profile prod \
  | jq -r '.job_id')

echo "Job created with ID: $JOB_ID"

# Run job
databricks jobs run-now --job-id $JOB_ID --profile prod

echo "Deployment complete!"
```

### Batch Operations

```bash
# Start multiple clusters
for cluster_id in $(cat cluster-ids.txt); do
  databricks clusters start --cluster-id $cluster_id
done

# Export all notebooks from a directory
databricks workspace ls /Users/user@example.com -r | \
  grep '\.py$' | \
  while read path; do
    databricks workspace export "$path" "./backup$path"
  done

# Run multiple jobs
for job_id in 101 102 103; do
  databricks jobs run-now --job-id $job_id &
done
wait
```

### JSON Processing with jq

```bash
# Get cluster IDs by name pattern
databricks clusters list --output JSON | \
  jq -r '.clusters[] | select(.cluster_name | contains("prod")) | .cluster_id'

# Get running job count
databricks jobs runs list --active-only --output JSON | \
  jq '.runs | length'

# Extract notebook paths
databricks workspace ls /Users -r --output JSON | \
  jq -r '.[] | select(.object_type == "NOTEBOOK") | .path'
```

### Error Handling

```bash
#!/bin/bash

# Function with error handling
run_job_safely() {
  local job_id=$1

  if ! databricks jobs run-now --job-id "$job_id" 2>/tmp/error.log; then
    echo "Error running job $job_id:"
    cat /tmp/error.log
    return 1
  fi

  echo "Job $job_id started successfully"
  return 0
}

# Usage with retry logic
MAX_RETRIES=3
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  if run_job_safely 123; then
    break
  fi

  RETRY_COUNT=$((RETRY_COUNT + 1))
  echo "Retry $RETRY_COUNT of $MAX_RETRIES..."
  sleep 5
done
```

### CI/CD Integration

```bash
# GitHub Actions example
name: Deploy to Databricks

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Databricks CLI
        run: |
          pip install databricks-cli

      - name: Configure Databricks
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
        run: |
          databricks configure --token <<EOF
          $DATABRICKS_HOST
          $DATABRICKS_TOKEN
          EOF

      - name: Deploy Notebooks
        run: |
          databricks workspace import_dir ./notebooks /Production/notebooks --overwrite

      - name: Run Tests
        run: |
          databricks jobs run-now --job-id 123 --wait
```

### Configuration Management

```bash
# Environment-based configuration
#!/bin/bash

ENV=${1:-dev}

case $ENV in
  dev)
    export DATABRICKS_HOST="https://dev-workspace.cloud.databricks.com"
    export DATABRICKS_TOKEN="$DEV_TOKEN"
    ;;
  staging)
    export DATABRICKS_HOST="https://staging-workspace.cloud.databricks.com"
    export DATABRICKS_TOKEN="$STAGING_TOKEN"
    ;;
  prod)
    export DATABRICKS_HOST="https://prod-workspace.cloud.databricks.com"
    export DATABRICKS_TOKEN="$PROD_TOKEN"
    ;;
  *)
    echo "Unknown environment: $ENV"
    exit 1
    ;;
esac

echo "Configured for $ENV environment"

# Run deployment
databricks workspace import_dir ./notebooks /Shared/notebooks --overwrite
```

---

## Common Patterns

### Backup and Restore

```bash
#!/bin/bash
# Backup workspace

BACKUP_DIR="./backup-$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

echo "Backing up workspace..."
databricks workspace export_dir / "$BACKUP_DIR/workspace"

echo "Backing up jobs..."
databricks jobs list --output JSON > "$BACKUP_DIR/jobs.json"

echo "Backing up clusters..."
databricks clusters list --output JSON > "$BACKUP_DIR/clusters.json"

echo "Backup complete: $BACKUP_DIR"
```

### Migration Between Workspaces

```bash
#!/bin/bash
# Migrate resources from source to target workspace

SOURCE_PROFILE="source"
TARGET_PROFILE="target"
TEMP_DIR="./migration-temp"

mkdir -p "$TEMP_DIR"

# Export from source
databricks workspace export_dir /Production "$TEMP_DIR/workspace" \
  --profile $SOURCE_PROFILE

# Import to target
databricks workspace import_dir "$TEMP_DIR/workspace" /Production \
  --overwrite --profile $TARGET_PROFILE

# Clean up
rm -rf "$TEMP_DIR"

echo "Migration complete!"
```

---

## Troubleshooting

### Common Issues

```bash
# Issue: Authentication failed
# Solution: Verify token and host
databricks workspace ls / --debug

# Issue: Command not found
# Solution: Check installation
which databricks
pip show databricks-cli

# Issue: Permission denied
# Solution: Check ACLs and permissions
databricks secrets list-acls --scope my-secrets

# Issue: Timeout
# Solution: Increase timeout
export DATABRICKS_CLI_TIMEOUT=300
```

### Debug Mode

```bash
# Enable debug output
databricks workspace ls / --debug

# Verbose logging
databricks --debug clusters list

# Check configuration
cat ~/.databrickscfg
```

---

## Related Documentation

- [Workspace API](../api/workspace.md)
- [Jobs API](../api/jobs.md)
- [Clusters API](../api/clusters.md)
- [Unity Catalog API](../api/unity-catalog.md)

---

## Additional Resources

- [Databricks CLI GitHub](https://github.com/databricks/databricks-cli)
- [CLI Documentation](https://docs.databricks.com/dev-tools/cli/index.html)
- [API Reference](https://docs.databricks.com/api/index.html)
