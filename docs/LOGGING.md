# Enterprise Logging System

This document provides comprehensive documentation for the Degen Digest enterprise logging system.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Setup and Configuration](#setup-and-configuration)
- [Usage Patterns](#usage-patterns)
- [Log Categories](#log-categories)
- [Monitoring and Alerting](#monitoring-and-alerting)
- [Performance Considerations](#performance-considerations)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Overview

The Degen Digest platform uses an enterprise-grade structured logging system that provides:

- **Structured JSON Logging** - Machine-readable logs for analysis
- **Log Rotation** - Automatic log rotation and archival
- **Performance Monitoring** - Request timing and resource usage
- **Error Tracking** - Comprehensive error tracking and alerting
- **Audit Logging** - Security and compliance audit trails
- **Business Metrics** - Key business metrics and KPIs
- **Request Correlation** - End-to-end request tracing
- **Context Management** - Thread-local context for correlation

## Architecture

### Logging Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Application   │───▶│  Enterprise     │───▶│   Log Outputs   │
│     Code        │    │   Logger        │    │                 │
└─────────────────┘    └─────────────────┘    │ • Console       │
                                              │ • Files         │
                                              │ • Cloud Logging │
                                              │ • External APIs │
                                              └─────────────────┘
```

### Components

1. **EnterpriseLogger** - Main logging class with enterprise features
2. **Log Formatters** - JSON and console formatters
3. **Log Handlers** - File and console handlers with rotation
4. **Context Management** - Thread-local storage for request context
5. **Performance Tracking** - Built-in performance monitoring
6. **Error Tracking** - Comprehensive error tracking and alerting

## Setup and Configuration

### Environment Variables

```bash
# Core logging configuration
LOG_LEVEL=INFO                    # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_FORMAT=json                   # Log format (json, console)
LOG_FILE=logs/degen_digest.log    # Log file path
LOG_MAX_SIZE_MB=100              # Maximum log file size in MB
LOG_BACKUP_COUNT=5               # Number of backup files to keep

# Feature toggles
ENABLE_CLOUD_LOGGING=true        # Enable cloud logging integration
ENABLE_AUDIT_LOGGING=true        # Enable audit logging
ENABLE_PERFORMANCE_LOGGING=true  # Enable performance monitoring
ENABLE_SECURITY_LOGGING=true     # Enable security event logging
ENABLE_BUSINESS_LOGGING=true     # Enable business metrics logging
ENABLE_DATA_QUALITY_LOGGING=true # Enable data quality monitoring
ENABLE_API_LOGGING=true          # Enable API call logging
ENABLE_DATABASE_LOGGING=true     # Enable database operation logging
ENABLE_CRAWLER_LOGGING=true      # Enable crawler operation logging
ENABLE_DASHBOARD_LOGGING=true    # Enable dashboard interaction logging
```

### Python Configuration

```python
from utils.enterprise_logging import initialize_logging, get_logger

# Initialize the logging system
logger = initialize_logging({
    'level': 'INFO',
    'format': 'json',
    'file_path': 'logs/degen_digest.log',
    'max_size': 100 * 1024 * 1024,  # 100MB
    'backup_count': 5
})

# Get a logger for your module
logger = get_logger('your_module_name')
```

### Log Levels

| Level        | Description                    | Usage                           |
| ------------ | ------------------------------ | ------------------------------- |
| **DEBUG**    | Detailed debugging information | Development and troubleshooting |
| **INFO**     | General operational messages   | Normal operation tracking       |
| **WARNING**  | Warning conditions             | Potential issues                |
| **ERROR**    | Error conditions               | Failed operations               |
| **CRITICAL** | Critical system failures       | System outages                  |

## Usage Patterns

### Basic Logging

```python
from utils.enterprise_logging import get_logger

logger = get_logger('my_module')

# Basic logging
logger.info("Application started")
logger.warning("Rate limit approaching")
logger.error("Database connection failed", error=str(e))
logger.critical("System shutdown required")
```

### Structured Logging with Context

```python
# Log with additional context
logger.info("User login successful",
           user_id="user123",
           ip_address="192.168.1.1",
           user_agent="Mozilla/5.0...",
           login_method="oauth")

# Log with performance metrics
logger.info("API request completed",
           endpoint="/api/digest",
           method="GET",
           status_code=200,
           response_time_ms=150,
           request_size_bytes=1024)
```

### Request Context Management

```python
from utils.enterprise_logging import get_logger

logger = get_logger('api')

# Set request context for correlation
logger.set_request_context(
    request_id="req_12345",
    user_id="user123",
    session_id="sess_67890",
    ip_address="192.168.1.1",
    user_agent="Mozilla/5.0..."
)

# All subsequent logs will include request context
logger.info("Processing request")
logger.info("Database query executed")
logger.info("Response sent")

# Clear context when done
logger.clear_request_context()
```

### Performance Monitoring

```python
from utils.enterprise_logging import get_logger

logger = get_logger('performance')

# Using performance timer context manager
with logger.performance_timer("database_query", table="users"):
    # Database operation
    result = database.query("SELECT * FROM users")

# Performance metrics are automatically tracked
```

### Error Tracking

```python
from utils.enterprise_logging import get_logger, log_error_with_context

logger = get_logger('error_handler')

try:
    # Some operation that might fail
    result = risky_operation()
except Exception as e:
    # Log error with context
    log_error_with_context(
        error=e,
        context={
            'operation': 'risky_operation',
            'user_id': 'user123',
            'input_data': {'key': 'value'}
        },
        logger_name='error_handler'
    )
    raise
```

## Log Categories

### 1. Application Logs

```python
# Main application logs
logger = get_logger('main')
logger.info("Application started", version="2.0.0", environment="production")
logger.info("Configuration loaded", config_keys=list(config.keys()))
logger.info("Application shutting down", uptime_seconds=3600)
```

### 2. API Logs

```python
# API request/response logs
logger = get_logger('api')
logger.api_log(
    method="POST",
    endpoint="/api/digest",
    status_code=200,
    response_time=0.25,
    user_id="user123",
    request_size=1024
)
```

### 3. Database Logs

```python
# Database operation logs
logger = get_logger('database')
logger.database_log(
    operation="SELECT",
    table="tweets",
    duration=0.05,
    rows_returned=100,
    query_hash="abc123"
)
```

### 4. Crawler Logs

```python
# Crawler operation logs
logger = get_logger('crawler')
logger.crawler_log(
    source="twitter",
    action="login",
    username="gorebroai",
    success=True,
    duration_seconds=2.5
)
```

### 5. Dashboard Logs

```python
# Dashboard interaction logs
logger = get_logger('dashboard')
logger.dashboard_log(
    action="page_view",
    page="analytics",
    user_id="user123",
    session_duration=300
)
```

### 6. Audit Logs

```python
# Security audit logs
logger = get_logger('audit')
logger.audit_log(
    event="user_login",
    user_id="user123",
    ip_address="192.168.1.1",
    success=True,
    login_method="password"
)
```

### 7. Security Logs

```python
# Security event logs
logger = get_logger('security')
logger.security_log(
    event="failed_login_attempt",
    severity="warning",
    ip_address="192.168.1.1",
    username="user123",
    attempt_count=3
)
```

### 8. Business Logs

```python
# Business metrics logs
logger = get_logger('business')
logger.business_log(
    event="digest_generated",
    digest_date="2025-07-03",
    content_count=150,
    source_count=4,
    generation_time_seconds=30
)
```

### 9. Data Quality Logs

```python
# Data quality issue logs
logger = get_logger('data_quality')
logger.data_quality_log(
    issue="missing_required_field",
    data_source="twitter",
    field_name="user_id",
    record_count=5,
    severity="warning"
)
```

## Decorators

### Function Call Logging

```python
from utils.enterprise_logging import log_function_call

@log_function_call()
def process_data(data):
    # Function implementation
    return processed_data
```

### Database Operation Logging

```python
from utils.enterprise_logging import log_database_operation

@log_database_operation()
def save_tweet(tweet_data, table="tweets"):
    # Database operation
    return result
```

### API Call Logging

```python
from utils.enterprise_logging import log_api_call

@log_api_call()
def call_external_api(endpoint="/api/data", method="GET"):
    # API call implementation
    return response
```

### Performance Monitoring

```python
from utils.enterprise_logging import log_performance_metrics

@log_performance_metrics()
def expensive_operation():
    # Expensive operation
    return result
```

### Security Event Logging

```python
from utils.enterprise_logging import log_security_event

@log_security_event()
def authenticate_user(username, password):
    # Authentication logic
    return auth_result
```

## Monitoring and Alerting

### Log Analysis

```python
# Get metrics summary
logger = get_logger('monitoring')
metrics = logger.get_metrics_summary()

print(f"Performance metrics: {metrics['performance_metrics']}")
print(f"Error counts: {metrics['error_counts']}")
print(f"Audit events: {metrics['audit_events_count']}")
```

### Error Rate Monitoring

```python
# Monitor error rates
error_counts = logger.error_counts
for error_key, error_info in error_counts.items():
    if error_info['count'] > 10:  # Alert threshold
        logger.warning(f"High error rate for {error_key}",
                      count=error_info['count'],
                      first_occurrence=error_info['first_occurrence'])
```

### Performance Monitoring

```python
# Monitor performance metrics
performance_metrics = logger.performance_metrics
for operation, metrics in performance_metrics.items():
    if metrics['avg_duration'] > 1.0:  # Alert threshold
        logger.warning(f"Slow operation: {operation}",
                      avg_duration=metrics['avg_duration'],
                      count=metrics['count'])
```

### Health Checks

```python
from utils.enterprise_logging import log_system_health

@log_system_health()
def check_database_connection():
    # Database health check
    return {"status": "healthy", "response_time": 0.05}

@log_system_health()
def check_api_endpoints():
    # API health check
    return {"status": "healthy", "endpoints": ["/health", "/status"]}
```

## Performance Considerations

### Log Volume Management

```python
# Use appropriate log levels
logger.debug("Detailed debug info")  # Only in development
logger.info("Normal operation")      # Production logging
logger.warning("Potential issues")   # Monitor closely
logger.error("Actual problems")      # Alert immediately
```

### Structured Data

```python
# Good: Structured data
logger.info("User action",
           action="login",
           user_id="user123",
           timestamp="2025-07-03T10:30:00Z")

# Bad: Unstructured text
logger.info("User user123 logged in at 2025-07-03T10:30:00Z")
```

### Context Management

```python
# Set context once at request start
logger.set_request_context(request_id="req_123", user_id="user123")

# Use context throughout request
logger.info("Processing step 1")
logger.info("Processing step 2")
logger.info("Processing step 3")

# Clear context at request end
logger.clear_request_context()
```

## Troubleshooting

### Common Issues

1. **Logs Not Appearing**

   ```python
   # Check log level
   logger.debug("This won't appear if level is INFO")

   # Check log file permissions
   import os
   os.access('logs/degen_digest.log', os.W_OK)
   ```

2. **Performance Impact**

   ```python
   # Use lazy evaluation for expensive operations
   logger.debug("Expensive data", data=expensive_operation())  # Bad
   logger.debug("Expensive data", data=lambda: expensive_operation())  # Good
   ```

3. **Memory Leaks**
   ```python
   # Clear context after each request
   try:
       logger.set_request_context(request_id="req_123")
       # Process request
   finally:
       logger.clear_request_context()
   ```

### Debug Mode

```python
# Enable debug logging
import os
os.environ['LOG_LEVEL'] = 'DEBUG'
os.environ['LOG_FORMAT'] = 'console'

# Reinitialize logging
from utils.enterprise_logging import initialize_logging
initialize_logging()
```

### Log Analysis Tools

```bash
# View recent logs
tail -f logs/degen_digest.log

# Search for errors
grep "ERROR" logs/degen_digest.log

# Count log entries by level
grep -o '"level":"[^"]*"' logs/degen_digest.log | sort | uniq -c

# Extract performance metrics
grep "performance_timer" logs/degen_digest.log | jq '.duration_seconds'
```

## Best Practices

### 1. Use Appropriate Log Levels

```python
# DEBUG: Detailed debugging information
logger.debug("Variable value", variable_name="user_id", value=user_id)

# INFO: General operational messages
logger.info("User logged in", user_id=user_id, method="oauth")

# WARNING: Warning conditions
logger.warning("Rate limit approaching", remaining_requests=10)

# ERROR: Error conditions
logger.error("Database connection failed", error=str(e), retry_count=3)

# CRITICAL: Critical system failures
logger.critical("System shutdown required", reason="memory_exhaustion")
```

### 2. Include Relevant Context

```python
# Good: Include relevant context
logger.error("API call failed",
            endpoint="/api/data",
            method="GET",
            status_code=500,
            user_id=user_id,
            request_id=request_id)

# Bad: Missing context
logger.error("API call failed")
```

### 3. Use Structured Data

```python
# Good: Structured data
logger.info("Data processed",
           record_count=1000,
           processing_time_ms=1500,
           success_count=995,
           error_count=5)

# Bad: Unstructured text
logger.info("Processed 1000 records in 1.5 seconds with 5 errors")
```

### 4. Handle Sensitive Data

```python
# Good: Mask sensitive data
logger.info("User login",
           user_id=user_id,
           ip_address=ip_address,
           password="***")  # Masked

# Bad: Log sensitive data
logger.info("User login", password=password)  # Never do this
```

### 5. Use Request Correlation

```python
# Set correlation ID at request start
request_id = str(uuid.uuid4())
logger.set_request_context(request_id=request_id, user_id=user_id)

# All logs in this request will include the correlation ID
logger.info("Processing request")
logger.info("Database query")
logger.info("Response sent")

# Clear context at request end
logger.clear_request_context()
```

### 6. Monitor Log Volume

```python
# Use sampling for high-volume operations
import random

def log_high_volume_operation(operation_data):
    if random.random() < 0.01:  # Log 1% of operations
        logger.info("High volume operation", data=operation_data)
```

### 7. Performance Monitoring

```python
# Use performance timers for expensive operations
with logger.performance_timer("expensive_operation"):
    result = expensive_operation()

# Monitor specific metrics
logger.info("Batch processing completed",
           batch_size=len(batch),
           processing_time_ms=processing_time * 1000,
           memory_usage_mb=memory_usage)
```

### 8. Error Handling

```python
# Log errors with full context
try:
    result = risky_operation()
except Exception as e:
    logger.error("Operation failed",
                operation="risky_operation",
                error=str(e),
                error_type=type(e).__name__,
                traceback=traceback.format_exc(),
                context={"user_id": user_id, "data": data})
    raise
```

## Integration with External Systems

### Cloud Logging

```python
# Google Cloud Logging integration
import google.cloud.logging

client = google.cloud.logging.Client()
client.setup_logging()

# Logs will be sent to Google Cloud Logging
logger.info("Cloud logging test")
```

### Log Aggregation

```python
# Send logs to external aggregation service
import requests

def send_to_aggregator(log_entry):
    requests.post("https://log-aggregator.com/logs", json=log_entry)

# Custom handler for external aggregation
class ExternalHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        send_to_aggregator(log_entry)
```

### Monitoring Dashboards

```python
# Export metrics for monitoring dashboards
def export_metrics():
    logger = get_logger('monitoring')
    metrics = logger.get_metrics_summary()

    # Send to monitoring system
    requests.post("https://monitoring.com/metrics", json=metrics)
```

This comprehensive logging system provides enterprise-grade monitoring, debugging, and compliance capabilities for the Degen Digest platform.
