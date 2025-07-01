#!/usr/bin/env python3
"""
Comprehensive monitoring and logging test script for Degen Digest
"""

import sys
import os
import time
import json
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.advanced_logging import (
    setup_logging, get_logger, log_function_call, log_database_operation,
    log_api_call, log_cloud_function_execution, log_performance_metrics,
    log_system_health, log_data_quality_issue, log_security_event, log_business_event
)
from utils.monitoring import system_monitor
from storage.db import engine, Tweet, RedditPost, Digest, LLMUsage
from sqlmodel import Session, select, func

def test_logging_system():
    """Test the comprehensive logging system"""
    print("🧪 Testing Comprehensive Logging System...")
    
    # Setup logging
    setup_logging(level="DEBUG", log_file="logs/test_monitoring.log")
    logger = get_logger(__name__)
    
    # Test basic logging
    logger.info("Starting comprehensive logging test")
    logger.debug("Debug message test")
    logger.warning("Warning message test")
    logger.error("Error message test")
    
    # Test structured logging
    logger.info("structured_log_test", 
               test_type="comprehensive",
               timestamp=datetime.now(timezone.utc).isoformat(),
               features=["structured", "performance", "monitoring"])
    
    print("✅ Basic logging tests completed")

def test_function_logging():
    """Test function call logging decorators"""
    print("🧪 Testing Function Call Logging...")
    
    logger = get_logger(__name__)
    
    @log_function_call
    def test_function(param1, param2, kwarg1="default"):
        """Test function for logging"""
        time.sleep(0.1)  # Simulate work
        return f"Result: {param1} + {param2} + {kwarg1}"
    
    @log_database_operation("test_query")
    def test_database_operation():
        """Test database operation logging"""
        with Session(engine) as session:
            count = session.exec(select(func.count()).select_from(Tweet)).one()
            return count
    
    @log_api_call("test_api", "/test/endpoint")
    def test_api_call():
        """Test API call logging"""
        time.sleep(0.05)  # Simulate API call
        return {"status": "success", "data": "test"}
    
    # Execute test functions
    try:
        result1 = test_function("value1", "value2", kwarg1="custom")
        logger.info(f"Function result: {result1}")
        
        result2 = test_database_operation()
        logger.info(f"Database result: {result2}")
        
        result3 = test_api_call()
        logger.info(f"API result: {result3}")
        
        print("✅ Function logging tests completed")
        
    except Exception as e:
        logger.error(f"Function logging test failed: {e}")
        print(f"❌ Function logging test failed: {e}")

def test_performance_logging():
    """Test performance metrics logging"""
    print("🧪 Testing Performance Metrics Logging...")
    
    logger = get_logger(__name__)
    
    # Test performance metrics
    log_performance_metrics("test_operation", 
                          duration_seconds=1.5,
                          items_processed=100,
                          memory_usage_mb=50.5,
                          cpu_usage_percent=25.3)
    
    # Test system health logging
    log_system_health("test_component", "healthy", {
        "response_time_ms": 150,
        "error_rate": 0.01,
        "throughput": 1000
    })
    
    # Test data quality logging
    log_data_quality_issue("duplicate_data", "medium", {
        "duplicate_count": 5,
        "total_records": 1000,
        "duplicate_percentage": 0.5
    })
    
    # Test security event logging
    log_security_event("api_rate_limit", "warning", {
        "api_endpoint": "/api/data",
        "rate_limit": 100,
        "current_requests": 95
    })
    
    # Test business event logging
    log_business_event("digest_generated", {
        "digest_id": "test_123",
        "content_items": 50,
        "generation_time": 30.5
    })
    
    print("✅ Performance logging tests completed")

def test_monitoring_system():
    """Test the comprehensive monitoring system"""
    print("🧪 Testing Comprehensive Monitoring System...")
    
    logger = get_logger(__name__)
    
    try:
        # Run comprehensive monitoring
        logger.info("Starting comprehensive system monitoring test")
        
        metrics = system_monitor.run_comprehensive_monitoring()
        
        # Display results
        print(f"📊 Monitoring Results:")
        print(f"  - System metrics collected: {'system' in metrics}")
        print(f"  - Database health checked: {'database' in metrics}")
        print(f"  - Cloud function status: {'cloud_function' in metrics}")
        print(f"  - API health monitored: {'apis' in metrics}")
        print(f"  - Data quality assessed: {'data_quality' in metrics}")
        
        # Save test results
        test_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "test_type": "comprehensive_monitoring",
            "metrics_collected": list(metrics.keys()),
            "overall_status": "success"
        }
        
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / "monitoring_test_results.json", 'w') as f:
            json.dump(test_results, f, indent=2, default=str)
        
        print("✅ Monitoring system tests completed")
        
    except Exception as e:
        logger.error(f"Monitoring test failed: {e}")
        print(f"❌ Monitoring test failed: {e}")

def test_database_monitoring():
    """Test database-specific monitoring"""
    print("🧪 Testing Database Monitoring...")
    
    logger = get_logger(__name__)
    
    try:
        # Test database health check
        db_health = system_monitor.check_database_health()
        
        print(f"📊 Database Health Results:")
        print(f"  - Overall status: {db_health.get('overall_status', 'unknown')}")
        print(f"  - Tweet count: {db_health.get('data_counts', {}).get('total_tweets', 0)}")
        print(f"  - Reddit count: {db_health.get('data_counts', {}).get('total_reddit_posts', 0)}")
        print(f"  - Data freshness: {db_health.get('data_freshness', {}).get('status', 'unknown')}")
        
        # Test data quality check
        data_quality = system_monitor.check_data_quality()
        
        print(f"📈 Data Quality Results:")
        print(f"  - Quality score: {data_quality.get('data_quality_score', 0)}")
        print(f"  - Duplicate tweets: {data_quality.get('duplicate_tweets', 0)}")
        print(f"  - Malformed tweets: {data_quality.get('malformed_tweets', 0)}")
        
        print("✅ Database monitoring tests completed")
        
    except Exception as e:
        logger.error(f"Database monitoring test failed: {e}")
        print(f"❌ Database monitoring test failed: {e}")

def test_alert_generation():
    """Test alert generation system"""
    print("🧪 Testing Alert Generation...")
    
    logger = get_logger(__name__)
    
    try:
        # Create test metrics that should generate alerts
        test_metrics = {
            "system": {
                "cpu_percent": 85,  # Should trigger warning
                "memory_percent": 90  # Should trigger warning
            },
            "database": {
                "overall_status": "critical"  # Should trigger critical alert
            },
            "data_quality": {
                "data_quality_score": 65  # Should trigger warning
            }
        }
        
        # Generate alerts
        alerts = system_monitor.generate_alerts(test_metrics)
        
        print(f"🚨 Alert Generation Results:")
        print(f"  - Total alerts generated: {len(alerts)}")
        
        critical_alerts = [a for a in alerts if a.get("level") == "critical"]
        warning_alerts = [a for a in alerts if a.get("level") == "warning"]
        
        print(f"  - Critical alerts: {len(critical_alerts)}")
        print(f"  - Warning alerts: {len(warning_alerts)}")
        
        # Display alert details
        for alert in alerts:
            print(f"    - {alert.get('level').upper()}: {alert.get('message')}")
        
        print("✅ Alert generation tests completed")
        
    except Exception as e:
        logger.error(f"Alert generation test failed: {e}")
        print(f"❌ Alert generation test failed: {e}")

def test_log_file_analysis():
    """Test log file analysis and verification"""
    print("🧪 Testing Log File Analysis...")
    
    log_file = Path("logs/test_monitoring.log")
    
    if log_file.exists():
        # Read and analyze log file
        with open(log_file, 'r') as f:
            log_content = f.read()
        
        # Count different log levels
        info_count = log_content.count("INFO")
        debug_count = log_content.count("DEBUG")
        warning_count = log_content.count("WARNING")
        error_count = log_content.count("ERROR")
        
        print(f"📋 Log File Analysis:")
        print(f"  - INFO messages: {info_count}")
        print(f"  - DEBUG messages: {debug_count}")
        print(f"  - WARNING messages: {warning_count}")
        print(f"  - ERROR messages: {error_count}")
        print(f"  - Total log entries: {info_count + debug_count + warning_count + error_count}")
        
        # Check for structured logging
        json_entries = log_content.count('"timestamp"')
        print(f"  - Structured JSON entries: {json_entries}")
        
        print("✅ Log file analysis completed")
    else:
        print("⚠️ Log file not found - skipping analysis")

def main():
    """Run all monitoring and logging tests"""
    print("🚀 Starting Comprehensive Monitoring and Logging Tests")
    print("=" * 60)
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Run all tests
    test_logging_system()
    print()
    
    test_function_logging()
    print()
    
    test_performance_logging()
    print()
    
    test_monitoring_system()
    print()
    
    test_database_monitoring()
    print()
    
    test_alert_generation()
    print()
    
    test_log_file_analysis()
    print()
    
    print("=" * 60)
    print("🎉 All monitoring and logging tests completed!")
    print()
    print("📁 Generated files:")
    print("  - logs/test_monitoring.log (comprehensive test logs)")
    print("  - output/monitoring_test_results.json (test results)")
    print("  - output/system_metrics.json (system metrics)")
    print("  - output/system_alerts.json (generated alerts)")
    print()
    print("🔍 Next steps:")
    print("  1. Check the Health Monitor dashboard page")
    print("  2. Review the generated log files")
    print("  3. Verify metrics and alerts are being collected")
    print("  4. Test the cloud function with comprehensive logging")

if __name__ == "__main__":
    main() 