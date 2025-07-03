"""
Enterprise-level logging system for Degen Digest.

This module provides comprehensive logging capabilities including:
- Structured logging with JSON and console formats
- Log rotation and archival
- Performance monitoring
- Error tracking and alerting
- Audit logging
- Security event logging
- Business metrics logging
- Request/response logging
- Database operation logging
- API call logging
- Cloud function execution logging
- Data quality monitoring
- System health monitoring
"""

import inspect
import json
import logging
import logging.handlers
import os
import sys
import threading
import time
import traceback
import uuid
from collections.abc import Callable
from contextlib import contextmanager
from datetime import UTC, datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any

try:
    # structlog import removed as it was unused
    STRUCTLOG_AVAILABLE = False
except ImportError:
    STRUCTLOG_AVAILABLE = False

# Global logging configuration
LOG_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": os.getenv("LOG_FORMAT", "console"),
    "file_path": os.getenv("LOG_FILE", "logs/degen_digest.log"),
    "max_size": int(os.getenv("LOG_MAX_SIZE_MB", "100")) * 1024 * 1024,  # 100MB
    "backup_count": int(os.getenv("LOG_BACKUP_COUNT", "5")),
    "enable_cloud_logging": os.getenv("ENABLE_CLOUD_LOGGING", "true").lower() == "true",
    "enable_audit_logging": os.getenv("ENABLE_AUDIT_LOGGING", "true").lower() == "true",
    "enable_performance_logging": os.getenv(
        "ENABLE_PERFORMANCE_LOGGING", "true"
    ).lower()
    == "true",
    "enable_security_logging": os.getenv("ENABLE_SECURITY_LOGGING", "true").lower()
    == "true",
    "enable_business_logging": os.getenv("ENABLE_BUSINESS_LOGGING", "true").lower()
    == "true",
    "enable_data_quality_logging": os.getenv(
        "ENABLE_DATA_QUALITY_LOGGING", "true"
    ).lower()
    == "true",
    "enable_api_logging": os.getenv("ENABLE_API_LOGGING", "true").lower() == "true",
    "enable_database_logging": os.getenv("ENABLE_DATABASE_LOGGING", "true").lower()
    == "true",
    "enable_crawler_logging": os.getenv("ENABLE_CRAWLER_LOGGING", "true").lower()
    == "true",
    "enable_dashboard_logging": os.getenv("ENABLE_DASHBOARD_LOGGING", "true").lower()
    == "true",
}


class EnterpriseLogger:
    """Enterprise-level logger with comprehensive features."""

    def __init__(self, name: str, config: dict[str, Any] | None = None):
        self.name = name
        self.config = config or LOG_CONFIG
        self.logger = self._setup_logger()
        self.performance_metrics = {}
        self.error_counts = {}
        self.audit_events = []
        self.security_events = []
        self.business_events = []
        self.data_quality_issues = []

        # Thread-local storage for request context
        self._local = threading.local()

        # Generate unique logger instance ID
        self.instance_id = str(uuid.uuid4())[:8]

    def _setup_logger(self) -> logging.Logger:
        """Setup logger with enterprise features."""
        logger = logging.getLogger(self.name)
        logger.setLevel(getattr(logging, self.config["level"].upper()))

        # Clear existing handlers
        logger.handlers.clear()

        # Create logs directory
        log_dir = Path(self.config["file_path"]).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            self.config["file_path"],
            maxBytes=self.config["max_size"],
            backupCount=self.config["backup_count"],
            encoding="utf-8",
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)

        # Set formatter based on configuration
        if self.config["format"] == "json":
            formatter = self._create_json_formatter()
        else:
            formatter = self._create_console_formatter()

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def _create_json_formatter(self) -> logging.Formatter:
        """Create JSON formatter for structured logging."""

        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": datetime.fromtimestamp(
                        record.created, tz=UTC
                    ).isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno,
                    "process_id": os.getpid(),
                    "thread_id": threading.get_ident(),
                }

                # Add exception info if present
                if record.exc_info:
                    log_entry["exception"] = {
                        "type": record.exc_info[0].__name__,
                        "message": str(record.exc_info[1]),
                        "traceback": traceback.format_exception(*record.exc_info),
                    }

                # Add extra fields
                if hasattr(record, "extra_fields"):
                    log_entry.update(record.extra_fields)

                return json.dumps(log_entry, ensure_ascii=False)

        return JSONFormatter()

    def _create_console_formatter(self) -> logging.Formatter:
        """Create console formatter for human-readable logs."""
        return logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def _log_with_context(
        self, level: int, message: str, extra_fields: dict[str, Any] | None = None
    ):
        """Log message with context and extra fields."""
        if extra_fields is None:
            extra_fields = {}

        # Add request context if available
        if hasattr(self._local, "request_id"):
            extra_fields["request_id"] = self._local.request_id

        if hasattr(self._local, "user_id"):
            extra_fields["user_id"] = self._local.user_id

        if hasattr(self._local, "session_id"):
            extra_fields["session_id"] = self._local.session_id

        if hasattr(self._local, "ip_address"):
            extra_fields["ip_address"] = self._local.ip_address

        if hasattr(self._local, "user_agent"):
            extra_fields["user_agent"] = self._local.user_agent

        # Add logger instance ID
        extra_fields["logger_instance_id"] = self.instance_id

        # Add timestamp
        extra_fields["timestamp"] = datetime.now(UTC).isoformat()

        # Create log record with extra fields
        record = self.logger.makeRecord(self.name, level, "", 0, message, (), None)
        record.extra_fields = extra_fields

        self.logger.handle(record)

    def info(self, message: str, **kwargs):
        """Log info message with extra fields."""
        self._log_with_context(logging.INFO, message, kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message with extra fields."""
        self._log_with_context(logging.WARNING, message, kwargs)

    def error(self, message: str, **kwargs):
        """Log error message with extra fields."""
        self._log_with_context(logging.ERROR, message, kwargs)
        self._track_error(message, kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message with extra fields."""
        self._log_with_context(logging.CRITICAL, message, kwargs)
        self._track_error(message, kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message with extra fields."""
        self._log_with_context(logging.DEBUG, message, kwargs)

    def _track_error(self, message: str, extra_fields: dict[str, Any]):
        """Track error for monitoring and alerting."""
        error_key = f"{message}:{extra_fields.get('error_type', 'unknown')}"
        if error_key not in self.error_counts:
            self.error_counts[error_key] = {
                "count": 0,
                "first_occurrence": datetime.now(UTC),
                "last_occurrence": datetime.now(UTC),
                "examples": [],
            }

        self.error_counts[error_key]["count"] += 1
        self.error_counts[error_key]["last_occurrence"] = datetime.now(UTC)

        # Keep up to 5 examples
        if len(self.error_counts[error_key]["examples"]) < 5:
            self.error_counts[error_key]["examples"].append(
                {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "extra_fields": extra_fields,
                }
            )

    def set_request_context(
        self,
        request_id: str,
        user_id: str | None = None,
        session_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ):
        """Set request context for correlation."""
        self._local.request_id = request_id
        if user_id:
            self._local.user_id = user_id
        if session_id:
            self._local.session_id = session_id
        if ip_address:
            self._local.ip_address = ip_address
        if user_agent:
            self._local.user_agent = user_agent

    def clear_request_context(self):
        """Clear request context."""
        if hasattr(self._local, "request_id"):
            delattr(self._local, "request_id")
        if hasattr(self._local, "user_id"):
            delattr(self._local, "user_id")
        if hasattr(self._local, "session_id"):
            delattr(self._local, "session_id")
        if hasattr(self._local, "ip_address"):
            delattr(self._local, "ip_address")
        if hasattr(self._local, "user_agent"):
            delattr(self._local, "user_agent")

    @contextmanager
    def performance_timer(self, operation: str, **kwargs):
        """Context manager for performance timing."""
        if not self.config["enable_performance_logging"]:
            yield
            return

        start_time = time.time()
        operation_id = str(uuid.uuid4())[:8]

        self.info(
            f"Performance timer started: {operation}",
            operation=operation,
            operation_id=operation_id,
            **kwargs,
        )

        try:
            yield operation_id
        finally:
            duration = time.time() - start_time
            self.info(
                f"Performance timer completed: {operation}",
                operation=operation,
                operation_id=operation_id,
                duration_seconds=duration,
                **kwargs,
            )

            # Track performance metrics
            if operation not in self.performance_metrics:
                self.performance_metrics[operation] = {
                    "count": 0,
                    "total_duration": 0,
                    "min_duration": float("inf"),
                    "max_duration": 0,
                    "avg_duration": 0,
                }

            metrics = self.performance_metrics[operation]
            metrics["count"] += 1
            metrics["total_duration"] += duration
            metrics["min_duration"] = min(metrics["min_duration"], duration)
            metrics["max_duration"] = max(metrics["max_duration"], duration)
            metrics["avg_duration"] = metrics["total_duration"] / metrics["count"]

    def audit_log(self, event: str, user_id: str | None = None, **kwargs):
        """Log audit events."""
        if not self.config["enable_audit_logging"]:
            return

        audit_entry = {
            "event": event,
            "user_id": user_id or getattr(self._local, "user_id", None),
            "timestamp": datetime.now(UTC).isoformat(),
            "ip_address": getattr(self._local, "ip_address", None),
            "user_agent": getattr(self._local, "user_agent", None),
            "session_id": getattr(self._local, "session_id", None),
            "request_id": getattr(self._local, "request_id", None),
            **kwargs,
        }

        self.info(f"AUDIT: {event}", **audit_entry)
        self.audit_events.append(audit_entry)

    def security_log(self, event: str, severity: str = "info", **kwargs):
        """Log security events."""
        if not self.config["enable_security_logging"]:
            return

        security_entry = {
            "event": event,
            "severity": severity,
            "timestamp": datetime.now(UTC).isoformat(),
            "ip_address": getattr(self._local, "ip_address", None),
            "user_agent": getattr(self._local, "user_agent", None),
            "session_id": getattr(self._local, "session_id", None),
            "request_id": getattr(self._local, "request_id", None),
            **kwargs,
        }

        if severity == "critical":
            self.critical(f"SECURITY: {event}", **security_entry)
        elif severity == "warning":
            self.warning(f"SECURITY: {event}", **security_entry)
        else:
            self.info(f"SECURITY: {event}", **security_entry)

        self.security_events.append(security_entry)

    def business_log(self, event: str, **kwargs):
        """Log business events."""
        if not self.config["enable_business_logging"]:
            return

        business_entry = {
            "event": event,
            "timestamp": datetime.now(UTC).isoformat(),
            "session_id": getattr(self._local, "session_id", None),
            "request_id": getattr(self._local, "request_id", None),
            **kwargs,
        }

        self.info(f"BUSINESS: {event}", **business_entry)
        self.business_events.append(business_entry)

    def data_quality_log(self, issue: str, data_source: str, **kwargs):
        """Log data quality issues."""
        if not self.config["enable_data_quality_logging"]:
            return

        quality_entry = {
            "issue": issue,
            "data_source": data_source,
            "timestamp": datetime.now(UTC).isoformat(),
            "session_id": getattr(self._local, "session_id", None),
            "request_id": getattr(self._local, "request_id", None),
            **kwargs,
        }

        self.warning(f"DATA_QUALITY: {issue}", **quality_entry)
        self.data_quality_issues.append(quality_entry)

    def api_log(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        response_time: float,
        **kwargs,
    ):
        """Log API calls."""
        if not self.config["enable_api_logging"]:
            return

        api_entry = {
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "response_time_ms": response_time * 1000,
            "timestamp": datetime.now(UTC).isoformat(),
            "session_id": getattr(self._local, "session_id", None),
            "request_id": getattr(self._local, "request_id", None),
            **kwargs,
        }

        if status_code >= 400:
            self.error(f"API_CALL: {method} {endpoint}", **api_entry)
        else:
            self.info(f"API_CALL: {method} {endpoint}", **api_entry)

    def database_log(self, operation: str, table: str, duration: float, **kwargs):
        """Log database operations."""
        if not self.config["enable_database_logging"]:
            return

        db_entry = {
            "operation": operation,
            "table": table,
            "duration_ms": duration * 1000,
            "timestamp": datetime.now(UTC).isoformat(),
            "session_id": getattr(self._local, "session_id", None),
            "request_id": getattr(self._local, "request_id", None),
            **kwargs,
        }

        self.info(f"DATABASE: {operation} on {table}", **db_entry)

    def crawler_log(self, source: str, action: str, **kwargs):
        """Log crawler operations."""
        if not self.config["enable_crawler_logging"]:
            return

        crawler_entry = {
            "source": source,
            "action": action,
            "timestamp": datetime.now(UTC).isoformat(),
            "session_id": getattr(self._local, "session_id", None),
            "request_id": getattr(self._local, "request_id", None),
            **kwargs,
        }

        self.info(f"CRAWLER: {action} from {source}", **crawler_entry)

    def dashboard_log(self, action: str, page: str, **kwargs):
        """Log dashboard interactions."""
        if not self.config["enable_dashboard_logging"]:
            return

        dashboard_entry = {
            "action": action,
            "page": page,
            "timestamp": datetime.now(UTC).isoformat(),
            "session_id": getattr(self._local, "session_id", None),
            "request_id": getattr(self._local, "request_id", None),
            **kwargs,
        }

        self.info(f"DASHBOARD: {action} on {page}", **dashboard_entry)

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get summary of all metrics."""
        return {
            "performance_metrics": self.performance_metrics,
            "error_counts": self.error_counts,
            "audit_events_count": len(self.audit_events),
            "security_events_count": len(self.security_events),
            "business_events_count": len(self.business_events),
            "data_quality_issues_count": len(self.data_quality_issues),
            "logger_instance_id": self.instance_id,
            "logger_name": self.name,
        }


# Global logger instances
_loggers = {}


def get_logger(name: str) -> EnterpriseLogger:
    """Get or create an enterprise logger instance."""
    if name not in _loggers:
        _loggers[name] = EnterpriseLogger(name)
    return _loggers[name]


# Decorators for common logging patterns
def log_function_call(logger_name: str | None = None):
    """Decorator to log function calls with timing."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name or func.__module__)

            # Get function signature
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            with logger.performance_timer(f"function_call:{func.__name__}"):
                logger.info(
                    f"Function called: {func.__name__}",
                    function=func.__name__,
                    module=func.__module__,
                    args=dict(bound_args.arguments),
                )

                try:
                    result = func(*args, **kwargs)
                    logger.info(
                        f"Function completed: {func.__name__}",
                        function=func.__name__,
                        success=True,
                    )
                    return result
                except Exception as e:
                    logger.error(
                        f"Function failed: {func.__name__}",
                        function=func.__name__,
                        error=str(e),
                        error_type=type(e).__name__,
                        success=False,
                    )
                    raise

        return wrapper

    return decorator


def log_database_operation(logger_name: str | None = None):
    """Decorator to log database operations."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name or func.__module__)

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                logger.database_log(
                    operation=func.__name__,
                    table=kwargs.get("table", "unknown"),
                    duration=duration,
                    success=True,
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.database_log(
                    operation=func.__name__,
                    table=kwargs.get("table", "unknown"),
                    duration=duration,
                    success=False,
                    error=str(e),
                )
                raise

        return wrapper

    return decorator


def log_api_call(logger_name: str | None = None):
    """Decorator to log API calls."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name or func.__module__)

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                # Extract method and endpoint from function name or kwargs
                method = kwargs.get("method", "GET")
                endpoint = kwargs.get("endpoint", func.__name__)
                status_code = (
                    getattr(result, "status_code", 200)
                    if hasattr(result, "status_code")
                    else 200
                )

                logger.api_log(
                    method=method,
                    endpoint=endpoint,
                    status_code=status_code,
                    response_time=duration,
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.api_log(
                    method=kwargs.get("method", "GET"),
                    endpoint=kwargs.get("endpoint", func.__name__),
                    status_code=500,
                    response_time=duration,
                    error=str(e),
                )
                raise

        return wrapper

    return decorator


def log_cloud_function_execution(logger_name: str | None = None):
    """Decorator to log cloud function executions."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name or func.__module__)

            function_id = str(uuid.uuid4())
            logger.info(
                f"Cloud function started: {func.__name__}",
                function_name=func.__name__,
                function_id=function_id,
                args_count=len(args),
                kwargs_keys=list(kwargs.keys()),
            )

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                logger.info(
                    f"Cloud function completed: {func.__name__}",
                    function_name=func.__name__,
                    function_id=function_id,
                    duration_seconds=duration,
                    success=True,
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Cloud function failed: {func.__name__}",
                    function_name=func.__name__,
                    function_id=function_id,
                    duration_seconds=duration,
                    error=str(e),
                    error_type=type(e).__name__,
                    success=False,
                )
                raise

        return wrapper

    return decorator


def log_performance_metrics(logger_name: str | None = None):
    """Decorator to log performance metrics."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name or func.__module__)

            with logger.performance_timer(f"performance_metrics:{func.__name__}"):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def log_system_health(logger_name: str | None = None):
    """Decorator to log system health checks."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name or func.__module__)

            try:
                result = func(*args, **kwargs)
                logger.info(
                    f"System health check passed: {func.__name__}",
                    health_check=func.__name__,
                    status="healthy",
                    result=result,
                )
                return result
            except Exception as e:
                logger.error(
                    f"System health check failed: {func.__name__}",
                    health_check=func.__name__,
                    status="unhealthy",
                    error=str(e),
                )
                raise

        return wrapper

    return decorator


def log_data_quality_issue(logger_name: str | None = None):
    """Decorator to log data quality issues."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name or func.__module__)

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.data_quality_log(
                    issue=str(e),
                    data_source=kwargs.get("data_source", "unknown"),
                    function=func.__name__,
                    error_type=type(e).__name__,
                )
                raise

        return wrapper

    return decorator


def log_security_event(logger_name: str | None = None):
    """Decorator to log security events."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name or func.__module__)

            logger.security_log(
                event=f"security_check:{func.__name__}",
                severity=kwargs.get("severity", "info"),
                function=func.__name__,
            )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_business_event(logger_name: str | None = None):
    """Decorator to log business events."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name or func.__module__)

            logger.business_log(
                event=f"business_operation:{func.__name__}",
                function=func.__name__,
                **kwargs,
            )

            return func(*args, **kwargs)

        return wrapper

    return decorator


# Initialize logging system
def initialize_logging(config: dict[str, Any] | None = None):
    """Initialize the enterprise logging system."""
    global LOG_CONFIG

    if config:
        LOG_CONFIG.update(config)

    # Create main application logger
    main_logger = get_logger("main")
    main_logger.info(
        "Enterprise logging system initialized",
        config=LOG_CONFIG,
        python_version=sys.version,
        platform=sys.platform,
    )

    return main_logger


# Utility functions for common logging patterns
def log_configuration(component: str, config: dict[str, Any]):
    """Log configuration details."""
    logger = get_logger(component)
    logger.info(
        f"Configuration loaded: {component}", component=component, config=config
    )


def log_startup(component: str, version: str = "1.0.0"):
    """Log component startup."""
    logger = get_logger(component)
    logger.info(
        f"Component started: {component}",
        component=component,
        version=version,
        startup_time=datetime.now(UTC).isoformat(),
    )


def log_shutdown(component: str):
    """Log component shutdown."""
    logger = get_logger(component)
    logger.info(
        f"Component shutting down: {component}",
        component=component,
        shutdown_time=datetime.now(UTC).isoformat(),
    )


def log_error_with_context(
    error: Exception, context: dict[str, Any], logger_name: str = "error"
):
    """Log error with additional context."""
    logger = get_logger(logger_name)
    logger.error(
        f"Error occurred: {str(error)}",
        error_type=type(error).__name__,
        error_message=str(error),
        traceback=traceback.format_exc(),
        **context,
    )


def log_data_processing(
    data_source: str,
    record_count: int,
    processing_time: float,
    success_count: int,
    error_count: int,
    logger_name: str = "data_processing",
):
    """Log data processing metrics."""
    logger = get_logger(logger_name)
    logger.info(
        f"Data processing completed: {data_source}",
        data_source=data_source,
        record_count=record_count,
        processing_time_seconds=processing_time,
        success_count=success_count,
        error_count=error_count,
        success_rate=success_count / record_count if record_count > 0 else 0,
    )


def log_crawler_session(
    source: str,
    session_id: str,
    tweets_collected: int,
    duration: float,
    errors: list[str],
    logger_name: str = "crawler",
):
    """Log crawler session results."""
    logger = get_logger(logger_name)
    logger.info(
        f"Crawler session completed: {source}",
        source=source,
        session_id=session_id,
        tweets_collected=tweets_collected,
        duration_seconds=duration,
        error_count=len(errors),
        errors=errors,
        success=len(errors) == 0,
    )


def log_digest_generation(
    digest_date: str,
    source_count: int,
    content_count: int,
    generation_time: float,
    logger_name: str = "digest",
):
    """Log digest generation metrics."""
    logger = get_logger(logger_name)
    logger.info(
        f"Digest generated: {digest_date}",
        digest_date=digest_date,
        source_count=source_count,
        content_count=content_count,
        generation_time_seconds=generation_time,
    )


def log_dashboard_interaction(
    user_action: str, page: str, session_duration: float, logger_name: str = "dashboard"
):
    """Log dashboard user interactions."""
    logger = get_logger(logger_name)
    logger.dashboard_log(
        action=user_action, page=page, session_duration_seconds=session_duration
    )


def log_cloud_storage_operation(
    operation: str,
    bucket: str,
    object_path: str,
    file_size: int,
    duration: float,
    logger_name: str = "cloud_storage",
):
    """Log cloud storage operations."""
    logger = get_logger(logger_name)
    logger.info(
        f"Cloud storage operation: {operation}",
        operation=operation,
        bucket=bucket,
        object_path=object_path,
        file_size_bytes=file_size,
        duration_seconds=duration,
    )


# Export all functions and classes
__all__ = [
    "EnterpriseLogger",
    "get_logger",
    "initialize_logging",
    "log_function_call",
    "log_database_operation",
    "log_api_call",
    "log_cloud_function_execution",
    "log_performance_metrics",
    "log_system_health",
    "log_data_quality_issue",
    "log_security_event",
    "log_business_event",
    "log_configuration",
    "log_startup",
    "log_shutdown",
    "log_error_with_context",
    "log_data_processing",
    "log_crawler_session",
    "log_digest_generation",
    "log_dashboard_interaction",
    "log_cloud_storage_operation",
    "STRUCTLOG_AVAILABLE",
]
