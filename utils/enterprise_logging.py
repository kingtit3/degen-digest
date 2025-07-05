#!/usr/bin/env python3
"""
Enterprise Logging System for DegenDigest
Comprehensive logging with structured data, multiple outputs, and monitoring
"""

import json
import logging
import logging.handlers
import os
import sys
import threading
import time
import traceback
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class LogContext:
    """Structured log context for consistent logging"""

    service_name: str
    operation: str
    request_id: str
    user_id: str | None = None
    session_id: str | None = None
    correlation_id: str | None = None
    source_ip: str | None = None
    user_agent: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    duration_ms: float | None = None
    status: str = "started"
    error_code: str | None = None
    error_message: str | None = None
    metadata: dict[str, Any] | None = None


class EnterpriseLogger:
    """
    Enterprise-grade logging system with structured logging, multiple outputs,
    and comprehensive monitoring capabilities.
    """

    def __init__(
        self,
        service_name: str,
        log_level: str = "INFO",
        log_dir: str = "logs",
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        enable_console: bool = True,
        enable_file: bool = True,
        enable_json: bool = True,
        enable_cloud_logging: bool = False,
    ):
        self.service_name = service_name
        self.log_level = getattr(logging, log_level.upper())
        self.log_dir = Path(log_dir)
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.enable_json = enable_json
        self.enable_cloud_logging = enable_cloud_logging

        # Create log directory
        self.log_dir.mkdir(exist_ok=True)

        # Initialize logger
        self.logger = logging.getLogger(f"degen_digest.{service_name}")
        self.logger.setLevel(self.log_level)

        # Clear existing handlers
        self.logger.handlers.clear()

        # Add handlers
        self._setup_handlers()

        # Thread-local storage for context
        self._context = threading.local()

        # Performance tracking
        self._performance_data = {}

    def _setup_handlers(self):
        """Setup logging handlers"""

        # Console handler with colored output
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            console_formatter = ColoredFormatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

        # File handler with rotation
        if self.enable_file:
            file_handler = logging.handlers.RotatingFileHandler(
                self.log_dir / f"{self.service_name}.log",
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
            )
            file_handler.setLevel(self.log_level)
            file_formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

        # JSON handler for structured logging
        if self.enable_json:
            json_handler = logging.handlers.RotatingFileHandler(
                self.log_dir / f"{self.service_name}_structured.json",
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
            )
            json_handler.setLevel(self.log_level)
            json_formatter = JSONFormatter()
            json_handler.setFormatter(json_formatter)
            self.logger.addHandler(json_handler)

        # Error handler for critical errors
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / f"{self.service_name}_errors.log",
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
        )
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s\n"
            "Exception: %(exc_info)s\n"
            "Stack Trace: %(stack_info)s\n"
        )
        error_handler.setFormatter(error_formatter)
        self.logger.addHandler(error_handler)

        # Performance handler
        perf_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / f"{self.service_name}_performance.log",
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
        )
        perf_handler.setLevel(logging.INFO)
        perf_formatter = PerformanceFormatter()
        perf_handler.setFormatter(perf_formatter)
        self.logger.addHandler(perf_handler)

    def set_context(self, context: LogContext):
        """Set the current logging context"""
        self._context.current = context

    def get_context(self) -> LogContext | None:
        """Get the current logging context"""
        return getattr(self._context, "current", None)

    def clear_context(self):
        """Clear the current logging context"""
        if hasattr(self._context, "current"):
            delattr(self._context, "current")

    @contextmanager
    def operation_context(
        self, operation: str, request_id: str | None = None, **kwargs
    ):
        """Context manager for operation logging"""
        if request_id is None:
            request_id = str(uuid.uuid4())

        context = LogContext(
            service_name=self.service_name,
            operation=operation,
            request_id=request_id,
            start_time=datetime.now(UTC),
            **kwargs,
        )

        self.set_context(context)

        try:
            self.info(
                f"Starting operation: {operation}", extra={"operation": operation}
            )
            yield context
            context.status = "completed"
            context.end_time = datetime.now(UTC)
            if context.start_time:
                context.duration_ms = (
                    context.end_time - context.start_time
                ).total_seconds() * 1000
            self.info(
                f"Completed operation: {operation}", extra={"operation": operation}
            )
        except Exception as e:
            context.status = "failed"
            context.error_code = type(e).__name__
            context.error_message = str(e)
            context.end_time = datetime.now(UTC)
            if context.start_time:
                context.duration_ms = (
                    context.end_time - context.start_time
                ).total_seconds() * 1000
            self.error(
                f"Failed operation: {operation}",
                exc_info=True,
                extra={"operation": operation},
            )
            raise
        finally:
            self.clear_context()

    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message"""
        self._log(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self._log(logging.CRITICAL, message, **kwargs)

    def _log(self, level: int, message: str, **kwargs):
        """Internal logging method"""
        context = self.get_context()

        # Add context information to kwargs
        if context:
            kwargs.update(asdict(context))

        # Add timestamp
        kwargs["timestamp"] = datetime.now(UTC).isoformat()

        # Log with extra data
        self.logger.log(level, message, extra=kwargs)

    def log_performance(self, operation: str, duration_ms: float, **kwargs):
        """Log performance metrics"""
        perf_data = {
            "operation": operation,
            "duration_ms": duration_ms,
            "timestamp": datetime.now(UTC).isoformat(),
            "service_name": self.service_name,
            **kwargs,
        }

        # Store for aggregation
        if operation not in self._performance_data:
            self._performance_data[operation] = []
        self._performance_data[operation].append(perf_data)

        # Log performance
        self.info(
            f"Performance: {operation} took {duration_ms:.2f}ms",
            extra=perf_data,
            performance=True,
        )

    def log_api_call(
        self,
        method: str,
        url: str,
        status_code: int,
        duration_ms: float,
        request_size: int | None = None,
        response_size: int | None = None,
        **kwargs,
    ):
        """Log API call details"""
        api_data = {
            "api_call": True,
            "method": method,
            "url": url,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "request_size": request_size,
            "response_size": response_size,
            **kwargs,
        }

        level = logging.ERROR if status_code >= 400 else logging.INFO
        self.logger.log(
            level,
            f"API Call: {method} {url} - {status_code} ({duration_ms:.2f}ms)",
            extra=api_data,
        )

    def log_data_operation(
        self,
        operation: str,
        table: str,
        record_count: int,
        duration_ms: float,
        success: bool,
        **kwargs,
    ):
        """Log database/data operations"""
        data_data = {
            "data_operation": True,
            "operation": operation,
            "table": table,
            "record_count": record_count,
            "duration_ms": duration_ms,
            "success": success,
            **kwargs,
        }

        level = logging.ERROR if not success else logging.INFO
        self.logger.log(
            level,
            f"Data Operation: {operation} on {table} - {record_count} records ({duration_ms:.2f}ms)",
            extra=data_data,
        )

    def log_security_event(
        self,
        event_type: str,
        severity: str,
        user_id: str | None = None,
        ip_address: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        """Log security events"""
        security_data = {
            "security_event": True,
            "event_type": event_type,
            "severity": severity,
            "user_id": user_id,
            "ip_address": ip_address,
            "details": details or {},
            "timestamp": datetime.now(UTC).isoformat(),
        }

        level_map = {
            "low": logging.INFO,
            "medium": logging.WARNING,
            "high": logging.ERROR,
            "critical": logging.CRITICAL,
        }

        level = level_map.get(severity.lower(), logging.WARNING)
        self.logger.log(
            level, f"Security Event: {event_type} - {severity}", extra=security_data
        )

    def get_performance_summary(self) -> dict[str, Any]:
        """Get performance summary"""
        summary = {}
        for operation, data_list in self._performance_data.items():
            if data_list:
                durations = [d["duration_ms"] for d in data_list]
                summary[operation] = {
                    "count": len(durations),
                    "avg_duration_ms": sum(durations) / len(durations),
                    "min_duration_ms": min(durations),
                    "max_duration_ms": max(durations),
                    "total_duration_ms": sum(durations),
                }
        return summary

    def export_logs(self, output_file: str, log_type: str = "all"):
        """Export logs to file"""
        log_files = []

        if log_type in ["all", "main"]:
            log_files.append(self.log_dir / f"{self.service_name}.log")
        if log_type in ["all", "json"]:
            log_files.append(self.log_dir / f"{self.service_name}_structured.json")
        if log_type in ["all", "errors"]:
            log_files.append(self.log_dir / f"{self.service_name}_errors.log")
        if log_type in ["all", "performance"]:
            log_files.append(self.log_dir / f"{self.service_name}_performance.log")

        with open(output_file, "w") as f:
            for log_file in log_files:
                if log_file.exists():
                    f.write(f"\n{'='*50}\n")
                    f.write(f"File: {log_file.name}\n")
                    f.write(f"{'='*50}\n")
                    f.write(log_file.read_text())
                    f.write("\n")


class ColoredFormatter(logging.Formatter):
    """Colored console formatter"""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "getMessage",
                "exc_info",
                "exc_text",
                "stack_info",
            ]:
                log_entry[key] = value

        # Add exception info
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }

        return json.dumps(log_entry, default=str)


class PerformanceFormatter(logging.Formatter):
    """Performance-specific formatter"""

    def format(self, record):
        if getattr(record, "performance", False):
            return f"PERF | {record.getMessage()}"
        return super().format(record)


# Global logger instance
_global_logger = None


def get_logger(service_name: str = "main", **kwargs) -> EnterpriseLogger:
    """Get or create global logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = EnterpriseLogger(service_name, **kwargs)
    return _global_logger


def setup_logging(service_name: str = "main", **kwargs) -> EnterpriseLogger:
    """Setup logging for the application"""
    return get_logger(service_name, **kwargs)


# Convenience functions
def log_info(message: str, **kwargs):
    """Log info message using global logger"""
    get_logger().info(message, **kwargs)


def log_error(message: str, **kwargs):
    """Log error message using global logger"""
    get_logger().error(message, **kwargs)


def log_warning(message: str, **kwargs):
    """Log warning message using global logger"""
    get_logger().warning(message, **kwargs)


def log_debug(message: str, **kwargs):
    """Log debug message using global logger"""
    get_logger().debug(message, **kwargs)


def log_critical(message: str, **kwargs):
    """Log critical message using global logger"""
    get_logger().critical(message, **kwargs)
