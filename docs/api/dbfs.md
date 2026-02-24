# Databricks File System (DBFS) API

## Overview

The DBFS API provides programmatic access to the Databricks File System, a distributed file system mounted into a Databricks workspace. DBFS allows you to store and access files, data, and libraries across clusters.

## Base Endpoint

```
/api/2.0/dbfs
```

## What is DBFS?

DBFS is an abstraction layer on top of scalable object storage (AWS S3, Azure Blob Storage, Google Cloud Storage) that provides:

- **File system interface**: Standard file operations (read, write, list, delete)
- **Cluster access**: All clusters can access DBFS
- **Persistence**: Data persists beyond cluster lifecycle
- **Performance**: Optimized for distributed workloads

## DBFS Paths

### Path Format

```
dbfs:/path/to/file
/dbfs/path/to/file (when accessing from driver)
```

### Common DBFS Directories

| Path | Purpose |
|------|---------|
| `/FileStore` | User-uploaded files, accessible via web UI |
| `/databricks-datasets` | Sample datasets provided by Databricks |
| `/user/hive/warehouse` | Default location for managed tables |
| `/tmp` | Temporary files (cleared periodically) |
| `/mnt` | Mount points for cloud storage |

## Authentication

All requests require authentication. See [Authentication Guide](../getting-started/authentication.md).

```python
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
```

---

## List Directory Contents

List files and directories at a given path.

### Endpoint

```
GET /api/2.0/dbfs/list
```

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| path | string | Yes | The path to list |

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
    f"{DATABRICKS_HOST}/api/2.0/dbfs/list",
    headers=headers,
    params={"path": "/FileStore"}
)

files = response.json().get("files", [])

for file in files:
    file_type = "DIR" if file["is_dir"] else "FILE"
    size = file.get("file_size", 0)
    print(f"[{file_type}] {file['path']} ({size} bytes)")
```

### SDK Example

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# List directory contents
for file in client.dbfs.list(path="/FileStore"):
    file_type = "DIR" if file.is_dir else "FILE"
    print(f"[{file_type}] {file.path} ({file.file_size} bytes)")
```

### Response

```json
{
  "files": [
    {
      "path": "/FileStore/data.csv",
      "is_dir": false,
      "file_size": 1024000
    },
    {
      "path": "/FileStore/images",
      "is_dir": true,
      "file_size": 0
    }
  ]
}
```

---

## Get File Status

Get metadata about a file or directory.

### Endpoint

```
GET /api/2.0/dbfs/get-status
```

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| path | string | Yes | The path to check |

### Example

```python
import requests

response = requests.get(
    f"{DATABRICKS_HOST}/api/2.0/dbfs/get-status",
    headers=headers,
    params={"path": "/FileStore/data.csv"}
)

status = response.json()
print(f"Path: {status['path']}")
print(f"Size: {status['file_size']} bytes")
print(f"Modified: {status['modification_time']}")
```

### SDK Example

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# Get file status
status = client.dbfs.get_status(path="/FileStore/data.csv")
print(f"Size: {status.file_size} bytes")
print(f"Is directory: {status.is_dir}")
```

### Response

```json
{
  "path": "/FileStore/data.csv",
  "is_dir": false,
  "file_size": 1024000,
  "modification_time": 1699564800000
}
```

---

## Create Directory

Create a directory and its parent directories if they don't exist.

### Endpoint

```
POST /api/2.0/dbfs/mkdirs
```

### Request Body

```json
{
  "path": "/FileStore/my-project/data"
}
```

### Example

```python
import requests

response = requests.post(
    f"{DATABRICKS_HOST}/api/2.0/dbfs/mkdirs",
    headers=headers,
    json={"path": "/FileStore/my-project/data"}
)

if response.status_code == 200:
    print("Directory created successfully!")
```

### SDK Example

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# Create directory (creates parent directories too)
client.dbfs.mkdirs(path="/FileStore/my-project/data")
print("Directory created!")
```

---

## Upload File (Small Files)

Upload a file to DBFS. For files under 1MB, use the PUT method.

### Endpoint

```
POST /api/2.0/dbfs/put
```

### Request Body

```json
{
  "path": "/FileStore/data.csv",
  "contents": "<base64-encoded-content>",
  "overwrite": true
}
```

### Example

```python
import requests
import base64

# Read file
with open("data.csv", "rb") as f:
    content = f.read()

# Encode to base64
encoded_content = base64.b64encode(content).decode('utf-8')

response = requests.post(
    f"{DATABRICKS_HOST}/api/2.0/dbfs/put",
    headers=headers,
    json={
        "path": "/FileStore/data.csv",
        "contents": encoded_content,
        "overwrite": True
    }
)

if response.status_code == 200:
    print("File uploaded successfully!")
```

### SDK Example

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# Upload file
with open("data.csv", "rb") as f:
    content = f.read()

client.dbfs.put(
    path="/FileStore/data.csv",
    contents=content,
    overwrite=True
)

print("File uploaded!")
```

---

## Upload Large File (Streaming)

For files larger than 1MB, use the streaming API.

### Process

1. Create handle with `create`
2. Add blocks with `add-block`
3. Close handle with `close`

### Create Handle

```
POST /api/2.0/dbfs/create
```

```json
{
  "path": "/FileStore/large-file.dat",
  "overwrite": true
}
```

### Add Block

```
POST /api/2.0/dbfs/add-block
```

```json
{
  "handle": 12345,
  "data": "<base64-encoded-data>"
}
```

### Close Handle

```
POST /api/2.0/dbfs/close
```

```json
{
  "handle": 12345
}
```

### Complete Example

```python
import requests
import base64

def upload_large_file(local_path, dbfs_path):
    """Upload large file to DBFS using streaming API"""
    
    # Step 1: Create handle
    response = requests.post(
        f"{DATABRICKS_HOST}/api/2.0/dbfs/create",
        headers=headers,
        json={
            "path": dbfs_path,
            "overwrite": True
        }
    )
    handle = response.json()["handle"]
    
    # Step 2: Upload in chunks
    chunk_size = 1024 * 1024  # 1MB chunks
    
    try:
        with open(local_path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                
                encoded_chunk = base64.b64encode(chunk).decode('utf-8')
                
                requests.post(
                    f"{DATABRICKS_HOST}/api/2.0/dbfs/add-block",
                    headers=headers,
                    json={
                        "handle": handle,
                        "data": encoded_chunk
                    }
                )
                print(f"Uploaded {len(chunk)} bytes")
        
        # Step 3: Close handle
        requests.post(
            f"{DATABRICKS_HOST}/api/2.0/dbfs/close",
            headers=headers,
            json={"handle": handle}
        )
        
        print(f"File uploaded successfully to {dbfs_path}")
        
    except Exception as e:
        print(f"Upload failed: {e}")
        # Attempt to close handle on error
        requests.post(
            f"{DATABRICKS_HOST}/api/2.0/dbfs/close",
            headers=headers,
            json={"handle": handle}
        )

# Upload large file
upload_large_file("large_dataset.csv", "/FileStore/large_dataset.csv")
```

---

## Read File

Read contents of a file from DBFS.

### Endpoint

```
GET /api/2.0/dbfs/read
```

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| path | string | Yes | The file path to read |
| offset | integer | No | Starting byte offset (default: 0) |
| length | integer | No | Number of bytes to read (default: 1MB) |

### Example

```python
import requests
import base64

response = requests.get(
    f"{DATABRICKS_HOST}/api/2.0/dbfs/read",
    headers=headers,
    params={
        "path": "/FileStore/data.csv",
        "offset": 0,
        "length": 1024000
    }
)

# Decode base64 content
data = response.json()
content = base64.b64decode(data["data"])

# Save to local file
with open("downloaded_data.csv", "wb") as f:
    f.write(content)

print("File downloaded successfully!")
```

### SDK Example

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# Read file
file_data = client.dbfs.read(path="/FileStore/data.csv")

# Save to local file
with open("downloaded_data.csv", "wb") as f:
    f.write(file_data.data)

print("File downloaded!")
```

### Response

```json
{
  "bytes_read": 1024000,
  "data": "<base64-encoded-content>"
}
```

---

## Download Large File

```python
import requests
import base64

def download_large_file(dbfs_path, local_path):
    """Download large file from DBFS"""
    
    # Get file size
    status_response = requests.get(
        f"{DATABRICKS_HOST}/api/2.0/dbfs/get-status",
        headers=headers,
        params={"path": dbfs_path}
    )
    file_size = status_response.json()["file_size"]
    
    # Download in chunks
    chunk_size = 1024 * 1024  # 1MB chunks
    offset = 0
    
    with open(local_path, "wb") as f:
        while offset < file_size:
            response = requests.get(
                f"{DATABRICKS_HOST}/api/2.0/dbfs/read",
                headers=headers,
                params={
                    "path": dbfs_path,
                    "offset": offset,
                    "length": chunk_size
                }
            )
            
            data = response.json()
            content = base64.b64decode(data["data"])
            f.write(content)
            
            bytes_read = data["bytes_read"]
            offset += bytes_read
            
            print(f"Downloaded {offset}/{file_size} bytes")
    
    print(f"File downloaded to {local_path}")

# Download large file
download_large_file("/FileStore/large_dataset.csv", "large_dataset.csv")
```

---

## Move File or Directory

Move or rename a file or directory.

### Endpoint

```
POST /api/2.0/dbfs/move
```

### Request Body

```json
{
  "source_path": "/FileStore/old-name.csv",
  "destination_path": "/FileStore/new-name.csv"
}
```

### Example

```python
import requests

response = requests.post(
    f"{DATABRICKS_HOST}/api/2.0/dbfs/move",
    headers=headers,
    json={
        "source_path": "/FileStore/data.csv",
        "destination_path": "/FileStore/archived/data.csv"
    }
)

if response.status_code == 200:
    print("File moved successfully!")
```

### SDK Example

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# Move file
client.dbfs.move(
    source_path="/FileStore/data.csv",
    destination_path="/FileStore/archived/data.csv"
)

print("File moved!")
```

---

## Delete File or Directory

Delete a file or directory.

### Endpoint

```
POST /api/2.0/dbfs/delete
```

### Request Body

```json
{
  "path": "/FileStore/data.csv",
  "recursive": false
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| path | string | Yes | The path to delete |
| recursive | boolean | No | Delete recursively (for directories) |

### Example

```python
import requests

# Delete file
response = requests.post(
    f"{DATABRICKS_HOST}/api/2.0/dbfs/delete",
    headers=headers,
    json={
        "path": "/FileStore/data.csv",
        "recursive": False
    }
)

# Delete directory recursively
response = requests.post(
    f"{DATABRICKS_HOST}/api/2.0/dbfs/delete",
    headers=headers,
    json={
        "path": "/FileStore/my-project",
        "recursive": True
    }
)

if response.status_code == 200:
    print("Deleted successfully!")
```

### SDK Example

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# Delete file
client.dbfs.delete(path="/FileStore/data.csv", recursive=False)

# Delete directory recursively
client.dbfs.delete(path="/FileStore/my-project", recursive=True)

print("Deleted successfully!")
```

---

## Complete Examples

### File Upload/Download Manager

```python
from databricks.sdk import WorkspaceClient
import os

class DBFSFileManager:
    """Manage DBFS file operations"""
    
    def __init__(self):
        self.client = WorkspaceClient()
    
    def upload_file(self, local_path, dbfs_path, overwrite=True):
        """Upload file to DBFS"""
        with open(local_path, "rb") as f:
            content = f.read()
        
        self.client.dbfs.put(
            path=dbfs_path,
            contents=content,
            overwrite=overwrite
        )
        
        print(f"✓ Uploaded {local_path} to {dbfs_path}")
    
    def download_file(self, dbfs_path, local_path):
        """Download file from DBFS"""
        file_data = self.client.dbfs.read(path=dbfs_path)
        
        with open(local_path, "wb") as f:
            f.write(file_data.data)
        
        print(f"✓ Downloaded {dbfs_path} to {local_path}")
    
    def upload_directory(self, local_dir, dbfs_dir):
        """Upload entire directory to DBFS"""
        # Create base directory
        self.client.dbfs.mkdirs(path=dbfs_dir)
        
        # Walk through local directory
        for root, dirs, files in os.walk(local_dir):
            # Create subdirectories
            for dir_name in dirs:
                local_subdir = os.path.join(root, dir_name)
                rel_path = os.path.relpath(local_subdir, local_dir)
                dbfs_subdir = f"{dbfs_dir}/{rel_path}".replace("\\", "/")
                self.client.dbfs.mkdirs(path=dbfs_subdir)
            
            # Upload files
            for file_name in files:
                local_file = os.path.join(root, file_name)
                rel_path = os.path.relpath(local_file, local_dir)
                dbfs_file = f"{dbfs_dir}/{rel_path}".replace("\\", "/")
                self.upload_file(local_file, dbfs_file)
        
        print(f"✓ Uploaded directory {local_dir} to {dbfs_dir}")
    
    def list_files(self, dbfs_path, recursive=False):
        """List files in DBFS directory"""
        files = []
        
        for item in self.client.dbfs.list(path=dbfs_path):
            if item.is_dir and recursive:
                # Recursively list subdirectories
                files.extend(self.list_files(item.path, recursive=True))
            else:
                files.append({
                    "path": item.path,
                    "size": item.file_size,
                    "is_dir": item.is_dir
                })
        
        return files
    
    def get_directory_size(self, dbfs_path):
        """Calculate total size of directory"""
        total_size = 0
        
        for item in self.client.dbfs.list(path=dbfs_path):
            if item.is_dir:
                total_size += self.get_directory_size(item.path)
            else:
                total_size += item.file_size
        
        return total_size

# Usage
manager = DBFSFileManager()

# Upload file
manager.upload_file("data.csv", "/FileStore/data.csv")

# Download file
manager.download_file("/FileStore/data.csv", "downloaded.csv")

# Upload directory
manager.upload_directory("./my-data", "/FileStore/my-data")

# List files
files = manager.list_files("/FileStore", recursive=True)
for file in files:
    print(f"{file['path']}: {file['size']} bytes")

# Get directory size
size = manager.get_directory_size("/FileStore/my-data")
print(f"Total size: {size / (1024*1024):.2f} MB")
```

### Batch File Operations

```python
from databricks.sdk import WorkspaceClient
from concurrent.futures import ThreadPoolExecutor
import os

def batch_upload_files(file_mapping):
    """Upload multiple files in parallel"""
    client = WorkspaceClient()
    
    def upload_single_file(local_path, dbfs_path):
        try:
            with open(local_path, "rb") as f:
                content = f.read()
            
            client.dbfs.put(path=dbfs_path, contents=content, overwrite=True)
            return f"✓ {local_path} -> {dbfs_path}"
        except Exception as e:
            return f"✗ {local_path}: {e}"
    
    # Upload in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(upload_single_file, local, dbfs)
            for local, dbfs in file_mapping.items()
        ]
        
        for future in futures:
            print(future.result())

# Upload multiple files
files_to_upload = {
    "data1.csv": "/FileStore/data1.csv",
    "data2.csv": "/FileStore/data2.csv",
    "data3.csv": "/FileStore/data3.csv"
}

batch_upload_files(files_to_upload)
```

### DBFS Browser

```python
from databricks.sdk import WorkspaceClient

class DBFSBrowser:
    """Interactive DBFS browser"""
    
    def __init__(self):
        self.client = WorkspaceClient()
        self.current_path = "/"
    
    def ls(self, path=None):
        """List directory contents"""
        path = path or self.current_path
        
        try:
            items = list(self.client.dbfs.list(path=path))
            
            print(f"\nDirectory: {path}")
            print("-" * 60)
            
            for item in items:
                icon = "📁" if item.is_dir else "📄"
                size = f"{item.file_size:,} bytes" if not item.is_dir else ""
                print(f"{icon} {item.path.split('/')[-1]:<40} {size}")
            
            print(f"\nTotal items: {len(items)}")
            
        except Exception as e:
            print(f"Error: {e}")
    
    def cd(self, path):
        """Change directory"""
        # Verify path exists
        try:
            status = self.client.dbfs.get_status(path=path)
            if status.is_dir:
                self.current_path = path
                print(f"Changed to: {path}")
            else:
                print(f"Error: {path} is not a directory")
        except Exception as e:
            print(f"Error: {e}")
    
    def pwd(self):
        """Print working directory"""
        print(self.current_path)
    
    def cat(self, path):
        """Display file contents"""
        try:
            data = self.client.dbfs.read(path=path)
            print(data.data.decode('utf-8'))
        except Exception as e:
            print(f"Error: {e}")
    
    def rm(self, path, recursive=False):
        """Remove file or directory"""
        try:
            self.client.dbfs.delete(path=path, recursive=recursive)
            print(f"✓ Deleted: {path}")
        except Exception as e:
            print(f"Error: {e}")

# Usage
browser = DBFSBrowser()
browser.ls("/FileStore")
browser.cd("/FileStore")
browser.pwd()
```

---

## Best Practices

### File Size Considerations

```python
# Good: Use streaming API for large files (>1MB)
def upload_file_smart(local_path, dbfs_path):
    """Upload file with appropriate method based on size"""
    file_size = os.path.getsize(local_path)
    
    if file_size < 1024 * 1024:  # Less than 1MB
        # Use simple PUT
        with open(local_path, "rb") as f:
            client.dbfs.put(path=dbfs_path, contents=f.read())
    else:
        # Use streaming API
        upload_large_file(local_path, dbfs_path)
```

### Error Handling

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import DatabricksError

client = WorkspaceClient()

# Good: Handle errors gracefully
try:
    client.dbfs.get_status(path="/FileStore/data.csv")
except DatabricksError as e:
    if e.error_code == "RESOURCE_DOES_NOT_EXIST":
        print("File not found")
    else:
        print(f"Error: {e}")
```

### Path Management

```python
# Good: Always use absolute paths
dbfs_path = "/FileStore/data.csv"

# Good: Use forward slashes
dbfs_path = "/FileStore/my-project/data.csv"

# Avoid: Backslashes or relative paths
# dbfs_path = "FileStore\\data.csv"  # Don't do this
```

### Resource Cleanup

```python
# Good: Clean up temporary files
def process_with_temp_files():
    temp_path = "/tmp/processing/data.csv"
    
    try:
        # Upload and process
        client.dbfs.put(path=temp_path, contents=data)
        process_data(temp_path)
    finally:
        # Always clean up
        try:
            client.dbfs.delete(path=temp_path)
        except:
            pass
```

---

## Troubleshooting

### File Not Found

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# Check if file exists before operations
def file_exists(path):
    try:
        client.dbfs.get_status(path=path)
        return True
    except:
        return False

if file_exists("/FileStore/data.csv"):
    print("File exists!")
else:
    print("File not found")
```

### Permission Errors

```python
# Ensure you have write permissions to the path
# Use /FileStore for user-accessible storage
# Use /tmp for temporary files
```

### Large File Upload Issues

```python
# Use chunked upload for reliability
# Implement retry logic for failed chunks
# Monitor upload progress

def upload_with_retry(local_path, dbfs_path, max_retries=3):
    """Upload with retry logic"""
    for attempt in range(max_retries):
        try:
            upload_large_file(local_path, dbfs_path)
            print("Upload successful!")
            return
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise
```

---

## Related Documentation

- [API Overview](overview.md)
- [Python SDK Guide](../sdk/python.md)
- [Quick Start Guide](../getting-started/quickstart.md)
- [Workspace API](workspace.md)

## Additional Resources

- [Official DBFS Documentation](https://docs.databricks.com/dbfs/index.html)
- [DBFS API Reference](https://docs.databricks.com/api/workspace/dbfs)
- [File Upload Best Practices](https://docs.databricks.com/dev-tools/api/latest/dbfs.html)