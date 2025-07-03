# Monitoring Guide

This document provides comprehensive monitoring, logging, and alerting information for the Degen Digest platform.

## Table of Contents

- [Logging System](#logging-system)
- [Metrics Collection](#metrics-collection)
- [Health Checks](#health-checks)
- [Alerting](#alerting)
- [Troubleshooting](#troubleshooting)
- [Performance Monitoring](#performance-monitoring)
- [Security Monitoring](#security-monitoring)

## Logging System

### Logging Architecture

The system uses a structured logging approach with multiple levels and outputs:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Application   │───▶│  Log Processor  │───▶│   Log Outputs   │
│     Logs        │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    │ • Console       │
                                              │ • Files         │
                                              │ • Cloud Logging │
                                              │ • External APIs │
                                              └─────────────────┘
```

### Log Levels

| Level        | Description                    | Usage                           |
| ------------ | ------------------------------ | ------------------------------- |
| **DEBUG**    | Detailed debugging information | Development and troubleshooting |
| **INFO**     | General operational messages   | Normal operation tracking       |
| **WARNING**  | Warning conditions             | Potential issues                |
| **ERROR**    | Error conditions               | Failed operations               |
| **CRITICAL** | Critical system failures       | System outages                  |

### Structured Logging

The system uses structured logging with consistent fields:

```python
# Example structured log entry
{
    "timestamp": "2025-07-03T14:30:00Z",
    "level": "INFO",
    "logger": "crawler.twitter",
    "message": "Crawl session completed",
    "crawl_id": "crawl_20250703_143000",
    "tweets_collected": 45,
    "duration_seconds": 180,
    "success": true,
    "errors": [],
    "metadata": {
        "source": "twitter",
        "session_id": "sess_12345",
        "user_agent": "DegenDigest/2.0"
    }
}
```

### Logging Configuration

#### Environment Variables

```bash
# Logging configuration
LOG_LEVEL=INFO
LOG_FORMAT=json  # or console
LOG_FILE=logs/degen_digest.log
LOG_MAX_SIZE=100MB
LOG_BACKUP_COUNT=5
```

#### Python Configuration

```python
# utils/advanced_logging.py
import logging
import structlog
from pathlib import Path

def configure_logging(level: str = "INFO", format: str = "json"):
    """Configure structured logging"""

    # Create logs directory
    Path("logs").mkdir(exist_ok=True)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if format == "json"
            else structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(message)s",
        handlers=[
            logging.FileHandler("logs/degen_digest.log"),
            logging.StreamHandler()
        ]
    )
```

### Log Categories

#### 1. Application Logs

```python
# Main application logs
logger = get_logger("main")
logger.info("Application started", version="2.0.0", environment="production")
logger.error("Database connection failed", error=str(e), retry_count=3)
```

#### 2. Crawler Logs

```python
# Crawler-specific logs
logger = get_logger("crawler.twitter")
logger.info("Starting Twitter crawl",
           username="gorebroai",
           max_tweets=100,
           session_id="sess_12345")
logger.warning("Rate limit approaching",
              requests_remaining=10,
              reset_time="2025-07-03T15:00:00Z")
```

#### 3. Data Processing Logs

```python
# Data processing logs
logger = get_logger("processor.analyzer")
logger.info("Processing batch",
           batch_size=1000,
           source="twitter",
           processing_time_ms=1500)
logger.error("Processing failed",
            error=str(e),
            batch_id="batch_12345",
            retry_attempt=2)
```

#### 4. API Logs

```python
# API request/response logs
logger = get_logger("api.requests")
logger.info("API request",
           method="POST",
           endpoint="/api/digest",
           status_code=200,
           response_time_ms=250,
           user_agent="DegenDigest/2.0")
```

### Log Rotation

```python
# utils/log_rotation.py
import logging.handlers
from pathlib import Path

def setup_log_rotation(log_file: str = "logs/degen_digest.log"):
    """Setup log rotation with size and time limits"""

    handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=100 * 1024 * 1024,  # 100MB
        backupCount=5
    )

    # Also setup time-based rotation
    time_handler = logging.handlers.TimedRotatingFileHandler(
        log_file,
        when="midnight",
        interval=1,
        backupCount=30
    )

    return handler, time_handler
```

## Metrics Collection

### Key Metrics

#### 1. System Metrics

```python
# utils/metrics.py
import psutil
import time
from typing import Dict, Any

class SystemMetrics:
    """Collect system performance metrics"""

    @staticmethod
    def collect_system_metrics() -> Dict[str, Any]:
        """Collect current system metrics"""
        return {
            "timestamp": time.time(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "network_io": psutil.net_io_counters()._asdict(),
            "load_average": psutil.getloadavg()
        }

    @staticmethod
    def collect_process_metrics() -> Dict[str, Any]:
        """Collect process-specific metrics"""
        process = psutil.Process()
        return {
            "timestamp": time.time(),
            "pid": process.pid,
            "cpu_percent": process.cpu_percent(),
            "memory_percent": process.memory_percent(),
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "num_threads": process.num_threads(),
            "open_files": len(process.open_files()),
            "connections": len(process.connections())
        }
```

#### 2. Business Metrics

```python
# utils/business_metrics.py
class BusinessMetrics:
    """Collect business-specific metrics"""

    @staticmethod
    def collect_crawler_metrics() -> Dict[str, Any]:
        """Collect crawler performance metrics"""
        return {
            "timestamp": time.time(),
            "crawls_completed": get_crawl_count(),
            "tweets_collected": get_tweet_count(),
            "crawl_success_rate": get_success_rate(),
            "average_crawl_time": get_avg_crawl_time(),
            "errors_count": get_error_count(),
            "rate_limit_hits": get_rate_limit_count()
        }

    @staticmethod
    def collect_processing_metrics() -> Dict[str, Any]:
        """Collect data processing metrics"""
        return {
            "timestamp": time.time(),
            "items_processed": get_processed_count(),
            "processing_time_ms": get_processing_time(),
            "quality_score": get_quality_score(),
            "duplicates_removed": get_duplicate_count(),
            "ai_processing_time": get_ai_processing_time()
        }
```

#### 3. API Metrics

```python
# utils/api_metrics.py
class APIMetrics:
    """Collect API performance metrics"""

    @staticmethod
    def collect_api_metrics() -> Dict[str, Any]:
        """Collect API performance metrics"""
        return {
            "timestamp": time.time(),
            "requests_per_minute": get_request_rate(),
            "average_response_time": get_avg_response_time(),
            "error_rate": get_error_rate(),
            "active_connections": get_active_connections(),
            "endpoint_usage": get_endpoint_usage()
        }
```

### Metrics Storage

#### Google Cloud Monitoring

```python
# utils/cloud_metrics.py
from google.cloud import monitoring_v3
from google.cloud.monitoring_v3 import TimeSeries

class CloudMetrics:
    """Send metrics to Google Cloud Monitoring"""

    def __init__(self, project_id: str):
        self.client = monitoring_v3.MetricServiceClient()
        self.project_name = f"projects/{project_id}"

    def write_metric(self, metric_type: str, value: float, labels: Dict[str, str]):
        """Write a metric to Cloud Monitoring"""
        series = TimeSeries()
        series.metric.type = f"custom.googleapis.com/{metric_type}"
        series.resource.type = "global"
        series.resource.labels["project_id"] = self.project_id

        # Add labels
        for key, value in labels.items():
            series.metric.labels[key] = value

        # Add data point
        point = series.points.add()
        point.value.double_value = value
        point.interval.end_time.seconds = int(time.time())

        # Write to Cloud Monitoring
        self.client.create_time_series(self.project_name, [series])
```

#### Local Metrics Storage

```python
# utils/local_metrics.py
import sqlite3
from datetime import datetime

class LocalMetrics:
    """Store metrics locally for analysis"""

    def __init__(self, db_path: str = "logs/metrics.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize metrics database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    labels TEXT,
                    source TEXT
                )
            """)

    def store_metric(self, name: str, value: float, labels: Dict[str, str] = None, source: str = "system"):
        """Store a metric in the local database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO metrics (metric_name, metric_value, labels, source)
                VALUES (?, ?, ?, ?)
            """, (name, value, json.dumps(labels) if labels else None, source))
```

## Health Checks

### Health Check Endpoints

```python
# utils/health_checks.py
from typing import Dict, Any
import requests
import sqlite3

class HealthChecker:
    """Comprehensive health checking system"""

    def __init__(self):
        self.checks = {
            "database": self.check_database,
            "storage": self.check_storage,
            "apis": self.check_external_apis,
            "crawler": self.check_crawler,
            "system": self.check_system_resources
        }

    def check_database(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            start_time = time.time()
            with sqlite3.connect("output/degen_digest.db") as conn:
                conn.execute("SELECT 1")
                response_time = (time.time() - start_time) * 1000

            return {
                "status": "healthy",
                "response_time_ms": response_time,
                "error": None
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "response_time_ms": None,
                "error": str(e)
            }

    def check_storage(self) -> Dict[str, Any]:
        """Check Google Cloud Storage connectivity"""
        try:
            from google.cloud import storage
            client = storage.Client()
            bucket = client.bucket("degen-digest-data")

            # Test write access
            blob = bucket.blob("health_check_test")
            blob.upload_from_string("test")
            blob.delete()

            return {
                "status": "healthy",
                "bucket": "degen-digest-data",
                "error": None
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "bucket": "degen-digest-data",
                "error": str(e)
            }

    def check_external_apis(self) -> Dict[str, Any]:
        """Check external API connectivity"""
        apis = {
            "openrouter": "https://openrouter.ai/api/v1/models",
            "twitter": "https://api.twitter.com/2/tweets",
            "newsapi": "https://newsapi.org/v2/top-headlines"
        }

        results = {}
        for name, url in apis.items():
            try:
                response = requests.get(url, timeout=10)
                results[name] = {
                    "status": "healthy" if response.status_code < 500 else "unhealthy",
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "status_code": response.status_code
                }
            except Exception as e:
                results[name] = {
                    "status": "unhealthy",
                    "response_time_ms": None,
                    "error": str(e)
                }

        return results

    def check_crawler(self) -> Dict[str, Any]:
        """Check crawler service health"""
        try:
            response = requests.get(
                "https://solana-crawler-128671663649.us-central1.run.app/status",
                timeout=10
            )
            data = response.json()

            return {
                "status": "healthy" if data.get("crawler_running") else "stopped",
                "crawler_running": data.get("crawler_running", False),
                "pid": data.get("crawler_pid"),
                "response_time_ms": response.elapsed.total_seconds() * 1000
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        import psutil

        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "load_average": psutil.getloadavg(),
            "status": "healthy" if psutil.cpu_percent() < 80 else "warning"
        }

    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {}
        overall_status = "healthy"

        for check_name, check_func in self.checks.items():
            try:
                results[check_name] = check_func()
                if results[check_name].get("status") == "unhealthy":
                    overall_status = "unhealthy"
            except Exception as e:
                results[check_name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                overall_status = "unhealthy"

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": overall_status,
            "checks": results
        }
```

### Health Check API

```python
# dashboard/health_api.py
from flask import Flask, jsonify
from utils.health_checks import HealthChecker

app = Flask(__name__)
health_checker = HealthChecker()

@app.route('/health')
def health_check():
    """Basic health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    })

@app.route('/health/detailed')
def detailed_health_check():
    """Detailed health check with all components"""
    return jsonify(health_checker.run_all_checks())

@app.route('/health/ready')
def readiness_check():
    """Readiness check for Kubernetes"""
    health = health_checker.run_all_checks()
    if health["overall_status"] == "healthy":
        return jsonify({"status": "ready"}), 200
    else:
        return jsonify({"status": "not ready"}), 503
```

## Alerting

### Alert Configuration

```python
# utils/alerting.py
import smtplib
import requests
from email.mime.text import MIMEText
from typing import Dict, Any, List

class AlertManager:
    """Manage system alerts and notifications"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.alert_history = []

    def send_email_alert(self, subject: str, message: str, recipients: List[str]):
        """Send email alert"""
        if not self.config.get("email", {}).get("enabled"):
            return

        msg = MIMEText(message)
        msg['Subject'] = f"[Degen Digest Alert] {subject}"
        msg['From'] = self.config["email"]["from"]
        msg['To'] = ", ".join(recipients)

        try:
            with smtplib.SMTP(self.config["email"]["smtp_server"],
                            self.config["email"]["smtp_port"]) as server:
                server.starttls()
                server.login(self.config["email"]["username"],
                           self.config["email"]["password"])
                server.send_message(msg)

            self.log_alert("email", subject, "sent")
        except Exception as e:
            self.log_alert("email", subject, f"failed: {str(e)}")

    def send_slack_alert(self, message: str, channel: str = "#alerts"):
        """Send Slack alert"""
        if not self.config.get("slack", {}).get("enabled"):
            return

        payload = {
            "channel": channel,
            "text": message,
            "username": "Degen Digest Bot",
            "icon_emoji": ":warning:"
        }

        try:
            response = requests.post(
                self.config["slack"]["webhook_url"],
                json=payload,
                timeout=10
            )
            response.raise_for_status()

            self.log_alert("slack", message[:50], "sent")
        except Exception as e:
            self.log_alert("slack", message[:50], f"failed: {str(e)}")

    def check_alert_conditions(self, metrics: Dict[str, Any]):
        """Check if alert conditions are met"""
        alerts = []

        # CPU usage alert
        if metrics.get("cpu_percent", 0) > self.config["thresholds"]["cpu"]:
            alerts.append({
                "type": "high_cpu",
                "severity": "warning",
                "message": f"CPU usage is {metrics['cpu_percent']}%"
            })

        # Memory usage alert
        if metrics.get("memory_percent", 0) > self.config["thresholds"]["memory"]:
            alerts.append({
                "type": "high_memory",
                "severity": "warning",
                "message": f"Memory usage is {metrics['memory_percent']}%"
            })

        # Crawler failure alert
        if not metrics.get("crawler_running", True):
            alerts.append({
                "type": "crawler_stopped",
                "severity": "critical",
                "message": "Crawler service has stopped"
            })

        # Database connection alert
        if metrics.get("database_status") == "unhealthy":
            alerts.append({
                "type": "database_error",
                "severity": "critical",
                "message": "Database connection failed"
            })

        return alerts

    def process_alerts(self, alerts: List[Dict[str, Any]]):
        """Process and send alerts"""
        for alert in alerts:
            message = f"[{alert['severity'].upper()}] {alert['message']}"

            if alert["severity"] in ["critical", "error"]:
                self.send_email_alert(alert["type"], message,
                                    self.config["email"]["critical_recipients"])
                self.send_slack_alert(message, "#critical-alerts")
            elif alert["severity"] == "warning":
                self.send_slack_alert(message, "#alerts")

    def log_alert(self, method: str, subject: str, status: str):
        """Log alert delivery status"""
        self.alert_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "method": method,
            "subject": subject,
            "status": status
        })
```

### Alert Rules

```yaml
# config/alert_rules.yaml
alerts:
  system:
    cpu_usage:
      threshold: 80
      severity: warning
      message: "CPU usage is above 80%"

    memory_usage:
      threshold: 85
      severity: warning
      message: "Memory usage is above 85%"

    disk_usage:
      threshold: 90
      severity: critical
      message: "Disk usage is above 90%"

  crawler:
    stopped:
      severity: critical
      message: "Crawler service has stopped"

    high_error_rate:
      threshold: 10
      severity: warning
      message: "Crawler error rate is above 10%"

    slow_response:
      threshold: 300
      severity: warning
      message: "Crawler response time is above 5 minutes"

  database:
    connection_failed:
      severity: critical
      message: "Database connection failed"

    slow_queries:
      threshold: 1000
      severity: warning
      message: "Database queries are taking longer than 1 second"

  api:
    high_error_rate:
      threshold: 5
      severity: warning
      message: "API error rate is above 5%"

    slow_response:
      threshold: 2000
      severity: warning
      message: "API response time is above 2 seconds"
```

## Troubleshooting

### Common Issues

#### 1. Crawler Not Starting

**Symptoms:**

- Crawler status shows "not running"
- No new data being collected
- Error logs in crawler service

**Diagnosis:**

```bash
# Check crawler logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=solana-crawler" --limit=50

# Check crawler status
curl https://solana-crawler-128671663649.us-central1.run.app/status

# Check credentials
echo $TWITTER_USERNAME
echo $TWITTER_PASSWORD
```

**Solutions:**

- Verify Twitter credentials are correct
- Check if Twitter account is locked
- Restart crawler service
- Check network connectivity

#### 2. Database Connection Issues

**Symptoms:**

- Application errors related to database
- Health checks failing
- Data not being saved

**Diagnosis:**

```bash
# Check database file
ls -la output/degen_digest.db

# Check database permissions
sqlite3 output/degen_digest.db "SELECT 1;"

# Check disk space
df -h
```

**Solutions:**

- Verify database file exists and is writable
- Check disk space availability
- Restart application
- Recreate database if corrupted

#### 3. API Rate Limiting

**Symptoms:**

- API calls failing with 429 errors
- Slow response times
- Reduced data collection

**Diagnosis:**

```bash
# Check API logs
grep "429" logs/degen_digest.log

# Check rate limit headers
curl -I https://api.twitter.com/2/tweets
```

**Solutions:**

- Implement exponential backoff
- Reduce request frequency
- Use multiple API keys
- Cache responses

### Debugging Tools

#### 1. Log Analysis

```bash
# Search for errors
grep "ERROR" logs/degen_digest.log

# Search for specific patterns
grep "crawler" logs/degen_digest.log | tail -20

# Analyze log patterns
awk '{print $4}' logs/degen_digest.log | sort | uniq -c | sort -nr
```

#### 2. Performance Analysis

```python
# utils/performance_profiler.py
import cProfile
import pstats
import io
from functools import wraps

def profile_function(func):
    """Decorator to profile function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        result = func(*args, **kwargs)
        pr.disable()

        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats(20)

        logger.info(f"Performance profile for {func.__name__}:\n{s.getvalue()}")
        return result
    return wrapper
```

#### 3. Memory Analysis

```python
# utils/memory_profiler.py
import tracemalloc
from functools import wraps

def track_memory(func):
    """Decorator to track memory usage"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        result = func(*args, **kwargs)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        logger.info(f"Memory usage for {func.__name__}: "
                   f"current={current/1024/1024:.2f}MB, "
                   f"peak={peak/1024/1024:.2f}MB")
        return result
    return wrapper
```

## Performance Monitoring

### Performance Metrics

```python
# utils/performance_monitor.py
import time
from typing import Dict, Any, Callable

class PerformanceMonitor:
    """Monitor application performance"""

    def __init__(self):
        self.metrics = {}

    def time_function(self, func: Callable) -> Callable:
        """Decorator to time function execution"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = (time.time() - start_time) * 1000

            func_name = func.__name__
            if func_name not in self.metrics:
                self.metrics[func_name] = []

            self.metrics[func_name].append(execution_time)

            # Keep only last 100 measurements
            if len(self.metrics[func_name]) > 100:
                self.metrics[func_name] = self.metrics[func_name][-100:]

            logger.info(f"Function {func_name} took {execution_time:.2f}ms")
            return result
        return wrapper

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all monitored functions"""
        summary = {}

        for func_name, times in self.metrics.items():
            if times:
                summary[func_name] = {
                    "count": len(times),
                    "avg_time_ms": sum(times) / len(times),
                    "min_time_ms": min(times),
                    "max_time_ms": max(times),
                    "p95_time_ms": sorted(times)[int(len(times) * 0.95)]
                }

        return summary
```

### Resource Monitoring

```python
# utils/resource_monitor.py
import psutil
import threading
import time
from typing import Dict, Any

class ResourceMonitor:
    """Monitor system resource usage"""

    def __init__(self, interval: int = 60):
        self.interval = interval
        self.monitoring = False
        self.metrics_history = []
        self.max_history = 1440  # 24 hours at 1-minute intervals

    def start_monitoring(self):
        """Start resource monitoring"""
        self.monitoring = True
        thread = threading.Thread(target=self._monitor_loop)
        thread.daemon = True
        thread.start()

    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring = False

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            metrics = self.collect_metrics()
            self.metrics_history.append(metrics)

            # Keep only recent history
            if len(self.metrics_history) > self.max_history:
                self.metrics_history = self.metrics_history[-self.max_history:]

            time.sleep(self.interval)

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect current resource metrics"""
        return {
            "timestamp": time.time(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "network_io": psutil.net_io_counters()._asdict(),
            "load_average": psutil.getloadavg()
        }

    def get_resource_summary(self) -> Dict[str, Any]:
        """Get resource usage summary"""
        if not self.metrics_history:
            return {}

        recent_metrics = self.metrics_history[-60:]  # Last hour

        return {
            "current": self.metrics_history[-1],
            "hourly_avg": {
                "cpu_percent": sum(m["cpu_percent"] for m in recent_metrics) / len(recent_metrics),
                "memory_percent": sum(m["memory_percent"] for m in recent_metrics) / len(recent_metrics),
                "disk_percent": sum(m["disk_percent"] for m in recent_metrics) / len(recent_metrics)
            },
            "peak": {
                "cpu_percent": max(m["cpu_percent"] for m in recent_metrics),
                "memory_percent": max(m["memory_percent"] for m in recent_metrics),
                "disk_percent": max(m["disk_percent"] for m in recent_metrics)
            }
        }
```

## Security Monitoring

### Security Logging

```python
# utils/security_monitor.py
import hashlib
import hmac
from typing import Dict, Any

class SecurityMonitor:
    """Monitor security-related events"""

    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode()

    def log_security_event(self, event_type: str, details: Dict[str, Any], severity: str = "info"):
        """Log security-related events"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "severity": severity,
            "details": details,
            "hash": self._generate_event_hash(event_type, details)
        }

        logger.warning(f"Security event: {event_type}", extra=event)

    def _generate_event_hash(self, event_type: str, details: Dict[str, Any]) -> str:
        """Generate hash for security event"""
        data = f"{event_type}:{json.dumps(details, sort_keys=True)}"
        return hmac.new(self.secret_key, data.encode(), hashlib.sha256).hexdigest()

    def log_failed_login(self, username: str, ip_address: str, reason: str):
        """Log failed login attempts"""
        self.log_security_event("failed_login", {
            "username": username,
            "ip_address": ip_address,
            "reason": reason
        }, severity="warning")

    def log_api_abuse(self, endpoint: str, ip_address: str, request_count: int):
        """Log API abuse attempts"""
        self.log_security_event("api_abuse", {
            "endpoint": endpoint,
            "ip_address": ip_address,
            "request_count": request_count
        }, severity="warning")

    def log_data_access(self, user: str, data_type: str, access_type: str):
        """Log data access events"""
        self.log_security_event("data_access", {
            "user": user,
            "data_type": data_type,
            "access_type": access_type
        }, severity="info")
```

### Security Alerts

```python
# utils/security_alerts.py
class SecurityAlertManager:
    """Manage security alerts"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.failed_login_attempts = {}
        self.api_abuse_attempts = {}

    def check_failed_logins(self, username: str, ip_address: str) -> bool:
        """Check for suspicious failed login patterns"""
        key = f"{username}:{ip_address}"

        if key not in self.failed_login_attempts:
            self.failed_login_attempts[key] = []

        self.failed_login_attempts[key].append(time.time())

        # Remove attempts older than 1 hour
        cutoff = time.time() - 3600
        self.failed_login_attempts[key] = [
            t for t in self.failed_login_attempts[key] if t > cutoff
        ]

        # Alert if more than 5 failed attempts in 1 hour
        if len(self.failed_login_attempts[key]) > 5:
            self.send_security_alert("multiple_failed_logins", {
                "username": username,
                "ip_address": ip_address,
                "attempt_count": len(self.failed_login_attempts[key])
            })
            return True

        return False

    def check_api_abuse(self, endpoint: str, ip_address: str) -> bool:
        """Check for API abuse patterns"""
        key = f"{endpoint}:{ip_address}"

        if key not in self.api_abuse_attempts:
            self.api_abuse_attempts[key] = []

        self.api_abuse_attempts[key].append(time.time())

        # Remove attempts older than 1 minute
        cutoff = time.time() - 60
        self.api_abuse_attempts[key] = [
            t for t in self.api_abuse_attempts[key] if t > cutoff
        ]

        # Alert if more than 100 requests per minute
        if len(self.api_abuse_attempts[key]) > 100:
            self.send_security_alert("api_abuse", {
                "endpoint": endpoint,
                "ip_address": ip_address,
                "request_count": len(self.api_abuse_attempts[key])
            })
            return True

        return False

    def send_security_alert(self, alert_type: str, details: Dict[str, Any]):
        """Send security alert"""
        message = f"SECURITY ALERT: {alert_type} - {json.dumps(details)}"

        # Send to security team
        self.send_email_alert("Security Alert", message,
                            self.config["security"]["alert_recipients"])

        # Send to Slack security channel
        self.send_slack_alert(message, "#security")

        # Log the alert
        logger.critical(f"Security alert: {alert_type}", extra=details)
```

---

_For more information, see the [Troubleshooting Guide](TROUBLESHOOTING.md) and [Security Guide](SECURITY.md)._
