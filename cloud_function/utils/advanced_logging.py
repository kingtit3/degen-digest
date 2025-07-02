"""Advanced structured logging configuration for Degen Digest.

This centralises log formatting so every module can simply do::

    from utils.advanced_logging import get_logger, configure_logging
    configure_logging(json=True)  # typically called once from main entry-point
    logger = get_logger(__name__)

The helper produces **JSON** logs by default when the environment variable
`LOG_FORMAT=json` is present (e.g. inside Docker) and colourful rich logs during
local development.  All standard-library ``logging`` calls are captured and
forwarded to *structlog* so third-party libraries continue to work.

Key features
------------
* Optional per-request or per-task context (``request_id``) bound via
  ``structlog.contextvars``.
* ISO8601 UTC timestamps.
* Easy to switch between human and machine format via env or parameter.
* Adds ``exc_info`` rendering only at *ERROR* level.
"""

from __future__ import annotations

import logging
import os
import sys
import time
import traceback
import types
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any, Dict
from collections.abc import Callable

# ---------------------------------------------------------------------------
# Optional structlog import.  If the dependency isn't available (e.g. in a
# minimal CI environment) we fall back to stdlib logging so that unit-tests do
# not crash with ``ModuleNotFoundError``.
# ---------------------------------------------------------------------------


try:
    import structlog  # type: ignore

    _STRUCTLOG_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover
    # ------------------------------------------------------------------
    # Create a minimal stub so the rest of this module can be imported even
    # when structlog isn't installed (e.g. in lightweight CI environments).
    # ------------------------------------------------------------------
    structlog = types.ModuleType("structlog")  # type: ignore

    def _noop(*_a, **_kw):  # noqa: D401
        return None

    structlog.get_logger = lambda name=None, **kw: logging.getLogger(name)  # type: ignore[attr-defined]
    structlog.configure = _noop  # type: ignore[attr-defined]
    structlog.PrintLoggerFactory = lambda: None  # type: ignore[attr-defined]
    structlog.processors = types.SimpleNamespace(
        TimeStamper=lambda *a, **kw: _noop,
        StackInfoRenderer=_noop,
        format_exc_info=_noop,
        UnicodeDecoder=_noop,
        JSONRenderer=_noop,
    )
    # Provide a real sub-module so that "import structlog.contextvars as ctx"
    # succeeds when structlog is absent.
    contextvars_mod = types.ModuleType("structlog.contextvars")
    contextvars_mod.merge_contextvars = _noop  # type: ignore[attr-defined]
    sys.modules["structlog.contextvars"] = contextvars_mod
    structlog.contextvars = contextvars_mod  # type: ignore[attr-defined]

    sys.modules["structlog"] = structlog  # type: ignore[arg-type]
    _STRUCTLOG_AVAILABLE = False

# ---------------------------------------------------------------------------
# Real structured implementation when structlog is present
# ---------------------------------------------------------------------------

if _STRUCTLOG_AVAILABLE:
    # ---------------------------------------------------------------------------
    # Public helpers
    # ---------------------------------------------------------------------------

    def configure_logging(
        *, json: bool | None = None, level: str | int = "INFO"
    ) -> None:
        """Configure structlog + stdlib logging.

        Args:
            json: Force JSON output.  If *None* (default) we choose JSON when the
                environment variable ``LOG_FORMAT`` is set to ``json`` *or* when
                stdout is *not* a TTY (i.e. running in containers / CI).
            level: Root logging level as string (e.g. ``"DEBUG"``) or numeric.
        """

        # ------------------------------------------------------------------
        # Decide on output format
        # ------------------------------------------------------------------
        if json is None:
            json = (
                os.getenv("LOG_FORMAT", "console").lower() == "json"
                or not sys.stdout.isatty()
            )

        timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)

        # Shared processors for both chains
        shared_processors: list[structlog.typing.Processor] = [
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,  # Adds tracebacks to event dict on error.
            timestamper,
        ]

        if json:
            renderer: structlog.typing.Processor = structlog.processors.JSONRenderer()
        else:
            try:
                from rich.console import Console

                console = Console(force_terminal=True, color_system="auto")

                def _rich_renderer(_: str, __: str, event_dict: dict[str, Any]) -> str:  # type: ignore[override]
                    level = event_dict.pop("level", "info").upper()
                    ts = event_dict.pop("timestamp", "-")
                    msg = event_dict.pop("event", "")
                    rest = " ".join(f"{k}={v!r}" for k, v in event_dict.items())
                    console.print(
                        f"[bold cyan]{ts}[/] | [bold]{level:<8}[/] | {msg} {rest}"
                    )
                    return ""

                renderer = _rich_renderer  # type: ignore[assignment]
            except Exception:  # pragma: no cover – rich is optional
                renderer = structlog.dev.ConsoleRenderer()

        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                *shared_processors,
                structlog.processors.UnicodeDecoder(),
                renderer,
            ],
            wrapper_class=structlog.make_filtering_bound_logger(
                getattr(logging, str(level).upper(), level)
            ),
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )

        # Stdlib -> structlog bridge – simple setup: format messages via structlog
        logging.basicConfig(level=level, format="%(message)s")

    def get_logger(name: str):
        """Return a structlog logger bound with module name."""
        return structlog.get_logger(name=name)


# ---------------------------------------------------------------------------
# Fallback implementation when structlog is absent
# ---------------------------------------------------------------------------

if not _STRUCTLOG_AVAILABLE:
    # ---------------------------------------------------------------------------
    # Public helpers
    # ---------------------------------------------------------------------------

    def configure_logging(
        *, json: bool | None = None, level: str | int = "INFO"
    ) -> None:  # type: ignore[override]
        """Fallback basicConfig when structlog is absent."""

        logging.basicConfig(
            level=level,
            format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def get_logger(name: str):  # type: ignore[override]
        """Return stdlib logger in structlog-less environments."""

        return logging.getLogger(name)


def setup_logging(level: str = "INFO", log_file: str = "logs/degen_digest.log"):
    """Setup comprehensive logging for the entire application"""

    # Create logs directory
    Path("logs").mkdir(exist_ok=True)

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
    )

    # Set specific loggers
    loggers_to_configure = [
        "storage.db",
        "processor.scorer",
        "processor.classifier",
        "processor.summarizer",
        "processor.viral_predictor",
        "processor.content_clustering",
        "scrapers",
        "utils",
        "dashboard",
        "cloud_function",
    ]

    for logger_name in loggers_to_configure:
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, level.upper()))


def log_function_call(func: Callable) -> Callable:
    """Decorator to log function calls with parameters and timing"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)

        # Log function entry
        start_time = time.time()
        logger.info(
            "function_call_start",
            function_name=func.__name__,
            module=func.__module__,
            args_count=len(args),
            kwargs_keys=list(kwargs.keys()),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        try:
            result = func(*args, **kwargs)

            # Log successful completion
            execution_time = time.time() - start_time
            logger.info(
                "function_call_success",
                function_name=func.__name__,
                execution_time_seconds=execution_time,
                result_type=type(result).__name__,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

            return result

        except Exception as e:
            # Log error with full context
            execution_time = time.time() - start_time
            logger.error(
                "function_call_error",
                function_name=func.__name__,
                error_type=type(e).__name__,
                error_message=str(e),
                execution_time_seconds=execution_time,
                traceback=traceback.format_exc(),
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            raise

    return wrapper


def log_database_operation(operation: str):
    """Decorator to log database operations"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger("storage.db")

            start_time = time.time()
            logger.info(
                "database_operation_start",
                operation=operation,
                function_name=func.__name__,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

            try:
                result = func(*args, **kwargs)

                execution_time = time.time() - start_time
                logger.info(
                    "database_operation_success",
                    operation=operation,
                    function_name=func.__name__,
                    execution_time_seconds=execution_time,
                    result_type=type(result).__name__,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )

                return result

            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    "database_operation_error",
                    operation=operation,
                    function_name=func.__name__,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    execution_time_seconds=execution_time,
                    traceback=traceback.format_exc(),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )
                raise

        return wrapper

    return decorator


def log_api_call(api_name: str, endpoint: str = None):
    """Decorator to log API calls"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger("api")

            start_time = time.time()
            logger.info(
                "api_call_start",
                api_name=api_name,
                endpoint=endpoint,
                function_name=func.__name__,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

            try:
                result = func(*args, **kwargs)

                execution_time = time.time() - start_time
                logger.info(
                    "api_call_success",
                    api_name=api_name,
                    endpoint=endpoint,
                    function_name=func.__name__,
                    execution_time_seconds=execution_time,
                    result_type=type(result).__name__,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )

                return result

            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    "api_call_error",
                    api_name=api_name,
                    endpoint=endpoint,
                    function_name=func.__name__,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    execution_time_seconds=execution_time,
                    traceback=traceback.format_exc(),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )
                raise

        return wrapper

    return decorator


def log_cloud_function_execution(function_name: str):
    """Decorator to log cloud function executions"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger("cloud_function")

            start_time = time.time()
            logger.info(
                "cloud_function_start",
                function_name=function_name,
                execution_id=os.environ.get("K_REVISION", "unknown"),
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

            try:
                result = func(*args, **kwargs)

                execution_time = time.time() - start_time
                logger.info(
                    "cloud_function_success",
                    function_name=function_name,
                    execution_time_seconds=execution_time,
                    result_type=type(result).__name__,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )

                return result

            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    "cloud_function_error",
                    function_name=function_name,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    execution_time_seconds=execution_time,
                    traceback=traceback.format_exc(),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )
                raise

        return wrapper

    return decorator


def log_performance_metrics(operation: str, **metrics):
    """Log performance metrics"""
    logger = get_logger("performance")
    logger.info(
        "performance_metrics",
        operation=operation,
        metrics=metrics,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


def log_system_health(component: str, status: str, details: dict[str, Any] = None):
    """Log system health status"""
    logger = get_logger("health")
    logger.info(
        "system_health",
        component=component,
        status=status,
        details=details or {},
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


def log_data_quality_issue(issue_type: str, severity: str, details: dict[str, Any]):
    """Log data quality issues"""
    logger = get_logger("data_quality")
    logger.warning(
        "data_quality_issue",
        issue_type=issue_type,
        severity=severity,
        details=details,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


def log_security_event(event_type: str, severity: str, details: dict[str, Any]):
    """Log security events"""
    logger = get_logger("security")
    logger.warning(
        "security_event",
        event_type=event_type,
        severity=severity,
        details=details,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


def log_business_event(event_type: str, details: dict[str, Any]):
    """Log business events"""
    logger = get_logger("business")
    logger.info(
        "business_event",
        event_type=event_type,
        details=details,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


# Export for use in other modules
__all__ = [
    "setup_logging",
    "get_logger",
    "log_function_call",
    "log_database_operation",
    "log_api_call",
    "log_cloud_function_execution",
    "log_performance_metrics",
    "log_system_health",
    "log_data_quality_issue",
    "log_security_event",
    "log_business_event",
    "_STRUCTLOG_AVAILABLE",
]
