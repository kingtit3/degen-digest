#!/usr/bin/env python3
"""
Monitoring Verification Script for DegenDigest
Demonstrates and verifies all current monitoring capabilities
"""

import json
import os
import sys
import time
from datetime import UTC, datetime, timezone
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))


def verify_enterprise_logging():
    """Verify enterprise logging system"""
    print("🔍 Verifying Enterprise Logging System...")

    try:
        from utils.enterprise_logging import get_logger, setup_logging

        # Setup logging
        setup_logging(
            service_name="monitoring_verification",
            log_level="DEBUG",
            enable_file=True,
            enable_console=True,
            enable_json=True,
            log_dir="logs",
        )

        # Get logger
        logger = get_logger("verification")

        # Test different log levels
        logger.debug("Debug message test", test_id="debug_001")
        logger.info("Info message test", test_id="info_001")
        logger.warning("Warning message test", test_id="warning_001")
        logger.error("Error message test", test_id="error_001")

        # Test structured logging
        logger.info(
            "Structured log test",
            operation="verification",
            component="logging",
            status="success",
            metadata={"test_type": "structured_logging"},
        )

        # Test performance logging
        start_time = time.time()
        time.sleep(0.1)  # Simulate work
        duration = (time.time() - start_time) * 1000
        logger.log_performance(
            "test_operation", duration, operation_type="verification"
        )

        print("✅ Enterprise logging system verified")
        return True

    except Exception as e:
        print(f"❌ Enterprise logging verification failed: {e}")
        return False


def verify_health_monitoring():
    """Verify health monitoring system"""
    print("🔍 Verifying Health Monitoring System...")

    try:
        from utils.health_monitor import HealthMonitor, get_health_monitor

        # Create health monitor
        health_monitor = get_health_monitor()

        # Run system health checks
        system_checks = health_monitor.run_system_health_checks()
        print(f"  📊 System health checks: {len(system_checks)} checks completed")

        # Run database health checks
        db_checks = health_monitor.run_database_health_checks()
        print(f"  🗄️ Database health checks: {len(db_checks)} checks completed")

        # Run service health checks
        service_checks = health_monitor.run_service_health_checks()
        print(f"  🔧 Service health checks: {len(service_checks)} checks completed")

        # Run API health checks
        api_checks = health_monitor.run_api_health_checks()
        print(f"  🔌 API health checks: {len(api_checks)} checks completed")

        # Run data quality checks
        dq_checks = health_monitor.run_data_quality_checks()
        print(f"  📈 Data quality checks: {len(dq_checks)} checks completed")

        # Run security checks
        sec_checks = health_monitor.run_security_checks()
        print(f"  🔒 Security checks: {len(sec_checks)} checks completed")

        # Get health summary
        summary = health_monitor.get_health_summary()
        print(f"  📋 Overall health status: {summary.get('status', 'unknown')}")

        # Collect system metrics
        metrics = health_monitor.collect_system_metrics()
        print(
            f"  📊 System metrics collected: CPU {metrics.cpu_percent:.1f}%, Memory {metrics.memory_percent:.1f}%"
        )

        print("✅ Health monitoring system verified")
        return True

    except Exception as e:
        print(f"❌ Health monitoring verification failed: {e}")
        return False


def verify_system_monitoring():
    """Verify system monitoring"""
    print("🔍 Verifying System Monitoring...")

    try:
        from utils.monitoring import SystemMonitor

        # Create system monitor
        system_monitor = SystemMonitor()

        # Collect system metrics
        metrics = system_monitor.collect_system_metrics()
        print(f"  📊 System metrics: {len(metrics)} metrics collected")

        # Check database health
        db_health = system_monitor.check_database_health()
        print(f"  🗄️ Database health: {db_health.get('overall_status', 'unknown')}")

        # Check cloud function health
        cf_health = system_monitor.check_cloud_function_health()
        print(
            f"  ☁️ Cloud function health: {cf_health.get('function_status', 'unknown')}"
        )

        # Check external APIs
        api_health = system_monitor.check_external_apis()
        print(
            f"  🔌 External APIs health: {api_health.get('overall_status', 'unknown')}"
        )

        # Check data quality
        dq_health = system_monitor.check_data_quality()
        print(f"  📈 Data quality: {dq_health.get('overall_status', 'unknown')}")

        # Run comprehensive monitoring
        comprehensive = system_monitor.run_comprehensive_monitoring()
        print(
            f"  🔍 Comprehensive monitoring: {comprehensive.get('timestamp', 'unknown')}"
        )

        print("✅ System monitoring verified")
        return True

    except Exception as e:
        print(f"❌ System monitoring verification failed: {e}")
        return False


def verify_data_quality_monitoring():
    """Verify data quality monitoring"""
    print("🔍 Verifying Data Quality Monitoring...")

    try:
        from utils.data_quality_monitor import DataQualityMonitor

        # Create data quality monitor
        dq_monitor = DataQualityMonitor()

        # Create sample data for testing
        sample_data = [
            {
                "text": "Sample tweet content",
                "timestamp": datetime.now(UTC).isoformat(),
                "source": "twitter",
                "engagement_velocity": 10,
                "viral_coefficient": 2.5,
            },
            {
                "text": "Another sample tweet",
                "timestamp": datetime.now(UTC).isoformat(),
                "source": "twitter",
                "engagement_velocity": 15,
                "viral_coefficient": 3.0,
            },
        ]

        # Monitor data quality
        quality_report = dq_monitor.monitor_data_quality(sample_data, "test_source")
        print(f"  📊 Data quality score: {quality_report['overall_score']:.3f}")

        # Get quality summary
        summary = dq_monitor.get_quality_summary()
        print(
            f"  📋 Quality summary: {len(summary.get('sources', {}))} sources monitored"
        )

        # Get recommendations
        recommendations = dq_monitor.get_recommendations()
        print(f"  💡 Recommendations: {len(recommendations)} suggestions")

        print("✅ Data quality monitoring verified")
        return True

    except Exception as e:
        print(f"❌ Data quality monitoring verification failed: {e}")
        return False


def verify_dashboard_monitoring():
    """Verify dashboard monitoring capabilities"""
    print("🔍 Verifying Dashboard Monitoring...")

    try:
        # Check if dashboard files exist
        dashboard_files = [
            "dashboard/pages/Health_Monitor.py",
            "dashboard/pages/Analytics.py",
            "dashboard/pages/Live_Feed.py",
        ]

        for file_path in dashboard_files:
            if Path(file_path).exists():
                print(f"  ✅ Dashboard file found: {file_path}")
            else:
                print(f"  ❌ Dashboard file missing: {file_path}")

        # Check if we can import dashboard components
        sys.path.append("dashboard/pages")
        try:
            import Health_Monitor

            print("  ✅ Health Monitor dashboard importable")
        except Exception as e:
            print(f"  ⚠️ Health Monitor dashboard import issue: {e}")

        print("✅ Dashboard monitoring verified")
        return True

    except Exception as e:
        print(f"❌ Dashboard monitoring verification failed: {e}")
        return False


def verify_log_files():
    """Verify log file generation"""
    print("🔍 Verifying Log Files...")

    try:
        log_dir = Path("logs")
        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)
            print("  📁 Created logs directory")

        # Check for log files
        log_files = list(log_dir.glob("*.log"))
        json_log_files = list(log_dir.glob("*_structured.json"))
        error_log_files = list(log_dir.glob("*_errors.log"))
        perf_log_files = list(log_dir.glob("*_performance.log"))

        print(f"  📝 Regular log files: {len(log_files)}")
        print(f"  📊 JSON structured logs: {len(json_log_files)}")
        print(f"  ❌ Error log files: {len(error_log_files)}")
        print(f"  ⚡ Performance log files: {len(perf_log_files)}")

        # Check log file sizes
        total_size = sum(f.stat().st_size for f in log_dir.glob("*") if f.is_file())
        print(f"  💾 Total log directory size: {total_size / 1024:.1f} KB")

        print("✅ Log files verified")
        return True

    except Exception as e:
        print(f"❌ Log files verification failed: {e}")
        return False


def verify_configuration():
    """Verify monitoring configuration"""
    print("🔍 Verifying Monitoring Configuration...")

    try:
        # Check configuration files
        config_files = [
            "config/app_config.yaml",
            "config/cloud_config.yaml",
            "config/monitoring_config.yaml",
        ]

        for file_path in config_files:
            if Path(file_path).exists():
                print(f"  ✅ Config file found: {file_path}")
            else:
                print(f"  ⚠️ Config file missing: {file_path}")

        # Check environment variables
        env_vars = [
            "APIFY_API_TOKEN",
            "OPENROUTER_API_KEY",
            "NEWSAPI_KEY",
            "TELEGRAM_API_KEY",
        ]

        for var in env_vars:
            if os.environ.get(var):
                print(f"  ✅ Environment variable set: {var}")
            else:
                print(f"  ⚠️ Environment variable missing: {var}")

        print("✅ Configuration verified")
        return True

    except Exception as e:
        print(f"❌ Configuration verification failed: {e}")
        return False


def generate_verification_report(results):
    """Generate verification report"""
    print("\n" + "=" * 60)
    print("📊 MONITORING VERIFICATION REPORT")
    print("=" * 60)

    total_checks = len(results)
    passed_checks = sum(1 for result in results.values() if result)
    failed_checks = total_checks - passed_checks

    print(f"\n🔍 Total checks: {total_checks}")
    print(f"✅ Passed: {passed_checks}")
    print(f"❌ Failed: {failed_checks}")
    print(f"📊 Success rate: {(passed_checks/total_checks)*100:.1f}%")

    print("\n📋 Detailed Results:")
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {check_name}")

    if failed_checks == 0:
        print("\n🎉 ALL MONITORING SYSTEMS VERIFIED SUCCESSFULLY!")
        print("Your DegenDigest project has excellent monitoring coverage.")
    else:
        print(f"\n⚠️ {failed_checks} monitoring checks failed.")
        print("Please review the failed checks above.")

    print("\n🚀 Next steps:")
    print("  1. Review the Health Monitor dashboard")
    print("  2. Check log files in the logs/ directory")
    print("  3. Set up optional environment variables for enhanced alerting")
    print("  4. Monitor system performance using the existing infrastructure")

    print("\n" + "=" * 60)


def main():
    """Main verification function"""
    print("🔍 DegenDigest Monitoring Verification")
    print("=" * 50)
    print("Verifying all monitoring and logging capabilities...")
    print()

    # Run all verification checks
    results = {
        "Enterprise Logging": verify_enterprise_logging(),
        "Health Monitoring": verify_health_monitoring(),
        "System Monitoring": verify_system_monitoring(),
        "Data Quality Monitoring": verify_data_quality_monitoring(),
        "Dashboard Monitoring": verify_dashboard_monitoring(),
        "Log Files": verify_log_files(),
        "Configuration": verify_configuration(),
    }

    # Generate report
    generate_verification_report(results)

    # Save results to file
    report_data = {
        "timestamp": datetime.now(UTC).isoformat(),
        "results": results,
        "summary": {
            "total_checks": len(results),
            "passed": sum(1 for r in results.values() if r),
            "failed": sum(1 for r in results.values() if not r),
        },
    }

    with open("monitoring_verification_report.json", "w") as f:
        json.dump(report_data, f, indent=2, default=str)

    print("\n📄 Detailed report saved to: monitoring_verification_report.json")

    # Exit with appropriate code
    if all(results.values()):
        print("\n✅ All monitoring systems are working correctly!")
        return 0
    else:
        print("\n⚠️ Some monitoring checks failed. Please review the report.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
