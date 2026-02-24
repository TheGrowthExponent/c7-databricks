# Databricks Tokens API Reference

## Overview

The Tokens API allows you to create, list, and revoke personal access tokens (PATs) for Databricks workspace authentication. Tokens are used to authenticate API requests, CLI operations, and programmatic access to Databricks resources.

## Base URL

```
https://<databricks-instance>/api/2.0/token
```

## Authentication

Token API requests require authentication using an existing personal access token or Azure AD token:

```
Authorization: Bearer <token>
```

## Token Lifecycle

1. **Creation** - Generate a new token with optional expiration
2. **Active** - Token can be used for authentication
3. **Revoked** - Token is deactivated and cannot be used

## Token Best Practices

- Set expiration times for security
- Use service principal tokens for production systems
- Store tokens securely (environment variables, secret managers)
- Rotate tokens regularly
- Revoke unused or compromised tokens immediately
- Use different tokens for different applications

---

## Endpoints

### Create Token

Create a new personal access token.

**Endpoint:** `POST /api/2.0/token/create`

**Request Body:**
- `lifetime_seconds` (optional) - Token lifetime in seconds (default: no expiration)
- `comment` (optional) - Description/comment for the token

**Request Example:**

```bash
curl -X POST \
  'https://<databricks-instance>/api/2.0/token/create' \
  -H 'Authorization: Bearer <existing-token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "lifetime_seconds": 7776000,
    "comment": "Token for CI/CD pipeline"
  }'
```

**Python Example:**

```python
import requests

url = "https://<databricks-instance>/api/2.0/token/create"
headers = {
    "Authorization": f"Bearer {existing_token}",
    "Content-Type": "application/json"
}
data = {
    "lifetime_seconds": 7776000,  # 90 days
    "comment": "Token for CI/CD pipeline"
}

response = requests.post(url, headers=headers, json=data)
result = response.json()

token_value = result["token_value"]
token_info = result["token_info"]

print(f"New Token ID: {token_info['token_id']}")
print(f"Token Value: {token_value}")
print(f"Creation Time: {token_info['creation_time']}")
print(f"Expiry Time: {token_info['expiry_time']}")

# IMPORTANT: Save token_value securely - it cannot be retrieved later
```

**Response:**

```json
{
  "token_value": "dapi1234567890abcdef1234567890abcdef",
  "token_info": {
    "token_id": "a1b2c3d4e5f67890",
    "creation_time": 1609459200000,
    "expiry_time": 1617235200000,
    "comment": "Token for CI/CD pipeline"
  }
}
```

**Important Notes:**
- The `token_value` is only returned once during creation
- Store the token securely immediately - it cannot be retrieved later
- If `lifetime_seconds` is not specified, the token never expires (not recommended)

---

### List Tokens

List all active tokens for the authenticated user.

**Endpoint:** `GET /api/2.0/token/list`

**Request Example:**

```bash
curl -X GET \
  'https://<databricks-instance>/api/2.0/token/list' \
  -H 'Authorization: Bearer <token>'
```

**Python Example:**

```python
import requests
from datetime import datetime

url = "https://<databricks-instance>/api/2.0/token/list"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(url, headers=headers)
result = response.json()

tokens = result.get("token_infos", [])

for token_info in tokens:
    token_id = token_info["token_id"]
    comment = token_info.get("comment", "No comment")
    creation_time = datetime.fromtimestamp(token_info["creation_time"] / 1000)
    
    if "expiry_time" in token_info:
        expiry_time = datetime.fromtimestamp(token_info["expiry_time"] / 1000)
        print(f"Token ID: {token_id}")
        print(f"  Comment: {comment}")
        print(f"  Created: {creation_time}")
        print(f"  Expires: {expiry_time}")
    else:
        print(f"Token ID: {token_id}")
        print(f"  Comment: {comment}")
        print(f"  Created: {creation_time}")
        print(f"  Expires: Never")
    print()
```

**Response:**

```json
{
  "token_infos": [
    {
      "token_id": "a1b2c3d4e5f67890",
      "creation_time": 1609459200000,
      "expiry_time": 1617235200000,
      "comment": "Token for CI/CD pipeline"
    },
    {
      "token_id": "b2c3d4e5f6789012",
      "creation_time": 1609459200000,
      "comment": "Development token"
    }
  ]
}
```

---

### Revoke Token

Revoke (delete) an existing token.

**Endpoint:** `POST /api/2.0/token/delete`

**Request Body:**
- `token_id` (required) - The ID of the token to revoke

**Request Example:**

```bash
curl -X POST \
  'https://<databricks-instance>/api/2.0/token/delete' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "token_id": "a1b2c3d4e5f67890"
  }'
```

**Python Example:**

```python
import requests

url = "https://<databricks-instance>/api/2.0/token/delete"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
data = {
    "token_id": "a1b2c3d4e5f67890"
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    print("Token revoked successfully")
else:
    print(f"Error: {response.text}")
```

**Response:** `200 OK` (empty body on success)

**Important Notes:**
- Revoked tokens cannot be recovered
- Applications using revoked tokens will immediately lose access
- You cannot revoke the token you're currently using (use a different token)

---

## Python SDK Examples

### Using Databricks SDK

```python
from databricks.sdk import WorkspaceClient
from datetime import timedelta

# Initialize client
w = WorkspaceClient()

# Create a token with 90-day expiration
token_response = w.token_management.create_obo_token(
    application_id="my-app",
    lifetime_seconds=int(timedelta(days=90).total_seconds()),
    comment="Automated data pipeline token"
)

print(f"New Token: {token_response.token_value}")
print(f"Token ID: {token_response.token_info.token_id}")

# List all tokens
tokens = w.token_management.list()
for token in tokens:
    print(f"Token ID: {token.token_id}, Comment: {token.comment}")

# Revoke a token
w.token_management.delete(token_id="a1b2c3d4e5f67890")
print("Token revoked")
```

---

## Advanced Examples

### Token Management Class

Complete token management utility:

```python
import requests
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import os
import json

class TokenManager:
    """Databricks token management utility"""
    
    def __init__(self, host: str, token: str):
        """
        Initialize TokenManager
        
        Args:
            host: Databricks workspace URL
            token: Existing authentication token
        """
        self.host = host.rstrip('/')
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def create_token(
        self, 
        comment: str, 
        lifetime_days: Optional[int] = 90
    ) -> Dict:
        """
        Create a new token
        
        Args:
            comment: Description for the token
            lifetime_days: Token lifetime in days (None for no expiration)
            
        Returns:
            Dictionary with token_value and token_info
        """
        url = f"{self.host}/api/2.0/token/create"
        
        data = {"comment": comment}
        if lifetime_days:
            data["lifetime_seconds"] = lifetime_days * 86400
        
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        
        # Log token creation (without the token value)
        print(f"Created token: {result['token_info']['token_id']}")
        print(f"Comment: {comment}")
        print(f"Expires: {self._format_timestamp(result['token_info'].get('expiry_time'))}")
        
        return result
    
    def list_tokens(self) -> List[Dict]:
        """
        List all active tokens
        
        Returns:
            List of token info dictionaries
        """
        url = f"{self.host}/api/2.0/token/list"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        return response.json().get("token_infos", [])
    
    def revoke_token(self, token_id: str) -> None:
        """
        Revoke a token
        
        Args:
            token_id: ID of the token to revoke
        """
        url = f"{self.host}/api/2.0/token/delete"
        data = {"token_id": token_id}
        
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        
        print(f"Revoked token: {token_id}")
    
    def list_expiring_tokens(self, days: int = 30) -> List[Dict]:
        """
        List tokens expiring within specified days
        
        Args:
            days: Number of days to check
            
        Returns:
            List of expiring tokens
        """
        tokens = self.list_tokens()
        expiring = []
        
        threshold = datetime.now() + timedelta(days=days)
        threshold_ms = int(threshold.timestamp() * 1000)
        
        for token in tokens:
            if "expiry_time" in token:
                if token["expiry_time"] <= threshold_ms:
                    expiring.append(token)
        
        return expiring
    
    def cleanup_old_tokens(self, pattern: Optional[str] = None) -> int:
        """
        Revoke tokens matching a pattern
        
        Args:
            pattern: Comment pattern to match (e.g., "temp-")
            
        Returns:
            Number of tokens revoked
        """
        tokens = self.list_tokens()
        revoked_count = 0
        
        for token in tokens:
            comment = token.get("comment", "")
            if pattern and pattern in comment:
                self.revoke_token(token["token_id"])
                revoked_count += 1
        
        return revoked_count
    
    def rotate_token(
        self, 
        old_token_id: str, 
        comment: str, 
        lifetime_days: int = 90
    ) -> Dict:
        """
        Rotate a token (create new, revoke old)
        
        Args:
            old_token_id: ID of token to revoke
            comment: Comment for new token
            lifetime_days: Lifetime for new token
            
        Returns:
            New token information
        """
        # Create new token first
        new_token = self.create_token(comment, lifetime_days)
        
        # Revoke old token
        self.revoke_token(old_token_id)
        
        print(f"Token rotated successfully")
        return new_token
    
    def display_tokens(self) -> None:
        """Display all tokens in a formatted table"""
        tokens = self.list_tokens()
        
        print(f"\n{'Token ID':<20} {'Comment':<30} {'Created':<20} {'Expires':<20}")
        print("-" * 90)
        
        for token in tokens:
            token_id = token["token_id"][:16] + "..."
            comment = token.get("comment", "No comment")[:28]
            created = self._format_timestamp(token["creation_time"])
            expires = self._format_timestamp(token.get("expiry_time", None))
            
            print(f"{token_id:<20} {comment:<30} {created:<20} {expires:<20}")
    
    @staticmethod
    def _format_timestamp(timestamp_ms: Optional[int]) -> str:
        """Format timestamp for display"""
        if timestamp_ms is None:
            return "Never"
        dt = datetime.fromtimestamp(timestamp_ms / 1000)
        return dt.strftime("%Y-%m-%d %H:%M")


# Usage Examples
if __name__ == "__main__":
    # Initialize manager
    manager = TokenManager(
        host="https://<databricks-instance>",
        token=os.environ.get("DATABRICKS_TOKEN")
    )
    
    # Create a new token
    new_token = manager.create_token(
        comment="API automation token",
        lifetime_days=90
    )
    print(f"New token value: {new_token['token_value']}")
    
    # List all tokens
    manager.display_tokens()
    
    # Find expiring tokens
    expiring = manager.list_expiring_tokens(days=7)
    print(f"\nTokens expiring in 7 days: {len(expiring)}")
    
    # Cleanup temporary tokens
    revoked = manager.cleanup_old_tokens(pattern="temp-")
    print(f"Revoked {revoked} temporary tokens")
```

---

### Token Rotation Script

Automated token rotation for CI/CD:

```python
import requests
import os
import json
from datetime import datetime, timedelta

def rotate_cicd_token(
    host: str,
    current_token: str,
    secret_store_update_func,
    lifetime_days: int = 90
):
    """
    Rotate CI/CD token and update secret store
    
    Args:
        host: Databricks workspace URL
        current_token: Current token value
        secret_store_update_func: Function to update secret store
        lifetime_days: New token lifetime
    """
    headers = {
        "Authorization": f"Bearer {current_token}",
        "Content-Type": "application/json"
    }
    
    # Get current token ID
    list_url = f"{host}/api/2.0/token/list"
    response = requests.get(list_url, headers=headers)
    tokens = response.json().get("token_infos", [])
    
    # Find token expiring soonest
    expiring_token = min(
        tokens,
        key=lambda t: t.get("expiry_time", float('inf'))
    )
    
    print(f"Rotating token: {expiring_token['token_id']}")
    print(f"Comment: {expiring_token.get('comment', 'N/A')}")
    
    # Create new token
    create_url = f"{host}/api/2.0/token/create"
    create_data = {
        "lifetime_seconds": lifetime_days * 86400,
        "comment": f"CI/CD token (rotated {datetime.now().strftime('%Y-%m-%d')})"
    }
    
    create_response = requests.post(create_url, headers=headers, json=create_data)
    new_token_data = create_response.json()
    
    new_token_value = new_token_data["token_value"]
    new_token_id = new_token_data["token_info"]["token_id"]
    
    print(f"Created new token: {new_token_id}")
    
    # Update secret store (e.g., AWS Secrets Manager, Azure Key Vault)
    try:
        secret_store_update_func(new_token_value)
        print("Updated secret store")
    except Exception as e:
        print(f"Error updating secret store: {e}")
        # Don't revoke old token if secret store update fails
        return
    
    # Revoke old token
    delete_url = f"{host}/api/2.0/token/delete"
    delete_data = {"token_id": expiring_token["token_id"]}
    requests.post(delete_url, headers=headers, json=delete_data)
    
    print(f"Revoked old token: {expiring_token['token_id']}")
    print("Token rotation complete")


# Example with AWS Secrets Manager
def update_aws_secret(token_value: str):
    """Update token in AWS Secrets Manager"""
    import boto3
    
    client = boto3.client('secretsmanager')
    client.update_secret(
        SecretId='databricks/token',
        SecretString=token_value
    )


# Example with Azure Key Vault
def update_azure_keyvault(token_value: str):
    """Update token in Azure Key Vault"""
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential
    
    credential = DefaultAzureCredential()
    client = SecretClient(
        vault_url="https://<keyvault-name>.vault.azure.net/",
        credential=credential
    )
    client.set_secret("databricks-token", token_value)


# Usage
rotate_cicd_token(
    host="https://<databricks-instance>",
    current_token=os.environ.get("DATABRICKS_TOKEN"),
    secret_store_update_func=update_aws_secret,
    lifetime_days=90
)
```

---

### Token Expiry Monitor

Monitor and alert on expiring tokens:

```python
import requests
from datetime import datetime, timedelta
from typing import List, Dict
import smtplib
from email.mime.text import MIMEText

class TokenExpiryMonitor:
    """Monitor token expiration and send alerts"""
    
    def __init__(self, host: str, token: str):
        self.host = host.rstrip('/')
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def check_expiring_tokens(self, warning_days: int = 30) -> List[Dict]:
        """
        Check for tokens expiring within warning period
        
        Args:
            warning_days: Days before expiration to warn
            
        Returns:
            List of expiring token information
        """
        url = f"{self.host}/api/2.0/token/list"
        response = requests.get(url, headers=self.headers)
        tokens = response.json().get("token_infos", [])
        
        now_ms = int(datetime.now().timestamp() * 1000)
        warning_threshold = now_ms + (warning_days * 86400 * 1000)
        
        expiring = []
        for token in tokens:
            if "expiry_time" in token:
                expiry = token["expiry_time"]
                if now_ms <= expiry <= warning_threshold:
                    days_until = (expiry - now_ms) / (86400 * 1000)
                    expiring.append({
                        "token_id": token["token_id"],
                        "comment": token.get("comment", "No comment"),
                        "expiry_time": expiry,
                        "days_until_expiry": int(days_until)
                    })
        
        return sorted(expiring, key=lambda x: x["days_until_expiry"])
    
    def send_alert(self, expiring_tokens: List[Dict], recipient: str):
        """
        Send email alert about expiring tokens
        
        Args:
            expiring_tokens: List of expiring tokens
            recipient: Email address to send alert
        """
        if not expiring_tokens:
            return
        
        subject = f"Databricks Token Expiration Alert - {len(expiring_tokens)} token(s)"
        
        body = "The following Databricks tokens are expiring soon:\n\n"
        for token in expiring_tokens:
            body += f"Token ID: {token['token_id']}\n"
            body += f"Comment: {token['comment']}\n"
            body += f"Days until expiry: {token['days_until_expiry']}\n"
            body += f"Expiry date: {datetime.fromtimestamp(token['expiry_time'] / 1000).strftime('%Y-%m-%d %H:%M')}\n"
            body += "-" * 50 + "\n"
        
        body += "\nPlease rotate these tokens before they expire.\n"
        
        # Create email
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = "databricks-monitor@example.com"
        msg['To'] = recipient
        
        # Send email (configure SMTP settings)
        with smtplib.SMTP('smtp.example.com', 587) as server:
            server.starttls()
            server.login("username", "password")
            server.send_message(msg)
        
        print(f"Alert sent to {recipient}")
    
    def generate_report(self) -> str:
        """Generate token status report"""
        url = f"{self.host}/api/2.0/token/list"
        response = requests.get(url, headers=self.headers)
        tokens = response.json().get("token_infos", [])
        
        report = "Databricks Token Status Report\n"
        report += "=" * 70 + "\n\n"
        report += f"Total tokens: {len(tokens)}\n"
        report += f"Report date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        # Categorize tokens
        expired = []
        expiring_soon = []
        active = []
        no_expiry = []
        
        now_ms = int(datetime.now().timestamp() * 1000)
        warning_ms = now_ms + (30 * 86400 * 1000)
        
        for token in tokens:
            if "expiry_time" not in token:
                no_expiry.append(token)
            elif token["expiry_time"] <= now_ms:
                expired.append(token)
            elif token["expiry_time"] <= warning_ms:
                expiring_soon.append(token)
            else:
                active.append(token)
        
        report += f"Expired: {len(expired)}\n"
        report += f"Expiring soon (30 days): {len(expiring_soon)}\n"
        report += f"Active: {len(active)}\n"
        report += f"No expiration: {len(no_expiry)}\n\n"
        
        if expiring_soon:
            report += "Tokens expiring soon:\n"
            report += "-" * 70 + "\n"
            for token in expiring_soon:
                days = (token["expiry_time"] - now_ms) / (86400 * 1000)
                report += f"  {token['token_id']}: {token.get('comment', 'N/A')} ({int(days)} days)\n"
        
        return report


# Usage
monitor = TokenExpiryMonitor(
    host="https://<databricks-instance>",
    token=os.environ.get("DATABRICKS_TOKEN")
)

# Check for expiring tokens
expiring = monitor.check_expiring_tokens(warning_days=30)
print(f"Found {len(expiring)} expiring tokens")

# Send alert if tokens are expiring
if expiring:
    monitor.send_alert(expiring, "admin@example.com")

# Generate report
report = monitor.generate_report()
print(report)
```

---

## Error Handling

### Common Error Codes

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | `INVALID_PARAMETER_VALUE` | Invalid lifetime_seconds value |
| 400 | `MAX_TOKEN_LIFETIME_EXCEEDED` | Token lifetime exceeds maximum allowed |
| 404 | `RESOURCE_DOES_NOT_EXIST` | Token ID not found |
| 403 | `PERMISSION_DENIED` | Insufficient permissions |
| 409 | `QUOTA_EXCEEDED` | Maximum number of tokens reached |

### Error Handling Example

```python
import requests
from requests.exceptions import RequestException

def create_token_safely(host: str, token: str, comment: str, lifetime_days: int = 90):
    """Create token with comprehensive error handling"""
    
    url = f"{host}/api/2.0/token/create"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "lifetime_seconds": lifetime_days * 86400,
        "comment": comment
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        print(f"Token created successfully: {result['token_info']['token_id']}")
        return result
        
    except RequestException as e:
        if e.response is not None:
            error_data = e.response.json()
            error_code = error_data.get("error_code")
            
            if error_code == "QUOTA_EXCEEDED":
                print("Error: Maximum number of tokens reached")
                print("Please revoke unused tokens and try again")
            elif error_code == "MAX_TOKEN_LIFETIME_EXCEEDED":
                print(f"Error: Requested lifetime ({lifetime_days} days) exceeds maximum")
                print("Try reducing the lifetime_days parameter")
            elif error_code == "INVALID_PARAMETER_VALUE":
                print("Error: Invalid parameter value")
            else:
                print(f"Error: {error_data.get('message')}")
        else:
            print(f"Network error: {str(e)}")
        
        return None
```

---

## Security Best Practices

### 1. Secure Token Storage

```python
import os
import keyring
from cryptography.fernet import Fernet

# Use environment variables (recommended)
token = os.environ.get("DATABRICKS_TOKEN")

# Use system keyring
keyring.set_password("databricks", "token", token_value)
token = keyring.get_password("databricks", "token")

# Encrypt tokens in configuration files
def encrypt_token(token: str, key: bytes) -> bytes:
    """Encrypt token for storage"""
    f = Fernet(key)
    return f.encrypt(token.encode())

def decrypt_token(encrypted: bytes, key: bytes) -> str:
    """Decrypt token from storage"""
    f = Fernet(key)
    return f.decrypt(encrypted).decode()
```

### 2. Token Validation

```python
def validate_token(host: str, token: str) -> bool:
    """Validate that a token is active and working"""
    url = f"{host}/api/2.0/token/list"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        return response.status_code == 200
    except:
        return False
```

### 3. Principle of Least Privilege

```python
# Create tokens with limited lifetime
short_lived_token = create_token(
    comment="Temporary analysis token",
    lifetime_days=1  # Expires in 24 hours
)

# Use service principals for production
# Service principals provide better audit trails and access control
```

---

## Related APIs

- [Permissions API](./permissions.md) - Manage token permissions
- [Workspace API](./workspace.md) - Use tokens to access workspace
- [Clusters API](./clusters.md) - Use tokens to manage clusters
- [Jobs API](./jobs.md) - Use tokens to run jobs

---

## Additional Resources

- [Databricks Authentication Documentation](https://docs.databricks.com/dev-tools/auth.html)
- [Token Management Best Practices](https://docs.databricks.com/administration-guide/access-control/tokens.html)
- [Service Principal Authentication](https://docs.databricks.com/administration-guide/users-groups/service-principals.html)