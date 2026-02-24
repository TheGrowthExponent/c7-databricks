# Databricks Security Best Practices

## Overview

This guide provides comprehensive security best practices for Databricks, covering authentication, authorization, data encryption, network security, secrets management, and compliance.

## Table of Contents

1. [Authentication and Access Control](#authentication-and-access-control)
2. [Secrets Management](#secrets-management)
3. [Data Encryption](#data-encryption)
4. [Network Security](#network-security)
5. [Unity Catalog Security](#unity-catalog-security)
6. [Audit and Compliance](#audit-and-compliance)
7. [Secure Development Practices](#secure-development-practices)

---

## Authentication and Access Control

### Personal Access Tokens

```python
import os

# ✅ GOOD: Store tokens securely in environment variables
token = os.environ.get("DATABRICKS_TOKEN")

# ❌ BAD: Hardcoding tokens
token = "dapi1234567890abcdef"  # Never do this!

# ✅ GOOD: Use token rotation
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Create token with expiration
token_response = w.token_management.create_obo_token(
    application_id="my-app",
    lifetime_seconds=7776000,  # 90 days
    comment="Automated pipeline token"
)

# Store securely
import keyring
keyring.set_password("databricks", "token", token_response.token_value)
```

### Service Principal Authentication

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.oauth import ClientCredentials

# ✅ BEST: Use service principals for production
credentials = ClientCredentials(
    client_id=os.environ.get("DATABRICKS_CLIENT_ID"),
    client_secret=os.environ.get("DATABRICKS_CLIENT_SECRET")
)

w = WorkspaceClient(
    host=os.environ.get("DATABRICKS_HOST"),
    credentials=credentials
)

# Service principals provide:
# - Better audit trails
# - No personal attribution
# - Centralized management
# - Fine-grained permissions
```

### Multi-Factor Authentication (MFA)

```python
# Enable MFA for all users via Admin Console
# Settings > Workspace settings > Authentication > Multi-factor authentication

# Enforce MFA for specific groups
# 1. Create group with MFA requirement
# 2. Add users to group
# 3. Configure conditional access policies
```

### Role-Based Access Control (RBAC)

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Create groups for RBAC
w.groups.create(display_name="data-engineers")
w.groups.create(display_name="data-analysts")
w.groups.create(display_name="data-scientists")

# Assign users to groups
w.groups.patch(
    id="group-id",
    operations=[{
        "op": "add",
        "path": "members",
        "value": [{"value": "user@example.com"}]
    }]
)

# Grant permissions to groups (not individuals)
spark.sql("""
    GRANT SELECT ON CATALOG production TO `data-analysts`
""")

spark.sql("""
    GRANT ALL PRIVILEGES ON CATALOG development TO `data-engineers`
""")
```

---

## Secrets Management

### Databricks Secrets

```python
# Create secret scope
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Create scope
w.secrets.create_scope(scope="production-secrets")

# Add secrets via CLI (not API for security)
# databricks secrets put --scope production-secrets --key db-password

# ✅ GOOD: Retrieve secrets in notebooks
db_password = dbutils.secrets.get(scope="production-secrets", key="db-password")

# Use in connections
jdbc_url = f"jdbc:postgresql://host:5432/db"
df = spark.read.format("jdbc") \
    .option("url", jdbc_url) \
    .option("dbtable", "table") \
    .option("user", "dbuser") \
    .option("password", dbutils.secrets.get("production-secrets", "db-password")) \
    .load()

# ❌ BAD: Printing secrets
# print(db_password)  # Never log secrets!
```

### Azure Key Vault Integration

```python
# Create Azure Key Vault-backed scope
# databricks secrets create-scope --scope akv-secrets \
#   --scope-backend-type AZURE_KEYVAULT \
#   --resource-id /subscriptions/.../resourceGroups/.../providers/Microsoft.KeyVault/vaults/my-vault \
#   --dns-name https://my-vault.vault.azure.net/

# Access secrets
secret_value = dbutils.secrets.get(scope="akv-secrets", key="api-key")

# Benefits:
# - Centralized secret management
# - Automatic rotation support
# - Enhanced audit logging
# - Integration with Azure RBAC
```

### AWS Secrets Manager Integration

```python
import boto3
import json

def get_secret(secret_name):
    """Retrieve secret from AWS Secrets Manager"""
    
    # Use IAM role attached to cluster
    client = boto3.client('secretsmanager', region_name='us-west-2')
    
    try:
        response = client.get_secret_value(SecretId=secret_name)
        
        if 'SecretString' in response:
            secret = json.loads(response['SecretString'])
            return secret
        else:
            # Binary secret
            return response['SecretBinary']
            
    except Exception as e:
        print(f"Error retrieving secret: {str(e)}")
        raise

# Usage
db_credentials = get_secret("production/database/credentials")
username = db_credentials['username']
password = db_credentials['password']
```

### Secrets Best Practices

```python
# ✅ GOOD: Limit secret scope access
# Grant access only to specific users/groups
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Set ACL on secret scope
w.secrets.put_acl(
    scope="production-secrets",
    principal="data-engineers",
    permission="READ"
)

# ❌ BAD: Using plaintext configuration files
config = {
    "api_key": "abc123",  # Never store secrets in config files
    "password": "secret123"
}

# ✅ GOOD: Reference secrets in config
config = {
    "api_key_secret": "production-secrets/api-key",
    "password_secret": "production-secrets/db-password"
}

def get_config_value(secret_path):
    scope, key = secret_path.split("/")
    return dbutils.secrets.get(scope=scope, key=key)
```

---

## Data Encryption

### Encryption at Rest

```python
# Delta Lake encryption (automatic with workspace encryption)
# All data written to Delta tables is encrypted

# Verify encryption settings
spark.sql("DESCRIBE EXTENDED catalog.schema.table").show()

# Customer-managed keys (CMK)
# Configure via cloud provider:
# - AWS: Use AWS KMS
# - Azure: Use Azure Key Vault
# - GCP: Use Cloud KMS

# Create encrypted table
spark.sql("""
    CREATE TABLE catalog.schema.encrypted_data (
        id INT,
        sensitive_data STRING
    ) USING DELTA
    LOCATION 's3://encrypted-bucket/data/'
    TBLPROPERTIES (
        'delta.encryption.mode' = 'server-side-encryption'
    )
""")
```

### Encryption in Transit

```python
# All Databricks connections use TLS 1.2+
# No configuration needed for:
# - JDBC/ODBC connections
# - REST API calls
# - Inter-node communication

# ✅ GOOD: Verify HTTPS connections
import requests

response = requests.get(
    "https://databricks-instance/api/2.0/clusters/list",
    headers={"Authorization": f"Bearer {token}"},
    verify=True  # Verify SSL certificate
)
```

### Column-Level Encryption

```python
from pyspark.sql.functions import col, expr

# Encrypt sensitive columns
def encrypt_column(df, column_name, encryption_key_secret):
    """Encrypt a column using AES encryption"""
    
    key = dbutils.secrets.get(scope="encryption-keys", key=encryption_key_secret)
    
    encrypted_df = df.withColumn(
        f"{column_name}_encrypted",
        expr(f"aes_encrypt({column_name}, '{key}')")
    ).drop(column_name)
    
    return encrypted_df

# Usage
df = spark.read.format("delta").table("catalog.schema.customers")
encrypted_df = encrypt_column(df, "ssn", "customer-encryption-key")

# Decrypt when needed
def decrypt_column(df, encrypted_column_name, original_name, encryption_key_secret):
    """Decrypt an encrypted column"""
    
    key = dbutils.secrets.get(scope="encryption-keys", key=encryption_key_secret)
    
    decrypted_df = df.withColumn(
        original_name,
        expr(f"aes_decrypt({encrypted_column_name}, '{key}')").cast("string")
    ).drop(encrypted_column_name)
    
    return decrypted_df
```

### Data Masking

```python
from pyspark.sql.functions import col, when, regexp_replace, substring, concat, lit

def mask_pii(df):
    """Mask personally identifiable information"""
    
    masked_df = df \
        .withColumn(
            "email_masked",
            concat(
                substring(col("email"), 1, 3),
                lit("***@"),
                regexp_replace(col("email"), ".*@", "")
            )
        ) \
        .withColumn(
            "ssn_masked",
            concat(lit("XXX-XX-"), substring(col("ssn"), -4, 4))
        ) \
        .withColumn(
            "phone_masked",
            concat(lit("(XXX) XXX-"), substring(col("phone"), -4, 4))
        )
    
    return masked_df

# Use for non-production environments
df = spark.read.format("delta").table("production.customers")
masked_df = mask_pii(df)
masked_df.write.format("delta").mode("overwrite").saveAsTable("dev.customers_masked")
```

---

## Network Security

### Private Link / VNet Injection

```python
# Configure workspace with private connectivity
# Azure: VNet injection
# AWS: PrivateLink
# GCP: Private Service Connect

# Benefits:
# - No public internet exposure
# - Traffic stays within private network
# - Compliance with network security policies

# Configuration is done at workspace creation time
```

### IP Access Lists

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Create IP access list
w.ip_access_lists.create(
    label="office-network",
    list_type="ALLOW",
    ip_addresses=["203.0.113.0/24", "198.51.100.0/24"]
)

# Enable IP access lists
w.workspace_conf.set_status(
    keys={"enableIpAccessLists": "true"}
)

# Block all except allowed IPs
w.ip_access_lists.create(
    label="block-all",
    list_type="BLOCK",
    ip_addresses=["0.0.0.0/0"]
)
```

### Secure Cluster Configuration

```python
# Cluster security best practices
cluster_config = {
    "cluster_name": "secure-cluster",
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "Standard_DS3_v2",
    "num_workers": 2,
    
    # Security configurations
    "spark_conf": {
        # Enable encryption
        "spark.ssl.enabled": "true",
        
        # Secure shuffle
        "spark.authenticate": "true",
        "spark.authenticate.secret": "{{ secrets/cluster-secrets/shuffle-secret }}",
        
        # Network encryption
        "spark.network.crypto.enabled": "true",
        
        # Disable unnecessary features
        "spark.ui.enabled": "false"
    },
    
    # IAM role (AWS) or Managed Identity (Azure)
    "aws_attributes": {
        "instance_profile_arn": "arn:aws:iam::account:instance-profile/databricks-role"
    },
    
    # Cluster isolation
    "enable_elastic_disk": False,
    "enable_local_disk_encryption": True
}
```

---

## Unity Catalog Security

### Catalog-Level Security

```python
# Create catalog with access control
spark.sql("""
    CREATE CATALOG IF NOT EXISTS production
    COMMENT 'Production data catalog'
""")

# Grant catalog permissions
spark.sql("""
    GRANT USAGE ON CATALOG production TO `data-analysts`
""")

spark.sql("""
    GRANT ALL PRIVILEGES ON CATALOG production TO `data-engineers`
""")

# Deny access by default (principle of least privilege)
spark.sql("""
    REVOKE ALL PRIVILEGES ON CATALOG production FROM `users`
""")
```

### Schema-Level Security

```python
# Create schema with permissions
spark.sql("""
    CREATE SCHEMA IF NOT EXISTS production.sensitive_data
    COMMENT 'Sensitive customer data'
""")

# Grant schema permissions
spark.sql("""
    GRANT USAGE, SELECT ON SCHEMA production.sensitive_data TO `analysts-pii-approved`
""")

# Create schema for different security levels
spark.sql("CREATE SCHEMA production.public_data")
spark.sql("CREATE SCHEMA production.internal_data")
spark.sql("CREATE SCHEMA production.confidential_data")
```

### Table-Level Security

```python
# Row-level security using views
spark.sql("""
    CREATE OR REPLACE VIEW production.sales.regional_sales AS
    SELECT * FROM production.sales.all_sales
    WHERE region = current_user_region()
""")

# Grant view access
spark.sql("""
    GRANT SELECT ON VIEW production.sales.regional_sales TO `regional-managers`
""")

# Column-level security
spark.sql("""
    CREATE OR REPLACE VIEW production.customers.customer_summary AS
    SELECT 
        customer_id,
        name,
        email,
        -- Mask sensitive fields
        'XXX-XX-' || RIGHT(ssn, 4) as ssn_masked,
        total_purchases
    FROM production.customers.customer_details
""")

# Dynamic views based on user
spark.sql("""
    CREATE OR REPLACE VIEW production.sales.filtered_sales AS
    SELECT * FROM production.sales.all_sales
    WHERE 
        CASE 
            WHEN is_member('admins') THEN TRUE
            WHEN is_member('managers') THEN amount < 10000
            WHEN is_member('analysts') THEN amount < 1000
            ELSE FALSE
        END
""")
```

### Data Lineage and Audit

```python
# Unity Catalog automatically tracks lineage
# View lineage in Databricks UI or via API

from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Get table lineage
lineage = w.catalog.get_lineage(
    table_name="production.sales.transactions"
)

# Audit table access
spark.sql("""
    SELECT 
        event_time,
        user_identity,
        action_name,
        request_params
    FROM system.access.audit
    WHERE request_params.table_name = 'production.sales.transactions'
    ORDER BY event_time DESC
    LIMIT 100
""").show()
```

---

## Audit and Compliance

### Audit Logging

```python
# Enable audit logs (configured at account level)
# Logs are sent to cloud storage

# Query audit logs
audit_df = spark.read.format("json").load("s3://audit-bucket/logs/")

# Common audit queries
# 1. Failed authentication attempts
failed_auth = audit_df.filter(
    (col("actionName") == "login") & 
    (col("response.statusCode") != 200)
)

# 2. Data access by user
user_access = audit_df.filter(
    (col("userIdentity.email") == "user@example.com") &
    (col("actionName").isin(["read", "write", "delete"]))
)

# 3. Permission changes
permission_changes = audit_df.filter(
    col("actionName").isin(["grant", "revoke"])
)

# 4. Sensitive table access
sensitive_access = audit_df.filter(
    col("requestParams.table_name").like("%pii%")
)
```

### Compliance Monitoring

```python
from datetime import datetime, timedelta

def compliance_report():
    """Generate security compliance report"""
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "checks": []
    }
    
    # Check 1: All users have MFA enabled
    users = w.users.list()
    mfa_enabled = sum(1 for u in users if u.mfa_enabled)
    
    report["checks"].append({
        "check": "MFA Coverage",
        "passed": mfa_enabled == len(list(users)),
        "details": f"{mfa_enabled}/{len(list(users))} users"
    })
    
    # Check 2: No long-lived tokens
    tokens = w.token_management.list()
    expired_tokens = [t for t in tokens if t.expiry_time and t.expiry_time > 90*24*60*60]
    
    report["checks"].append({
        "check": "Token Expiration",
        "passed": len(expired_tokens) == 0,
        "details": f"{len(expired_tokens)} tokens expire > 90 days"
    })
    
    # Check 3: Audit logs are enabled
    audit_enabled = spark.sql("""
        SELECT COUNT(*) as log_count 
        FROM system.access.audit 
        WHERE event_date >= current_date() - 1
    """).collect()[0]['log_count']
    
    report["checks"].append({
        "check": "Audit Logging",
        "passed": audit_enabled > 0,
        "details": f"{audit_enabled} log entries in last 24h"
    })
    
    return report

# Run compliance checks
report = compliance_report()
print(json.dumps(report, indent=2))
```

### Data Retention Policies

```python
# Implement data retention
def apply_retention_policy(table_name, retention_days, date_column):
    """
    Delete data older than retention period
    """
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    
    # Log action
    print(f"Applying retention policy to {table_name}")
    print(f"Deleting records older than {cutoff_date}")
    
    # Delete old data
    from delta.tables import DeltaTable
    
    delta_table = DeltaTable.forName(spark, table_name)
    
    deleted_count = delta_table.delete(
        f"{date_column} < '{cutoff_date.strftime('%Y-%m-%d')}'"
    )
    
    print(f"Deleted {deleted_count} records")
    
    # Vacuum to remove files
    delta_table.vacuum(retention_days * 24)  # Convert to hours
    
    return deleted_count

# Apply retention policies
apply_retention_policy("catalog.schema.logs", retention_days=90, date_column="log_date")
apply_retention_policy("catalog.schema.temp_data", retention_days=30, date_column="created_date")
```

---

## Secure Development Practices

### Code Review Checklist

```python
# Security code review checklist:
# [ ] No hardcoded credentials
# [ ] Secrets retrieved from secret store
# [ ] Input validation implemented
# [ ] SQL injection prevention (parameterized queries)
# [ ] Proper error handling (no sensitive data in errors)
# [ ] Least privilege permissions
# [ ] Audit logging enabled
# [ ] Data encryption for sensitive fields

# ✅ GOOD: Parameterized queries
def get_customer_data(customer_id):
    query = """
        SELECT * FROM customers 
        WHERE customer_id = ?
    """
    return spark.sql(query, [customer_id])

# ❌ BAD: String concatenation (SQL injection risk)
def get_customer_data_bad(customer_id):
    query = f"SELECT * FROM customers WHERE customer_id = {customer_id}"
    return spark.sql(query)
```

### Input Validation

```python
from pyspark.sql.functions import col, regexp_extract, length

def validate_input(df, column, validation_type):
    """Validate input data"""
    
    if validation_type == "email":
        # Email validation
        valid = df.filter(
            col(column).rlike(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        )
        invalid = df.subtract(valid)
        
    elif validation_type == "phone":
        # Phone validation
        valid = df.filter(
            col(column).rlike(r"^\d{3}-\d{3}-\d{4}$")
        )
        invalid = df.subtract(valid)
        
    elif validation_type == "ssn":
        # SSN validation
        valid = df.filter(
            col(column).rlike(r"^\d{3}-\d{2}-\d{4}$")
        )
        invalid = df.subtract(valid)
    
    # Log invalid records
    if invalid.count() > 0:
        print(f"Found {invalid.count()} invalid {validation_type} records")
        invalid.write.format("delta").mode("append").saveAsTable("audit.invalid_data")
    
    return valid

# Usage
df = spark.read.format("delta").table("raw.customer_data")
validated_df = validate_input(df, "email", "email")
```

### Secure Notebook Practices

```python
# ✅ GOOD: Clear sensitive outputs
dbutils.notebook.exit(json.dumps({"status": "success"}))  # OK
# dbutils.notebook.exit(json.dumps({"password": secret}))  # BAD!

# ✅ GOOD: Limit display of sensitive data
df = spark.read.format("delta").table("customers")
df.select("customer_id", "name").show(10)  # Show limited, non-sensitive columns

# ❌ BAD: Displaying sensitive data
# df.show()  # May expose PII

# ✅ GOOD: Use notebook parameters for configuration
dbutils.widgets.text("environment", "dev", "Environment")
env = dbutils.widgets.get("environment")

config = {
    "dev": {"scope": "dev-secrets"},
    "prod": {"scope": "prod-secrets"}
}

secrets_scope = config[env]["scope"]
```

### Dependency Management

```python
# Use approved libraries only
# Maintain an allow-list of packages

APPROVED_PACKAGES = {
    "pandas": ">=1.3.0,<2.0.0",
    "numpy": ">=1.21.0",
    "scikit-learn": ">=1.0.0",
    "mlflow": ">=2.0.0"
}

def validate_requirements(requirements_file):
    """Validate that only approved packages are used"""
    
    with open(requirements_file, "r") as f:
        requirements = f.readlines()
    
    for req in requirements:
        package = req.split("==")[0].strip()
        
        if package not in APPROVED_PACKAGES:
            raise SecurityError(f"Package {package} is not approved")
    
    print("All packages approved")

# Scan for vulnerabilities
# Use tools like: pip-audit, safety, snyk
```

---

## Security Checklist

### Production Deployment Checklist

- [ ] Service principals configured (no personal tokens)
- [ ] MFA enabled for all users
- [ ] Secrets stored in secret manager (no hardcoded)
- [ ] IP access lists configured
- [ ] Audit logging enabled
- [ ] Unity Catalog permissions configured
- [ ] Data encryption at rest enabled
- [ ] TLS/HTTPS for all connections
- [ ] Row/column-level security implemented
- [ ] Data retention policies defined
- [ ] Regular security audits scheduled
- [ ] Compliance monitoring automated
- [ ] Incident response plan documented
- [ ] Regular backup and recovery tested
- [ ] Network isolation (PrivateLink/VNet) configured

### Regular Security Reviews

```python
def monthly_security_review():
    """Automated monthly security review"""
    
    review_items = []
    
    # 1. Review token expiration
    tokens = w.token_management.list()
    expiring_tokens = [t for t in tokens if t.expiry_time and 
                      (t.expiry_time - datetime.now().timestamp()) < 30*24*60*60]
    review_items.append({
        "item": "Tokens expiring in 30 days",
        "count": len(expiring_tokens)
    })
    
    # 2. Review unused permissions
    # Query for permissions not used in 90 days
    unused_perms = spark.sql("""
        SELECT table_name, grantee, privilege
        FROM system.information_schema.table_privileges tp
        LEFT JOIN system.access.audit a 
            ON tp.table_name = a.request_params.table_name
            AND tp.grantee = a.user_identity.email
        WHERE a.event_time IS NULL 
            OR a.event_time < current_date() - 90
    """)
    
    review_items.append({
        "item": "Unused permissions (90+ days)",
        "count": unused_perms.count()
    })
    
    # 3. Review cluster configurations
    # Check for clusters without encryption
    
    # 4. Review workspace access
    # Check for external users
    
    return review_items
```

---

## Related Documentation

- [Unity Catalog Security](../api/unity-catalog.md)
- [Secrets API](../api/secrets.md)
- [Tokens API](../api/tokens.md)
- [Audit Logging](./audit-logging.md)

---

## Additional Resources

- [Databricks Security Guide](https://docs.databricks.com/security/index.html)
- [Unity Catalog Security Model](https://docs.databricks.com/data-governance/unity-catalog/manage-privileges/index.html)
- [Compliance Certifications](https://www.databricks.com/trust)
- [Security Best Practices](https://docs.databricks.com/security/best-practices.html)