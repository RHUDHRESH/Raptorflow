# Raptorflow Infrastructure

This directory contains the infrastructure components and configurations for the Raptorflow backend system.

## Overview

The infrastructure layer provides:
- **GCP Integration**: Google Cloud Platform services integration
- **Cloud Storage**: File storage and management
- **BigQuery**: Analytics and data warehousing
- **Cloud Tasks**: Background job processing
- **Pub/Sub**: Event messaging and pub/sub
- **Secrets Management**: Secure credential storage
- **Monitoring**: Cloud monitoring and logging
- **Tracing**: Distributed tracing support

## Components

### Cloud Storage (`storage.py`)

Provides integration with Google Cloud Storage for file management:

```python
from infrastructure.storage import CloudStorage

storage = CloudStorage()

# Upload file
await storage.upload_file("bucket", "path/to/file.txt", content, "text/plain")

# Download file
content = await storage.download_file("bucket", "path/to/file.txt")

# Generate signed URL
signed_url = await storage.generate_signed_url("bucket", "path/to/file.txt", expiration=3600)
```

**Features:**
- File upload/download with automatic content type detection
- Signed URL generation for secure access
- Bucket management and configuration
- Error handling and retry logic

### BigQuery (`bigquery.py`)

Provides analytics and data warehousing capabilities:

```python
from infrastructure.bigquery import BigQueryClient

bigquery = BigQueryClient()

# Execute query
results = await bigquery.execute_query("SELECT * FROM table WHERE condition = ?", params)

# Insert rows
await bigquery.insert_rows("dataset.table", rows)

# Create table
await bigquery.create_table_if_not_exists("dataset.table", schema)
```

**Features:**
- Async query execution with parameter binding
- Bulk data insertion
- Table management
- Schema validation
- Query result processing

### Cloud Tasks (`cloud_tasks.py`)

Provides background job scheduling and execution:

```python
from infrastructure.cloud_tasks import CloudTasksClient

tasks = CloudTasksClient()

# Create task
await tasks.create_task(
    queue="default",
    handler_url="https://api.example.com/process",
    payload={"data": "value"},
    delay_seconds=60
)

# Delete task
await tasks.delete_task("projects/project/locations/location/tasks/task-id")
```

**Features:**
- Task creation and management
- Scheduled/delayed execution
- Queue management
- Task monitoring

### Pub/Sub (`pubsub_client.py`)

Provides event messaging and pub/sub capabilities:

```python
from infrastructure.pubsub_client import PubSubClient

pubsub = PubSubClient()

# Publish message
await pubsub.publish("topic-name", {"event": "data"})

# Subscribe to messages
async def message_handler(message):
    print(f"Received: {message}")

await pubsub.subscribe("subscription-name", message_handler)
```

**Features:**
- Message publishing and subscription
- Topic and subscription management
- Message filtering
- Async message handling

### Secrets Manager (`secrets.py`)

Provides secure credential storage and management:

```python
from infrastructure.secrets import SecretsManager

secrets = SecretsManager()

# Store secret
await secrets.set_secret("secret-name", "secret-value")

# Retrieve secret
value = await secrets.get_secret("secret-name")
```

**Features:**
- Secure secret storage
- Version management
- Access control
- Automatic rotation support

## Configuration

### Environment Variables

Required environment variables:

```bash
# GCP Configuration
GCP_PROJECT_ID=your-project-id
GCP_REGION=us-central1
GCP_CREDENTIALS_PATH=path/to/service-account.json

# Storage Buckets
EVIDENCE_BUCKET=raptorflow-evidence
EXPORTS_BUCKET=raptorflow-exports
ASSETS_BUCKET=raptorflow-assets

# BigQuery
BIGQUERY_DATASET=raptorflow_analytics

# Cloud Tasks
CLOUD_TASKS_LOCATION=us-central1

# Pub/Sub
PUBSUB_PROJECT_ID=your-project-id
```

### Service Account Permissions

The service account needs the following IAM roles:

- `roles/storage.admin` - For Cloud Storage access
- `roles/bigquery.admin` - For BigQuery operations
- `roles/cloudtasks.admin` - For Cloud Tasks management
- `roles/pubsub.admin` - For Pub/Sub operations
- `roles/secretmanager.admin` - For Secrets Manager access

## Usage Examples

### File Upload with Metadata

```python
from infrastructure.storage import CloudStorage

storage = CloudStorage()

# Upload with metadata
metadata = {
    "content_type": "application/json",
    "user_id": "user-123",
    "workspace_id": "workspace-456",
    "created_at": "2024-01-01T00:00:00Z"
}

await storage.upload_file(
    bucket="evidence",
    path="documents/file.json",
    content=json.dumps(data),
    content_type="application/json",
    metadata=metadata
)
```

### Analytics Query with Parameters

```python
from infrastructure.bigquery import BigQueryClient

bigquery = BigQueryClient()

# Parameterized query
query = """
SELECT user_id, COUNT(*) as count
FROM `analytics.events`
WHERE event_date >= @start_date
AND event_type = @event_type
GROUP BY user_id
ORDER BY count DESC
"""

params = {
    "start_date": "2024-01-01",
    "event_type": "page_view"
}

results = await bigquery.execute_query(query, params)
```

### Event Publishing

```python
from infrastructure.pubsub_client import PubSubClient
from datetime import datetime

pubsub = PubSubClient()

# Publish structured event
event = {
    "event_id": "evt-123",
    "event_type": "user_action",
    "timestamp": datetime.utcnow().isoformat(),
    "user_id": "user-456",
    "action": "login",
    "metadata": {
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0..."
    }
}

await pubsub.publish("user-events", event)
```

## Monitoring and Logging

### Cloud Monitoring Integration

```python
from infrastructure.monitoring import CloudMonitoring

monitoring = CloudMonitoring()

# Record custom metric
await monitoring.record_metric(
    name="custom_requests_total",
    value=1,
    labels={
        "endpoint": "/api/v1/users",
        "method": "GET",
        "status": "200"
    }
)

# Create alert policy
await monitoring.create_alert_policy(
    name="High Error Rate",
    conditions={
        "metric_type": "cloudmonitoring.googleapis.com/error_count",
        "aggregation": "RATE",
        "threshold_value": 10,
        "duration": "300s"
    }
)
```

### Structured Logging

```python
from infrastructure.logging import CloudLogging

logging = CloudLogging()

# Configure structured logging
logging.configure_logging()

# Log with context
logging.log_with_context(
    level="INFO",
    message="User login successful",
    user_id="user-123",
    ip_address="192.168.1.1",
    request_id="req-456"
)
```

## Error Handling

All infrastructure components include comprehensive error handling:

```python
from infrastructure.storage import CloudStorage
from infrastructure.exceptions import StorageError

storage = CloudStorage()

try:
    await storage.upload_file("bucket", "path", content)
except StorageError as e:
    logger.error(f"Storage operation failed: {e}")
    # Handle error appropriately
```

### Common Error Types

- `StorageError`: Cloud Storage operation failures
- `BigQueryError`: BigQuery query failures
- `TasksError`: Cloud Tasks operation failures
- `PubSubError`: Pub/Sub operation failures
- `SecretsError`: Secrets Manager operation failures

## Testing

### Mock Services for Testing

```python
from infrastructure.storage import CloudStorage
from infrastructure.testing import MockCloudStorage

# Use mock for testing
storage = MockCloudStorage()

# Mock returns predictable data
content = await storage.download_file("bucket", "path")
assert content == b"mock content"
```

### Integration Tests

```python
import pytest
from infrastructure.storage import CloudStorage

@pytest.mark.asyncio
async def test_storage_upload_download():
    storage = CloudStorage()

    # Test upload
    await storage.upload_file("test-bucket", "test-file.txt", b"test content")

    # Test download
    content = await storage.download_file("test-bucket", "test-file.txt")
    assert content == b"test content"
```

## Deployment

### Terraform Configuration

Infrastructure is managed through Terraform:

```hcl
# gcp/terraform/main.tf
resource "google_storage_bucket" "evidence_bucket" {
  name     = "raptorflow-evidence"
  location = var.region
}

resource "google_bigquery_dataset" "analytics" {
  dataset_id = "raptorflow_analytics"
  location   = var.region
}
```

### Environment-Specific Configurations

- **Development**: Uses development buckets and datasets
- **Staging**: Uses staging environment with test data
- **Production**: Uses production resources with proper access controls

## Security

### Access Control

- Service accounts with least privilege principle
- IAM roles scoped to specific resources
- VPC Service Connector for private connectivity

### Data Protection

- Encryption at rest and in transit
- Access logging and audit trails
- Data retention policies

## Performance

### Optimization Tips

1. **Batch Operations**: Use bulk operations for BigQuery
2. **Caching**: Cache frequently accessed data
3. **Connection Pooling**: Reuse connections where possible
4. **Async Operations**: Use async/await for I/O operations

### Monitoring

- Monitor API call latency and error rates
- Track resource usage and costs
- Set up alerts for critical failures

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Check service account permissions
2. **Quota Exceeded**: Monitor API usage and limits
3. **Network Issues**: Check VPC configuration
4. **Data Format**: Validate data formats before operations

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

When adding new infrastructure components:

1. Follow the existing code structure
2. Include comprehensive error handling
3. Add unit tests and integration tests
4. Update documentation
5. Consider security implications

## Support

For infrastructure-related issues:
1. Check the logs in Cloud Console
2. Verify IAM permissions
3. Review quota and usage limits
4. Consult the GCP documentation

For code-related issues:
1. Check the error messages and logs
2. Review the documentation
3. Create an issue with detailed reproduction steps
4. Include relevant configuration details
