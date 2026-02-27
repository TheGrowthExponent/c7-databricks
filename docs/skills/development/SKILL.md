---
title: "Development & Deployment Skills"
description: "Application development, deployment automation, and DevOps practices on Databricks"
category: "development"
tags:
  [
    "development",
    "deployment",
    "devops",
    "cicd",
    "asset-bundles",
    "databricks-apps",
    "python-sdk",
    "automation",
    "infrastructure-as-code",
    "multi-environment",
  ]
priority: "high"
skills_count: 6
last_updated: 2026-02-27
version: "1.0.0"
status: "partial"
---

# Development & Deployment Skills

This directory contains skills and patterns for application development, deployment, and DevOps on Databricks.

## 📚 Skills Overview

### Well Covered Skills

#### 1. Databricks Python SDK

**Status**: ✅ Covered
**Priority**: -
**Description**: Comprehensive guide to programmatic Databricks interaction

**Key Topics**:

- SDK installation and configuration
- Authentication methods
- Service client usage
- Workspace management
- Jobs and clusters APIs
- Unity Catalog operations
- Error handling patterns

**Use Cases**:

- Infrastructure automation
- CI/CD integration
- Custom tooling development
- Batch operations
- Monitoring and reporting
- Resource provisioning

**Related Documentation**:

- [Python SDK Guide](../../sdk/python.md) ✅ (1,172 lines)
- [Authentication Guide](../../getting-started/authentication.md) ✅
- [API Overview](../../api/overview.md) ✅

---

#### 2. Databricks Configuration

**Status**: ✅ Covered
**Priority**: -
**Description**: Configure Databricks CLI and SDK for different environments

**Key Topics**:

- Configuration file setup (.databrickscfg)
- Environment variables
- Profile management
- Authentication configuration
- Connection profiles
- Workspace URL configuration

**Use Cases**:

- Multi-environment setup (dev/staging/prod)
- CI/CD configuration
- Team collaboration
- Credential management
- Automated deployments

**Related Documentation**:

- [Setup Guide](../../getting-started/setup.md) ✅
- [Authentication Guide](../../getting-started/authentication.md) ✅
- [CLI Reference](../../cli/README.md) ✅

---

### High Priority Skills

#### 3. Databricks Asset Bundles (DABs)

**Status**: ❌ Not yet documented
**Priority**: HIGH
**Description**: Modern deployment framework for Databricks resources

**Key Topics**:

- Bundle structure and configuration
- Resource definitions (jobs, pipelines, models)
- Multi-environment deployments
- Variable management
- CI/CD integration
- Git integration
- Templating and reusability
- Deployment validation

**Use Cases**:

- Production deployments
- Multi-environment management
- Infrastructure as Code
- Team collaboration
- Version control integration
- Automated testing and deployment

**Prerequisites**:

- Databricks CLI installed
- Git repository setup
- Understanding of YAML configuration
- Workspace admin permissions

**Related Documentation**:

- [Jobs API](../../api/jobs.md)
- [Python SDK](../../sdk/python.md)
- [CLI Reference](../../cli/README.md)

---

#### 4. Databricks Apps (Python)

**Status**: ❌ Not yet documented
**Priority**: HIGH
**Description**: Build and deploy full-stack applications on Databricks

**Key Topics**:

- App framework setup
- Python backend development
- Frontend integration (Streamlit, Dash)
- Authentication and security
- Data access patterns
- Deployment and hosting
- App monitoring
- Custom UI components

**Use Cases**:

- Interactive dashboards
- Data exploration tools
- ML model interfaces
- Self-service analytics apps
- Internal tools and utilities
- Customer-facing applications

**Prerequisites**:

- Python proficiency
- Web framework knowledge (Streamlit/Dash)
- Unity Catalog access
- App hosting permissions

**Related Documentation**:

- [Python SDK](../../sdk/python.md)
- [Authentication](../../getting-started/authentication.md)
- [Security Best Practices](../../best-practices/security.md)

---

#### 5. Databricks Apps (APX Framework)

**Status**: ❌ Not yet documented
**Priority**: HIGH
**Description**: Advanced application framework for enterprise applications

**Key Topics**:

- APX framework architecture
- Application structure
- API development
- Frontend integration
- State management
- Authentication flows
- Production deployment
- Scalability patterns

**Use Cases**:

- Enterprise applications
- Complex workflows
- Multi-user applications
- API-driven solutions
- Production-grade apps

**Prerequisites**:

- Advanced Python knowledge
- REST API development
- React/JavaScript for frontend
- DevOps experience

**Related Documentation**:

- [Python SDK](../../sdk/python.md)
- [API Overview](../../api/overview.md)

---

### Low Priority Skills

#### 6. Databricks Lakebase Provisioned

**Status**: ❌ Not covered
**Priority**: LOW
**Description**: Provisioned lakehouse infrastructure management

**Key Topics**:

- Provisioned infrastructure setup
- Capacity planning
- Resource allocation
- Performance tuning
- Cost optimization

**Use Cases**:

- Enterprise deployments
- High-performance requirements
- Predictable workloads
- Dedicated resources

**Prerequisites**:

- Enterprise account
- Infrastructure planning
- Cost analysis

---

## 🎯 Quick Start Examples

### Example 1: Basic Python SDK Usage

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import Task, NotebookTask
from databricks.sdk.service.compute import ClusterSpec

# Initialize client (uses default auth from .databrickscfg)
w = WorkspaceClient()

# List workspaces
for workspace in w.workspaces.list():
    print(f"Workspace: {workspace.workspace_name}")

# Create a simple job
job = w.jobs.create(
    name="my-python-job",
    tasks=[
        Task(
            task_key="main_task",
            description="Process daily data",
            notebook_task=NotebookTask(
                notebook_path="/Users/user@company.com/my_notebook"
            ),
            new_cluster=ClusterSpec(
                spark_version="13.3.x-scala2.12",
                node_type_id="i3.xlarge",
                num_workers=2
            )
        )
    ]
)

print(f"Created job: {job.job_id}")

# Run the job
run = w.jobs.run_now(job_id=job.job_id)
print(f"Started run: {run.run_id}")

# Get run status
run_info = w.jobs.get_run(run_id=run.run_id)
print(f"Run state: {run_info.state.life_cycle_state}")
```

### Example 2: Databricks Configuration Setup

```bash
# Create .databrickscfg file
cat > ~/.databrickscfg << EOF
[DEFAULT]
host = https://your-workspace.cloud.databricks.com
token = dapi1234567890abcdef

[development]
host = https://dev-workspace.cloud.databricks.com
token = dapi_dev_token

[staging]
host = https://staging-workspace.cloud.databricks.com
token = dapi_staging_token

[production]
host = https://prod-workspace.cloud.databricks.com
token = dapi_prod_token
EOF

# Set appropriate permissions
chmod 600 ~/.databrickscfg
```

```python
# Use specific profile in Python
from databricks.sdk import WorkspaceClient

# Use production profile
w_prod = WorkspaceClient(profile="production")

# Use development profile
w_dev = WorkspaceClient(profile="development")

# Or use environment variables
import os
os.environ["DATABRICKS_HOST"] = "https://workspace.cloud.databricks.com"
os.environ["DATABRICKS_TOKEN"] = "dapi1234567890"

w = WorkspaceClient()
```

### Example 3: Asset Bundles Structure

```yaml
# databricks.yml - Root bundle configuration
bundle:
  name: my-project

variables:
  warehouse_id:
    description: SQL Warehouse for queries
    default: abc123

targets:
  development:
    mode: development
    workspace:
      host: https://dev-workspace.cloud.databricks.com
    variables:
      warehouse_id: dev-warehouse-id

  production:
    mode: production
    workspace:
      host: https://prod-workspace.cloud.databricks.com
    variables:
      warehouse_id: prod-warehouse-id
    run_as:
      service_principal_name: prod-service-principal

resources:
  jobs:
    daily_etl:
      name: daily-etl-${bundle.environment}
      tasks:
        - task_key: extract
          notebook_task:
            notebook_path: ./notebooks/extract.py
          new_cluster:
            spark_version: 13.3.x-scala2.12
            node_type_id: i3.xlarge
            num_workers: 2

        - task_key: transform
          depends_on:
            - task_key: extract
          notebook_task:
            notebook_path: ./notebooks/transform.py
          existing_cluster_id: ${var.shared_cluster_id}

  pipelines:
    streaming_pipeline:
      name: streaming-pipeline-${bundle.environment}
      storage: /pipelines/${bundle.environment}
      configuration:
        warehouse_id: ${var.warehouse_id}
      libraries:
        - notebook:
            path: ./pipelines/dlt_pipeline.py

  models:
    ml_model:
      name: customer-churn-model-${bundle.environment}
      tags:
        - key: environment
          value: ${bundle.environment}
```

```bash
# Deploy asset bundle
databricks bundle deploy --target development

# Validate bundle
databricks bundle validate --target production

# Run a job from bundle
databricks bundle run daily_etl --target production

# Destroy resources
databricks bundle destroy --target development
```

### Example 4: Streamlit App on Databricks

```python
# app.py - Simple Streamlit app
import streamlit as st
from databricks import sql
import pandas as pd
import os

st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Sales Analytics Dashboard")

# Connect to Databricks SQL
@st.cache_resource
def get_connection():
    return sql.connect(
        server_hostname=os.getenv("DATABRICKS_SERVER_HOSTNAME"),
        http_path=os.getenv("DATABRICKS_HTTP_PATH"),
        access_token=os.getenv("DATABRICKS_TOKEN")
    )

# Query data
@st.cache_data(ttl=600)
def load_data(query):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    df = cursor.fetchall_arrow().to_pandas()
    cursor.close()
    return df

# Sidebar filters
st.sidebar.header("Filters")
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(pd.Timestamp.now() - pd.Timedelta(days=30), pd.Timestamp.now())
)

region = st.sidebar.multiselect(
    "Select Regions",
    options=["North", "South", "East", "West"],
    default=["North", "South", "East", "West"]
)

# Main content
col1, col2, col3 = st.columns(3)

# Load metrics
metrics_query = f"""
SELECT
    SUM(revenue) as total_revenue,
    COUNT(DISTINCT order_id) as total_orders,
    AVG(revenue) as avg_order_value
FROM main.sales.orders
WHERE order_date BETWEEN '{date_range[0]}' AND '{date_range[1]}'
    AND region IN ({','.join([f"'{r}'" for r in region])})
"""

metrics = load_data(metrics_query)

with col1:
    st.metric(
        "Total Revenue",
        f"${metrics['total_revenue'][0]:,.2f}",
        delta="12.5%"
    )

with col2:
    st.metric(
        "Total Orders",
        f"{metrics['total_orders'][0]:,}",
        delta="8.2%"
    )

with col3:
    st.metric(
        "Avg Order Value",
        f"${metrics['avg_order_value'][0]:,.2f}",
        delta="-2.1%"
    )

# Revenue trend chart
st.subheader("Revenue Trend")
trend_query = f"""
SELECT
    DATE_TRUNC('day', order_date) as date,
    SUM(revenue) as revenue
FROM main.sales.orders
WHERE order_date BETWEEN '{date_range[0]}' AND '{date_range[1]}'
    AND region IN ({','.join([f"'{r}'" for r in region])})
GROUP BY DATE_TRUNC('day', order_date)
ORDER BY date
"""

trend_data = load_data(trend_query)
st.line_chart(trend_data.set_index('date'))

# Top products table
st.subheader("Top Products")
products_query = f"""
SELECT
    product_name,
    SUM(quantity) as units_sold,
    SUM(revenue) as revenue
FROM main.sales.order_items
WHERE order_date BETWEEN '{date_range[0]}' AND '{date_range[1]}'
    AND region IN ({','.join([f"'{r}'" for r in region])})
GROUP BY product_name
ORDER BY revenue DESC
LIMIT 10
"""

products = load_data(products_query)
st.dataframe(products, use_container_width=True)
```

### Example 5: CI/CD Pipeline with Asset Bundles

```yaml
# .github/workflows/deploy.yml
name: Deploy to Databricks

on:
  push:
    branches:
      - main
      - develop
  pull_request:
    branches:
      - main

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"

      - name: Install Databricks CLI
        run: |
          pip install databricks-cli

      - name: Validate Bundle
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
        run: |
          databricks bundle validate --target development

  deploy-dev:
    needs: validate
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"

      - name: Install Databricks CLI
        run: |
          pip install databricks-cli

      - name: Deploy to Development
        env:
          DATABRICKS_HOST: ${{ secrets.DEV_DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DEV_DATABRICKS_TOKEN }}
        run: |
          databricks bundle deploy --target development

  deploy-prod:
    needs: validate
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"

      - name: Install Databricks CLI
        run: |
          pip install databricks-cli

      - name: Deploy to Production
        env:
          DATABRICKS_HOST: ${{ secrets.PROD_DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.PROD_DATABRICKS_TOKEN }}
        run: |
          databricks bundle deploy --target production

      - name: Run Integration Tests
        env:
          DATABRICKS_HOST: ${{ secrets.PROD_DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.PROD_DATABRICKS_TOKEN }}
        run: |
          databricks bundle run integration_tests --target production
```

### Example 6: Infrastructure Automation

```python
# infrastructure/setup_workspace.py
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import compute, sql, catalog

def setup_workspace(environment: str):
    """
    Setup Databricks workspace infrastructure
    """
    w = WorkspaceClient()

    # Create cluster policy
    policy = w.cluster_policies.create(
        name=f"{environment}-policy",
        definition="""{
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
            }
        }"""
    )
    print(f"Created policy: {policy.policy_id}")

    # Create SQL warehouse
    warehouse = w.warehouses.create(
        name=f"{environment}-warehouse",
        cluster_size="Small",
        max_num_clusters=1,
        auto_stop_mins=20,
        enable_serverless_compute=True,
        tags={
            "environment": environment,
            "cost-center": "analytics"
        }
    )
    print(f"Created warehouse: {warehouse.id}")

    # Create shared cluster
    cluster = w.clusters.create(
        cluster_name=f"{environment}-shared",
        spark_version="13.3.x-scala2.12",
        node_type_id="i3.xlarge",
        autoscale=compute.AutoScale(min_workers=2, max_workers=8),
        autotermination_minutes=30,
        spark_conf={
            "spark.databricks.delta.preview.enabled": "true"
        },
        custom_tags={
            "environment": environment,
            "team": "data-engineering"
        }
    )
    print(f"Created cluster: {cluster.cluster_id}")

    # Create Unity Catalog schema
    schema = w.schemas.create(
        catalog_name="main",
        name=f"{environment}_workspace",
        comment=f"Schema for {environment} environment"
    )
    print(f"Created schema: {schema.full_name}")

    return {
        "policy_id": policy.policy_id,
        "warehouse_id": warehouse.id,
        "cluster_id": cluster.cluster_id,
        "schema_name": schema.full_name
    }

if __name__ == "__main__":
    import sys
    env = sys.argv[1] if len(sys.argv) > 1 else "development"

    resources = setup_workspace(env)
    print(f"\nSetup complete for {env}:")
    print(f"Resources: {resources}")
```

---

## 🔧 Common Patterns

### Pattern 1: Multi-Environment Configuration

```python
# config.py - Environment-aware configuration
import os
from dataclasses import dataclass
from databricks.sdk import WorkspaceClient

@dataclass
class EnvironmentConfig:
    name: str
    host: str
    warehouse_id: str
    catalog: str
    schema: str

    @classmethod
    def from_env(cls, env_name: str):
        configs = {
            "development": cls(
                name="development",
                host=os.getenv("DEV_DATABRICKS_HOST"),
                warehouse_id="dev-warehouse-id",
                catalog="dev_catalog",
                schema="dev_schema"
            ),
            "staging": cls(
                name="staging",
                host=os.getenv("STAGING_DATABRICKS_HOST"),
                warehouse_id="staging-warehouse-id",
                catalog="staging_catalog",
                schema="staging_schema"
            ),
            "production": cls(
                name="production",
                host=os.getenv("PROD_DATABRICKS_HOST"),
                warehouse_id="prod-warehouse-id",
                catalog="main",
                schema="prod_schema"
            )
        }
        return configs[env_name]

    def get_client(self):
        return WorkspaceClient(
            host=self.host,
            token=os.getenv(f"{self.name.upper()}_DATABRICKS_TOKEN")
        )

# Usage
config = EnvironmentConfig.from_env("production")
w = config.get_client()
```

### Pattern 2: Resource Tagging

```python
# Tag all resources for cost tracking and organization
def create_tagged_job(name: str, tags: dict):
    """Create job with standard tags"""

    standard_tags = {
        "team": os.getenv("TEAM_NAME", "unknown"),
        "cost-center": os.getenv("COST_CENTER", "unknown"),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "created-by": "automation",
        "managed-by": "asset-bundles"
    }

    # Merge with provided tags
    all_tags = {**standard_tags, **tags}

    job = w.jobs.create(
        name=name,
        tags=all_tags,
        # ... rest of configuration
    )

    return job
```

### Pattern 3: Blue-Green Deployment

```python
# blue_green_deploy.py
from databricks.sdk import WorkspaceClient

def blue_green_deploy(job_name: str, new_config: dict):
    """
    Deploy new job version with blue-green strategy
    """
    w = WorkspaceClient()

    # Get existing job (blue)
    jobs = w.jobs.list(name=job_name)
    blue_job = next((j for j in jobs if j.settings.name == job_name), None)

    # Create new job (green)
    green_job = w.jobs.create(
        name=f"{job_name}-green",
        **new_config
    )

    print(f"Created green job: {green_job.job_id}")

    # Run smoke tests on green
    test_run = w.jobs.run_now(job_id=green_job.job_id)
    w.jobs.wait_get_run_job_terminated_or_skipped(run_id=test_run.run_id)

    test_result = w.jobs.get_run(run_id=test_run.run_id)

    if test_result.state.result_state == "SUCCESS":
        # Promote green to blue
        if blue_job:
            w.jobs.delete(job_id=blue_job.job_id)

        w.jobs.update(
            job_id=green_job.job_id,
            new_settings={"name": job_name}
        )

        print(f"Successfully promoted green to blue")
        return green_job.job_id
    else:
        # Rollback - delete green
        w.jobs.delete(job_id=green_job.job_id)
        raise Exception("Deployment failed - rolled back")
```

---

## 📊 Best Practices

### Application Development

1. **Code Organization**
   - Separate business logic from infrastructure
   - Use configuration files for environment settings
   - Implement proper error handling
   - Write unit and integration tests

2. **Security**
   - Never hardcode credentials
   - Use service principals for automation
   - Implement least-privilege access
   - Encrypt sensitive data
   - Rotate tokens regularly

3. **Performance**
   - Cache expensive operations
   - Implement connection pooling
   - Use async operations where possible
   - Monitor resource usage

### Deployment

1. **Asset Bundles**
   - Use version control for bundle definitions
   - Separate configuration by environment
   - Implement validation before deployment
   - Use descriptive resource names
   - Document bundle structure

2. **CI/CD**
   - Automate testing and deployment
   - Implement approval gates for production
   - Use separate credentials per environment
   - Maintain deployment logs
   - Enable rollback procedures

3. **Infrastructure as Code**
   - Version control all infrastructure
   - Use consistent naming conventions
   - Tag resources for tracking
   - Document dependencies
   - Implement drift detection

### SDK Development

1. **Error Handling**
   - Catch specific exceptions
   - Implement retry logic with backoff
   - Log errors with context
   - Provide meaningful error messages

2. **Resource Management**
   - Clean up resources after use
   - Implement timeout settings
   - Monitor API rate limits
   - Use pagination for large results

3. **Testing**
   - Mock Databricks services in tests
   - Test against development workspace
   - Validate configurations before deployment
   - Implement integration tests

---

## 🚀 Getting Started Checklist

### For Python SDK

- [ ] Install databricks-sdk: `pip install databricks-sdk`
- [ ] Configure authentication (.databrickscfg or env vars)
- [ ] Initialize WorkspaceClient
- [ ] Test connection with simple API call
- [ ] Implement error handling
- [ ] Create your first automation script
- [ ] Add logging and monitoring

### For Asset Bundles

- [ ] Install Databricks CLI: `pip install databricks-cli`
- [ ] Initialize bundle: `databricks bundle init`
- [ ] Define resources in databricks.yml
- [ ] Configure targets (dev/staging/prod)
- [ ] Validate bundle: `databricks bundle validate`
- [ ] Deploy to development: `databricks bundle deploy --target dev`
- [ ] Test deployed resources
- [ ] Set up CI/CD pipeline
- [ ] Deploy to production with approval

### For Databricks Apps

- [ ] Choose framework (Streamlit/Dash)
- [ ] Create app directory structure
- [ ] Develop app locally
- [ ] Test with local Databricks connection
- [ ] Configure app.yml for deployment
- [ ] Deploy to Databricks Apps
- [ ] Configure authentication and permissions
- [ ] Monitor app usage and performance

---

## 🔍 Advanced Topics

### Custom SDK Extensions

```python
# custom_client.py - Extend SDK with custom functionality
from databricks.sdk import WorkspaceClient
from typing import List, Dict

class ExtendedWorkspaceClient(WorkspaceClient):
    """Extended client with helper methods"""

    def get_all_jobs_by_tag(self, tag_key: str, tag_value: str) -> List:
        """Get all jobs with specific tag"""
        all_jobs = []
        for job in self.jobs.list():
            if job.settings.tags.get(tag_key) == tag_value:
                all_jobs.append(job)
        return all_jobs

    def bulk_update_job_tags(self, job_ids: List[int], tags: Dict[str, str]):
        """Update tags for multiple jobs"""
        for job_id in job_ids:
            job = self.jobs.get(job_id=job_id)
            existing_tags = job.settings.tags or {}
            updated_tags = {**existing_tags, **tags}

            self.jobs.update(
                job_id=job_id,
                new_settings={"tags": updated_tags}
            )

    def cleanup_old_runs(self, job_id: int, keep_last_n: int = 10):
        """Clean up old job runs, keeping only the last N"""
        runs = list(self.jobs.list_runs(job_id=job_id))
        runs_to_delete = sorted(runs, key=lambda r: r.start_time, reverse=True)[keep_last_n:]

        for run in runs_to_delete:
            self.jobs.delete_run(run_id=run.run_id)
```

### Monitoring and Observability

```python
# monitoring.py - Add observability to deployments
import logging
from datetime import datetime
from databricks.sdk import WorkspaceClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonitoredDeployment:
    def __init__(self, w: WorkspaceClient):
        self.w = w
        self.deployment_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def deploy_with_monitoring(self, job_config: dict):
        """Deploy job with comprehensive logging"""

        logger.info(f"Starting deployment: {self.deployment_id}")

        try:
            # Create job
            job = self.w.jobs.create(**job_config)
            logger.info(f"Created job: {job.job_id}")

            # Add monitoring tags
            self.w.jobs.update(
                job_id=job.job_id,
                new_settings={
                    "tags": {
                        "deployment_id": self.deployment_id,
                        "deployed_at": datetime.now().isoformat()
                    }
                }
            )

            # Run validation
            logger.info("Running validation tests")
            test_run = self.w.jobs.run_now(job_id=job.job_id)

            # Wait for completion
            result = self.w.jobs.wait_get_run_job_terminated_or_skipped(
                run_id=test_run.run_id
            )

            if result.state.result_state == "SUCCESS":
                logger.info("Deployment successful")
                return job
            else:
                logger.error(f"Validation failed: {result.state.state_message}")
                raise Exception("Deployment validation failed")

        except Exception as e:
            logger.error(f"Deployment failed: {str(e)}")
            raise
```

---

## 📖 Additional Resources

### Official Documentation

- [Databricks Python SDK](https://docs.databricks.com/en/dev-tools/sdk-python.html)
- [Asset Bundles](https://docs.databricks.com/en/dev-tools/bundles/index.html)
- [Databricks Apps](https://docs.databricks.com/en/dev-tools/databricks-apps/index.html)
- [CLI Reference](https://docs.databricks.com/en/dev-tools/cli/index.html)

### Tutorials

- [Python SDK Guide](../../sdk/python.md)
- [Setup Guide](../../getting-started/setup.md)
- [Authentication Guide](../../getting-started/authentication.md)
- [CLI Reference](../../cli/README.md)

### API References

- [Jobs API](../../api/jobs.md)
- [Clusters API](../../api/clusters.md)
- [Workspace API](../../api/workspace.md)
- [All APIs](../../api/overview.md)

---

## 🏷️ Tags

`development` `deployment` `devops` `python-sdk` `asset-bundles` `dabs` `databricks-apps` `ci-cd` `automation` `infrastructure-as-code` `iac` `streamlit` `cli` `configuration`

---

**Last Updated**: 2026-01-15
**Status**: SDK and config well documented - Asset Bundles and Apps need detailed guides
**Maintainer**: Context7 Documentation Team
