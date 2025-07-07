"""
Enterprise-Level Logging System for FarmChecker.xyz
==================================================

This module provides comprehensive logging capabilities including:
- Structured JSON logging
- Performance monitoring
- Audit trails
- Error tracking
- Request/response logging
- Security event logging
- Business metrics logging

Author: FarmChecker.xyz Development Team
Version: 1.0.0
"""

import json
import logging
import time
import uuid
import traceback
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union
from functools import wraps
import os
import sys
from dataclasses import dataclass, asdict
from enum import Enum

class LogLevel(Enum):
    """Log levels for enterprise logging"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    AUDIT = "AUDIT"
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"
    BUSINESS = "BUSINESS"

class EventType(Enum):
    """Event types for structured logging"""
    # System Events
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    HEALTH_CHECK = "health_check"
    
    # API Events
    API_REQUEST = "api_request"
    API_RESPONSE = "api_response"
    API_ERROR = "api_error"
    
    # Data Events
    DATA_FETCH = "data_fetch"
    DATA_PROCESS = "data_process"
    DATA_STORE = "data_store"
    DATA_MIGRATION = "data_migration"
    
    # Crawler Events
    CRAWLER_START = "crawler_start"
    CRAWLER_COMPLETE = "crawler_complete"
    CRAWLER_ERROR = "crawler_error"
    
    # Business Events
    USER_ACTION = "user_action"
    BUSINESS_METRIC = "business_metric"
    
    # Security Events
    AUTH_ATTEMPT = "auth_attempt"
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    SECURITY_VIOLATION = "security_violation"
    
    # Performance Events
    PERFORMANCE_METRIC = "performance_metric"
    SLOW_QUERY = "slow_query"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"

@dataclass
class LogContext:
    """Context information for structured logging"""
    request_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    correlation_id: Optional[str] = None

@dataclass
class PerformanceMetrics:
    """Performance metrics for monitoring"""
    duration_ms: float
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    database_queries: Optional[int] = None
    cache_hits: Optional[int] = None
    cache_misses: Optional[int] = None

class EnterpriseLogger:
    """
    Enterprise-level logging system with structured logging capabilities
    """
    
    def __init__(self, service_name: str, environment: str = "production"):
        self.service_name = service_name
        self.environment = environment
        self.logger = logging.getLogger(f"farmchecker.{service_name}")
        self.logger.setLevel(logging.INFO)
        
        # Configure handlers
        self._setup_handlers()
        
        # Performance tracking
        self.performance_data = {}
        
    def _setup_handlers(self):
        """Setup logging handlers"""
        # Console handler for development
        if self.environment == "development":
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(console_handler)
        
        # File handler for production
        if self.environment == "production":
            log_dir = "/var/log/farmchecker"
            os.makedirs(log_dir, exist_ok=True)
            
            # Application logs
            app_handler = logging.FileHandler(f"{log_dir}/{self.service_name}.log")
            app_handler.setFormatter(logging.Formatter('%(message)s'))
            self.logger.addHandler(app_handler)
            
            # Error logs
            error_handler = logging.FileHandler(f"{log_dir}/{self.service_name}_errors.log")
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(logging.Formatter('%(message)s'))
            self.logger.addHandler(error_handler)
            
            # Performance logs
            perf_handler = logging.FileHandler(f"{log_dir}/{self.service_name}_performance.log")
            perf_handler.setLevel(logging.INFO)
            perf_handler.setFormatter(logging.Formatter('%(message)s'))
            self.logger.addHandler(perf_handler)
    
    def _create_log_entry(self, 
                         level: LogLevel,
                         event_type: EventType,
                         message: str,
                         context: Optional[LogContext] = None,
                         data: Optional[Dict[str, Any]] = None,
                         performance: Optional[PerformanceMetrics] = None,
                         error: Optional[Exception] = None) -> Dict[str, Any]:
        """Create a structured log entry"""
        
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level.value,
            "event_type": event_type.value,
            "service": self.service_name,
            "environment": self.environment,
            "message": message,
            "log_id": str(uuid.uuid4())
        }
        
        # Add context
        if context:
            log_entry["context"] = asdict(context)
        
        # Add data
        if data:
            log_entry["data"] = data
        
        # Add performance metrics
        if performance:
            log_entry["performance"] = asdict(performance)
        
        # Add error information
        if error:
            log_entry["error"] = {
                "type": type(error).__name__,
                "message": str(error),
                "traceback": traceback.format_exc()
            }
        
        return log_entry
    
    def log(self, 
            level: LogLevel,
            event_type: EventType,
            message: str,
            context: Optional[LogContext] = None,
            data: Optional[Dict[str, Any]] = None,
            performance: Optional[PerformanceMetrics] = None,
            error: Optional[Exception] = None):
        """Log a structured event"""
        
        log_entry = self._create_log_entry(
            level, event_type, message, context, data, performance, error
        )
        
        # Convert to JSON string
        log_message = json.dumps(log_entry, default=str)
        
        # Log based on level
        if level == LogLevel.DEBUG:
            self.logger.debug(log_message)
        elif level == LogLevel.INFO:
            self.logger.info(log_message)
        elif level == LogLevel.WARNING:
            self.logger.warning(log_message)
        elif level == LogLevel.ERROR:
            self.logger.error(log_message)
        elif level == LogLevel.CRITICAL:
            self.logger.critical(log_message)
        else:
            # Custom levels
            self.logger.info(log_message)
    
    def log_api_request(self, 
                       method: str,
                       endpoint: str,
                       request_id: str,
                       user_id: Optional[str] = None,
                       ip_address: Optional[str] = None,
                       user_agent: Optional[str] = None,
                       request_data: Optional[Dict[str, Any]] = None):
        """Log API request"""
        
        context = LogContext(
            request_id=request_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            method=method
        )
        
        data = {"request_data": request_data} if request_data else None
        
        self.log(
            level=LogLevel.INFO,
            event_type=EventType.API_REQUEST,
            message=f"API Request: {method} {endpoint}",
            context=context,
            data=data
        )
    
    def log_api_response(self,
                        request_id: str,
                        status_code: int,
                        response_time_ms: float,
                        response_size_bytes: Optional[int] = None,
                        error: Optional[Exception] = None):
        """Log API response"""
        
        context = LogContext(request_id=request_id)
        
        performance = PerformanceMetrics(duration_ms=response_time_ms)
        
        level = LogLevel.ERROR if error else LogLevel.INFO
        event_type = EventType.API_ERROR if error else EventType.API_RESPONSE
        
        data = {
            "status_code": status_code,
            "response_size_bytes": response_size_bytes
        }
        
        self.log(
            level=level,
            event_type=event_type,
            message=f"API Response: {status_code} ({response_time_ms:.2f}ms)",
            context=context,
            data=data,
            performance=performance,
            error=error
        )
    
    def log_crawler_event(self,
                         crawler_name: str,
                         event_type: EventType,
                         message: str,
                         data_count: Optional[int] = None,
                         error: Optional[Exception] = None,
                         performance: Optional[PerformanceMetrics] = None):
        """Log crawler events"""
        
        data = {
            "crawler_name": crawler_name,
            "data_count": data_count
        }
        
        level = LogLevel.ERROR if error else LogLevel.INFO
        
        self.log(
            level=level,
            event_type=event_type,
            message=message,
            data=data,
            performance=performance,
            error=error
        )
    
    def log_business_metric(self,
                           metric_name: str,
                           metric_value: Union[int, float, str],
                           category: str,
                           user_id: Optional[str] = None):
        """Log business metrics"""
        
        context = LogContext(request_id=str(uuid.uuid4()), user_id=user_id)
        
        data = {
            "metric_name": metric_name,
            "metric_value": metric_value,
            "category": category
        }
        
        self.log(
            level=LogLevel.BUSINESS,
            event_type=EventType.BUSINESS_METRIC,
            message=f"Business Metric: {metric_name} = {metric_value}",
            context=context,
            data=data
        )
    
    def log_security_event(self,
                          event_type: EventType,
                          message: str,
                          user_id: Optional[str] = None,
                          ip_address: Optional[str] = None,
                          details: Optional[Dict[str, Any]] = None):
        """Log security events"""
        
        context = LogContext(
            request_id=str(uuid.uuid4()),
            user_id=user_id,
            ip_address=ip_address
        )
        
        self.log(
            level=LogLevel.SECURITY,
            event_type=event_type,
            message=message,
            context=context,
            data=details
        )
    
    def log_performance_metric(self,
                              metric_name: str,
                              value: float,
                              unit: str,
                              threshold: Optional[float] = None):
        """Log performance metrics"""
        
        performance = PerformanceMetrics(duration_ms=value)
        
        data = {
            "metric_name": metric_name,
            "unit": unit,
            "threshold": threshold,
            "is_above_threshold": threshold and value > threshold
        }
        
        level = LogLevel.WARNING if (threshold and value > threshold) else LogLevel.PERFORMANCE
        
        self.log(
            level=level,
            event_type=EventType.PERFORMANCE_METRIC,
            message=f"Performance: {metric_name} = {value}{unit}",
            data=data,
            performance=performance
        )
    
    def performance_monitor(self, operation_name: str):
        """Decorator for performance monitoring"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = self._get_memory_usage()
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Calculate metrics
                    duration = (time.time() - start_time) * 1000
                    end_memory = self._get_memory_usage()
                    memory_used = end_memory - start_memory if end_memory and start_memory else None
                    
                    performance = PerformanceMetrics(
                        duration_ms=duration,
                        memory_usage_mb=memory_used
                    )
                    
                    self.log(
                        level=LogLevel.PERFORMANCE,
                        event_type=EventType.PERFORMANCE_METRIC,
                        message=f"Operation completed: {operation_name}",
                        data={"operation_name": operation_name},
                        performance=performance
                    )
                    
                    return result
                    
                except Exception as e:
                    duration = (time.time() - start_time) * 1000
                    performance = PerformanceMetrics(duration_ms=duration)
                    
                    self.log(
                        level=LogLevel.ERROR,
                        event_type=EventType.PERFORMANCE_METRIC,
                        message=f"Operation failed: {operation_name}",
                        data={"operation_name": operation_name},
                        performance=performance,
                        error=e
                    )
                    raise
                    
            return wrapper
        return decorator
    
    def _get_memory_usage(self) -> Optional[float]:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except ImportError:
            return None
    
    def log_system_startup(self, version: str, config: Dict[str, Any]):
        """Log system startup"""
        self.log(
            level=LogLevel.INFO,
            event_type=EventType.SYSTEM_STARTUP,
            message=f"System startup: {self.service_name} v{version}",
            data={"version": version, "config": config}
        )
    
    def log_system_shutdown(self, reason: str = "normal"):
        """Log system shutdown"""
        self.log(
            level=LogLevel.INFO,
            event_type=EventType.SYSTEM_SHUTDOWN,
            message=f"System shutdown: {self.service_name} - {reason}",
            data={"reason": reason}
        )

# Global logger instances
web_logger = EnterpriseLogger("web-app", os.getenv("ENVIRONMENT", "production"))
api_logger = EnterpriseLogger("api", os.getenv("ENVIRONMENT", "production"))
crawler_logger = EnterpriseLogger("crawler", os.getenv("ENVIRONMENT", "production"))
database_logger = EnterpriseLogger("database", os.getenv("ENVIRONMENT", "production"))

def get_logger(service_name: str) -> EnterpriseLogger:
    """Get a logger instance for a specific service"""
    return EnterpriseLogger(service_name, os.getenv("ENVIRONMENT", "production")) 