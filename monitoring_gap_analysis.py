#!/usr/bin/env python3
"""
Monitoring Gap Analysis for DegenDigest
Identifies missing monitoring coverage and provides comprehensive recommendations
"""

import inspect
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Set


@dataclass
class MonitoringGap:
    """Represents a monitoring gap in the system"""

    component: str
    gap_type: str
    description: str
    severity: str  # "critical", "high", "medium", "low"
    recommendation: str
    files_affected: list[str] = None


class MonitoringGapAnalyzer:
    """
    Analyzes the DegenDigest project for monitoring gaps and provides recommendations
    """

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.gaps: list[MonitoringGap] = []
        self.components_analyzed: set[str] = set()

    def analyze_project(self) -> list[MonitoringGap]:
        """Perform comprehensive monitoring gap analysis"""
        print("🔍 Analyzing DegenDigest project for monitoring gaps...")

        # Analyze different components
        self._analyze_crawlers()
        self._analyze_data_processing()
        self._analyze_dashboard()
        self._analyze_cloud_functions()
        self._analyze_database()
        self._analyze_apis()
        self._analyze_security()
        self._analyze_performance()
        self._analyze_cost_tracking()
        self._analyze_alerting()
        self._analyze_logging()

        return self.gaps

    def _analyze_crawlers(self):
        """Analyze crawler monitoring coverage"""
        print("  📊 Analyzing crawlers...")

        crawler_files = [
            "scrapers/twitter_playwright_enhanced.py",
            "scrapers/twitter_apify.py",
            "scrapers/reddit_rss.py",
            "scrapers/newsapi_headlines.py",
            "scrapers/telegram_telethon.py",
            "scrapers/dexscreener.py",
            "scrapers/dexpaprika.py",
            "continuous_twitter_crawler.py",
            "continuous_dexscreener_crawler.py",
            "continuous_dexpaprika_crawler.py",
        ]

        for file_path in crawler_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self._analyze_file_monitoring(file_path, "crawler")

        # Check for missing crawler monitoring
        if not self._has_component_monitoring("crawler"):
            self.gaps.append(
                MonitoringGap(
                    component="crawler",
                    gap_type="monitoring",
                    description="No comprehensive crawler monitoring system",
                    severity="critical",
                    recommendation="Implement crawler-specific health checks, performance monitoring, and error tracking",
                    files_affected=crawler_files,
                )
            )

    def _analyze_data_processing(self):
        """Analyze data processing monitoring coverage"""
        print("  🔄 Analyzing data processing...")

        processor_files = [
            "processor/enhanced_viral_predictor.py",
            "processor/google_ai_summarizer.py",
            "processor/content_clustering.py",
            "processor/classifier.py",
            "processor/scorer.py",
            "processor/buzz.py",
            "enhanced_data_pipeline.py",
        ]

        for file_path in processor_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self._analyze_file_monitoring(file_path, "processor")

        # Check for missing AI processing monitoring
        if not self._has_component_monitoring("ai_processing"):
            self.gaps.append(
                MonitoringGap(
                    component="ai_processing",
                    gap_type="monitoring",
                    description="No AI processing performance and cost monitoring",
                    severity="high",
                    recommendation="Implement token usage tracking, cost monitoring, and performance metrics for AI operations",
                    files_affected=processor_files,
                )
            )

    def _analyze_dashboard(self):
        """Analyze dashboard monitoring coverage"""
        print("  📈 Analyzing dashboard...")

        dashboard_files = [
            "dashboard/main.py",
            "dashboard/app.py",
            "dashboard/pages/Health_Monitor.py",
            "dashboard/pages/Analytics.py",
            "dashboard/pages/Live_Feed.py",
        ]

        for file_path in dashboard_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self._analyze_file_monitoring(file_path, "dashboard")

        # Check for missing user activity monitoring
        if not self._has_component_monitoring("user_activity"):
            self.gaps.append(
                MonitoringGap(
                    component="dashboard",
                    gap_type="user_monitoring",
                    description="No user activity and engagement monitoring",
                    severity="medium",
                    recommendation="Implement user session tracking, page view analytics, and feature usage monitoring",
                    files_affected=dashboard_files,
                )
            )

    def _analyze_cloud_functions(self):
        """Analyze cloud function monitoring coverage"""
        print("  ☁️ Analyzing cloud functions...")

        cloud_files = ["cloud_function/main.py", "cloud_function/utils/monitoring.py"]

        for file_path in cloud_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self._analyze_file_monitoring(file_path, "cloud_function")

        # Check for missing cloud function monitoring
        if not self._has_component_monitoring("cloud_function"):
            self.gaps.append(
                MonitoringGap(
                    component="cloud_function",
                    gap_type="monitoring",
                    description="Limited cloud function execution monitoring",
                    severity="high",
                    recommendation="Implement execution time tracking, memory usage monitoring, and cold start detection",
                    files_affected=cloud_files,
                )
            )

    def _analyze_database(self):
        """Analyze database monitoring coverage"""
        print("  🗄️ Analyzing database...")

        db_files = ["storage/db.py", "utils/monitoring.py"]

        for file_path in db_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self._analyze_file_monitoring(file_path, "database")

        # Check for missing database monitoring
        if not self._has_component_monitoring("database"):
            self.gaps.append(
                MonitoringGap(
                    component="database",
                    gap_type="monitoring",
                    description="Limited database performance and health monitoring",
                    severity="critical",
                    recommendation="Implement query performance monitoring, connection pool tracking, and data integrity checks",
                    files_affected=db_files,
                )
            )

    def _analyze_apis(self):
        """Analyze API monitoring coverage"""
        print("  🔌 Analyzing APIs...")

        api_files = [
            "scrapers/twitter_apify.py",
            "scrapers/newsapi_headlines.py",
            "scrapers/dexscreener.py",
            "scrapers/dexpaprika.py",
        ]

        for file_path in api_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self._analyze_file_monitoring(file_path, "api")

        # Check for missing API monitoring
        if not self._has_component_monitoring("api"):
            self.gaps.append(
                MonitoringGap(
                    component="api",
                    gap_type="monitoring",
                    description="No comprehensive API health and rate limit monitoring",
                    severity="high",
                    recommendation="Implement API response time tracking, rate limit monitoring, and error rate tracking",
                    files_affected=api_files,
                )
            )

    def _analyze_security(self):
        """Analyze security monitoring coverage"""
        print("  🔒 Analyzing security...")

        security_files = ["utils/enterprise_logging.py", "utils/health_monitor.py"]

        for file_path in security_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self._analyze_file_monitoring(file_path, "security")

        # Check for missing security monitoring
        if not self._has_component_monitoring("security"):
            self.gaps.append(
                MonitoringGap(
                    component="security",
                    gap_type="monitoring",
                    description="Limited security event monitoring and threat detection",
                    severity="critical",
                    recommendation="Implement authentication failure tracking, suspicious activity detection, and access pattern monitoring",
                    files_affected=security_files,
                )
            )

    def _analyze_performance(self):
        """Analyze performance monitoring coverage"""
        print("  ⚡ Analyzing performance...")

        performance_files = [
            "utils/enterprise_logging.py",
            "utils/monitoring.py",
            "utils/health_monitor.py",
        ]

        for file_path in performance_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self._analyze_file_monitoring(file_path, "performance")

        # Check for missing performance monitoring
        if not self._has_component_monitoring("performance"):
            self.gaps.append(
                MonitoringGap(
                    component="performance",
                    gap_type="monitoring",
                    description="Limited application performance monitoring",
                    severity="high",
                    recommendation="Implement response time tracking, throughput monitoring, and resource utilization tracking",
                    files_affected=performance_files,
                )
            )

    def _analyze_cost_tracking(self):
        """Analyze cost tracking coverage"""
        print("  💰 Analyzing cost tracking...")

        cost_files = ["processor/google_ai_summarizer.py", "utils/llm_cache.py"]

        for file_path in cost_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self._analyze_file_monitoring(file_path, "cost")

        # Check for missing cost tracking
        if not self._has_component_monitoring("cost"):
            self.gaps.append(
                MonitoringGap(
                    component="cost_tracking",
                    gap_type="monitoring",
                    description="No comprehensive cost tracking and budget monitoring",
                    severity="high",
                    recommendation="Implement API cost tracking, LLM usage monitoring, and budget alerts",
                    files_affected=cost_files,
                )
            )

    def _analyze_alerting(self):
        """Analyze alerting coverage"""
        print("  🚨 Analyzing alerting...")

        alerting_files = ["utils/health_monitor.py", "utils/monitoring.py"]

        for file_path in alerting_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self._analyze_file_monitoring(file_path, "alerting")

        # Check for missing alerting
        if not self._has_component_monitoring("alerting"):
            self.gaps.append(
                MonitoringGap(
                    component="alerting",
                    gap_type="monitoring",
                    description="Limited alerting and notification system",
                    severity="critical",
                    recommendation="Implement multi-channel alerting (email, Slack, webhook) with escalation policies",
                    files_affected=alerting_files,
                )
            )

    def _analyze_logging(self):
        """Analyze logging coverage"""
        print("  📝 Analyzing logging...")

        logging_files = [
            "utils/enterprise_logging.py",
            "utils/advanced_logging.py",
            "utils/logger.py",
        ]

        for file_path in logging_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self._analyze_file_monitoring(file_path, "logging")

        # Check for missing structured logging
        if not self._has_component_monitoring("structured_logging"):
            self.gaps.append(
                MonitoringGap(
                    component="logging",
                    gap_type="structured_logging",
                    description="Inconsistent structured logging across components",
                    severity="medium",
                    recommendation="Implement consistent structured logging with correlation IDs and context tracking",
                    files_affected=logging_files,
                )
            )

    def _analyze_file_monitoring(self, file_path: str, component: str):
        """Analyze monitoring coverage in a specific file"""
        try:
            full_path = self.project_root / file_path
            if not full_path.exists():
                return

            content = full_path.read_text()

            # Check for logging usage
            has_logging = any(
                keyword in content
                for keyword in ["get_logger", "logger.", "logging.", "log_"]
            )

            # Check for monitoring usage
            has_monitoring = any(
                keyword in content
                for keyword in ["monitor", "health_check", "metrics", "performance"]
            )

            # Check for error handling
            has_error_handling = any(
                keyword in content
                for keyword in ["try:", "except", "error", "exception"]
            )

            # Check for structured logging
            has_structured_logging = any(
                keyword in content
                for keyword in ["structured", "context", "correlation", "request_id"]
            )

            # Record findings
            if has_logging:
                self.components_analyzed.add(f"{component}_logging")
            if has_monitoring:
                self.components_analyzed.add(f"{component}_monitoring")
            if has_error_handling:
                self.components_analyzed.add(f"{component}_error_handling")
            if has_structured_logging:
                self.components_analyzed.add(f"{component}_structured_logging")

        except Exception as e:
            print(f"    ⚠️ Error analyzing {file_path}: {e}")

    def _has_component_monitoring(self, component: str) -> bool:
        """Check if a component has monitoring coverage"""
        return any(comp.startswith(component) for comp in self.components_analyzed)

    def generate_report(self) -> dict[str, Any]:
        """Generate comprehensive monitoring gap report"""
        report = {
            "timestamp": str(Path(__file__).stat().st_mtime),
            "total_gaps": len(self.gaps),
            "components_analyzed": list(self.components_analyzed),
            "gaps_by_severity": {
                "critical": [gap for gap in self.gaps if gap.severity == "critical"],
                "high": [gap for gap in self.gaps if gap.severity == "high"],
                "medium": [gap for gap in self.gaps if gap.severity == "medium"],
                "low": [gap for gap in self.gaps if gap.severity == "low"],
            },
            "gaps_by_component": {},
            "recommendations": self._generate_recommendations(),
        }

        # Group gaps by component
        for gap in self.gaps:
            if gap.component not in report["gaps_by_component"]:
                report["gaps_by_component"][gap.component] = []
            report["gaps_by_component"][gap.component].append(gap)

        return report

    def _generate_recommendations(self) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = [
            "Implement comprehensive health monitoring for all system components",
            "Add structured logging with correlation IDs across all services",
            "Set up multi-channel alerting (email, Slack, webhook) with escalation policies",
            "Implement cost tracking and budget monitoring for all external APIs",
            "Add performance monitoring with response time and throughput tracking",
            "Set up security monitoring with authentication and access pattern tracking",
            "Implement data quality monitoring with completeness and accuracy checks",
            "Add user activity monitoring for dashboard and API usage",
            "Set up automated reporting with daily, weekly, and monthly summaries",
            "Implement log aggregation and centralized log management",
            "Add distributed tracing for request flow across services",
            "Set up capacity planning and resource utilization monitoring",
        ]

        return recommendations

    def save_report(
        self, report: dict[str, Any], output_file: str = "monitoring_gap_report.json"
    ):
        """Save the monitoring gap report"""
        output_path = self.project_root / output_file
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

        print(f"📄 Report saved to: {output_path}")

    def print_summary(self, report: dict[str, Any]):
        """Print a summary of the monitoring gap analysis"""
        print("\n" + "=" * 60)
        print("📊 MONITORING GAP ANALYSIS SUMMARY")
        print("=" * 60)

        print(f"\n🔍 Total gaps identified: {report['total_gaps']}")
        print(f"📋 Components analyzed: {len(report['components_analyzed'])}")

        print("\n🚨 Gaps by severity:")
        for severity, gaps in report["gaps_by_severity"].items():
            if gaps:
                print(f"  {severity.upper()}: {len(gaps)} gaps")
                for gap in gaps[:3]:  # Show first 3
                    print(f"    - {gap.component}: {gap.description}")
                if len(gaps) > 3:
                    print(f"    ... and {len(gaps) - 3} more")

        print("\n📈 Components with gaps:")
        for component, gaps in report["gaps_by_component"].items():
            print(f"  {component}: {len(gaps)} gaps")

        print("\n💡 Top recommendations:")
        for i, rec in enumerate(report["recommendations"][:5], 1):
            print(f"  {i}. {rec}")

        print("\n" + "=" * 60)


def main():
    """Main function to run monitoring gap analysis"""
    print("🔍 DegenDigest Monitoring Gap Analysis")
    print("=" * 50)

    # Create analyzer and run analysis
    analyzer = MonitoringGapAnalyzer()
    gaps = analyzer.analyze_project()

    # Generate and save report
    report = analyzer.generate_report()
    analyzer.save_report(report)

    # Print summary
    analyzer.print_summary(report)

    # Provide next steps
    print("\n🚀 Next steps:")
    print("  1. Review the detailed report in monitoring_gap_report.json")
    print("  2. Prioritize critical and high-severity gaps")
    print("  3. Run enhanced_monitoring_config.py to generate configurations")
    print("  4. Implement missing monitoring components")
    print("  5. Set up continuous monitoring service")

    # Exit with appropriate code based on critical gaps
    critical_gaps = len(report["gaps_by_severity"]["critical"])
    if critical_gaps > 0:
        print(
            f"\n⚠️  {critical_gaps} critical gaps found - immediate attention required!"
        )
        sys.exit(1)
    else:
        print("\n✅ No critical gaps found - system monitoring is in good shape!")
        sys.exit(0)


if __name__ == "__main__":
    main()
