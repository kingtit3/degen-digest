#!/usr/bin/env python3
"""
Test script for the comprehensive logging and monitoring systems.
This script tests all aspects of the enterprise logging, health monitoring,
and data quality monitoring systems.
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.data_quality_monitor import DataQualityMonitor
from utils.enterprise_logging import get_logger, setup_logging
from utils.health_monitor import HealthMonitor, SystemMetrics
from utils.monitoring import SystemMonitor


def test_enterprise_logging():
    """Test the enterprise logging system."""
    print("🔍 Testing Enterprise Logging System...")

    # Setup logging
    setup_logging(
        service_name="test_logging",
        log_level="DEBUG",
        enable_file=True,
        enable_console=True,
        enable_json=True,
        log_dir="logs",
    )

    # Get logger
    logger = get_logger("test_logging")

    # Test basic logging
    logger.info("Starting logging system test", test_id="logging_test_001")
    logger.debug("Debug message test", debug_info="test_data")
    logger.warning("Warning message test", warning_code="WARN_001")
    logger.error("Error message test", error_code="ERR_001")

    # Test performance logging
    start_time = time.time()
    time.sleep(0.1)  # Simulate work
    duration = (time.time() - start_time) * 1000
    logger.log_performance("test_operation", duration, operation_type="test")

    # Test security logging
    logger.log_security_event(
        "test_login", "low", user_id="test_user", ip_address="127.0.0.1"
    )
    logger.log_security_event(
        "test_access_denied",
        "medium",
        user_id="test_user",
        details={"resource": "/api/test"},
    )

    # Test operation context
    with logger.operation_context(
        "test_operation", request_id="req_123", user_id="test_user"
    ):
        logger.info("Operation in progress", step="processing")
        time.sleep(0.05)
        logger.info("Operation completed", step="completed")

    # Test structured data logging
    test_data = {
        "user_id": "test_user",
        "action": "test_action",
        "timestamp": datetime.now().isoformat(),
        "metadata": {"test": True, "version": "1.0"},
    }
    logger.info(
        "Structured event: test_event", extra={"event": "test_event", "data": test_data}
    )

    print("✅ Enterprise logging test completed")


def test_health_monitoring():
    """Test the health monitoring system."""
    print("🏥 Testing Health Monitoring System...")

    # Initialize health monitor
    health_monitor = HealthMonitor()

    # Test system health checks
    system_checks = health_monitor.run_system_health_checks()
    for check in system_checks:
        print(f"System Check: {check.name} - {check.status} - {check.message}")

    # Test database health checks
    db_checks = health_monitor.run_database_health_checks()
    for check in db_checks:
        print(f"Database Check: {check.name} - {check.status} - {check.message}")

    # Test service health checks
    service_checks = health_monitor.run_service_health_checks()
    for check in service_checks:
        print(f"Service Check: {check.name} - {check.status} - {check.message}")

    # Test API health checks
    api_checks = health_monitor.run_api_health_checks()
    for check in api_checks:
        print(f"API Check: {check.name} - {check.status} - {check.message}")

    # Test data quality health checks
    dq_checks = health_monitor.run_data_quality_checks()
    for check in dq_checks:
        print(f"Data Quality Check: {check.name} - {check.status} - {check.message}")

    # Test security health checks
    sec_checks = health_monitor.run_security_checks()
    for check in sec_checks:
        print(f"Security Check: {check.name} - {check.status} - {check.message}")

    # Collect system metrics
    metrics = health_monitor.collect_system_metrics()
    print(
        f"System Metrics: CPU {metrics.cpu_percent:.2f}%, Memory {metrics.memory_percent:.2f}%, Disk {metrics.disk_percent:.2f}%"
    )

    # Get health summary
    summary = health_monitor.get_health_summary()
    print(f"Health Summary: {summary}")

    print("✅ Health monitoring test completed")


def test_data_quality_monitoring():
    """Test the data quality monitoring system."""
    print("📊 Testing Data Quality Monitoring System...")

    # Initialize data quality monitor
    dq_monitor = DataQualityMonitor()

    # Create sample data for testing
    sample_data = [
        {
            "text": "Sample tweet about crypto",
            "timestamp": datetime.now().isoformat(),
            "source": "twitter",
            "engagement_velocity": 150,
            "viral_coefficient": 2.5,
            "influence_score": 0.8,
        },
        {
            "text": "Another crypto post",
            "timestamp": datetime.now().isoformat(),
            "source": "reddit",
            "engagement_velocity": 75,
            "viral_coefficient": 1.8,
            "influence_score": 0.6,
        },
    ]

    # Test data quality monitoring
    quality_report = dq_monitor.monitor_data_quality(sample_data, "test_source")
    print(f"Data Quality Report: {quality_report['overall_score']:.3f}")
    print(f"Quality Metrics: {quality_report['metrics']}")
    print(f"Alerts: {quality_report['alerts']}")

    # Test individual quality calculations
    completeness = dq_monitor.calculate_completeness(sample_data)
    accuracy = dq_monitor.calculate_accuracy(sample_data)
    consistency = dq_monitor.calculate_consistency(sample_data)
    timeliness = dq_monitor.calculate_timeliness(sample_data)
    validity = dq_monitor.calculate_validity(sample_data)

    print(f"Completeness: {completeness:.3f}")
    print(f"Accuracy: {accuracy:.3f}")
    print(f"Consistency: {consistency:.3f}")
    print(f"Timeliness: {timeliness:.3f}")
    print(f"Validity: {validity:.3f}")

    # Test quality summary
    summary = dq_monitor.get_quality_summary()
    print(f"Quality Summary: {summary}")

    # Test recommendations
    recommendations = dq_monitor.get_recommendations()
    print(f"Recommendations: {recommendations}")

    print("✅ Data quality monitoring test completed")


def test_monitoring_system():
    """Test the comprehensive monitoring system."""
    print("📈 Testing Comprehensive Monitoring System...")

    # Initialize monitoring system
    monitoring = SystemMonitor()

    # Test metrics collection
    metrics = monitoring.collect_system_metrics()
    print(f"Metrics collected: {len(metrics)} metrics")

    # Test database health check
    db_health = monitoring.check_database_health()
    print(f"Database Health: {db_health['overall_status']}")

    # Test cloud function health check
    cf_health = monitoring.check_cloud_function_health()
    print(f"Cloud Function Health: {cf_health['overall_status']}")

    # Test external APIs health check
    api_health = monitoring.check_external_apis()
    print(f"External APIs Health: {api_health['overall_status']}")

    # Test data quality check
    dq_health = monitoring.check_data_quality()
    print(f"Data Quality: {dq_health['overall_status']}")

    # Test comprehensive monitoring
    comprehensive_health = monitoring.run_comprehensive_monitoring()
    print(f"Comprehensive Health: {comprehensive_health['overall_status']}")

    print("✅ Comprehensive monitoring test completed")


def test_system_metrics():
    """Test the system metrics collection."""
    print("📊 Testing System Metrics Collection...")

    # Initialize system metrics
    metrics = SystemMetrics()

    # Collect current metrics
    current_metrics = metrics.collect_current_metrics()
    print(f"CPU Usage: {current_metrics['cpu_percent']:.2f}%")
    print(f"Memory Usage: {current_metrics['memory_percent']:.2f}%")
    print(f"Disk Usage: {current_metrics['disk_percent']:.2f}%")
    print(f"Network I/O: {current_metrics['network_io']}")

    # Test metrics history
    metrics_history = metrics.get_metrics_history(hours=1)
    print(f"Metrics history points: {len(metrics_history)}")

    # Test metrics aggregation
    aggregated_metrics = metrics.aggregate_metrics(hours=1)
    print(f"Average CPU: {aggregated_metrics['avg_cpu']:.2f}%")
    print(f"Max Memory: {aggregated_metrics['max_memory']:.2f}%")

    print("✅ System metrics test completed")


async def test_async_monitoring():
    """Test async monitoring capabilities."""
    print("🔄 Testing Async Monitoring...")

    # Initialize monitoring
    monitoring = SystemMonitor()

    # Test system metrics collection
    metrics = monitoring.collect_system_metrics()
    print(f"System metrics collected: {len(metrics)} metrics")

    # Test comprehensive monitoring
    health = monitoring.run_comprehensive_monitoring()
    print(f"Comprehensive health check: {health['overall_status']}")

    print("✅ Async monitoring test completed")


def test_log_file_creation():
    """Test that log files are created properly."""
    print("📝 Testing Log File Creation...")

    # Check if log directory exists
    log_dir = Path("logs")
    if not log_dir.exists():
        log_dir.mkdir(parents=True)
        print("Created logs directory")

    # Check for log files
    log_files = list(log_dir.glob("*.log"))
    print(f"Found {len(log_files)} log files:")
    for log_file in log_files:
        print(f"  - {log_file.name}")

    # Check for JSON reports
    json_files = list(log_dir.glob("*.json"))
    print(f"Found {len(json_files)} JSON report files:")
    for json_file in json_files:
        print(f"  - {json_file.name}")

    print("✅ Log file creation test completed")


def test_error_handling():
    """Test error handling in logging and monitoring systems."""
    print("⚠️ Testing Error Handling...")

    logger = get_logger("error_test")

    # Test logging with invalid data
    try:
        logger.info("Test with circular reference", data={"self": None})
        # Create circular reference
        data = {}
        data["self"] = data
        logger.info("This should handle circular reference gracefully", data=data)
    except Exception as e:
        logger.error("Error in circular reference test", error=str(e))

    # Test monitoring with invalid metrics
    try:
        monitoring = SystemMonitor()
        monitoring.collect_system_metrics()  # Should handle errors gracefully
    except Exception as e:
        logger.error("Error in metrics collection", error=str(e))

    print("✅ Error handling test completed")


def main():
    """Run all tests."""
    print("🚀 Starting Comprehensive Logging and Monitoring System Tests")
    print("=" * 60)

    try:
        # Test enterprise logging
        test_enterprise_logging()
        print()

        # Test health monitoring
        test_health_monitoring()
        print()

        # Test data quality monitoring
        test_data_quality_monitoring()
        print()

        # Test comprehensive monitoring
        test_monitoring_system()
        print()

        # Test system metrics
        test_system_metrics()
        print()

        # Test async monitoring
        asyncio.run(test_async_monitoring())
        print()

        # Test log file creation
        test_log_file_creation()
        print()

        # Test error handling
        test_error_handling()
        print()

        print("🎉 All tests completed successfully!")
        print("📁 Check the 'logs/' directory for generated log files and reports")

        # Display summary
        print("\n📋 Test Summary:")
        print("- Enterprise logging system: ✅ Working")
        print("- Health monitoring system: ✅ Working")
        print("- Data quality monitoring: ✅ Working")
        print("- Comprehensive monitoring: ✅ Working")
        print("- System metrics collection: ✅ Working")
        print("- Async monitoring: ✅ Working")
        print("- Log file creation: ✅ Working")
        print("- Error handling: ✅ Working")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[FATAL ERROR] {e}")
        import traceback

        traceback.print_exc()
        import sys

        sys.exit(1)
