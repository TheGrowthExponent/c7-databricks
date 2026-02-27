# Databricks Unity Catalog API Reference

## Overview

Unity Catalog is Databricks' unified governance solution for data and AI assets. The Unity Catalog API allows you to programmatically manage metastores, catalogs, schemas, tables, volumes, functions, and access control policies.

## Base URL

```
https://<databricks-instance>/api/2.1/unity-catalog
```

## Authentication

All Unity Catalog API requests require authentication using a personal access token or service principal token:

```
Authorization: Bearer <token>
```

## Key Concepts

### Hierarchy

Unity Catalog uses a three-level namespace:

- **Metastore** - Top-level container for metadata
- **Catalog** - Database namespace containing schemas
- **Schema** (Database) - Container for tables, views, and functions

Full object path: `catalog.schema.table`

### Securable Objects

- Metastores
- Catalogs
- Schemas
- Tables and Views
- Volumes (for non-tabular data)
- Functions
- Models (ML models)

---

## Metastore Management

### List Metastores

List all metastores in the account.

**Endpoint:** `GET /api/2.1/unity-catalog/metastores`

**Request Example:**

```bash
curl -X GET \
  'https://<databricks-instance>/api/2.1/unity-catalog/metastores' \
  -H 'Authorization: Bearer <token>'
```

**Python Example:**

```python
import requests

url = "https://<databricks-instance>/api/2.1/unity-catalog/metastores"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(url, headers=headers)
metastores = response.json().get("metastores", [])

for metastore in metastores:
    print(f"Metastore: {metastore['name']}")
    print(f"  ID: {metastore['metastore_id']}")
    print(f"  Region: {metastore['region']}")
```

**Response:**

```json
{
  "metastores": [
    {
      "metastore_id": "abc123-def456-ghi789",
      "name": "main-metastore",
      "storage_root": "s3://my-bucket/metastore",
      "region": "us-west-2",
      "owner": "admin@example.com",
      "created_at": 1609459200000,
      "updated_at": 1617235200000
    }
  ]
}
```

---

### Get Metastore

Get details about a specific metastore.

**Endpoint:** `GET /api/2.1/unity-catalog/metastores/{metastore_id}`

**Request Example:**

```bash
curl -X GET \
  'https://<databricks-instance>/api/2.1/unity-catalog/metastores/abc123-def456-ghi789' \
  -H 'Authorization: Bearer <token>'
```

**Python Example:**

```python
import requests

metastore_id = "abc123-def456-ghi789"
url = f"https://<databricks-instance>/api/2.1/unity-catalog/metastores/{metastore_id}"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(url, headers=headers)
metastore = response.json()

print(f"Name: {metastore['name']}")
print(f"Storage Root: {metastore['storage_root']}")
print(f"Owner: {metastore['owner']}")
```

---

## Catalog Management

### Create Catalog

Create a new catalog in the metastore.

**Endpoint:** `POST /api/2.1/unity-catalog/catalogs`

**Request Body:**

- `name` (required) - Catalog name
- `comment` (optional) - Description
- `properties` (optional) - Key-value properties
- `storage_root` (optional) - Storage location

**Request Example:**

```bash
curl -X POST \
  'https://<databricks-instance>/api/2.1/unity-catalog/catalogs' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "production",
    "comment": "Production data catalog",
    "properties": {
      "department": "analytics"
    }
  }'
```

**Python Example:**

```python
import requests

url = "https://<databricks-instance>/api/2.1/unity-catalog/catalogs"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
data = {
    "name": "production",
    "comment": "Production data catalog",
    "properties": {
        "department": "analytics",
        "env": "prod"
    }
}

response = requests.post(url, headers=headers, json=data)
catalog = response.json()

print(f"Created catalog: {catalog['name']}")
print(f"Catalog ID: {catalog['catalog_id']}")
```

**Response:**

```json
{
  "name": "production",
  "catalog_id": "cat123-456-789",
  "comment": "Production data catalog",
  "properties": {
    "department": "analytics"
  },
  "owner": "admin@example.com",
  "created_at": 1609459200000
}
```

---

### List Catalogs

List all catalogs in the metastore.

**Endpoint:** `GET /api/2.1/unity-catalog/catalogs`

**Request Example:**

```bash
curl -X GET \
  'https://<databricks-instance>/api/2.1/unity-catalog/catalogs' \
  -H 'Authorization: Bearer <token>'
```

**Python Example:**

```python
import requests

url = "https://<databricks-instance>/api/2.1/unity-catalog/catalogs"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(url, headers=headers)
catalogs = response.json().get("catalogs", [])

for catalog in catalogs:
    print(f"Catalog: {catalog['name']}")
    print(f"  Owner: {catalog['owner']}")
    print(f"  Comment: {catalog.get('comment', 'N/A')}")
```

---

### Update Catalog

Update catalog properties.

**Endpoint:** `PATCH /api/2.1/unity-catalog/catalogs/{catalog_name}`

**Request Body:**

- `comment` (optional) - Updated description
- `properties` (optional) - Updated properties
- `owner` (optional) - New owner

**Request Example:**

```bash
curl -X PATCH \
  'https://<databricks-instance>/api/2.1/unity-catalog/catalogs/production' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "comment": "Updated production catalog",
    "properties": {
      "department": "data-engineering"
    }
  }'
```

**Python Example:**

```python
import requests

catalog_name = "production"
url = f"https://<databricks-instance>/api/2.1/unity-catalog/catalogs/{catalog_name}"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
data = {
    "comment": "Updated production catalog",
    "properties": {
        "department": "data-engineering",
        "updated": "2026-02-27"
    }
}

response = requests.patch(url, headers=headers, json=data)
catalog = response.json()
print(f"Updated catalog: {catalog['name']}")
```

---

### Delete Catalog

Delete a catalog (must be empty).

**Endpoint:** `DELETE /api/2.1/unity-catalog/catalogs/{catalog_name}`

**Parameters:**

- `force` (optional) - Set to `true` to force delete non-empty catalog

**Request Example:**

```bash
curl -X DELETE \
  'https://<databricks-instance>/api/2.1/unity-catalog/catalogs/old_catalog?force=false' \
  -H 'Authorization: Bearer <token>'
```

**Python Example:**

```python
import requests

catalog_name = "old_catalog"
url = f"https://<databricks-instance>/api/2.1/unity-catalog/catalogs/{catalog_name}"
headers = {"Authorization": f"Bearer {token}"}
params = {"force": False}

response = requests.delete(url, headers=headers, params=params)
if response.status_code == 200:
    print(f"Deleted catalog: {catalog_name}")
```

---

## Schema Management

### Create Schema

Create a new schema (database) in a catalog.

**Endpoint:** `POST /api/2.1/unity-catalog/schemas`

**Request Body:**

- `name` (required) - Schema name
- `catalog_name` (required) - Parent catalog
- `comment` (optional) - Description
- `properties` (optional) - Key-value properties
- `storage_root` (optional) - Storage location

**Request Example:**

```bash
curl -X POST \
  'https://<databricks-instance>/api/2.1/unity-catalog/schemas' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "sales",
    "catalog_name": "production",
    "comment": "Sales department data"
  }'
```

**Python Example:**

```python
import requests

url = "https://<databricks-instance>/api/2.1/unity-catalog/schemas"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
data = {
    "name": "sales",
    "catalog_name": "production",
    "comment": "Sales department data",
    "properties": {
        "team": "sales",
        "region": "us-west"
    }
}

response = requests.post(url, headers=headers, json=data)
schema = response.json()

print(f"Created schema: {schema['full_name']}")
print(f"Schema ID: {schema['schema_id']}")
```

**Response:**

```json
{
  "name": "sales",
  "catalog_name": "production",
  "full_name": "production.sales",
  "schema_id": "sch123-456-789",
  "comment": "Sales department data",
  "properties": {
    "team": "sales",
    "region": "us-west"
  },
  "owner": "admin@example.com",
  "created_at": 1609459200000
}
```

---

### List Schemas

List all schemas in a catalog.

**Endpoint:** `GET /api/2.1/unity-catalog/schemas`

**Parameters:**

- `catalog_name` (required) - Catalog to list schemas from

**Request Example:**

```bash
curl -X GET \
  'https://<databricks-instance>/api/2.1/unity-catalog/schemas?catalog_name=production' \
  -H 'Authorization: Bearer <token>'
```

**Python Example:**

```python
import requests

url = "https://<databricks-instance>/api/2.1/unity-catalog/schemas"
headers = {"Authorization": f"Bearer {token}"}
params = {"catalog_name": "production"}

response = requests.get(url, headers=headers, params=params)
schemas = response.json().get("schemas", [])

for schema in schemas:
    print(f"Schema: {schema['full_name']}")
    print(f"  Owner: {schema['owner']}")
    print(f"  Comment: {schema.get('comment', 'N/A')}")
```

---

### Get Schema

Get details about a specific schema.

**Endpoint:** `GET /api/2.1/unity-catalog/schemas/{full_name}`

**Request Example:**

```bash
curl -X GET \
  'https://<databricks-instance>/api/2.1/unity-catalog/schemas/production.sales' \
  -H 'Authorization: Bearer <token>'
```

**Python Example:**

```python
import requests

schema_full_name = "production.sales"
url = f"https://<databricks-instance>/api/2.1/unity-catalog/schemas/{schema_full_name}"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(url, headers=headers)
schema = response.json()

print(f"Schema: {schema['full_name']}")
print(f"Catalog: {schema['catalog_name']}")
print(f"Owner: {schema['owner']}")
print(f"Storage: {schema.get('storage_root', 'Default')}")
```

---

### Delete Schema

Delete a schema (must be empty).

**Endpoint:** `DELETE /api/2.1/unity-catalog/schemas/{full_name}`

**Parameters:**

- `force` (optional) - Set to `true` to force delete non-empty schema

**Request Example:**

```bash
curl -X DELETE \
  'https://<databricks-instance>/api/2.1/unity-catalog/schemas/production.old_schema' \
  -H 'Authorization: Bearer <token>'
```

**Python Example:**

```python
import requests

schema_full_name = "production.old_schema"
url = f"https://<databricks-instance>/api/2.1/unity-catalog/schemas/{schema_full_name}"
headers = {"Authorization": f"Bearer {token}"}

response = requests.delete(url, headers=headers)
if response.status_code == 200:
    print(f"Deleted schema: {schema_full_name}")
```

---

## Table Management

### List Tables

List all tables in a schema.

**Endpoint:** `GET /api/2.1/unity-catalog/tables`

**Parameters:**

- `catalog_name` (required) - Catalog name
- `schema_name` (required) - Schema name

**Request Example:**

```bash
curl -X GET \
  'https://<databricks-instance>/api/2.1/unity-catalog/tables?catalog_name=production&schema_name=sales' \
  -H 'Authorization: Bearer <token>'
```

**Python Example:**

```python
import requests

url = "https://<databricks-instance>/api/2.1/unity-catalog/tables"
headers = {"Authorization": f"Bearer {token}"}
params = {
    "catalog_name": "production",
    "schema_name": "sales"
}

response = requests.get(url, headers=headers, params=params)
tables = response.json().get("tables", [])

for table in tables:
    print(f"Table: {table['full_name']}")
    print(f"  Type: {table['table_type']}")
    print(f"  Storage: {table.get('storage_location', 'N/A')}")
    print(f"  Columns: {len(table.get('columns', []))}")
```

---

### Get Table

Get detailed information about a table.

**Endpoint:** `GET /api/2.1/unity-catalog/tables/{full_name}`

**Request Example:**

```bash
curl -X GET \
  'https://<databricks-instance>/api/2.1/unity-catalog/tables/production.sales.customers' \
  -H 'Authorization: Bearer <token>'
```

**Python Example:**

```python
import requests

table_full_name = "production.sales.customers"
url = f"https://<databricks-instance>/api/2.1/unity-catalog/tables/{table_full_name}"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(url, headers=headers)
table = response.json()

print(f"Table: {table['full_name']}")
print(f"Type: {table['table_type']}")
print(f"Owner: {table['owner']}")
print(f"Storage: {table.get('storage_location', 'Managed')}")
print(f"\nColumns:")
for col in table.get('columns', []):
    print(f"  - {col['name']}: {col['type_name']}")
```

---

### Delete Table

Delete a table or view.

**Endpoint:** `DELETE /api/2.1/unity-catalog/tables/{full_name}`

**Request Example:**

```bash
curl -X DELETE \
  'https://<databricks-instance>/api/2.1/unity-catalog/tables/production.sales.old_table' \
  -H 'Authorization: Bearer <token>'
```

**Python Example:**

```python
import requests

table_full_name = "production.sales.old_table"
url = f"https://<databricks-instance>/api/2.1/unity-catalog/tables/{table_full_name}"
headers = {"Authorization": f"Bearer {token}"}

response = requests.delete(url, headers=headers)
if response.status_code == 200:
    print(f"Deleted table: {table_full_name}")
```

---

## Grants and Permissions

### Grant Permissions

Grant permissions on a securable object.

**Endpoint:** `POST /api/2.1/unity-catalog/permissions/{securable_type}/{full_name}`

**Securable Types:**

- `catalog`
- `schema`
- `table`
- `volume`
- `function`

**Privileges:**

- `SELECT` - Read data
- `MODIFY` - Insert, update, delete
- `CREATE` - Create child objects
- `USAGE` - Use object
- `ALL_PRIVILEGES` - All permissions

**Request Example:**

```bash
curl -X POST \
  'https://<databricks-instance>/api/2.1/unity-catalog/permissions/table/production.sales.customers' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "changes": [
      {
        "principal": "data-analysts",
        "add": ["SELECT", "MODIFY"]
      }
    ]
  }'
```

**Python Example:**

```python
import requests

table_full_name = "production.sales.customers"
url = f"https://<databricks-instance>/api/2.1/unity-catalog/permissions/table/{table_full_name}"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
data = {
    "changes": [
        {
            "principal": "data-analysts",
            "add": ["SELECT", "MODIFY"]
        },
        {
            "principal": "data-viewers",
            "add": ["SELECT"]
        }
    ]
}

response = requests.post(url, headers=headers, json=data)
if response.status_code == 200:
    print(f"Permissions granted on {table_full_name}")
```

---

### Get Permissions

Get current permissions on a securable object.

**Endpoint:** `GET /api/2.1/unity-catalog/permissions/{securable_type}/{full_name}`

**Request Example:**

```bash
curl -X GET \
  'https://<databricks-instance>/api/2.1/unity-catalog/permissions/table/production.sales.customers' \
  -H 'Authorization: Bearer <token>'
```

**Python Example:**

```python
import requests

table_full_name = "production.sales.customers"
url = f"https://<databricks-instance>/api/2.1/unity-catalog/permissions/table/{table_full_name}"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(url, headers=headers)
permissions = response.json()

print(f"Permissions for {table_full_name}:")
for grant in permissions.get("privilege_assignments", []):
    principal = grant["principal"]
    privileges = grant["privileges"]
    print(f"  {principal}: {', '.join(privileges)}")
```

---

### Revoke Permissions

Revoke permissions from a securable object.

**Request Example:**

```bash
curl -X POST \
  'https://<databricks-instance>/api/2.1/unity-catalog/permissions/table/production.sales.customers' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "changes": [
      {
        "principal": "data-viewers",
        "remove": ["MODIFY"]
      }
    ]
  }'
```

**Python Example:**

```python
import requests

table_full_name = "production.sales.customers"
url = f"https://<databricks-instance>/api/2.1/unity-catalog/permissions/table/{table_full_name}"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
data = {
    "changes": [
        {
            "principal": "data-viewers",
            "remove": ["MODIFY"]
        }
    ]
}

response = requests.post(url, headers=headers, json=data)
if response.status_code == 200:
    print(f"Permissions revoked on {table_full_name}")
```

---

## Python SDK Examples

### Using Databricks SDK

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import *

# Initialize client
w = WorkspaceClient()

# List catalogs
catalogs = w.catalogs.list()
for catalog in catalogs:
    print(f"Catalog: {catalog.name}")

# Create catalog
new_catalog = w.catalogs.create(
    name="analytics",
    comment="Analytics catalog"
)
print(f"Created catalog: {new_catalog.name}")

# Create schema
new_schema = w.schemas.create(
    name="reports",
    catalog_name="analytics",
    comment="Reporting tables"
)
print(f"Created schema: {new_schema.full_name}")

# List tables
tables = w.tables.list(
    catalog_name="production",
    schema_name="sales"
)
for table in tables:
    print(f"Table: {table.full_name}")

# Get table details
table = w.tables.get("production.sales.customers")
print(f"Table: {table.full_name}")
print(f"Columns: {len(table.columns)}")

# Grant permissions
w.grants.update(
    securable_type=SecurableType.TABLE,
    full_name="production.sales.customers",
    changes=[
        PermissionsChange(
            principal="data-analysts",
            add=[Privilege.SELECT, Privilege.MODIFY]
        )
    ]
)
```

---

## Advanced Examples

### Complete Catalog Management Class

```python
import requests
from typing import List, Dict, Optional

class UnityCatalogManager:
    """Unity Catalog management utility"""

    def __init__(self, host: str, token: str):
        self.host = host.rstrip('/')
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.base_url = f"{self.host}/api/2.1/unity-catalog"

    def create_catalog(self, name: str, comment: str = None, properties: Dict = None) -> Dict:
        """Create a new catalog"""
        url = f"{self.base_url}/catalogs"
        data = {"name": name}
        if comment:
            data["comment"] = comment
        if properties:
            data["properties"] = properties

        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def create_schema(self, catalog_name: str, schema_name: str, comment: str = None) -> Dict:
        """Create a new schema"""
        url = f"{self.base_url}/schemas"
        data = {
            "name": schema_name,
            "catalog_name": catalog_name
        }
        if comment:
            data["comment"] = comment

        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def list_tables(self, catalog_name: str, schema_name: str) -> List[Dict]:
        """List all tables in a schema"""
        url = f"{self.base_url}/tables"
        params = {
            "catalog_name": catalog_name,
            "schema_name": schema_name
        }

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json().get("tables", [])

    def get_table_details(self, full_name: str) -> Dict:
        """Get detailed table information"""
        url = f"{self.base_url}/tables/{full_name}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def grant_permissions(
        self,
        securable_type: str,
        full_name: str,
        principal: str,
        privileges: List[str]
    ) -> None:
        """Grant permissions on an object"""
        url = f"{self.base_url}/permissions/{securable_type}/{full_name}"
        data = {
            "changes": [
                {
                    "principal": principal,
                    "add": privileges
                }
            ]
        }

        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()

    def get_permissions(self, securable_type: str, full_name: str) -> Dict:
        """Get current permissions"""
        url = f"{self.base_url}/permissions/{securable_type}/{full_name}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def clone_permissions(
        self,
        source_type: str,
        source_name: str,
        target_type: str,
        target_name: str
    ) -> None:
        """Clone permissions from one object to another"""
        # Get source permissions
        source_perms = self.get_permissions(source_type, source_name)

        # Apply to target
        for grant in source_perms.get("privilege_assignments", []):
            principal = grant["principal"]
            privileges = grant["privileges"]

            self.grant_permissions(
                target_type,
                target_name,
                principal,
                privileges
            )

        print(f"Cloned permissions from {source_name} to {target_name}")

# Usage
manager = UnityCatalogManager(
    host="https://<databricks-instance>",
    token="<your-token>"
)

# Create catalog and schema
catalog = manager.create_catalog("analytics", "Analytics data")
schema = manager.create_schema("analytics", "reports", "Reporting tables")

# List tables
tables = manager.list_tables("production", "sales")
for table in tables:
    print(f"Table: {table['full_name']}")

# Grant permissions
manager.grant_permissions(
    securable_type="table",
    full_name="production.sales.customers",
    principal="data-analysts",
    privileges=["SELECT", "MODIFY"]
)
```

---

### Catalog Migration Script

```python
import requests
from typing import List, Dict

def migrate_catalog_structure(
    source_catalog: str,
    target_catalog: str,
    host: str,
    token: str
):
    """
    Migrate catalog structure (schemas and permissions) to new catalog
    Does not copy data, only metadata
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    base_url = f"{host}/api/2.1/unity-catalog"

    # Get source catalog info
    source_url = f"{base_url}/catalogs/{source_catalog}"
    source_info = requests.get(source_url, headers=headers).json()

    # Create target catalog
    create_catalog_url = f"{base_url}/catalogs"
    catalog_data = {
        "name": target_catalog,
        "comment": f"Migrated from {source_catalog}",
        "properties": source_info.get("properties", {})
    }
    requests.post(create_catalog_url, headers=headers, json=catalog_data)
    print(f"Created catalog: {target_catalog}")

    # Get schemas from source
    schemas_url = f"{base_url}/schemas"
    schemas_params = {"catalog_name": source_catalog}
    schemas_response = requests.get(schemas_url, headers=headers, params=schemas_params)
    schemas = schemas_response.json().get("schemas", [])

    # Create schemas in target
    for schema in schemas:
        schema_data = {
            "name": schema["name"],
            "catalog_name": target_catalog,
            "comment": schema.get("comment", ""),
            "properties": schema.get("properties", {})
        }
        requests.post(schemas_url, headers=headers, json=schema_data)
        print(f"Created schema: {target_catalog}.{schema['name']}")

        # Copy schema permissions
        source_schema_name = f"{source_catalog}.{schema['name']}"
        target_schema_name = f"{target_catalog}.{schema['name']}"

        perms_url = f"{base_url}/permissions/schema/{source_schema_name}"
        perms = requests.get(perms_url, headers=headers).json()

        for grant in perms.get("privilege_assignments", []):
            grant_url = f"{base_url}/permissions/schema/{target_schema_name}"
            grant_data = {
                "changes": [{
                    "principal": grant["principal"],
                    "add": grant["privileges"]
                }]
            }
            requests.post(grant_url, headers=headers, json=grant_data)

        print(f"Copied permissions for {target_schema_name}")

    print(f"Migration complete: {source_catalog} -> {target_catalog}")

# Usage
migrate_catalog_structure(
    source_catalog="production",
    target_catalog="production_v2",
    host="https://<databricks-instance>",
    token="<your-token>"
)
```

---

## Best Practices

### 1. Naming Conventions

```python
# Use lowercase with underscores
good_catalog = "sales_analytics"
good_schema = "customer_data"
good_table = "daily_transactions"

# Avoid special characters
bad_catalog = "Sales-Analytics!"  # Don't use hyphens or special chars
```

### 2. Access Control Hierarchy

```python
# Grant at highest appropriate level
# Schema-level grant (preferred for team access)
manager.grant_permissions(
    securable_type="schema",
    full_name="production.sales",
    principal="sales-team",
    privileges=["USAGE", "SELECT"]
)

# Table-level grant (for specific access)
manager.grant_permissions(
    securable_type="table",
    full_name="production.sales.sensitive_data",
    principal="managers-only",
    privileges=["SELECT"]
)
```

### 3. Audit and Compliance

```python
def audit_permissions(catalog_name: str, token: str, host: str):
    """Generate permissions audit report"""
    headers = {"Authorization": f"Bearer {token}"}
    base_url = f"{host}/api/2.1/unity-catalog"

    # Get all schemas
    schemas_url = f"{base_url}/schemas"
    params = {"catalog_name": catalog_name}
    schemas = requests.get(schemas_url, headers=headers, params=params).json()

    report = []
    for schema in schemas.get("schemas", []):
        schema_name = schema["full_name"]

        # Get permissions
        perms_url = f"{base_url}/permissions/schema/{schema_name}"
        perms = requests.get(perms_url, headers=headers).json()

        for grant in perms.get("privilege_assignments", []):
            report.append({
                "object": schema_name,
                "principal": grant["principal"],
                "privileges": grant["privileges"]
            })

    return report
```

---

## Related APIs

- [SQL API](./sql.md) - Execute queries on Unity Catalog tables
- [Permissions API](./permissions.md) - Detailed permission management
- [Workspace API](./workspace.md) - Manage notebooks accessing Unity Catalog

---

## Additional Resources

- [Unity Catalog Documentation](https://docs.databricks.com/data-governance/unity-catalog/index.html)
- [Unity Catalog Best Practices](https://docs.databricks.com/data-governance/unity-catalog/best-practices.html)
- [Unity Catalog API Reference](https://docs.databricks.com/api/workspace/catalogs)
