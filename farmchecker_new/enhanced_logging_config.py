#!/usr/bin/env python3
"""
Enhanced Enterprise-Level Logging Configuration for FarmChecker.xyz
==================================================================

This module provides comprehensive logging capabilities including:
- Structured JSON logging with correlation IDs
- Performance monitoring and timing
- Request/response logging
- Database operation logging
- Content processing logging
- Error tracking with full stack traces
- Business metrics logging
- Security event logging
- API endpoint monitoring

Author: FarmChecker.xyz Development Team
Version: 2.0.0
"""

import json
import logging
import time
import uuid
import traceback
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union, List
from functools import wraps
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from contextvars import ContextVar

# Context variables for request tracking
request_id: ContextVar[str] = ContextVar('request_id', default='')
user_agent: ContextVar[str] = ContextVar('user_agent', default='')
client_ip: ContextVar[str] = ContextVar('client_ip', default='')

class LogLevel(Enum):
    """Enhanced log levels for enterprise logging"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    AUDIT = "AUDIT"
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"
    BUSINESS = "BUSINESS"
    API = "API"
    DATABASE = "DATABASE"
    CONTENT = "CONTENT"

@dataclass
class LogContext:
    """Context information for structured logging"""
    request_id: str
    user_agent: str = ""
    client_ip: str = ""
    session_id: str = ""
    user_id: str = ""
    operation: str = ""
    component: str = ""
    start_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    success: Optional[bool] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.start_time is None:
            self.start_time = datetime.now(timezone.utc)

class EnhancedJSONFormatter(logging.Formatter):
    """Enhanced JSON formatter with structured data"""
    
    def format(self, record):
        # Create base log entry
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread_id": threading.get_ident(),
            "process_id": os.getpid(),
        }
        
        # Add context information
        if hasattr(record, 'context'):
            log_entry.update(asdict(record.context))
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 
                          'exc_text', 'stack_info', 'context']:
                log_entry[key] = value
        
        # Add exception information
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add stack info
        if record.stack_info:
            log_entry["stack_info"] = self.formatStack(record.stack_info)
        
        return json.dumps(log_entry, default=str)

class PerformanceFormatter(logging.Formatter):
    """Specialized formatter for performance logging"""
    
    def format(self, record):
        if hasattr(record, 'context') and record.context.duration_ms:
            return f"PERF | {record.context.operation} took {record.context.duration_ms:.2f}ms | {record.getMessage()}"
        return f"PERF | {record.getMessage()}"

class EnhancedLogger:
    """
    Enhanced enterprise-level logging system
    """
    
    def __init__(self, service_name: str, environment: str = "production"):
        self.service_name = service_name
        self.environment = environment
        self.logger = logging.getLogger(f"farmchecker.{service_name}")
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Configure handlers
        self._setup_handlers()
        
        # Performance tracking
        self.performance_data = {}
        
    def _setup_handlers(self):
        """Setup comprehensive logging handlers"""
        
        # Console handler for development
        if self.environment == "development":
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)
            console_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
        
        # JSON handler for structured logging
        json_handler = logging.StreamHandler(sys.stdout)
        json_handler.setLevel(logging.INFO)
        json_formatter = EnhancedJSONFormatter()
        json_handler.setFormatter(json_formatter)
        self.logger.addHandler(json_handler)
        
        # Performance handler
        perf_handler = logging.StreamHandler(sys.stdout)
        perf_handler.setLevel(logging.INFO)
        perf_formatter = PerformanceFormatter()
        perf_handler.setFormatter(perf_formatter)
        self.logger.addHandler(perf_handler)
    
    def _create_context(self, operation: str, component: str = "", **kwargs) -> LogContext:
        """Create logging context"""
        return LogContext(
            request_id=request_id.get(),
            user_agent=user_agent.get(),
            client_ip=client_ip.get(),
            operation=operation,
            component=component,
            **kwargs
        )
    
    def log_api_request(self, method: str, path: str, status_code: int, duration_ms: float, 
                       request_size: int = 0, response_size: int = 0, **kwargs):
        """Log API request details"""
        context = self._create_context(
            operation="api_request",
            component="api",
            duration_ms=duration_ms,
            success=200 <= status_code < 400,
            metadata={
                "method": method,
                "path": path,
                "status_code": status_code,
                "request_size": request_size,
                "response_size": response_size,
                **kwargs
            }
        )
        
        self.logger.info(
            f"API {method} {path} - {status_code} ({duration_ms:.2f}ms)",
            extra={"context": context}
        )
    
    def log_database_operation(self, operation: str, table: str, duration_ms: float, 
                              record_count: int = 0, success: bool = True, error: str = None, **kwargs):
        """Log database operation details"""
        context = self._create_context(
            operation="database_operation",
            component="database",
            duration_ms=duration_ms,
            success=success,
            error_message=error,
            metadata={
                "db_operation": operation,
                "table": table,
                "record_count": record_count,
                **kwargs
            }
        )
        
        self.logger.info(
            f"DB {operation} on {table} - {record_count} records ({duration_ms:.2f}ms)",
            extra={"context": context}
        )
    
    def log_content_processing(self, content_type: str, content_id: str, operation: str,
                              input_length: int, output_length: int, duration_ms: float,
                              success: bool = True, error: str = None, **kwargs):
        """Log content processing details"""
        context = self._create_context(
            operation="content_processing",
            component="content",
            duration_ms=duration_ms,
            success=success,
            error_message=error,
            metadata={
                "content_type": content_type,
                "content_id": content_id,
                "processing_operation": operation,
                "input_length": input_length,
                "output_length": output_length,
                **kwargs
            }
        )
        
        self.logger.info(
            f"Content {operation} on {content_type} {content_id} - {input_length}->{output_length} chars ({duration_ms:.2f}ms)",
            extra={"context": context}
        )
    
    def log_business_metric(self, metric_name: str, value: Union[int, float, str], 
                           category: str = "", **kwargs):
        """Log business metrics"""
        context = self._create_context(
            operation="business_metric",
            component="business",
            metadata={
                "metric_name": metric_name,
                "metric_value": value,
                "category": category,
                **kwargs
            }
        )
        
        self.logger.info(
            f"Business metric: {metric_name} = {value}",
            extra={"context": context}
        )
    
    def log_security_event(self, event_type: str, severity: str, user_id: str = "",
                          ip_address: str = "", details: str = "", **kwargs):
        """Log security events"""
        context = self._create_context(
            operation="security_event",
            component="security",
            user_id=user_id,
            metadata={
                "event_type": event_type,
                "severity": severity,
                "ip_address": ip_address,
                "details": details,
                **kwargs
            }
        )
        
        self.logger.warning(
            f"Security event: {event_type} - {severity} - {details}",
            extra={"context": context}
        )
    
    def log_performance(self, operation: str, duration_ms: float, **kwargs):
        """Log performance metrics"""
        context = self._create_context(
            operation="performance",
            component="performance",
            duration_ms=duration_ms,
            metadata=kwargs
        )
        
        self.logger.info(
            f"Performance: {operation} took {duration_ms:.2f}ms",
            extra={"context": context}
        )
    
    def log_error(self, error: Exception, operation: str = "", component: str = "", **kwargs):
        """Log errors with full context"""
        context = self._create_context(
            operation=operation or "error",
            component=component,
            success=False,
            error_message=str(error),
            metadata=kwargs
        )
        
        self.logger.error(
            f"Error in {operation}: {str(error)}",
            extra={"context": context},
            exc_info=True
        )

def performance_monitor(operation_name: str = None):
    """Decorator to monitor function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            operation = operation_name or f"{func.__module__}.{func.__name__}"
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                # Log performance
                logger = logging.getLogger(f"farmchecker.{func.__module__}")
                logger.info(
                    f"Performance: {operation} completed in {duration_ms:.2f}ms",
                    extra={
                        "context": LogContext(
                            request_id=request_id.get(),
                            operation="performance",
                            component=func.__module__,
                            duration_ms=duration_ms,
                            success=True
                        )
                    }
                )
                
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                # Log error with performance data
                logger = logging.getLogger(f"farmchecker.{func.__module__}")
                logger.error(
                    f"Error in {operation} after {duration_ms:.2f}ms: {str(e)}",
                    extra={
                        "context": LogContext(
                            request_id=request_id.get(),
                            operation="performance",
                            component=func.__module__,
                            duration_ms=duration_ms,
                            success=False,
                            error_message=str(e)
                        )
                    },
                    exc_info=True
                )
                raise
        return wrapper
    return decorator

def log_request_context(request):
    """Extract and set request context for logging"""
    # Generate request ID if not present
    if not request_id.get():
        request_id.set(str(uuid.uuid4()))
    
    # Set user agent
    user_agent.set(request.headers.get('User-Agent', ''))
    
    # Set client IP
    client_ip.set(request.headers.get('X-Forwarded-For', request.remote_addr))

# Global logger instance
_global_logger = None

def get_logger(service_name: str = "main") -> EnhancedLogger:
    """Get or create global logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = EnhancedLogger(service_name)
    return _global_logger

def setup_logging(service_name: str = "main", environment: str = "production") -> EnhancedLogger:
    """Setup enhanced logging for the application"""
    return get_logger(service_name) 