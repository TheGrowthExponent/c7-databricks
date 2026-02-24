# Databricks Documentation Sources Catalog

This document catalogs all Databricks components, APIs, and features that need to be documented for Context7.

## Last Updated
2024

---

## 1. Databricks REST API Endpoints

### 1.1 Workspace API
- **List workspace objects** - `GET /api/2.0/workspace/list`
- **Get workspace status** - `GET /api/2.0/workspace/get-status`
- **Export workspace item** - `GET /api/2.0/workspace/export`
- **Import workspace item** - `POST /api/2.0/workspace/import`
- **Delete workspace item** - `POST /api/2.0/workspace/delete`
- **Create directory** - `POST /api/2.0/workspace/mkdirs`

### 1.2 Clusters API
- **Create cluster** - `POST /api/2.0/clusters/create`
- **Edit cluster** - `POST /api/2.0/clusters/edit`
- **Start cluster** - `POST /api/2.0/clusters/start`
- **Restart cluster** - `POST /api/2.0/clusters/restart`
- **Terminate cluster** - `POST /api/2.0/clusters/delete`
- **Get cluster info** - `GET /api/2.0/clusters/get`
- **List clusters** - `GET /api/2.0/clusters/list`
- **Resize cluster** - `POST /api/2.0/clusters/resize`
- **Pin cluster** - `POST /api/2.0/clusters/pin`
- **Unpin cluster** - `POST /api/2.0/clusters/unpin`
- **List node types** - `GET /api/2.0/clusters/list-node-types`
- **Spark versions** - `GET /api/2.0/clusters/spark-versions`
- **Cluster events** - `POST /api/2.0/clusters/events`

### 1.3 Jobs API
- **Create job** - `POST /api/2.1/jobs/create`
- **List jobs** - `GET /api/2.1/jobs/list`
- **Get job** - `GET /api/2.1/jobs/get`
- **Update job** - `POST /api/2.1/jobs/update`
- **Delete job** - `POST /api/2.1/jobs/delete`
- **Run now** - `POST /api/2.1/jobs/run-now`
- **Run submit** - `POST /api/2.1/jobs/runs/submit`
- **List runs** - `GET /api/2.1/jobs/runs/list`
- **Get run** - `GET /api/2.1/jobs/runs/get`
- **Cancel run** - `POST /api/2.1/jobs/runs/cancel`
- **Get run output** - `GET /api/2.1/jobs/runs/get-output`
- **Export run** - `GET /api/2.1/jobs/runs/export`

### 1.4 DBFS API
- **Add block** - `POST /api/2.0/dbfs/add-block`
- **Close stream** - `POST /api/2.0/dbfs/close`
- **Create file** - `POST /api/2.0/dbfs/create`
- **Delete** - `POST /api/2.0/dbfs/delete`
- **Get status** - `GET /api/2.0/dbfs/get-status`
- **List directory** - `GET /api/2.0/dbfs/list`
- **Make directory** - `POST /api/2.0/dbfs/mkdirs`
- **Move** - `POST /api/2.0/dbfs/move`
- **Put file** - `POST /api/2.0/dbfs/put`
- **Read file** - `GET /api/2.0/dbfs/read`

### 1.5 Secrets API
- **Create scope** - `POST /api/2.0/secrets/scopes/create`
- **Delete scope** - `POST /api/2.0/secrets/scopes/delete`
- **List scopes** - `GET /api/2.0/secrets/scopes/list`
- **Put secret** - `POST /api/2.0/secrets/put`
- **Delete secret** - `POST /api/2.0/secrets/delete`
- **List secrets** - `GET /api/2.0/secrets/list`
- **Put ACL** - `POST /api/2.0/secrets/acls/put`
- **Delete ACL** - `POST /api/2.0/secrets/acls/delete`
- **Get ACL** - `GET /api/2.0/secrets/acls/get`
- **List ACLs** - `GET /api/2.0/secrets/acls/list`

### 1.6 Libraries API
- **All cluster statuses** - `GET /api/2.0/libraries/all-cluster-statuses`
- **Cluster status** - `GET /api/2.0/libraries/cluster-status`
- **Install** - `POST /api/2.0/libraries/install`
- **Uninstall** - `POST /api/2.0/libraries/uninstall`

### 1.7 SQL API
- **Execute statement** - `POST /api/2.0/sql/statements`
- **Get statement** - `GET /api/2.0/sql/statements/{statement_id}`
- **Cancel statement** - `POST /api/2.0/sql/statements/{statement_id}/cancel`
- **List warehouses** - `GET /api/2.0/sql/warehouses`
- **Get warehouse** - `GET /api/2.0/sql/warehouses/{id}`
- **Create warehouse** - `POST /api/2.0/sql/warehouses`
- **Edit warehouse** - `PATCH /api/2.0/sql/warehouses/{id}`
- **Delete warehouse** - `DELETE /api/2.0/sql/warehouses/{id}`
- **Start warehouse** - `POST /api/2.0/sql/warehouses/{id}/start`
- **Stop warehouse** - `POST /api/2.0/sql/warehouses/{id}/stop`

### 1.8 Unity Catalog API
- **List catalogs** - `GET /api/2.1/unity-catalog/catalogs`
- **Create catalog** - `POST /api/2.1/unity-catalog/catalogs`
- **Get catalog** - `GET /api/2.1/unity-catalog/catalogs/{name}`
- **Update catalog** - `PATCH /api/2.1/unity-catalog/catalogs/{name}`
- **Delete catalog** - `DELETE /api/2.1/unity-catalog/catalogs/{name}`
- **List schemas** - `GET /api/2.1/unity-catalog/schemas`
- **Create schema** - `POST /api/2.1/unity-catalog/schemas`
- **Get schema** - `GET /api/2.1/unity-catalog/schemas/{full_name}`
- **Update schema** - `PATCH /api/2.1/unity-catalog/schemas/{full_name}`
- **Delete schema** - `DELETE /api/2.1/unity-catalog/schemas/{full_name}`
- **List tables** - `GET /api/2.1/unity-catalog/tables`
- **Get table** - `GET /api/2.1/unity-catalog/tables/{full_name}`
- **Delete table** - `DELETE /api/2.1/unity-catalog/tables/{full_name}`

### 1.9 Token Management API
- **Create token** - `POST /api/2.0/token/create`
- **List tokens** - `GET /api/2.0/token/list`
- **Revoke token** - `POST /api/2.0/token/delete`

### 1.10 Instance Pools API
- **Create pool** - `POST /api/2.0/instance-pools/create`
- **Edit pool** - `POST /api/2.0/instance-pools/edit`
- **Delete pool** - `POST /api/2.0/instance-pools/delete`
- **Get pool** - `GET /api/2.0/instance-pools/get`
- **List pools** - `GET /api/2.0/instance-pools/list`

### 1.11 Repos API (Git Integration)
- **Create repo** - `POST /api/2.0/repos`
- **Get repo** - `GET /api/2.0/repos/{repo_id}`
- **Update repo** - `PATCH /api/2.0/repos/{repo_id}`
- **Delete repo** - `DELETE /api/2.0/repos/{repo_id}`
- **List repos** - `GET /api/2.0/repos`

### 1.12 Permissions API
- **Get permissions** - `GET /api/2.0/permissions/{object_type}/{object_id}`
- **Set permissions** - `PUT /api/2.0/permissions/{object_type}/{object_id}`
- **Update permissions** - `PATCH /api/2.0/permissions/{object_type}/{object_id}`

---

## 2. Python SDK (databricks-sdk-py)

### 2.1 Core Client
- `WorkspaceClient` - Main client for workspace operations
- `AccountClient` - Client for account-level operations
- Authentication methods (OAuth, PAT, Azure AD)

### 2.2 SDK Services
- `workspace` - Workspace API operations
- `clusters` - Cluster management
- `jobs` - Job operations
- `dbfs` - DBFS file operations
- `secrets` - Secret management
- `sql` - SQL warehouse operations
- `catalogs` - Unity Catalog operations
- `schemas` - Schema management
- `tables` - Table operations
- `volumes` - Volume operations
- `repos` - Git repo integration
- `instance_pools` - Instance pool management
- `libraries` - Library management
- `permissions` - Permission management
- `tokens` - Token management
- `pipelines` - Delta Live Tables pipelines

### 2.3 Service Models
- Cluster configuration models
- Job configuration models
- SQL warehouse configuration
- Unity Catalog models
- Permission models

---

## 3. Databricks SQL

### 3.1 DDL (Data Definition Language)
- `CREATE DATABASE/SCHEMA`
- `DROP DATABASE/SCHEMA`
- `ALTER DATABASE/SCHEMA`
- `CREATE TABLE`
- `CREATE TABLE AS SELECT (CTAS)`
- `DROP TABLE`
- `ALTER TABLE`
- `CREATE VIEW`
- `DROP VIEW`
- `CREATE FUNCTION`
- `DROP FUNCTION`

### 3.2 DML (Data Manipulation Language)
- `SELECT` statements
- `INSERT INTO`
- `INSERT OVERWRITE`
- `UPDATE`
- `DELETE`
- `MERGE INTO`
- `COPY INTO`

### 3.3 Delta Lake SQL Commands
- `OPTIMIZE`
- `VACUUM`
- `DESCRIBE HISTORY`
- `DESCRIBE DETAIL`
- `RESTORE TABLE`
- `CONVERT TO DELTA`
- `CLONE`

### 3.4 Unity Catalog SQL
- `USE CATALOG`
- `USE SCHEMA`
- `GRANT`
- `REVOKE`
- `SHOW GRANTS`
- `CREATE EXTERNAL LOCATION`
- `CREATE STORAGE CREDENTIAL`

### 3.5 SQL Functions
- Aggregate functions (SUM, COUNT, AVG, MAX, MIN, etc.)
- String functions (CONCAT, SUBSTRING, UPPER, LOWER, etc.)
- Date/time functions (CURRENT_DATE, DATE_ADD, DATEDIFF, etc.)
- Array functions (ARRAY_CONTAINS, EXPLODE, SIZE, etc.)
- Map functions
- JSON functions
- Window functions (ROW_NUMBER, RANK, LAG, LEAD, etc.)
- Mathematical functions

---

## 4. Databricks CLI

### 4.1 Configuration
- `databricks configure --token`
- `databricks configure --profile`
- Configuration file location and format

### 4.2 Workspace Commands
- `databricks workspace ls`
- `databricks workspace export`
- `databricks workspace import`
- `databricks workspace delete`
- `databricks workspace mkdirs`

### 4.3 Cluster Commands
- `databricks clusters create`
- `databricks clusters get`
- `databricks clusters list`
- `databricks clusters start`
- `databricks clusters restart`
- `databricks clusters delete`

### 4.4 Jobs Commands
- `databricks jobs create`
- `databricks jobs list`
- `databricks jobs get`
- `databricks jobs run-now`
- `databricks jobs reset`
- `databricks jobs delete`

### 4.5 DBFS Commands
- `databricks fs ls`
- `databricks fs cp`
- `databricks fs rm`
- `databricks fs mkdirs`
- `databricks fs cat`
- `databricks fs mv`

### 4.6 Secrets Commands
- `databricks secrets create-scope`
- `databricks secrets delete-scope`
- `databricks secrets list-scopes`
- `databricks secrets put`
- `databricks secrets delete`
- `databricks secrets list`

### 4.7 Repos Commands
- `databricks repos create`
- `databricks repos get`
- `databricks repos update`
- `databricks repos delete`
- `databricks repos list`

---

## 5. Machine Learning & MLflow

### 5.1 MLflow Tracking
- `mlflow.start_run()`
- `mlflow.log_param()`
- `mlflow.log_metric()`
- `mlflow.log_artifact()`
- `mlflow.end_run()`
- `mlflow.set_experiment()`
- `mlflow.get_experiment()`

### 5.2 MLflow Models
- `mlflow.pyfunc.log_model()`
- `mlflow.sklearn.log_model()`
- `mlflow.tensorflow.log_model()`
- `mlflow.pytorch.log_model()`
- `mlflow.spark.log_model()`
- Model registry operations
- Model serving

### 5.3 AutoML
- AutoML UI workflow
- AutoML API usage
- Generated notebooks
- Model selection and tuning

### 5.4 Feature Store
- `FeatureStoreClient`
- `create_table()`
- `write_table()`
- `read_table()`
- `create_training_set()`
- Feature lookup

### 5.5 Model Registry
- Register models
- Transition model stages
- Model versioning
- Model aliases
- Webhooks for model events

---

## 6. Delta Lake

### 6.1 Core Operations
- Reading Delta tables
- Writing Delta tables
- Upserting with MERGE
- Time travel queries
- Schema evolution
- Partition pruning

### 6.2 Optimization
- `OPTIMIZE` command
- Z-ordering
- Auto-optimize
- Auto-compaction

### 6.3 Data Management
- `VACUUM` command
- Data retention policies
- `DESCRIBE HISTORY`
- `RESTORE TABLE`

### 6.4 Streaming
- Structured Streaming with Delta
- Change Data Feed (CDF)
- Delta Live Tables

---

## 7. Databricks Connect

### 7.1 Setup & Configuration
- Installation
- Configuration with workspace
- Cluster requirements
- Local development setup

### 7.2 Usage Patterns
- Remote execution
- DataFrame operations
- Local debugging
- IDE integration

---

## 8. Delta Live Tables (DLT)

### 8.1 Pipeline Definition
- `@dlt.table` decorator
- `@dlt.view` decorator
- Streaming tables
- Materialized views

### 8.2 Pipeline Operations
- Creating pipelines
- Starting pipelines
- Monitoring pipelines
- Pipeline settings and configuration

### 8.3 Data Quality
- Expectations
- Constraint types
- Monitoring data quality

---

## 9. Authentication & Security

### 9.1 Authentication Methods
- Personal Access Tokens (PAT)
- OAuth 2.0
- Azure Active Directory (Azure AD)
- AWS IAM roles
- Service principals

### 9.2 Access Control
- Cluster access control
- Job access control
- Notebook access control
- Table access control (Unity Catalog)
- Fine-grained access control

### 9.3 Secrets Management
- Secret scopes
- Azure Key Vault integration
- AWS Secrets Manager integration
- Accessing secrets in notebooks

---

## 10. Common Use Cases & Patterns

### 10.1 ETL Patterns
- Batch processing
- Incremental loading
- Change data capture
- Data quality validation
- Error handling

### 10.2 Data Engineering
- Medallion architecture (Bronze, Silver, Gold)
- Slowly changing dimensions (SCD)
- Data pipelines with jobs
- Workflow orchestration

### 10.3 Data Science
- Exploratory data analysis
- Model training workflows
- Hyperparameter tuning
- Model deployment
- Batch inference

### 10.4 SQL Analytics
- Dashboard creation
- Query optimization
- Warehouse sizing
- Cost optimization

---

## 11. Performance & Optimization

### 11.1 Cluster Optimization
- Cluster sizing
- Autoscaling configuration
- Instance pool usage
- Spot instances

### 11.2 Query Optimization
- Partition pruning
- Predicate pushdown
- Caching strategies
- Broadcast joins

### 11.3 Cost Optimization
- Cluster policies
- Job scheduling
- Warehouse auto-suspend
- Storage optimization

---

## Documentation Priority

### High Priority (Start Here)
1. Getting Started & Authentication
2. Clusters API & SDK
3. Jobs API & SDK
4. Python SDK core client
5. Common SQL queries
6. Basic code examples

### Medium Priority
1. DBFS operations
2. Secrets management
3. Unity Catalog basics
4. MLflow tracking
5. Delta Lake operations
6. CLI commands

### Lower Priority (After Core)
1. Advanced Unity Catalog features
2. Delta Live Tables
3. Feature Store
4. AutoML
5. Advanced optimization
6. Repos and Git integration

---

## External Documentation Sources

- **Official Docs**: https://docs.databricks.com/
- **API Reference**: https://docs.databricks.com/api/
- **Python SDK**: https://github.com/databricks/databricks-sdk-py
- **CLI**: https://docs.databricks.com/dev-tools/cli/
- **Delta Lake**: https://docs.delta.io/
- **MLflow**: https://www.mlflow.org/docs/latest/index.html
- **SQL Reference**: https://docs.databricks.com/sql/language-manual/

---

## Notes

- Focus on practical, working examples
- Include error handling patterns
- Document common pitfalls and solutions
- Keep version compatibility in mind
- Regular updates needed as Databricks evolves