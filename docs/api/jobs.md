# Databricks Jobs API

## Overview

The Jobs API allows you to create, manage, and monitor automated workflows in Databricks. Jobs are the primary way to schedule and orchestrate notebooks, JAR files, Python scripts, and Delta Live Tables pipelines.

## Base Endpoint

```
/api/2.1/jobs
```

**Note**: Use API version 2.1 for jobs (not 2.0)

## Authentication

All requests require authentication. See [Authentication Guide](../getting-started/authentication.md).

```python
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
```

---

## Job Concepts

### Job Components

- **Job**: A configured workflow with one or more tasks
- **Task**: An individual unit of work (notebook, JAR, Python, DLT)
- **Run**: A single execution instance of a job
- **Trigger**: What initiates a job (manual, schedule, event)

### Task Types

- **Notebook Task**: Execute a Databricks notebook
- **Python Task**: Run a Python script
- **JAR Task**: Execute a Java/Scala JAR file
- **Spark Submit Task**: Submit Spark application
- **Pipeline Task**: Run Delta Live Tables pipeline
- **dbt Task**: Execute dbt models
- **SQL Task**: Run SQL queries

---

## Create Job

Create a new job with one or more tasks.

### Endpoint

```
POST /api/2.1/jobs/create
```

### Request Parameters

| Parameter           | Type    | Required | Description                            |
| ------------------- | ------- | -------- | -------------------------------------- |
| name                | string  | Yes      | Job name                               |
| tasks               | array   | Yes      | List of tasks to execute               |
| schedule            | object  | No       | Cron schedule for job                  |
| email_notifications | object  | No       | Email notification settings            |
| timeout_seconds     | integer | No       | Job timeout (default: no timeout)      |
| max_concurrent_runs | integer | No       | Max parallel runs (default: 1)         |
| tags                | object  | No       | Custom tags for organization           |
| format              | string  | No       | Job format (MULTI_TASK or SINGLE_TASK) |

### Simple Notebook Job

```json
{
  "name": "Daily ETL Job",
  "tasks": [
    {
      "task_key": "etl_task",
      "description": "Run ETL notebook",
      "notebook_task": {
        "notebook_path": "/Users/user@example.com/etl_notebook",
        "base_parameters": {
          "date": "{{job.start_time.iso_date}}"
        }
      },
      "existing_cluster_id": "1234-567890-abc123",
      "timeout_seconds": 3600,
      "max_retries": 2,
      "min_retry_interval_millis": 60000,
      "retry_on_timeout": true
    }
  ],
  "email_notifications": {
    "on_success": ["user@example.com"],
    "on_failure": ["user@example.com"],
    "on_start": []
  },
  "schedule": {
    "quartz_cron_expression": "0 0 2 * * ?",
    "timezone_id": "America/Los_Angeles",
    "pause_status": "UNPAUSED"
  },
  "max_concurrent_runs": 1,
  "tags": {
    "project": "analytics",
    "environment": "production"
  }
}
```

### Multi-Task Job with Dependencies

```json
{
  "name": "Multi-Stage Pipeline",
  "tasks": [
    {
      "task_key": "extract",
      "description": "Extract data from source",
      "notebook_task": {
        "notebook_path": "/Pipelines/extract",
        "base_parameters": {}
      },
      "new_cluster": {
        "spark_version": "13.3.x-scala2.12",
        "node_type_id": "i3.xlarge",
        "num_workers": 2
      }
    },
    {
      "task_key": "transform",
      "description": "Transform data",
      "depends_on": [{ "task_key": "extract" }],
      "notebook_task": {
        "notebook_path": "/Pipelines/transform",
        "base_parameters": {}
      },
      "existing_cluster_id": "1234-567890-abc123"
    },
    {
      "task_key": "load",
      "description": "Load data to warehouse",
      "depends_on": [{ "task_key": "transform" }],
      "notebook_task": {
        "notebook_path": "/Pipelines/load",
        "base_parameters": {}
      },
      "existing_cluster_id": "1234-567890-abc123"
    }
  ],
  "email_notifications": {
    "on_failure": ["data-team@example.com"]
  }
}
```

### Python Wheel Task

```json
{
  "name": "Python Package Job",
  "tasks": [
    {
      "task_key": "run_python_package",
      "python_wheel_task": {
        "package_name": "my_package",
        "entry_point": "main",
        "parameters": ["--input", "/data/input", "--output", "/data/output"]
      },
      "libraries": [
        {
          "whl": "dbfs:/FileStore/packages/my_package-1.0.0-py3-none-any.whl"
        }
      ],
      "new_cluster": {
        "spark_version": "13.3.x-scala2.12",
        "node_type_id": "i3.xlarge",
        "num_workers": 1
      }
    }
  ]
}
```

### Python SDK Example

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs

client = WorkspaceClient()

# Create simple notebook job
job = client.jobs.create(
    name="My ETL Job",
    tasks=[
        jobs.Task(
            task_key="etl_task",
            description="Run ETL process",
            notebook_task=jobs.NotebookTask(
                notebook_path="/Users/user@example.com/etl_notebook",
                base_parameters={"environment": "production"}
            ),
            existing_cluster_id="1234-567890-abc123",
            timeout_seconds=3600,
            max_retries=2
        )
    ],
    schedule=jobs.CronSchedule(
        quartz_cron_expression="0 0 2 * * ?",
        timezone_id="America/Los_Angeles"
    ),
    email_notifications=jobs.JobEmailNotifications(
        on_success=["user@example.com"],
        on_failure=["user@example.com"]
    ),
    tags={
        "project": "analytics",
        "owner": "data-team"
    }
)

print(f"Job created with ID: {job.job_id}")
```

### Python Requests Example

```python
import requests

DATABRICKS_HOST = "https://<workspace>.cloud.databricks.com"
DATABRICKS_TOKEN = "dapi..."

headers = {
    "Authorization": f"Bearer {DATABRICKS_TOKEN}",
    "Content-Type": "application/json"
}

job_config = {
    "name": "API Created Job",
    "tasks": [
        {
            "task_key": "main_task",
            "notebook_task": {
                "notebook_path": "/Users/user@example.com/notebook"
            },
            "existing_cluster_id": "1234-567890-abc123"
        }
    ]
}

response = requests.post(
    f"{DATABRICKS_HOST}/api/2.1/jobs/create",
    headers=headers,
    json=job_config
)

if response.status_code == 200:
    job_id = response.json()["job_id"]
    print(f"Job created: {job_id}")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

### Response

```json
{
  "job_id": 123456
}
```

---

## Get Job

Retrieve job configuration and metadata.

### Endpoint

```
GET /api/2.1/jobs/get
```

### Query Parameters

| Parameter | Type    | Required | Description |
| --------- | ------- | -------- | ----------- |
| job_id    | integer | Yes      | The job ID  |

### Example

```python
import requests

response = requests.get(
    f"{DATABRICKS_HOST}/api/2.1/jobs/get",
    headers=headers,
    params={"job_id": 123456}
)

job = response.json()
print(f"Job Name: {job['settings']['name']}")
print(f"Tasks: {len(job['settings']['tasks'])}")
```

### SDK Example

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

job = client.jobs.get(job_id=123456)

print(f"Job Name: {job.settings.name}")
print(f"Created by: {job.creator_user_name}")
print(f"Tasks: {len(job.settings.tasks)}")

for task in job.settings.tasks:
    print(f"  - {task.task_key}: {task.description}")
```

### Response

```json
{
  "job_id": 123456,
  "creator_user_name": "user@example.com",
  "settings": {
    "name": "Daily ETL Job",
    "tasks": [
      {
        "task_key": "etl_task",
        "notebook_task": {
          "notebook_path": "/Users/user@example.com/etl_notebook"
        },
        "existing_cluster_id": "1234-567890-abc123"
      }
    ],
    "schedule": {
      "quartz_cron_expression": "0 0 2 * * ?",
      "timezone_id": "America/Los_Angeles"
    }
  },
  "created_time": 1699564800000
}
```

---

## List Jobs

List all jobs in the workspace.

### Endpoint

```
GET /api/2.1/jobs/list
```

### Query Parameters

| Parameter    | Type    | Required | Description                        |
| ------------ | ------- | -------- | ---------------------------------- |
| limit        | integer | No       | Max results per page (default: 20) |
| offset       | integer | No       | Offset for pagination              |
| expand_tasks | boolean | No       | Include task details               |
| name         | string  | No       | Filter by job name                 |

### Example

```python
import requests

response = requests.get(
    f"{DATABRICKS_HOST}/api/2.1/jobs/list",
    headers=headers,
    params={
        "limit": 25,
        "expand_tasks": True
    }
)

jobs_list = response.json()

for job in jobs_list.get("jobs", []):
    print(f"ID: {job['job_id']}")
    print(f"Name: {job['settings']['name']}")
    print(f"Creator: {job['creator_user_name']}")
    print("-" * 40)
```

### SDK Example

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# List all jobs
for job in client.jobs.list():
    print(f"Job: {job.settings.name}")
    print(f"  ID: {job.job_id}")
    print(f"  Creator: {job.creator_user_name}")

    if job.settings.schedule:
        print(f"  Schedule: {job.settings.schedule.quartz_cron_expression}")

    print()
```

### Response

```json
{
  "jobs": [
    {
      "job_id": 123456,
      "creator_user_name": "user@example.com",
      "settings": {
        "name": "Daily ETL Job",
        "tasks": [...]
      }
    }
  ],
  "has_more": false
}
```

---

## Update Job

Update job configuration.

### Endpoint

```
POST /api/2.1/jobs/update
```

### Request Body

```json
{
  "job_id": 123456,
  "new_settings": {
    "name": "Updated Job Name",
    "tasks": [
      {
        "task_key": "etl_task",
        "notebook_task": {
          "notebook_path": "/Users/user@example.com/new_notebook"
        },
        "existing_cluster_id": "1234-567890-abc123"
      }
    ],
    "schedule": {
      "quartz_cron_expression": "0 0 3 * * ?",
      "timezone_id": "America/New_York"
    }
  }
}
```

### Example

```python
import requests

update_config = {
    "job_id": 123456,
    "new_settings": {
        "name": "Updated Job Name",
        "schedule": {
            "quartz_cron_expression": "0 0 3 * * ?",
            "timezone_id": "America/New_York"
        }
    }
}

response = requests.post(
    f"{DATABRICKS_HOST}/api/2.1/jobs/update",
    headers=headers,
    json=update_config
)

if response.status_code == 200:
    print("Job updated successfully!")
```

### SDK Example

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs

client = WorkspaceClient()

# Update job
client.jobs.update(
    job_id=123456,
    new_settings=jobs.JobSettings(
        name="Updated Job Name",
        schedule=jobs.CronSchedule(
            quartz_cron_expression="0 0 3 * * ?",
            timezone_id="America/New_York"
        )
    )
)

print("Job updated!")
```

---

## Delete Job

Delete a job permanently.

### Endpoint

```
POST /api/2.1/jobs/delete
```

### Request Body

```json
{
  "job_id": 123456
}
```

### Example

```python
import requests

response = requests.post(
    f"{DATABRICKS_HOST}/api/2.1/jobs/delete",
    headers=headers,
    json={"job_id": 123456}
)

if response.status_code == 200:
    print("Job deleted successfully!")
```

### SDK Example

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# Delete job
client.jobs.delete(job_id=123456)

print("Job deleted!")
```

---

## Run Now

Trigger an immediate job run.

### Endpoint

```
POST /api/2.1/jobs/run-now
```

### Request Body

```json
{
  "job_id": 123456,
  "notebook_params": {
    "environment": "production",
    "date": "2026-02-27"
  },
  "python_params": ["--config", "production"],
  "jar_params": ["input.csv", "output.csv"]
}
```

### Example

```python
import requests

run_config = {
    "job_id": 123456,
    "notebook_params": {
        "date": "2026-02-27",
        "environment": "production"
    }
}

response = requests.post(
    f"{DATABRICKS_HOST}/api/2.1/jobs/run-now",
    headers=headers,
    json=run_config
)

if response.status_code == 200:
    run_id = response.json()["run_id"]
    print(f"Job run started: {run_id}")
```

### SDK Example

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# Run job with parameters
run = client.jobs.run_now(
    job_id=123456,
    notebook_params={
        "date": "2026-02-27",
        "environment": "production"
    }
)

print(f"Run ID: {run.run_id}")

# Wait for run to complete
client.jobs.wait_get_run_job_terminated_or_skipped(run_id=run.run_id)

print("Run completed!")
```

### Response

```json
{
  "run_id": 789012,
  "number_in_job": 42
}
```

---

## Submit Run

Submit a one-time run without creating a job.

### Endpoint

```
POST /api/2.1/jobs/runs/submit
```

### Request Body

```json
{
  "run_name": "Ad-hoc Analysis",
  "tasks": [
    {
      "task_key": "analysis_task",
      "notebook_task": {
        "notebook_path": "/Users/user@example.com/analysis",
        "base_parameters": {
          "date": "2026-02-27"
        }
      },
      "new_cluster": {
        "spark_version": "13.3.x-scala2.12",
        "node_type_id": "i3.xlarge",
        "num_workers": 2
      }
    }
  ],
  "timeout_seconds": 3600
}
```

### Example

```python
import requests

submit_config = {
    "run_name": "Ad-hoc Analysis",
    "tasks": [
        {
            "task_key": "analysis",
            "notebook_task": {
                "notebook_path": "/Users/user@example.com/analysis"
            },
            "new_cluster": {
                "spark_version": "13.3.x-scala2.12",
                "node_type_id": "i3.xlarge",
                "num_workers": 2
            }
        }
    ]
}

response = requests.post(
    f"{DATABRICKS_HOST}/api/2.1/jobs/runs/submit",
    headers=headers,
    json=submit_config
)

if response.status_code == 200:
    run_id = response.json()["run_id"]
    print(f"Run submitted: {run_id}")
```

### SDK Example

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs, compute

client = WorkspaceClient()

# Submit one-time run
run = client.jobs.submit(
    run_name="Ad-hoc Analysis",
    tasks=[
        jobs.SubmitTask(
            task_key="analysis",
            notebook_task=jobs.NotebookTask(
                notebook_path="/Users/user@example.com/analysis",
                base_parameters={"date": "2026-02-27"}
            ),
            new_cluster=compute.ClusterSpec(
                spark_version="13.3.x-scala2.12",
                node_type_id="i3.xlarge",
                num_workers=2
            )
        )
    ],
    timeout_seconds=3600
)

print(f"Run ID: {run.run_id}")
```

---

## List Runs

List runs for a job.

### Endpoint

```
GET /api/2.1/jobs/runs/list
```

### Query Parameters

| Parameter      | Type    | Required | Description               |
| -------------- | ------- | -------- | ------------------------- |
| job_id         | integer | No       | Filter by job ID          |
| active_only    | boolean | No       | Show only active runs     |
| completed_only | boolean | No       | Show only completed runs  |
| limit          | integer | No       | Max results (default: 25) |
| offset         | integer | No       | Pagination offset         |

### Example

```python
import requests

response = requests.get(
    f"{DATABRICKS_HOST}/api/2.1/jobs/runs/list",
    headers=headers,
    params={
        "job_id": 123456,
        "limit": 10
    }
)

runs = response.json().get("runs", [])

for run in runs:
    print(f"Run ID: {run['run_id']}")
    print(f"State: {run['state']['life_cycle_state']}")
    print(f"Start Time: {run['start_time']}")
    print("-" * 40)
```

### SDK Example

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# List runs for a job
for run in client.jobs.list_runs(job_id=123456, limit=10):
    print(f"Run: {run.run_id}")
    print(f"  State: {run.state.life_cycle_state}")
    print(f"  Result: {run.state.result_state}")
    print(f"  Start: {run.start_time}")
    print()
```

---

## Get Run

Get details about a specific run.

### Endpoint

```
GET /api/2.1/jobs/runs/get
```

### Query Parameters

| Parameter | Type    | Required | Description |
| --------- | ------- | -------- | ----------- |
| run_id    | integer | Yes      | The run ID  |

### Example

```python
import requests

response = requests.get(
    f"{DATABRICKS_HOST}/api/2.1/jobs/runs/get",
    headers=headers,
    params={"run_id": 789012}
)

run = response.json()
print(f"Run ID: {run['run_id']}")
print(f"State: {run['state']['life_cycle_state']}")
print(f"Result: {run['state'].get('result_state', 'N/A')}")
```

### SDK Example

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

run = client.jobs.get_run(run_id=789012)

print(f"Run ID: {run.run_id}")
print(f"Job ID: {run.job_id}")
print(f"State: {run.state.life_cycle_state}")
print(f"Result: {run.state.result_state}")

# Get task runs
for task_run in run.tasks:
    print(f"Task: {task_run.task_key}")
    print(f"  State: {task_run.state.life_cycle_state}")
```

---

## Cancel Run

Cancel an active run.

### Endpoint

```
POST /api/2.1/jobs/runs/cancel
```

### Request Body

```json
{
  "run_id": 789012
}
```

### Example

```python
import requests

response = requests.post(
    f"{DATABRICKS_HOST}/api/2.1/jobs/runs/cancel",
    headers=headers,
    json={"run_id": 789012}
)

if response.status_code == 200:
    print("Run cancelled successfully!")
```

### SDK Example

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# Cancel run
client.jobs.cancel_run(run_id=789012)

print("Run cancelled!")
```

---

## Get Run Output

Get output from a run.

### Endpoint

```
GET /api/2.1/jobs/runs/get-output
```

### Query Parameters

| Parameter | Type    | Required | Description |
| --------- | ------- | -------- | ----------- |
| run_id    | integer | Yes      | The run ID  |

### Example

```python
import requests

response = requests.get(
    f"{DATABRICKS_HOST}/api/2.1/jobs/runs/get-output",
    headers=headers,
    params={"run_id": 789012}
)

output = response.json()
print(f"Notebook Output: {output.get('notebook_output', {})}")
print(f"Error: {output.get('error', 'None')}")
```

### SDK Example

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

output = client.jobs.get_run_output(run_id=789012)

print(f"Logs: {output.logs}")
print(f"Error: {output.error}")

if output.notebook_output:
    print(f"Result: {output.notebook_output.result}")
```

---

## Run Lifecycle States

| State          | Description             |
| -------------- | ----------------------- |
| PENDING        | Run is being set up     |
| RUNNING        | Run is executing        |
| TERMINATING    | Run is being terminated |
| TERMINATED     | Run has completed       |
| SKIPPED        | Run was skipped         |
| INTERNAL_ERROR | Internal system error   |

## Run Result States

| State    | Description                |
| -------- | -------------------------- |
| SUCCESS  | Run completed successfully |
| FAILED   | Run failed                 |
| TIMEDOUT | Run exceeded timeout       |
| CANCELED | Run was cancelled          |

---

## Advanced Examples

### Complete Job Workflow

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs, compute
import time

def create_and_monitor_job():
    """Create job, trigger run, and monitor completion"""
    client = WorkspaceClient()

    # 1. Create job
    print("Creating job...")
    job = client.jobs.create(
        name="Data Processing Pipeline",
        tasks=[
            jobs.Task(
                task_key="extract",
                notebook_task=jobs.NotebookTask(
                    notebook_path="/Pipelines/extract"
                ),
                new_cluster=compute.ClusterSpec(
                    spark_version="13.3.x-scala2.12",
                    node_type_id="i3.xlarge",
                    num_workers=2
                )
            ),
            jobs.Task(
                task_key="transform",
                depends_on=[jobs.TaskDependency(task_key="extract")],
                notebook_task=jobs.NotebookTask(
                    notebook_path="/Pipelines/transform"
                ),
                existing_cluster_id="1234-567890-abc123"
            )
        ],
        email_notifications=jobs.JobEmailNotifications(
            on_failure=["team@example.com"]
        ),
        tags={"pipeline": "etl", "version": "1.0"}
    )

    job_id = job.job_id
    print(f"Job created: {job_id}")

    # 2. Trigger run
    print("Triggering run...")
    run = client.jobs.run_now(
        job_id=job_id,
        notebook_params={"date": "2026-02-27"}
    )

    run_id = run.run_id
    print(f"Run started: {run_id}")

    # 3. Monitor run
    print("Monitoring run...")
    while True:
        run_info = client.jobs.get_run(run_id=run_id)
        state = run_info.state.life_cycle_state

        print(f"Current state: {state}")

        if state in ["TERMINATED", "SKIPPED", "INTERNAL_ERROR"]:
            result = run_info.state.result_state
            print(f"Run completed with result: {result}")

            if result == "SUCCESS":
                print("✓ Job completed successfully!")
            else:
                print(f"✗ Job failed: {run_info.state.state_message}")

            break

        time.sleep(10)

    # 4. Get output
    output = client.jobs.get_run_output(run_id=run_id)
    print(f"Output: {output}")

    return job_id, run_id

# Run workflow
job_id, run_id = create_and_monitor_job()
```

### Multi-Task Job with Branching

```python
def create_branching_pipeline():
    """Create job with parallel execution branches"""
    client = WorkspaceClient()

    job = client.jobs.create(
        name="Branching Pipeline",
        tasks=[
            # Root task
            jobs.Task(
                task_key="source",
                notebook_task=jobs.NotebookTask(
                    notebook_path="/Pipelines/source"
                ),
                existing_cluster_id="1234-567890-abc123"
            ),

            # Branch 1: Customer data
            jobs.Task(
                task_key="process_customers",
                depends_on=[jobs.TaskDependency(task_key="source")],
                notebook_task=jobs.NotebookTask(
                    notebook_path="/Pipelines/customers"
                ),
                existing_cluster_id="1234-567890-abc123"
            ),

            # Branch 2: Order data
            jobs.Task(
                task_key="process_orders",
                depends_on=[jobs.TaskDependency(task_key="source")],
                notebook_task=jobs.NotebookTask(
                    notebook_path="/Pipelines/orders"
                ),
                existing_cluster_id="1234-567890-abc123"
            ),

            # Merge branches
            jobs.Task(
                task_key="merge_results",
                depends_on=[
                    jobs.TaskDependency(task_key="process_customers"),
                    jobs.TaskDependency(task_key="process_orders")
                ],
                notebook_task=jobs.NotebookTask(
                    notebook_path="/Pipelines/merge"
                ),
                existing_cluster_id="1234-567890-abc123"
            )
        ],
        max_concurrent_runs=1
    )

    print(f"Branching pipeline created: {job.job_id}")
    return job.job_id

# Create pipeline
job_id = create_branching_pipeline()
```

### Job with Conditional Tasks

```python
def create_conditional_job():
    """Create job with conditional execution"""
    client = WorkspaceClient()

    job = client.jobs.create(
        name="Conditional Pipeline",
        tasks=[
            # Data quality check
            jobs.Task(
                task_key="quality_check",
                notebook_task=jobs.NotebookTask(
                    notebook_path="/Pipelines/quality_check"
                ),
                existing_cluster_id="1234-567890-abc123"
            ),

            # Process only if quality check passes
            jobs.Task(
                task_key="process_data",
                depends_on=[
                    jobs.TaskDependency(
                        task_key="quality_check",
                        outcome="true"  # Only run if previous task succeeds
                    )
                ],
                notebook_task=jobs.NotebookTask(
                    notebook_path="/Pipelines/process"
                ),
                existing_cluster_id="1234-567890-abc123"
            ),

            # Send alert if quality check fails
            jobs.Task(
                task_key="alert_failure",
                depends_on=[
                    jobs.TaskDependency(
                        task_key="quality_check",
                        outcome="false"
                    )
                ],
                notebook_task=jobs.NotebookTask(
                    notebook_path="/Alerts/quality_failure"
                ),
                existing_cluster_id="1234-567890-abc123"
            )
        ]
    )

    print(f"Conditional job created: {job.job_id}")
    return job.job_id

# Create conditional job
job_id = create_conditional_job()
```

### Batch Job Management

```python
def manage_multiple_jobs():
    """Manage multiple jobs as a batch"""
    client = WorkspaceClient()

    # List all jobs
    all_jobs = list(client.jobs.list())
    print(f"Total jobs: {len(all_jobs)}")

    # Find jobs with specific tag
    etl_jobs = [
        job for job in all_jobs
        if job.settings.tags and job.settings.tags.get("type") == "etl"
    ]

    print(f"ETL jobs: {len(etl_jobs)}")

    # Trigger all ETL jobs
    run_ids = []
    for job in etl_jobs:
        print(f"Triggering job: {job.settings.name}")
        run = client.jobs.run_now(job_id=job.job_id)
        run_ids.append(run.run_id)

    # Wait for all to complete
    print("Waiting for jobs to complete...")
    for run_id in run_ids:
        client.jobs.wait_get_run_job_terminated_or_skipped(run_id=run_id)

    print("All jobs completed!")

    # Check results
    for run_id in run_ids:
        run = client.jobs.get_run(run_id=run_id)
        print(f"Run {run_id}: {run.state.result_state}")

# Manage jobs
manage_multiple_jobs()
```

---

## Best Practices

### Job Configuration

```python
# Good: Use retries for fault tolerance
max_retries=3
min_retry_interval_millis=60000
retry_on_timeout=True

# Good: Set reasonable timeouts
timeout_seconds=3600  # 1 hour

# Good: Tag jobs for organization
tags={
    "project": "analytics",
    "environment": "production",
    "owner": "data-team"
}

# Good: Email notifications for failures
email_notifications=jobs.JobEmailNotifications(
    on_failure=["team@example.com"],
    on_success=["team@example.com"]
)
```

### Cluster Selection

```python
# Good: Use existing cluster for frequent jobs
existing_cluster_id="1234-567890-abc123"

# Good: Use job cluster for scheduled jobs
new_cluster=compute.ClusterSpec(
    spark_version="13.3.x-scala2.12",
    node_type_id="i3.xlarge",
    num_workers=2,
    autotermination_minutes=30  # Terminate after job
)

# Good: Right-size clusters based on workload
node_type_id="i3.2xlarge"  # For large jobs
num_workers=8
```

### Task Dependencies

```python
# Good: Clear dependency structure
jobs.Task(
    task_key="transform",
    depends_on=[
        jobs.TaskDependency(task_key="extract")
    ],
    ...
)

# Good: Parallel execution where possible
# Branch tasks that don't depend on each other
```

### Error Handling

```python
# Good: Implement retry logic
max_retries=2
retry_on_timeout=True

# Good: Send notifications on failure
email_notifications=jobs.JobEmailNotifications(
    on_failure=["oncall@example.com"]
)

# Good: Add error handling in notebooks
try:
    # Main logic
    process_data()
except Exception as e:
    # Log error
    dbutils.notebook.exit(f"ERROR: {str(e)}")
```

---

## Troubleshooting

### Job Won't Start

**Problem**: Job stuck in PENDING

**Solutions**:

- Check cluster availability
- Verify cluster configuration
- Check resource quotas
- Review cluster policies

### Task Failures

**Problem**: Tasks failing repeatedly

**Solutions**:

```python
# Increase timeout
timeout_seconds=7200  # 2 hours

# Add retry logic
max_retries=3
min_retry_interval_millis=120000

# Check logs
output = client.jobs.get_run_output(run_id=run_id)
print(output.error)
```

### Performance Issues

**Problem**: Jobs running slowly

**Solutions**:

- Right-size cluster
- Enable autoscaling
- Optimize notebook code
- Use appropriate instance types

---

## Related Documentation

- [API Overview](overview.md)
- [Clusters API](clusters.md)
- [Python SDK Guide](../sdk/python.md)
- [Quick Start Guide](../getting-started/quickstart.md)
- [Best Practices: General](../best-practices/general.md)

## Additional Resources

- [Official Jobs API Documentation](https://docs.databricks.com/api/workspace/jobs)
- [Workflow Orchestration Guide](https://docs.databricks.com/workflows/)
- [Job Scheduling Best Practices](https://docs.databricks.com/workflows/jobs/jobs.html)
