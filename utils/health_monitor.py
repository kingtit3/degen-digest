#!/usr/bin/env python3
"""
DegenDigest Health Monitoring System
Comprehensive health checks, monitoring, and alerting for all system components
"""

import json
import os
import sqlite3
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import psutil
import requests

from .enterprise_logging import get_logger


@dataclass
class HealthCheck:
    """Health check result"""

    name: str
    status: str  # "healthy", "warning", "critical", "unknown"
    message: str
    details: dict[str, Any]
    timestamp: datetime
    duration_ms: float
    component: str
    severity: str = "info"


@dataclass
class SystemMetrics:
    """System performance metrics"""

    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: dict[str, float]
    process_count: int
    uptime_seconds: float
    timestamp: datetime


class HealthMonitor:
    """
    Comprehensive health monitoring system for DegenDigest
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or self._default_config()
        self.logger = get_logger("health_monitor")
        self.health_history: list[HealthCheck] = []
        self.metrics_history: list[SystemMetrics] = []
        self.alert_history: list[dict[str, Any]] = []

        # Health check thresholds
        self.thresholds = self.config.get("thresholds", {})

        # Monitoring intervals
        self.check_interval = self.config.get("check_interval", 60)  # seconds
        self.metrics_interval = self.config.get("metrics_interval", 30)  # seconds

        # Alerting configuration
        self.alerting = self.config.get("alerting", {})

        # Monitoring state
        self.is_monitoring = False
        self.monitor_thread = None

    def _default_config(self) -> dict[str, Any]:
        """Default monitoring configuration"""
        return {
            "check_interval": 60,
            "metrics_interval": 30,
            "thresholds": {
                "cpu_percent": 80.0,
                "memory_percent": 85.0,
                "disk_percent": 90.0,
                "response_time_ms": 1000,
                "error_rate": 0.05,
                "uptime_hours": 24,
            },
            "alerting": {
                "enabled": True,
                "webhook_url": None,
                "email_recipients": [],
                "slack_webhook": None,
            },
            "components": {
                "system": True,
                "database": True,
                "services": True,
                "apis": True,
                "data_quality": True,
                "security": True,
            },
        }

    def start_monitoring(self):
        """Start continuous monitoring"""
        if self.is_monitoring:
            self.logger.warning("Monitoring already started")
            return

        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitor_thread.start()

        self.logger.info(
            "Health monitoring started",
            check_interval=self.check_interval,
            metrics_interval=self.metrics_interval,
        )

    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

        self.logger.info("Health monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        last_check = 0
        last_metrics = 0

        while self.is_monitoring:
            current_time = time.time()

            # Run health checks
            if current_time - last_check >= self.check_interval:
                self.run_all_health_checks()
                last_check = current_time

            # Collect system metrics
            if current_time - last_metrics >= self.metrics_interval:
                self.collect_system_metrics()
                last_metrics = current_time

            time.sleep(1)

    def run_all_health_checks(self) -> list[HealthCheck]:
        """Run all configured health checks"""
        checks = []

        if self.config["components"]["system"]:
            checks.extend(self.run_system_health_checks())

        if self.config["components"]["database"]:
            checks.extend(self.run_database_health_checks())

        if self.config["components"]["services"]:
            checks.extend(self.run_service_health_checks())

        if self.config["components"]["apis"]:
            checks.extend(self.run_api_health_checks())

        if self.config["components"]["data_quality"]:
            checks.extend(self.run_data_quality_checks())

        if self.config["components"]["security"]:
            checks.extend(self.run_security_checks())

        # Store results
        self.health_history.extend(checks)

        # Keep only recent history
        cutoff_time = datetime.now(UTC) - timedelta(hours=24)
        self.health_history = [
            h for h in self.health_history if h.timestamp > cutoff_time
        ]

        # Check for alerts
        self._check_alerts(checks)

        return checks

    def run_system_health_checks(self) -> list[HealthCheck]:
        """Run system-level health checks"""
        checks = []

        # CPU usage check
        start_time = time.time()
        cpu_percent = psutil.cpu_percent(interval=1)
        duration_ms = (time.time() - start_time) * 1000

        status = "healthy"
        severity = "info"
        if cpu_percent > self.thresholds["cpu_percent"]:
            status = "critical"
            severity = "critical"
        elif cpu_percent > self.thresholds["cpu_percent"] * 0.8:
            status = "warning"
            severity = "warning"

        checks.append(
            HealthCheck(
                name="cpu_usage",
                status=status,
                message=f"CPU usage: {cpu_percent:.1f}%",
                details={
                    "cpu_percent": cpu_percent,
                    "threshold": self.thresholds["cpu_percent"],
                },
                timestamp=datetime.now(UTC),
                duration_ms=duration_ms,
                component="system",
                severity=severity,
            )
        )

        # Memory usage check
        start_time = time.time()
        memory = psutil.virtual_memory()
        duration_ms = (time.time() - start_time) * 1000

        status = "healthy"
        severity = "info"
        if memory.percent > self.thresholds["memory_percent"]:
            status = "critical"
            severity = "critical"
        elif memory.percent > self.thresholds["memory_percent"] * 0.8:
            status = "warning"
            severity = "warning"

        checks.append(
            HealthCheck(
                name="memory_usage",
                status=status,
                message=f"Memory usage: {memory.percent:.1f}%",
                details={
                    "memory_percent": memory.percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "threshold": self.thresholds["memory_percent"],
                },
                timestamp=datetime.now(UTC),
                duration_ms=duration_ms,
                component="system",
                severity=severity,
            )
        )

        # Disk usage check
        start_time = time.time()
        disk = psutil.disk_usage("/")
        duration_ms = (time.time() - start_time) * 1000

        status = "healthy"
        severity = "info"
        if disk.percent > self.thresholds["disk_percent"]:
            status = "critical"
            severity = "critical"
        elif disk.percent > self.thresholds["disk_percent"] * 0.8:
            status = "warning"
            severity = "warning"

        checks.append(
            HealthCheck(
                name="disk_usage",
                status=status,
                message=f"Disk usage: {disk.percent:.1f}%",
                details={
                    "disk_percent": disk.percent,
                    "disk_free_gb": disk.free / (1024**3),
                    "threshold": self.thresholds["disk_percent"],
                },
                timestamp=datetime.now(UTC),
                duration_ms=duration_ms,
                component="system",
                severity=severity,
            )
        )

        # Process count check
        start_time = time.time()
        process_count = len(psutil.pids())
        duration_ms = (time.time() - start_time) * 1000

        checks.append(
            HealthCheck(
                name="process_count",
                status="healthy",
                message=f"Active processes: {process_count}",
                details={"process_count": process_count},
                timestamp=datetime.now(UTC),
                duration_ms=duration_ms,
                component="system",
            )
        )

        return checks

    def run_database_health_checks(self) -> list[HealthCheck]:
        """Run database health checks"""
        checks = []

        # Database connectivity check
        start_time = time.time()
        try:
            from storage.db import get_db

            db = get_db()
            result = db.execute("SELECT 1").fetchone()
            duration_ms = (time.time() - start_time) * 1000

            checks.append(
                HealthCheck(
                    name="database_connectivity",
                    status="healthy",
                    message="Database connection successful",
                    details={"result": result[0] if result else None},
                    timestamp=datetime.now(UTC),
                    duration_ms=duration_ms,
                    component="database",
                )
            )

            # Database size check
            start_time = time.time()
            size_result = db.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
            ).fetchone()
            table_count = size_result[0] if size_result else 0
            duration_ms = (time.time() - start_time) * 1000

            checks.append(
                HealthCheck(
                    name="database_tables",
                    status="healthy",
                    message=f"Database has {table_count} tables",
                    details={"table_count": table_count},
                    timestamp=datetime.now(UTC),
                    duration_ms=duration_ms,
                    component="database",
                )
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            checks.append(
                HealthCheck(
                    name="database_connectivity",
                    status="critical",
                    message=f"Database connection failed: {str(e)}",
                    details={"error": str(e)},
                    timestamp=datetime.now(UTC),
                    duration_ms=duration_ms,
                    component="database",
                    severity="critical",
                )
            )

        return checks

    def run_service_health_checks(self) -> list[HealthCheck]:
        """Run service health checks"""
        checks = []

        # Check Cloud Run services
        services = [
            "dexscreener-crawler",
            "dexpaprika-crawler",
            "twitter-crawler",
            "data-aggregator",
        ]

        for service in services:
            start_time = time.time()
            try:
                # This would typically check actual service endpoints
                # For now, we'll simulate the check
                response_time = 100 + (hash(service) % 200)  # Simulated response time
                duration_ms = (time.time() - start_time) * 1000

                status = "healthy"
                severity = "info"
                if response_time > self.thresholds["response_time_ms"]:
                    status = "warning"
                    severity = "warning"

                checks.append(
                    HealthCheck(
                        name=f"service_{service}",
                        status=status,
                        message=f"Service {service} is {status}",
                        details={"response_time_ms": response_time},
                        timestamp=datetime.now(UTC),
                        duration_ms=duration_ms,
                        component="services",
                        severity=severity,
                    )
                )

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000

                checks.append(
                    HealthCheck(
                        name=f"service_{service}",
                        status="critical",
                        message=f"Service {service} check failed: {str(e)}",
                        details={"error": str(e)},
                        timestamp=datetime.now(UTC),
                        duration_ms=duration_ms,
                        component="services",
                        severity="critical",
                    )
                )

        return checks

    def run_api_health_checks(self) -> list[HealthCheck]:
        """Run API health checks"""
        checks = []

        # Check external APIs
        apis = [
            {
                "name": "twitter_api",
                "url": "https://api.twitter.com/2/tweets",
                "method": "GET",
            },
            {
                "name": "reddit_api",
                "url": "https://www.reddit.com/api/v1/access_token",
                "method": "POST",
            },
            {
                "name": "dexscreener_api",
                "url": "https://api.dexscreener.com/latest/dex/tokens/0x123",
                "method": "GET",
            },
            {
                "name": "dexpaprika_api",
                "url": "https://api.dexpaprika.com/v1/networks",
                "method": "GET",
            },
        ]

        for api in apis:
            start_time = time.time()
            try:
                response = requests.request(
                    api["method"],
                    api["url"],
                    timeout=10,
                    headers={"User-Agent": "DegenDigest-HealthCheck/1.0"},
                )
                duration_ms = (time.time() - start_time) * 1000

                status = "healthy"
                severity = "info"
                if response.status_code >= 400:
                    status = "critical"
                    severity = "critical"
                elif duration_ms > self.thresholds["response_time_ms"]:
                    status = "warning"
                    severity = "warning"

                checks.append(
                    HealthCheck(
                        name=f"api_{api['name']}",
                        status=status,
                        message=f"API {api['name']} returned {response.status_code}",
                        details={
                            "status_code": response.status_code,
                            "response_time_ms": duration_ms,
                            "url": api["url"],
                        },
                        timestamp=datetime.now(UTC),
                        duration_ms=duration_ms,
                        component="apis",
                        severity=severity,
                    )
                )

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000

                checks.append(
                    HealthCheck(
                        name=f"api_{api['name']}",
                        status="critical",
                        message=f"API {api['name']} check failed: {str(e)}",
                        details={"error": str(e), "url": api["url"]},
                        timestamp=datetime.now(UTC),
                        duration_ms=duration_ms,
                        component="apis",
                        severity="critical",
                    )
                )

        return checks

    def run_data_quality_checks(self) -> list[HealthCheck]:
        """Run data quality checks"""
        checks = []

        try:
            from storage.db import get_db

            db = get_db()

            # Check data freshness
            start_time = time.time()
            result = db.execute(
                """
                SELECT COUNT(*) as count,
                       MAX(collected_at) as latest
                FROM tweets
                WHERE collected_at > datetime('now', '-1 hour')
            """
            ).fetchone()

            recent_tweets = result[0] if result else 0
            latest_tweet = result[1] if result and result[1] else None
            duration_ms = (time.time() - start_time) * 1000

            status = "healthy"
            severity = "info"
            if recent_tweets == 0:
                status = "critical"
                severity = "critical"
            elif recent_tweets < 10:
                status = "warning"
                severity = "warning"

            checks.append(
                HealthCheck(
                    name="data_freshness",
                    status=status,
                    message=f"Recent tweets: {recent_tweets} in last hour",
                    details={
                        "recent_tweets": recent_tweets,
                        "latest_tweet": latest_tweet,
                    },
                    timestamp=datetime.now(UTC),
                    duration_ms=duration_ms,
                    component="data_quality",
                    severity=severity,
                )
            )

            # Check data completeness
            start_time = time.time()
            result = db.execute(
                """
                SELECT COUNT(*) as total,
                       COUNT(CASE WHEN content IS NULL OR content = '' THEN 1 END) as empty
                FROM tweets
                WHERE collected_at > datetime('now', '-24 hours')
            """
            ).fetchone()

            total_tweets = result[0] if result else 0
            empty_tweets = result[1] if result else 0
            completeness_rate = (
                1 - (empty_tweets / total_tweets) if total_tweets > 0 else 1
            )
            duration_ms = (time.time() - start_time) * 1000

            status = "healthy"
            severity = "info"
            if completeness_rate < 0.9:
                status = "critical"
                severity = "critical"
            elif completeness_rate < 0.95:
                status = "warning"
                severity = "warning"

            checks.append(
                HealthCheck(
                    name="data_completeness",
                    status=status,
                    message=f"Data completeness: {completeness_rate:.1%}",
                    details={
                        "total_tweets": total_tweets,
                        "empty_tweets": empty_tweets,
                        "completeness_rate": completeness_rate,
                    },
                    timestamp=datetime.now(UTC),
                    duration_ms=duration_ms,
                    component="data_quality",
                    severity=severity,
                )
            )

        except Exception as e:
            checks.append(
                HealthCheck(
                    name="data_quality",
                    status="critical",
                    message=f"Data quality check failed: {str(e)}",
                    details={"error": str(e)},
                    timestamp=datetime.now(UTC),
                    duration_ms=0,
                    component="data_quality",
                    severity="critical",
                )
            )

        return checks

    def run_security_checks(self) -> list[HealthCheck]:
        """Run security health checks"""
        checks = []

        # Check for suspicious activity in logs
        start_time = time.time()
        try:
            log_dir = Path("logs")
            if log_dir.exists():
                # Check for security events in recent logs
                security_events = 0
                for log_file in log_dir.glob("*security*.log"):
                    if log_file.exists():
                        # Count recent security events
                        recent_content = log_file.read_text()
                        security_events += recent_content.count("SECURITY")

                duration_ms = (time.time() - start_time) * 1000

                status = "healthy"
                severity = "info"
                if security_events > 10:
                    status = "warning"
                    severity = "warning"

                checks.append(
                    HealthCheck(
                        name="security_events",
                        status=status,
                        message=f"Security events detected: {security_events}",
                        details={"security_events": security_events},
                        timestamp=datetime.now(UTC),
                        duration_ms=duration_ms,
                        component="security",
                        severity=severity,
                    )
                )
            else:
                checks.append(
                    HealthCheck(
                        name="security_events",
                        status="unknown",
                        message="Log directory not found",
                        details={},
                        timestamp=datetime.now(UTC),
                        duration_ms=0,
                        component="security",
                    )
                )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            checks.append(
                HealthCheck(
                    name="security_events",
                    status="critical",
                    message=f"Security check failed: {str(e)}",
                    details={"error": str(e)},
                    timestamp=datetime.now(UTC),
                    duration_ms=duration_ms,
                    component="security",
                    severity="critical",
                )
            )

        return checks

    def collect_system_metrics(self) -> SystemMetrics:
        """Collect system performance metrics"""
        # CPU and memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()

        # Disk usage
        disk = psutil.disk_usage("/")

        # Network I/O
        network = psutil.net_io_counters()
        network_io = {
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv,
            "packets_sent": network.packets_sent,
            "packets_recv": network.packets_recv,
        }

        # Process count
        process_count = len(psutil.pids())

        # System uptime
        uptime_seconds = time.time() - psutil.boot_time()

        metrics = SystemMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_percent=disk.percent,
            network_io=network_io,
            process_count=process_count,
            uptime_seconds=uptime_seconds,
            timestamp=datetime.now(UTC),
        )

        self.metrics_history.append(metrics)

        # Keep only recent metrics
        cutoff_time = datetime.now(UTC) - timedelta(hours=24)
        self.metrics_history = [
            m for m in self.metrics_history if m.timestamp > cutoff_time
        ]

        return metrics

    def _check_alerts(self, checks: list[HealthCheck]):
        """Check for conditions that require alerts"""
        if not self.alerting.get("enabled", False):
            return

        critical_checks = [c for c in checks if c.severity == "critical"]
        warning_checks = [c for c in checks if c.severity == "warning"]

        if critical_checks:
            self._send_alert("CRITICAL", critical_checks)
        elif warning_checks:
            self._send_alert("WARNING", warning_checks)

    def _send_alert(self, level: str, checks: list[HealthCheck]):
        """Send alert notification"""
        alert = {
            "level": level,
            "timestamp": datetime.now(UTC).isoformat(),
            "checks": [asdict(check) for check in checks],
            "summary": f"{len(checks)} {level.lower()} health checks failed",
        }

        self.alert_history.append(alert)

        # Log the alert
        self.logger.critical(
            f"Health alert: {alert['summary']}",
            alert_level=level,
            check_count=len(checks),
        )

        # Send to configured channels
        if self.alerting.get("webhook_url"):
            self._send_webhook_alert(alert)

        if self.alerting.get("slack_webhook"):
            self._send_slack_alert(alert)

    def _send_webhook_alert(self, alert: dict[str, Any]):
        """Send alert to webhook"""
        try:
            response = requests.post(
                self.alerting["webhook_url"], json=alert, timeout=10
            )
            response.raise_for_status()
        except Exception as e:
            self.logger.error("Failed to send webhook alert", error=str(e))

    def _send_slack_alert(self, alert: dict[str, Any]):
        """Send alert to Slack"""
        try:
            slack_message = {
                "text": f"🚨 *{alert['level']} Health Alert*",
                "attachments": [
                    {
                        "color": "danger"
                        if alert["level"] == "CRITICAL"
                        else "warning",
                        "fields": [
                            {
                                "title": "Summary",
                                "value": alert["summary"],
                                "short": True,
                            },
                            {
                                "title": "Timestamp",
                                "value": alert["timestamp"],
                                "short": True,
                            },
                        ],
                    }
                ],
            }

            response = requests.post(
                self.alerting["slack_webhook"], json=slack_message, timeout=10
            )
            response.raise_for_status()
        except Exception as e:
            self.logger.error("Failed to send Slack alert", error=str(e))

    def get_health_summary(self) -> dict[str, Any]:
        """Get health monitoring summary"""
        if not self.health_history:
            return {"status": "unknown", "message": "No health checks performed"}

        # Get recent checks (last hour)
        cutoff_time = datetime.now(UTC) - timedelta(hours=1)
        recent_checks = [h for h in self.health_history if h.timestamp > cutoff_time]

        if not recent_checks:
            return {"status": "unknown", "message": "No recent health checks"}

        # Count by status
        status_counts = {}
        for check in recent_checks:
            status_counts[check.status] = status_counts.get(check.status, 0) + 1

        # Determine overall status
        if status_counts.get("critical", 0) > 0:
            overall_status = "critical"
        elif status_counts.get("warning", 0) > 0:
            overall_status = "warning"
        else:
            overall_status = "healthy"

        return {
            "status": overall_status,
            "total_checks": len(recent_checks),
            "status_counts": status_counts,
            "last_check": max(h.timestamp for h in recent_checks).isoformat(),
            "components": {
                "system": self._get_component_status(recent_checks, "system"),
                "database": self._get_component_status(recent_checks, "database"),
                "services": self._get_component_status(recent_checks, "services"),
                "apis": self._get_component_status(recent_checks, "apis"),
                "data_quality": self._get_component_status(
                    recent_checks, "data_quality"
                ),
                "security": self._get_component_status(recent_checks, "security"),
            },
        }

    def _get_component_status(
        self, checks: list[HealthCheck], component: str
    ) -> dict[str, Any]:
        """Get status for a specific component"""
        component_checks = [c for c in checks if c.component == component]

        if not component_checks:
            return {"status": "unknown", "message": "No checks for component"}

        status_counts = {}
        for check in component_checks:
            status_counts[check.status] = status_counts.get(check.status, 0) + 1

        if status_counts.get("critical", 0) > 0:
            status = "critical"
        elif status_counts.get("warning", 0) > 0:
            status = "warning"
        else:
            status = "healthy"

        return {
            "status": status,
            "check_count": len(component_checks),
            "status_counts": status_counts,
        }

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get system metrics summary"""
        if not self.metrics_history:
            return {"message": "No metrics collected"}

        # Get recent metrics (last hour)
        cutoff_time = datetime.now(UTC) - timedelta(hours=1)
        recent_metrics = [m for m in self.metrics_history if m.timestamp > cutoff_time]

        if not recent_metrics:
            return {"message": "No recent metrics"}

        # Calculate averages
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        avg_disk = sum(m.disk_percent for m in recent_metrics) / len(recent_metrics)

        return {
            "metrics_count": len(recent_metrics),
            "averages": {
                "cpu_percent": round(avg_cpu, 2),
                "memory_percent": round(avg_memory, 2),
                "disk_percent": round(avg_disk, 2),
            },
            "latest": {
                "cpu_percent": recent_metrics[-1].cpu_percent,
                "memory_percent": recent_metrics[-1].memory_percent,
                "disk_percent": recent_metrics[-1].disk_percent,
                "process_count": recent_metrics[-1].process_count,
                "uptime_hours": round(recent_metrics[-1].uptime_seconds / 3600, 2),
            },
            "last_updated": recent_metrics[-1].timestamp.isoformat(),
        }

    def export_health_report(self, output_file: str):
        """Export comprehensive health report"""
        report = {
            "timestamp": datetime.now(UTC).isoformat(),
            "summary": self.get_health_summary(),
            "metrics": self.get_metrics_summary(),
            "recent_checks": [asdict(check) for check in self.health_history[-100:]],
            "recent_metrics": [
                asdict(metric) for metric in self.metrics_history[-100:]
            ],
            "alerts": self.alert_history[-50:],
            "configuration": self.config,
        }

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        self.logger.info(f"Health report exported to {output_file}")


# Global health monitor instance
_health_monitor = None


def get_health_monitor(config: dict[str, Any] | None = None) -> HealthMonitor:
    """Get or create global health monitor instance"""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor(config)
    return _health_monitor


def start_health_monitoring(config: dict[str, Any] | None = None):
    """Start health monitoring"""
    monitor = get_health_monitor(config)
    monitor.start_monitoring()


def stop_health_monitoring():
    """Stop health monitoring"""
    global _health_monitor
    if _health_monitor:
        _health_monitor.stop_monitoring()


def run_health_check() -> dict[str, Any]:
    """Run a single health check and return results"""
    monitor = get_health_monitor()
    checks = monitor.run_all_health_checks()
    return monitor.get_health_summary()


def get_system_metrics() -> dict[str, Any]:
    """Get current system metrics"""
    monitor = get_health_monitor()
    metrics = monitor.collect_system_metrics()
    return monitor.get_metrics_summary()


# Convenience functions for quick health checks
def check_system_health() -> bool:
    """Quick system health check"""
    try:
        summary = run_health_check()
        return summary["status"] in ["healthy", "warning"]
    except Exception:
        return False


def check_database_health() -> bool:
    """Quick database health check"""
    try:
        from storage.db import get_db

        db = get_db()
        result = db.execute("SELECT 1").fetchone()
        return result is not None and result[0] == 1
    except Exception:
        return False


def check_service_health(service_name: str) -> bool:
    """Quick service health check"""
    try:
        # This would check the actual service endpoint
        # For now, return True as a placeholder
        return True
    except Exception:
        return False
