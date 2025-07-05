# DegenDigest Logging System Documentation

## Overview

The DegenDigest logging system provides comprehensive, enterprise-grade logging capabilities with structured data, multiple output formats, and advanced monitoring features. This system is designed to handle high-volume logging requirements while maintaining performance and providing detailed insights into system behavior.

## Architecture

### Logging Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Application   │    │  Enterprise     │    │   Output        │
│   Code          │───▶│  Logger         │───▶│   Handlers      │
│                 │    │                 │    │                 │
│ • Crawlers      │    │ • Context       │    │ • Console       │
│ • Processors    │    │ • Performance   │    │ • File          │
│ • APIs          │    │ • Security      │    │ • JSON          │
│ • Dashboards    │    │ • Business      │    │ • Cloud         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Features

- **Structured Logging**: JSON-formatted logs with consistent schema
- **Context Management**: Request-level context tracking
- **Performance Monitoring**: Built-in performance metrics
- **Multiple Outputs**: Console, file, JSON, and cloud logging
- **Log Rotation**: Automatic log file rotation and compression
- **Security Logging**: Dedicated security event logging
- **Business Metrics**: Business event and metric tracking

## Usage

### Basic Logging

```python
from utils.enterprise_logging import get_logger

# Get logger instance
logger = get_logger("my_service")

# Basic logging
logger.info("Service started", service_name="my_service")
logger.warning("High memory usage detected", memory_usage=85.5)
logger.error("Database connection failed", error_code="DB_001")
logger.critical("System shutdown required", reason="critical_error")
```

### Context Management

```python
from utils.enterprise_logging import get_logger, LogContext

logger = get_logger("api_service")

# Set context for request
context = LogContext(
    service_name="api_service",
    operation="user_login",
    request_id="req_123",
    user_id="user_456",
    source_ip="192.168.1.1"
)
logger.set_context(context)

# Log with context
logger.info("User login attempt", username="john_doe")

# Clear context when done
logger.clear_context()
```

### Operation Context Manager

```python
from utils.enterprise_logging import get_logger

logger = get_logger("data_processor")

# Use context manager for automatic timing and error handling
with logger.operation_context("data_processing", request_id="req_123") as context:
    # Process data
    data = process_large_dataset()

    # Add custom metadata
    context.metadata = {"records_processed": len(data)}

    # Log performance
    logger.log_performance("data_processing", 1500.5, records=len(data))
```

### Performance Logging

```python
import time
from utils.enterprise_logging import get_logger

logger = get_logger("api_service")

def api_call():
    start_time = time.time()

    try:
        # Make API call
        response = make_external_api_call()

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Log performance
        logger.log_performance("external_api_call", duration_ms,
                             status_code=response.status_code)

        return response

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.log_performance("external_api_call", duration_ms,
                             error=str(e), success=False)
        raise
```

### API Call Logging

```python
from utils.enterprise_logging import get_logger

logger = get_logger("http_client")

def make_request(method, url, data=None):
    start_time = time.time()

    try:
        response = requests.request(method, url, json=data)
        duration_ms = (time.time() - start_time) * 1000

        logger.log_api_call(
            method=method,
            url=url,
            status_code=response.status_code,
            duration_ms=duration_ms,
            request_size=len(str(data)) if data else 0,
            response_size=len(response.content)
        )

        return response

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.log_api_call(
            method=method,
            url=url,
            status_code=0,
            duration_ms=duration_ms,
            error=str(e)
        )
        raise
```

### Security Event Logging

```python
from utils.enterprise_logging import get_logger

logger = get_logger("auth_service")

def log_login_attempt(username, success, ip_address, details=None):
    severity = "high" if not success else "low"

    logger.log_security_event(
        event_type="login_attempt",
        severity=severity,
        user_id=username,
        ip_address=ip_address,
        details={
            "success": success,
            "user_agent": details.get("user_agent"),
            "location": details.get("location")
        }
    )

def log_suspicious_activity(activity_type, user_id, ip_address, details):
    logger.log_security_event(
        event_type="suspicious_activity",
        severity="critical",
        user_id=user_id,
        ip_address=ip_address,
        details=details
    )
```

### Data Operation Logging

```python
from utils.enterprise_logging import get_logger

logger = get_logger("database_service")

def insert_records(table, records):
    start_time = time.time()

    try:
        # Insert records
        result = database.insert_many(table, records)
        duration_ms = (time.time() - start_time) * 1000

        logger.log_data_operation(
            operation="insert",
            table=table,
            record_count=len(records),
            duration_ms=duration_ms,
            success=True
        )

        return result

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000

        logger.log_data_operation(
            operation="insert",
            table=table,
            record_count=len(records),
            duration_ms=duration_ms,
            success=False,
            error=str(e)
        )
        raise
```

## Configuration

### Logger Initialization

```python
from utils.enterprise_logging import EnterpriseLogger

# Create logger with custom configuration
logger = EnterpriseLogger(
    service_name="my_service",
    log_level="INFO",
    log_dir="logs",
    max_file_size=10 * 1024 * 1024,  # 10MB
    backup_count=5,
    enable_console=True,
    enable_file=True,
    enable_json=True,
    enable_cloud_logging=False
)
```

### Environment Variables

```bash
# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_DIR=logs
LOG_MAX_SIZE_MB=10
LOG_BACKUP_COUNT=5

# Enable/Disable Features
ENABLE_CONSOLE_LOGGING=true
ENABLE_FILE_LOGGING=true
ENABLE_JSON_LOGGING=true
ENABLE_CLOUD_LOGGING=false

# Performance Monitoring
ENABLE_PERFORMANCE_LOGGING=true
PERFORMANCE_THRESHOLD_MS=1000

# Security Logging
ENABLE_SECURITY_LOGGING=true
SECURITY_LOG_LEVEL=WARNING
```

### Configuration File

```yaml
# config/logging_config.yaml
logging:
  level: INFO
  format: json
  directory: logs
  max_file_size_mb: 10
  backup_count: 5

  handlers:
    console:
      enabled: true
      level: INFO

    file:
      enabled: true
      level: DEBUG
      rotation: true

    json:
      enabled: true
      level: INFO

    cloud:
      enabled: false
      level: ERROR

  performance:
    enabled: true
    threshold_ms: 1000
    track_operations: true

  security:
    enabled: true
    level: WARNING
    track_events: true

  context:
    enabled: true
    track_request_id: true
    track_user_id: true
    track_session_id: true
```

## Log Formats

### Console Format

```
2024-01-01 12:00:00 | INFO     | degen_digest.my_service | Service started
2024-01-01 12:00:01 | WARNING  | degen_digest.my_service | High memory usage: 85.5%
2024-01-01 12:00:02 | ERROR    | degen_digest.my_service | Database connection failed
```

### JSON Format

```json
{
  "timestamp": "2024-01-01T12:00:00.000Z",
  "level": "INFO",
  "logger": "degen_digest.my_service",
  "message": "Service started",
  "module": "main",
  "function": "start_service",
  "line": 25,
  "service_name": "my_service",
  "operation": "service_startup",
  "request_id": "req_123",
  "user_id": "user_456",
  "metadata": {
    "version": "1.0.0",
    "environment": "production"
  }
}
```

### Performance Log Format

```
PERF | data_processing took 1500.50ms (records: 1000, success: true)
PERF | api_call took 250.30ms (status_code: 200, url: /api/data)
PERF | database_query took 45.20ms (table: users, operation: select)
```

## Log Analysis

### Performance Analysis

```python
from utils.enterprise_logging import get_logger

logger = get_logger("analytics")

# Get performance summary
summary = logger.get_performance_summary()

for operation, metrics in summary.items():
    print(f"Operation: {operation}")
    print(f"  Count: {metrics['count']}")
    print(f"  Average: {metrics['avg_duration_ms']:.2f}ms")
    print(f"  Min: {metrics['min_duration_ms']:.2f}ms")
    print(f"  Max: {metrics['max_duration_ms']:.2f}ms")
    print(f"  Total: {metrics['total_duration_ms']:.2f}ms")
```

### Log Export

```python
from utils.enterprise_logging import get_logger

logger = get_logger("export")

# Export all logs
logger.export_logs("exported_logs.txt", log_type="all")

# Export specific log types
logger.export_logs("errors_only.txt", log_type="errors")
logger.export_logs("performance_only.txt", log_type="performance")
logger.export_logs("structured_only.txt", log_type="json")
```

### Log Parsing

```python
import json
from pathlib import Path

def parse_json_logs(log_file):
    """Parse JSON-formatted logs for analysis"""
    logs = []

    with open(log_file, 'r') as f:
        for line in f:
            try:
                log_entry = json.loads(line.strip())
                logs.append(log_entry)
            except json.JSONDecodeError:
                continue

    return logs

def analyze_logs(logs):
    """Analyze logs for patterns and insights"""
    # Count by level
    level_counts = {}
    for log in logs:
        level = log.get('level', 'UNKNOWN')
        level_counts[level] = level_counts.get(level, 0) + 1

    # Find errors
    errors = [log for log in logs if log.get('level') == 'ERROR']

    # Performance analysis
    perf_logs = [log for log in logs if log.get('performance')]

    return {
        'total_logs': len(logs),
        'level_counts': level_counts,
        'error_count': len(errors),
        'performance_count': len(perf_logs)
    }
```

## Monitoring and Alerting

### Health Checks

```python
from utils.enterprise_logging import get_logger

logger = get_logger("health_monitor")

def check_logging_health():
    """Check logging system health"""
    try:
        # Test basic logging
        logger.info("Health check: logging system operational")

        # Check log file accessibility
        log_dir = Path("logs")
        if not log_dir.exists():
            logger.error("Log directory not found")
            return False

        # Check disk space
        disk_usage = log_dir.stat().st_size
        if disk_usage > 1024 * 1024 * 100:  # 100MB
            logger.warning("Log directory size exceeds threshold", size_mb=disk_usage/1024/1024)

        return True

    except Exception as e:
        logger.error("Logging health check failed", error=str(e))
        return False
```

### Alerting Rules

```python
from utils.enterprise_logging import get_logger

logger = get_logger("alerting")

def check_error_threshold():
    """Check if error rate exceeds threshold"""
    # This would typically query a monitoring system
    # For demonstration, we'll use a simple counter

    error_count = get_recent_error_count()
    total_count = get_recent_total_count()

    if total_count > 0:
        error_rate = error_count / total_count

        if error_rate > 0.05:  # 5% threshold
            logger.critical("Error rate exceeds threshold",
                          error_rate=error_rate,
                          threshold=0.05)
            send_alert("High error rate detected")

def check_performance_degradation():
    """Check for performance degradation"""
    recent_performance = get_recent_performance_metrics()

    for operation, metrics in recent_performance.items():
        avg_duration = metrics.get('avg_duration_ms', 0)

        if avg_duration > 1000:  # 1 second threshold
            logger.warning("Performance degradation detected",
                          operation=operation,
                          avg_duration_ms=avg_duration,
                          threshold_ms=1000)
```

## Best Practices

### 1. Log Level Usage

- **DEBUG**: Detailed debugging information
- **INFO**: General operational information
- **WARNING**: Potential issues that don't stop operation
- **ERROR**: Error conditions that affect functionality
- **CRITICAL**: System failures that require immediate attention

### 2. Context Management

```python
# Good: Use context manager for operations
with logger.operation_context("user_registration", user_id=user_id) as context:
    # Registration logic
    user = create_user(user_data)
    context.metadata = {"user_id": user.id}

# Bad: Manual context management
logger.set_context(context)
try:
    # Logic
    pass
finally:
    logger.clear_context()
```

### 3. Performance Logging

```python
# Good: Log performance with meaningful metrics
logger.log_performance("data_processing", duration_ms,
                      records_processed=len(data),
                      success_rate=success_count/total_count)

# Bad: Just logging duration
logger.info(f"Processing took {duration_ms}ms")
```

### 4. Error Logging

```python
# Good: Include context and error details
try:
    result = risky_operation()
except DatabaseError as e:
    logger.error("Database operation failed",
                operation="user_query",
                user_id=user_id,
                error_code=e.code,
                error_message=str(e),
                exc_info=True)

# Bad: Generic error logging
except Exception as e:
    logger.error("Something went wrong")
```

### 5. Security Logging

```python
# Good: Comprehensive security event logging
logger.log_security_event(
    event_type="authentication_failure",
    severity="high",
    user_id=username,
    ip_address=client_ip,
    details={
        "attempt_count": failed_attempts,
        "user_agent": request.headers.get("User-Agent"),
        "location": get_location_from_ip(client_ip)
    }
)

# Bad: Basic security logging
logger.warning(f"Failed login attempt for {username}")
```

## Troubleshooting

### Common Issues

#### 1. High Log Volume

**Symptoms**: Large log files, slow performance
**Solutions**:

- Adjust log levels
- Implement log filtering
- Use log rotation
- Consider log aggregation

#### 2. Missing Context

**Symptoms**: Logs without request/user context
**Solutions**:

- Ensure context is set before logging
- Use context managers
- Check thread-local storage

#### 3. Performance Impact

**Symptoms**: Slow application performance
**Solutions**:

- Use async logging
- Implement log buffering
- Reduce log verbosity
- Use sampling for high-volume operations

### Debugging Commands

```bash
# Check log file sizes
ls -lh logs/

# Search for specific errors
grep "ERROR" logs/*.log

# Analyze performance logs
grep "PERF" logs/performance.log

# Check recent activity
tail -100 logs/main.log

# Monitor log growth
watch -n 5 'ls -lh logs/'
```

---

This documentation provides comprehensive guidance for using the DegenDigest logging system. For specific implementation details, refer to the source code in `utils/enterprise_logging.py`.
