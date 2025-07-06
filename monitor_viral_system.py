#!/usr/bin/env python3
"""
Enhanced Viral Content System Monitor
Monitors all data sources and provides real-time insights into viral content collection
"""
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List

import requests

# Add current directory to path
sys.path.append(".")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ViralSystemMonitor:
    """Monitors the enhanced viral content system"""

    def __init__(self):
        self.project_id = "lucky-union-463615-t3"
        self.bucket_name = "degen-digest-data"
        self.region = "us-central1"

    def check_cloud_functions(self) -> dict[str, Any]:
        """Check status of all Cloud Functions"""
        try:
            import subprocess

            functions = [
                "enhanced-reddit-crawler",
                "enhanced-news-crawler",
                "enhanced-coingecko-crawler",
                "dexscreener-crawler",
                "dexpaprika-crawler",
                "viral-content-consolidator",
            ]

            status = {}

            for func_name in functions:
                try:
                    # Get function status
                    result = subprocess.run(
                        [
                            "gcloud",
                            "functions",
                            "describe",
                            func_name,
                            "--region",
                            self.region,
                            "--format",
                            "json",
                        ],
                        capture_output=True,
                        text=True,
                    )

                    if result.returncode == 0:
                        func_data = json.loads(result.stdout)
                        status[func_name] = {
                            "status": "active",
                            "url": func_data.get("httpsTrigger", {}).get("url", "N/A"),
                            "last_modified": func_data.get("updateTime", "N/A"),
                            "memory": func_data.get("availableMemoryMb", "N/A"),
                            "timeout": func_data.get("timeout", "N/A"),
                        }
                    else:
                        status[func_name] = {"status": "error", "error": result.stderr}

                except Exception as e:
                    status[func_name] = {"status": "error", "error": str(e)}

            return status

        except Exception as e:
            logger.error(f"❌ Error checking Cloud Functions: {e}")
            return {}

    def check_scheduler_jobs(self) -> dict[str, Any]:
        """Check status of Cloud Scheduler jobs"""
        try:
            import subprocess

            jobs = [
                "reddit-viral-crawler",
                "news-viral-crawler",
                "coingecko-viral-crawler",
                "dexscreener-viral-crawler",
                "dexpaprika-viral-crawler",
                "viral-content-consolidator",
            ]

            status = {}

            for job_name in jobs:
                try:
                    # Get job status
                    result = subprocess.run(
                        [
                            "gcloud",
                            "scheduler",
                            "jobs",
                            "describe",
                            job_name,
                            "--location",
                            self.region,
                            "--format",
                            "json",
                        ],
                        capture_output=True,
                        text=True,
                    )

                    if result.returncode == 0:
                        job_data = json.loads(result.stdout)
                        status[job_name] = {
                            "status": "active",
                            "schedule": job_data.get("schedule", "N/A"),
                            "last_run": job_data.get("lastAttemptTime", "N/A"),
                            "next_run": job_data.get("nextRunTime", "N/A"),
                            "uri": job_data.get("httpTarget", {}).get("uri", "N/A"),
                        }
                    else:
                        status[job_name] = {"status": "error", "error": result.stderr}

                except Exception as e:
                    status[job_name] = {"status": "error", "error": str(e)}

            return status

        except Exception as e:
            logger.error(f"❌ Error checking Scheduler jobs: {e}")
            return {}

    def check_data_collection(self) -> dict[str, Any]:
        """Check data collection status from GCS"""
        try:
            from google.cloud import storage

            client = storage.Client(project=self.project_id)
            bucket = client.bucket(self.bucket_name)

            data_sources = {
                "twitter": "data/twitter_latest.json",
                "reddit": "data/reddit_latest.json",
                "news": "data/news_latest.json",
                "coingecko": "data/coingecko_latest.json",
                "dexscreener": "data/dexscreener_latest.json",
                "dexpaprika": "data/dexpaprika_latest.json",
            }

            collection_status = {}

            for source, path in data_sources.items():
                try:
                    blob = bucket.blob(path)
                    if blob.exists():
                        # Get metadata
                        blob.reload()
                        last_modified = blob.updated
                        size = blob.size

                        # Check if data is recent (within last 2 hours)
                        hours_old = (
                            datetime.now(last_modified.tzinfo) - last_modified
                        ).total_seconds() / 3600

                        collection_status[source] = {
                            "status": "active" if hours_old < 2 else "stale",
                            "last_updated": last_modified.isoformat(),
                            "hours_old": round(hours_old, 1),
                            "size_bytes": size,
                            "size_mb": round(size / 1024 / 1024, 2),
                        }
                    else:
                        collection_status[source] = {
                            "status": "no_data",
                            "error": "No data file found",
                        }

                except Exception as e:
                    collection_status[source] = {"status": "error", "error": str(e)}

            return collection_status

        except Exception as e:
            logger.error(f"❌ Error checking data collection: {e}")
            return {}

    def check_viral_reports(self) -> dict[str, Any]:
        """Check viral content reports"""
        try:
            from google.cloud import storage

            client = storage.Client(project=self.project_id)
            bucket = client.bucket(self.bucket_name)

            # Check latest viral report
            viral_report_path = "viral_reports/viral_content_latest.json"
            blob = bucket.blob(viral_report_path)

            if blob.exists():
                blob.reload()
                last_modified = blob.updated
                size = blob.size

                # Get report content
                content = blob.download_as_text()
                report_data = json.loads(content)

                hours_old = (
                    datetime.now(last_modified.tzinfo) - last_modified
                ).total_seconds() / 3600

                return {
                    "status": "active" if hours_old < 2 else "stale",
                    "last_updated": last_modified.isoformat(),
                    "hours_old": round(hours_old, 1),
                    "size_mb": round(size / 1024 / 1024, 2),
                    "total_viral_items": report_data.get("summary", {}).get(
                        "total_viral_items", 0
                    ),
                    "explosive_content": report_data.get("summary", {})
                    .get("viral_score_ranges", {})
                    .get("explosive", 0),
                    "high_viral_content": report_data.get("summary", {})
                    .get("viral_score_ranges", {})
                    .get("high", 0),
                    "top_categories": report_data.get("category_breakdown", {}),
                    "recommendations": report_data.get("recommendations", []),
                }
            else:
                return {"status": "no_data", "error": "No viral report found"}

        except Exception as e:
            logger.error(f"❌ Error checking viral reports: {e}")
            return {"status": "error", "error": str(e)}

    def get_system_health(self) -> dict[str, Any]:
        """Get overall system health"""
        logger.info("🔍 Checking Enhanced Viral Content System Health...")

        # Check all components
        functions_status = self.check_cloud_functions()
        scheduler_status = self.check_scheduler_jobs()
        data_status = self.check_data_collection()
        viral_status = self.check_viral_reports()

        # Calculate overall health
        total_components = (
            len(functions_status) + len(scheduler_status) + len(data_status) + 1
        )
        healthy_components = 0

        # Count healthy functions
        for func_status in functions_status.values():
            if func_status.get("status") == "active":
                healthy_components += 1

        # Count healthy schedulers
        for sched_status in scheduler_status.values():
            if sched_status.get("status") == "active":
                healthy_components += 1

        # Count healthy data sources
        for data_source_status in data_status.values():
            if data_source_status.get("status") == "active":
                healthy_components += 1

        # Check viral reports
        if viral_status.get("status") == "active":
            healthy_components += 1

        health_percentage = (healthy_components / total_components) * 100

        return {
            "timestamp": datetime.now().isoformat(),
            "overall_health": {
                "percentage": round(health_percentage, 1),
                "status": "healthy"
                if health_percentage >= 80
                else "warning"
                if health_percentage >= 60
                else "critical",
                "healthy_components": healthy_components,
                "total_components": total_components,
            },
            "cloud_functions": functions_status,
            "scheduler_jobs": scheduler_status,
            "data_collection": data_status,
            "viral_reports": viral_status,
        }

    def print_health_report(self, health_data: dict[str, Any]):
        """Print formatted health report"""
        print("\n" + "=" * 60)
        print("🎯 ENHANCED VIRAL CONTENT SYSTEM HEALTH REPORT")
        print("=" * 60)

        # Overall health
        overall = health_data["overall_health"]
        status_emoji = (
            "🟢"
            if overall["status"] == "healthy"
            else "🟡"
            if overall["status"] == "warning"
            else "🔴"
        )

        print(
            f"\n{status_emoji} OVERALL SYSTEM HEALTH: {overall['percentage']}% ({overall['status'].upper()})"
        )
        print(
            f"   Healthy Components: {overall['healthy_components']}/{overall['total_components']}"
        )
        print(f"   Timestamp: {health_data['timestamp']}")

        # Cloud Functions
        print("\n🔧 CLOUD FUNCTIONS STATUS:")
        print("-" * 40)
        for func_name, status in health_data["cloud_functions"].items():
            status_emoji = "🟢" if status["status"] == "active" else "🔴"
            print(f"  {status_emoji} {func_name}: {status['status']}")
            if status["status"] == "active":
                print(f"     URL: {status['url'][:50]}...")

        # Scheduler Jobs
        print("\n⏰ SCHEDULER JOBS STATUS:")
        print("-" * 40)
        for job_name, status in health_data["scheduler_jobs"].items():
            status_emoji = "🟢" if status["status"] == "active" else "🔴"
            print(f"  {status_emoji} {job_name}: {status['status']}")
            if status["status"] == "active":
                print(f"     Schedule: {status['schedule']}")
                print(f"     Last Run: {status['last_run']}")

        # Data Collection
        print("\n📊 DATA COLLECTION STATUS:")
        print("-" * 40)
        total_items = 0
        for source, status in health_data["data_collection"].items():
            status_emoji = (
                "🟢"
                if status["status"] == "active"
                else "🟡"
                if status["status"] == "stale"
                else "🔴"
            )
            print(f"  {status_emoji} {source.upper()}: {status['status']}")
            if status["status"] in ["active", "stale"]:
                print(
                    f"     Last Updated: {status['last_updated']} ({status['hours_old']} hours ago)"
                )
                print(f"     Size: {status['size_mb']} MB")

        # Viral Reports
        print("\n🎯 VIRAL CONTENT REPORTS:")
        print("-" * 40)
        viral_status = health_data["viral_reports"]
        status_emoji = (
            "🟢"
            if viral_status["status"] == "active"
            else "🟡"
            if viral_status["status"] == "stale"
            else "🔴"
        )
        print(f"  {status_emoji} Viral Reports: {viral_status['status']}")

        if viral_status["status"] in ["active", "stale"]:
            print(
                f"     Last Updated: {viral_status['last_updated']} ({viral_status['hours_old']} hours ago)"
            )
            print(f"     Total Viral Items: {viral_status['total_viral_items']}")
            print(f"     Explosive Content: {viral_status['explosive_content']}")
            print(f"     High Viral Content: {viral_status['high_viral_content']}")

            # Top categories
            if viral_status.get("top_categories"):
                print("     Top Categories:")
                for category, data in list(viral_status["top_categories"].items())[:3]:
                    print(
                        f"       • {category}: {data['count']} items (avg score: {data['avg_score']:.1f})"
                    )

            # Recommendations
            if viral_status.get("recommendations"):
                print("     Recommendations:")
                for rec in viral_status["recommendations"][:3]:
                    print(f"       • {rec}")

        print("\n" + "=" * 60)

        # Recommendations
        print("\n💡 SYSTEM RECOMMENDATIONS:")
        print("-" * 40)

        if overall["percentage"] < 80:
            print("🔴 CRITICAL: System health below 80% - immediate attention required")

        # Check for stale data
        stale_sources = [
            source
            for source, status in health_data["data_collection"].items()
            if status["status"] == "stale"
        ]
        if stale_sources:
            print(f"🟡 WARNING: Stale data detected for: {', '.join(stale_sources)}")

        # Check for failed functions
        failed_functions = [
            func
            for func, status in health_data["cloud_functions"].items()
            if status["status"] == "error"
        ]
        if failed_functions:
            print(f"🔴 ERROR: Failed functions: {', '.join(failed_functions)}")

        # Check for failed schedulers
        failed_schedulers = [
            job
            for job, status in health_data["scheduler_jobs"].items()
            if status["status"] == "error"
        ]
        if failed_schedulers:
            print(f"🔴 ERROR: Failed schedulers: {', '.join(failed_schedulers)}")

        if overall["percentage"] >= 80:
            print("🟢 HEALTHY: System operating normally")

        print("\n" + "=" * 60)


def main():
    """Main function"""
    monitor = ViralSystemMonitor()

    try:
        # Get system health
        health_data = monitor.get_system_health()

        # Print report
        monitor.print_health_report(health_data)

        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"viral_system_health_{timestamp}.json"

        with open(report_file, "w") as f:
            json.dump(health_data, f, indent=2, default=str)

        print(f"\n📄 Health report saved to: {report_file}")

    except Exception as e:
        logger.error(f"❌ Error generating health report: {e}")
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
