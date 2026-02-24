# Databricks Workspace API Reference

## Overview

The Workspace API allows you to manage workspace objects like notebooks, directories, libraries, and experiments. This API is essential for programmatic workspace management, CI/CD pipelines, and automated deployments.

## Base URL

```
https://<databricks-instance>/api/2.0/workspace
```

## Authentication

All Workspace API requests require authentication using a personal access token or service principal token in the Authorization header:

```
Authorization: Bearer <token>
```

## Object Types

Workspace objects have different types:
- `NOTEBOOK` - Databricks notebook
- `DIRECTORY` - Folder/directory
- `LIBRARY` - JAR, Python wheel, or other library
- `REPO` - Git repository (Databricks Repos)
- `FILE` - Generic file

## Common Parameters

- `path` - Absolute path to workspace object (must start with `/`)
- `format` - Export/import format: `SOURCE`, `HTML`, `JUPYTER`, `DBC`
- `overwrite` - Boolean flag to overwrite existing objects

---

## Endpoints

### List Workspace Objects

List the contents of a directory in the workspace.

**Endpoint:** `GET /api/2.0/workspace/list`

**Parameters:**
- `path` (required) - The absolute path of the directory
- `notebooks_modified_after` (optional) - Filter notebooks by modification timestamp

**Request Example:**

```bash
curl -X GET \
  'https://<databricks-instance>/api/2.0/workspace/list?path=/Users/user@example.com' \
  -H 'Authorization: Bearer <token>'
```

**Python Example:**

```python
import requests

url = "https://<databricks-instance>/api/2.0/workspace/list"
headers = {"Authorization": f"Bearer {token}"}
params = {"path": "/Users/user@example.com"}

response = requests.get(url, headers=headers, params=params)
objects = response.json().get("objects", [])

for obj in objects:
    print(f"{obj['object_type']}: {obj['path']}")
```

**Response:**

```json
{
  "objects": [
    {
      "path": "/Users/user@example.com/notebook1",
      "object_type": "NOTEBOOK",
      "language": "PYTHON",
      "object_id": 123456
    },
    {
      "path": "/Users/user@example.com/folder1",
      "object_type": "DIRECTORY",
      "object_id": 123457
    }
  ]
}
```

---

### Get Workspace Object Status

Get metadata about a workspace object.

**Endpoint:** `GET /api/2.0/workspace/get-status`

**Parameters:**
- `path` (required) - The absolute path of the object

**Request Example:**

```bash
curl -X GET \
  'https://<databricks-instance>/api/2.0/workspace/get-status?path=/Users/user@example.com/notebook1' \
  -H 'Authorization: Bearer <token>'
```

**Python Example:**

```python
import requests

url = "https://<databricks-instance>/api/2.0/workspace/get-status"
headers = {"Authorization": f"Bearer {token}"}
params = {"path": "/Users/user@example.com/notebook1"}

response = requests.get(url, headers=headers, params=params)
status = response.json()

print(f"Type: {status['object_type']}")
print(f"Language: {status.get('language', 'N/A')}")
print(f"Created: {status['created_at']}")
```

**Response:**

```json
{
  "path": "/Users/user@example.com/notebook1",
  "object_type": "NOTEBOOK",
  "object_id": 123456,
  "language": "PYTHON",
  "created_at": 1609459200000,
  "modified_at": 1609545600000
}
```

---

### Create Directory

Create a new directory in the workspace.

**Endpoint:** `POST /api/2.0/workspace/mkdirs`

**Request Body:**
- `path` (required) - The absolute path of the directory to create

**Request Example:**

```bash
curl -X POST \
  'https://<databricks-instance>/api/2.0/workspace/mkdirs' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "path": "/Users/user@example.com/new_folder"
  }'
```

**Python Example:**

```python
import requests

url = "https://<databricks-instance>/api/2.0/workspace/mkdirs"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
data = {
    "path": "/Users/user@example.com/new_folder"
}

response = requests.post(url, headers=headers, json=data)
if response.status_code == 200:
    print("Directory created successfully")
```

**Response:** `200 OK` (empty body on success)

---

### Delete Workspace Object

Delete a workspace object (notebook, directory, or file).

**Endpoint:** `POST /api/2.0/workspace/delete`

**Request Body:**
- `path` (required) - The absolute path of the object to delete
- `recursive` (optional) - Set to `true` to recursively delete directories

**Request Example:**

```bash
curl -X POST \
  'https://<databricks-instance>/api/2.0/workspace/delete' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "path": "/Users/user@example.com/old_folder",
    "recursive": true
  }'
```

**Python Example:**

```python
import requests

url = "https://<databricks-instance>/api/2.0/workspace/delete"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
data = {
    "path": "/Users/user@example.com/old_folder",
    "recursive": True
}

response = requests.post(url, headers=headers, json=data)
if response.status_code == 200:
    print("Object deleted successfully")
```

**Response:** `200 OK` (empty body on success)

---

### Export Workspace Object

Export a notebook or directory from the workspace.

**Endpoint:** `GET /api/2.0/workspace/export`

**Parameters:**
- `path` (required) - The absolute path of the object to export
- `format` (optional) - Export format: `SOURCE`, `HTML`, `JUPYTER`, `DBC` (default: `SOURCE`)
- `direct_download` (optional) - Set to `true` for binary download

**Request Example:**

```bash
curl -X GET \
  'https://<databricks-instance>/api/2.0/workspace/export?path=/Users/user@example.com/notebook1&format=SOURCE' \
  -H 'Authorization: Bearer <token>'
```

**Python Example:**

```python
import requests
import base64

url = "https://<databricks-instance>/api/2.0/workspace/export"
headers = {"Authorization": f"Bearer {token}"}
params = {
    "path": "/Users/user@example.com/notebook1",
    "format": "SOURCE"
}

response = requests.get(url, headers=headers, params=params)
result = response.json()

# Decode base64 content
content = base64.b64decode(result["content"]).decode('utf-8')
print(content)
```

**Export as Jupyter Notebook:**

```python
import requests
import base64
import json

url = "https://<databricks-instance>/api/2.0/workspace/export"
headers = {"Authorization": f"Bearer {token}"}
params = {
    "path": "/Users/user@example.com/notebook1",
    "format": "JUPYTER"
}

response = requests.get(url, headers=headers, params=params)
result = response.json()

# Decode and save as .ipynb file
notebook_content = base64.b64decode(result["content"]).decode('utf-8')
with open("notebook1.ipynb", "w") as f:
    f.write(notebook_content)
```

**Response:**

```json
{
  "content": "IyBEYXRhYnJpY2tzIG5vdGVib29rIHNvdXJjZQ0KIyBDT01NQU5EIC0tLS0tLS0tLS0tCgpwcmludCgiSGVsbG8sIFdvcmxkISIp"
}
```

---

### Import Workspace Object

Import a notebook or directory into the workspace.

**Endpoint:** `POST /api/2.0/workspace/import`

**Request Body:**
- `path` (required) - The absolute path where the object should be imported
- `format` (required) - Import format: `SOURCE`, `HTML`, `JUPYTER`, `DBC`
- `language` (optional) - Language of the notebook: `PYTHON`, `SCALA`, `SQL`, `R`
- `content` (required) - Base64-encoded content
- `overwrite` (optional) - Set to `true` to overwrite existing objects

**Request Example:**

```bash
curl -X POST \
  'https://<databricks-instance>/api/2.0/workspace/import' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "path": "/Users/user@example.com/imported_notebook",
    "format": "SOURCE",
    "language": "PYTHON",
    "content": "IyBEYXRhYnJpY2tzIG5vdGVib29rIHNvdXJjZQpwcmludCgiSGVsbG8sIFdvcmxkISIp",
    "overwrite": true
  }'
```

**Python Example:**

```python
import requests
import base64

# Read notebook content
with open("local_notebook.py", "r") as f:
    content = f.read()

# Encode to base64
encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')

url = "https://<databricks-instance>/api/2.0/workspace/import"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
data = {
    "path": "/Users/user@example.com/imported_notebook",
    "format": "SOURCE",
    "language": "PYTHON",
    "content": encoded_content,
    "overwrite": True
}

response = requests.post(url, headers=headers, json=data)
if response.status_code == 200:
    print("Notebook imported successfully")
```

**Import Jupyter Notebook:**

```python
import requests
import base64

# Read Jupyter notebook
with open("notebook.ipynb", "r") as f:
    jupyter_content = f.read()

# Encode to base64
encoded_content = base64.b64encode(jupyter_content.encode('utf-8')).decode('utf-8')

url = "https://<databricks-instance>/api/2.0/workspace/import"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
data = {
    "path": "/Users/user@example.com/jupyter_notebook",
    "format": "JUPYTER",
    "content": encoded_content,
    "overwrite": True
}

response = requests.post(url, headers=headers, json=data)
if response.status_code == 200:
    print("Jupyter notebook imported successfully")
```

**Response:** `200 OK` (empty body on success)

---

## Python SDK Examples

### Using Databricks SDK

```python
from databricks.sdk import WorkspaceClient

# Initialize client
w = WorkspaceClient()

# List workspace objects
objects = w.workspace.list("/Users/user@example.com")
for obj in objects:
    print(f"{obj.object_type}: {obj.path}")

# Get object status
status = w.workspace.get_status("/Users/user@example.com/notebook1")
print(f"Type: {status.object_type}, Language: {status.language}")

# Create directory
w.workspace.mkdirs("/Users/user@example.com/new_folder")

# Export notebook
content = w.workspace.export("/Users/user@example.com/notebook1", format="SOURCE")
print(content)

# Import notebook
with open("local_notebook.py", "r") as f:
    notebook_content = f.read()
    
w.workspace.import_notebook(
    path="/Users/user@example.com/imported_notebook",
    format="SOURCE",
    language="PYTHON",
    content=notebook_content.encode('utf-8'),
    overwrite=True
)

# Delete object
w.workspace.delete("/Users/user@example.com/old_notebook")
```

---

## Advanced Examples

### Recursive Directory Export

Export an entire directory structure:

```python
import requests
import base64
import os
from pathlib import Path

def export_directory(workspace_path, local_path, token, instance):
    """Recursively export workspace directory to local filesystem"""
    
    headers = {"Authorization": f"Bearer {token}"}
    base_url = f"https://{instance}/api/2.0/workspace"
    
    # Create local directory
    os.makedirs(local_path, exist_ok=True)
    
    # List workspace objects
    list_url = f"{base_url}/list"
    params = {"path": workspace_path}
    response = requests.get(list_url, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"Error listing {workspace_path}: {response.text}")
        return
    
    objects = response.json().get("objects", [])
    
    for obj in objects:
        obj_path = obj["path"]
        obj_name = obj_path.split("/")[-1]
        obj_type = obj["object_type"]
        
        if obj_type == "DIRECTORY":
            # Recursively export subdirectory
            new_local_path = os.path.join(local_path, obj_name)
            export_directory(obj_path, new_local_path, token, instance)
            
        elif obj_type == "NOTEBOOK":
            # Export notebook
            export_url = f"{base_url}/export"
            export_params = {
                "path": obj_path,
                "format": "SOURCE"
            }
            export_response = requests.get(export_url, headers=headers, params=export_params)
            
            if export_response.status_code == 200:
                content = base64.b64decode(export_response.json()["content"])
                
                # Determine file extension
                language = obj.get("language", "PYTHON")
                ext_map = {"PYTHON": ".py", "SCALA": ".scala", "SQL": ".sql", "R": ".r"}
                ext = ext_map.get(language, ".txt")
                
                # Save to local file
                file_path = os.path.join(local_path, f"{obj_name}{ext}")
                with open(file_path, "wb") as f:
                    f.write(content)
                print(f"Exported: {obj_path} -> {file_path}")

# Usage
export_directory(
    workspace_path="/Users/user@example.com/project",
    local_path="./exported_project",
    token="<your-token>",
    instance="<databricks-instance>"
)
```

### Bulk Import from Git Repository

Import notebooks from a local Git repository:

```python
import requests
import base64
import os
from pathlib import Path

def import_directory(local_path, workspace_path, token, instance):
    """Recursively import local directory to workspace"""
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    base_url = f"https://{instance}/api/2.0/workspace"
    
    # Create workspace directory
    mkdirs_url = f"{base_url}/mkdirs"
    mkdirs_data = {"path": workspace_path}
    requests.post(mkdirs_url, headers=headers, json=mkdirs_data)
    
    # Import files
    for item in os.listdir(local_path):
        item_path = os.path.join(local_path, item)
        
        if os.path.isdir(item_path):
            # Recursively import subdirectory
            new_workspace_path = f"{workspace_path}/{item}"
            import_directory(item_path, new_workspace_path, token, instance)
            
        elif item.endswith(('.py', '.scala', '.sql', '.r')):
            # Import notebook
            with open(item_path, "r") as f:
                content = f.read()
            
            encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            
            # Determine language
            ext_map = {".py": "PYTHON", ".scala": "SCALA", ".sql": "SQL", ".r": "R"}
            language = ext_map.get(Path(item).suffix, "PYTHON")
            
            # Remove extension from workspace name
            notebook_name = Path(item).stem
            notebook_path = f"{workspace_path}/{notebook_name}"
            
            import_url = f"{base_url}/import"
            import_data = {
                "path": notebook_path,
                "format": "SOURCE",
                "language": language,
                "content": encoded_content,
                "overwrite": True
            }
            
            response = requests.post(import_url, headers=headers, json=import_data)
            if response.status_code == 200:
                print(f"Imported: {item_path} -> {notebook_path}")
            else:
                print(f"Error importing {item_path}: {response.text}")

# Usage
import_directory(
    local_path="./local_notebooks",
    workspace_path="/Users/user@example.com/imported_project",
    token="<your-token>",
    instance="<databricks-instance>"
)
```

### Search Notebooks by Content

Search for notebooks containing specific text:

```python
import requests
import base64
import re

def search_notebooks(root_path, search_text, token, instance):
    """Search for notebooks containing specific text"""
    
    headers = {"Authorization": f"Bearer {token}"}
    base_url = f"https://{instance}/api/2.0/workspace"
    
    results = []
    
    def search_recursive(path):
        # List objects
        list_url = f"{base_url}/list"
        params = {"path": path}
        response = requests.get(list_url, headers=headers, params=params)
        
        if response.status_code != 200:
            return
        
        objects = response.json().get("objects", [])
        
        for obj in objects:
            if obj["object_type"] == "DIRECTORY":
                search_recursive(obj["path"])
            elif obj["object_type"] == "NOTEBOOK":
                # Export and search notebook
                export_url = f"{base_url}/export"
                export_params = {
                    "path": obj["path"],
                    "format": "SOURCE"
                }
                export_response = requests.get(export_url, headers=headers, params=export_params)
                
                if export_response.status_code == 200:
                    content = base64.b64decode(export_response.json()["content"]).decode('utf-8')
                    
                    if search_text.lower() in content.lower():
                        # Find line numbers
                        lines = content.split('\n')
                        matches = []
                        for i, line in enumerate(lines, 1):
                            if search_text.lower() in line.lower():
                                matches.append((i, line.strip()))
                        
                        results.append({
                            "path": obj["path"],
                            "language": obj.get("language"),
                            "matches": matches
                        })
    
    search_recursive(root_path)
    return results

# Usage
results = search_notebooks(
    root_path="/Users/user@example.com",
    search_text="spark.read",
    token="<your-token>",
    instance="<databricks-instance>"
)

for result in results:
    print(f"\nFound in: {result['path']}")
    for line_num, line in result['matches']:
        print(f"  Line {line_num}: {line}")
```

---

## Error Handling

### Common Error Codes

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | `INVALID_PARAMETER_VALUE` | Invalid path or parameter |
| 400 | `RESOURCE_ALREADY_EXISTS` | Object already exists (use `overwrite: true`) |
| 404 | `RESOURCE_DOES_NOT_EXIST` | Object not found at specified path |
| 403 | `PERMISSION_DENIED` | Insufficient permissions |
| 500 | `INTERNAL_ERROR` | Internal server error |

### Error Handling Example

```python
import requests
from requests.exceptions import RequestException

def safe_workspace_operation(operation_func):
    """Wrapper for safe workspace operations with error handling"""
    try:
        response = operation_func()
        response.raise_for_status()
        return response.json() if response.text else {}
    except RequestException as e:
        if e.response is not None:
            error_data = e.response.json()
            error_code = error_data.get("error_code")
            error_message = error_data.get("message")
            
            if error_code == "RESOURCE_ALREADY_EXISTS":
                print(f"Object already exists: {error_message}")
                return None
            elif error_code == "RESOURCE_DOES_NOT_EXIST":
                print(f"Object not found: {error_message}")
                return None
            elif error_code == "PERMISSION_DENIED":
                print(f"Permission denied: {error_message}")
                return None
            else:
                print(f"Error {error_code}: {error_message}")
                raise
        else:
            print(f"Network error: {str(e)}")
            raise

# Usage
def list_operation():
    url = f"https://{instance}/api/2.0/workspace/list"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"path": "/Users/user@example.com"}
    return requests.get(url, headers=headers, params=params)

result = safe_workspace_operation(list_operation)
```

---

## Best Practices

### 1. Path Conventions

```python
# Always use absolute paths starting with /
correct_path = "/Users/user@example.com/notebook"
incorrect_path = "notebook"  # Will fail

# Use forward slashes, even on Windows
correct_path = "/Users/user@example.com/folder/notebook"
incorrect_path = "/Users/user@example.com\\folder\\notebook"  # Don't use backslashes
```

### 2. Batch Operations

For bulk operations, implement rate limiting and retries:

```python
import time
from functools import wraps

def rate_limit(max_per_second=10):
    """Rate limiting decorator"""
    min_interval = 1.0 / max_per_second
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

@rate_limit(max_per_second=5)
def export_notebook(path, token, instance):
    """Rate-limited notebook export"""
    url = f"https://{instance}/api/2.0/workspace/export"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"path": path, "format": "SOURCE"}
    response = requests.get(url, headers=headers, params=params)
    return response
```

### 3. Version Control Integration

Create a sync script for CI/CD:

```python
import os
import requests
import base64
from datetime import datetime

def sync_workspace_to_git(workspace_path, git_path, token, instance):
    """Export workspace to Git repository"""
    
    # Export from workspace
    export_directory(workspace_path, git_path, token, instance)
    
    # Git operations
    os.chdir(git_path)
    os.system('git add .')
    os.system(f'git commit -m "Workspace sync {datetime.now()}"')
    os.system('git push')

def sync_git_to_workspace(git_path, workspace_path, token, instance):
    """Import from Git repository to workspace"""
    
    # Git operations
    os.chdir(git_path)
    os.system('git pull')
    
    # Import to workspace
    import_directory(git_path, workspace_path, token, instance)
```

---

## Related APIs

- [Jobs API](./jobs.md) - Schedule and run notebooks
- [Clusters API](./clusters.md) - Manage compute clusters
- [Repos API](./repos.md) - Manage Git repositories
- [Secrets API](./secrets.md) - Manage secrets for notebooks

---

## Additional Resources

- [Databricks Workspace Documentation](https://docs.databricks.com/workspace/index.html)
- [Workspace API Reference](https://docs.databricks.com/dev-tools/api/latest/workspace.html)
- [Databricks CLI Workspace Commands](https://docs.databricks.com/dev-tools/cli/workspace-cli.html)