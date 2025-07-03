"""
Comprehensive monitoring system for Degen Digest gcloud infrastructure
"""

import json
import time
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import psutil
import requests
from sqlmodel import Session, func, select

from storage.db import Digest, LLMUsage, RedditPost, Tweet, engine
from utils.advanced_logging import (
    get_logger,
    log_performance_metrics,
    log_system_health,
)

logger = get_logger(__name__)


class SystemMonitor:
    """Comprehensive system monitoring for all components"""

    def __init__(self):
        self.output_dir = Path("output")
        self.metrics_file = self.output_dir / "system_metrics.json"
        self.alerts_file = self.output_dir / "system_alerts.json"
        self.start_time = time.time()

    def collect_system_metrics(self) -> dict[str, Any]:
        """Collect comprehensive system metrics"""
        try:
            # CPU and Memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # Network
            network = psutil.net_io_counters()

            # Process info
            process = psutil.Process()
            process_memory = process.memory_info()

            metrics = {
                "timestamp": datetime.now(UTC).isoformat(),
                "uptime_seconds": time.time() - self.start_time,
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "memory_used_gb": memory.used / (1024**3),
                    "disk_percent": disk.percent,
                    "disk_free_gb": disk.free / (1024**3),
                    "network_bytes_sent": network.bytes_sent,
                    "network_bytes_recv": network.bytes_recv,
                },
                "process": {
                    "memory_rss_mb": process_memory.rss / (1024**2),
                    "memory_vms_mb": process_memory.vms / (1024**2),
                    "cpu_percent": process.cpu_percent(),
                    "num_threads": process.num_threads(),
                    "open_files": len(process.open_files()),
                    "connections": len(process.connections()),
                },
            }

            log_performance_metrics("system_collection", **metrics)
            return metrics

        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {"error": str(e)}

    def check_database_health(self) -> dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            with Session(engine) as session:
                # Check table sizes
                tweet_count = session.exec(
                    select(func.count()).select_from(Tweet)
                ).one()
                reddit_count = session.exec(
                    select(func.count()).select_from(RedditPost)
                ).one()
                digest_count = session.exec(
                    select(func.count()).select_from(Digest)
                ).one()

                # Check recent activity
                cutoff = datetime.now(UTC) - timedelta(hours=24)
                recent_tweets = session.exec(
                    select(func.count())
                    .select_from(Tweet)
                    .where(Tweet.created_at >= cutoff)
                ).one()

                recent_reddit = session.exec(
                    select(func.count())
                    .select_from(RedditPost)
                    .where(RedditPost.created_at >= cutoff)
                ).one()

                # Calculate engagement metrics
                avg_engagement = (
                    session.exec(
                        select(
                            func.avg(
                                Tweet.like_count
                                + Tweet.retweet_count * 2
                                + Tweet.reply_count * 3
                            )
                        )
                    ).one()
                    or 0
                )

                # Check data freshness
                latest_tweet = session.exec(
                    select(Tweet).order_by(Tweet.created_at.desc()).limit(1)
                ).first()

                data_freshness = "unknown"
                if latest_tweet:
                    hours_since_latest = (
                        datetime.now(UTC) - latest_tweet.created_at
                    ).total_seconds() / 3600
                    if hours_since_latest < 1:
                        data_freshness = "very_fresh"
                    elif hours_since_latest < 6:
                        data_freshness = "fresh"
                    elif hours_since_latest < 24:
                        data_freshness = "stale"
                    else:
                        data_freshness = "very_stale"

                # Get LLM usage
                month = datetime.now(UTC).strftime("%Y-%m")
                usage = session.exec(
                    select(LLMUsage).where(LLMUsage.month == month)
                ).first()
                llm_cost = usage.cost_usd if usage else 0.0

                health_metrics = {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "overall_status": "healthy",
                    "data_counts": {
                        "total_tweets": tweet_count,
                        "total_reddit_posts": reddit_count,
                        "total_digests": digest_count,
                        "recent_tweets_24h": recent_tweets,
                        "recent_reddit_24h": recent_reddit,
                    },
                    "engagement_metrics": {
                        "average_engagement": float(avg_engagement),
                        "engagement_trend": "stable",
                    },
                    "data_freshness": {
                        "status": data_freshness,
                        "hours_since_latest": hours_since_latest
                        if latest_tweet
                        else None,
                    },
                    "llm_usage": {
                        "current_month_cost": llm_cost,
                        "cost_trend": "stable",
                    },
                    "system_health": {
                        "database_connection": "healthy",
                        "file_system": "healthy",
                        "api_endpoints": "healthy",
                    },
                }

                # Determine overall status
                if data_freshness == "very_stale" or recent_tweets == 0:
                    health_metrics["overall_status"] = "warning"
                if data_freshness == "very_stale" and recent_tweets == 0:
                    health_metrics["overall_status"] = "critical"

                return health_metrics

        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "timestamp": datetime.now(UTC).isoformat(),
                "overall_status": "error",
                "error": str(e),
            }

    def check_cloud_function_health(self) -> dict[str, Any]:
        """Check cloud function health and performance"""
        try:
            # Check cloud function logs
            function_url = "https://us-central1-lucky-union-463615-t3.cloudfunctions.net/farmchecker-data-refresh"

            response = requests.get(function_url, timeout=10)

            health_metrics = {
                "timestamp": datetime.now(UTC).isoformat(),
                "function_status": "healthy"
                if response.status_code == 200
                else "unhealthy",
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "status_code": response.status_code,
                "function_url": function_url,
            }

            return health_metrics

        except Exception as e:
            logger.error(f"Cloud function health check failed: {e}")
            return {
                "timestamp": datetime.now(UTC).isoformat(),
                "function_status": "error",
                "error": str(e),
            }

    def check_external_apis(self) -> dict[str, Any]:
        """Check external API health"""
        apis_to_check = {
            "twitter_api": "https://api.twitter.com/2/tweets",
            "reddit_api": "https://www.reddit.com/api/v1/access_token",
            "newsapi": "https://newsapi.org/v2/top-headlines",
        }

        api_health = {}

        for api_name, api_url in apis_to_check.items():
            try:
                response = requests.get(api_url, timeout=5)
                api_health[api_name] = {
                    "status": "healthy" if response.status_code < 500 else "unhealthy",
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "status_code": response.status_code,
                }
            except Exception as e:
                api_health[api_name] = {"status": "error", "error": str(e)}

        return {"timestamp": datetime.now(UTC).isoformat(), "apis": api_health}

    def check_data_quality(self) -> dict[str, Any]:
        """Check data quality metrics"""
        try:
            with Session(engine) as session:
                # Check for duplicate tweets
                duplicate_tweets = session.exec(
                    select(Tweet.tweet_id, func.count(Tweet.tweet_id))
                    .group_by(Tweet.tweet_id)
                    .having(func.count(Tweet.tweet_id) > 1)
                ).all()

                # Check for tweets without engagement
                no_engagement_tweets = session.exec(
                    select(func.count())
                    .select_from(Tweet)
                    .where(
                        Tweet.like_count == 0,
                        Tweet.retweet_count == 0,
                        Tweet.reply_count == 0,
                    )
                ).one()

                # Check for malformed data
                malformed_tweets = session.exec(
                    select(func.count())
                    .select_from(Tweet)
                    .where(Tweet.full_text.is_(None))
                ).one()

                quality_metrics = {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "duplicate_tweets": len(duplicate_tweets),
                    "no_engagement_tweets": no_engagement_tweets,
                    "malformed_tweets": malformed_tweets,
                    "data_quality_score": 100
                    - (len(duplicate_tweets) * 5)
                    - (malformed_tweets * 10),
                }

                return quality_metrics

        except Exception as e:
            logger.error(f"Data quality check failed: {e}")
            return {
                "timestamp": datetime.now(UTC).isoformat(),
                "error": str(e),
            }

    def generate_alerts(self, metrics: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate alerts based on metrics"""
        alerts = []

        # System alerts
        if metrics.get("system", {}).get("cpu_percent", 0) > 80:
            alerts.append(
                {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "level": "warning",
                    "category": "system",
                    "message": f"High CPU usage: {metrics['system']['cpu_percent']}%",
                    "recommendation": "Consider scaling up resources",
                }
            )

        if metrics.get("system", {}).get("memory_percent", 0) > 85:
            alerts.append(
                {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "level": "warning",
                    "category": "system",
                    "message": f"High memory usage: {metrics['system']['memory_percent']}%",
                    "recommendation": "Check for memory leaks or scale up",
                }
            )

        # Database alerts
        if metrics.get("database", {}).get("overall_status") == "critical":
            alerts.append(
                {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "level": "critical",
                    "category": "database",
                    "message": "Database health is critical",
                    "recommendation": "Immediate attention required",
                }
            )

        # Data quality alerts
        if metrics.get("data_quality", {}).get("data_quality_score", 100) < 70:
            alerts.append(
                {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "level": "warning",
                    "category": "data_quality",
                    "message": f"Low data quality score: {metrics['data_quality']['data_quality_score']}",
                    "recommendation": "Review data processing pipeline",
                }
            )

        return alerts

    def save_metrics(self, metrics: dict[str, Any]):
        """Save metrics to file"""
        try:
            self.output_dir.mkdir(exist_ok=True)
            with open(self.metrics_file, "w") as f:
                json.dump(metrics, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")

    def save_alerts(self, alerts: list[dict[str, Any]]):
        """Save alerts to file"""
        try:
            self.output_dir.mkdir(exist_ok=True)
            with open(self.alerts_file, "w") as f:
                json.dump(alerts, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving alerts: {e}")

    def run_comprehensive_monitoring(self) -> dict[str, Any]:
        """Run comprehensive monitoring and return all metrics"""
        logger.info("Starting comprehensive system monitoring...")

        # Collect all metrics
        system_metrics = self.collect_system_metrics()
        database_health = self.check_database_health()
        cloud_function_health = self.check_cloud_function_health()
        api_health = self.check_external_apis()
        data_quality = self.check_data_quality()

        # Combine all metrics
        all_metrics = {
            "timestamp": datetime.now(UTC).isoformat(),
            "system": system_metrics,
            "database": database_health,
            "cloud_function": cloud_function_health,
            "apis": api_health,
            "data_quality": data_quality,
        }

        # Generate alerts
        alerts = self.generate_alerts(all_metrics)

        # Save metrics and alerts
        self.save_metrics(all_metrics)
        self.save_alerts(alerts)

        # Log system health
        overall_status = "healthy"
        if any(alert["level"] == "critical" for alert in alerts):
            overall_status = "critical"
        elif any(alert["level"] == "warning" for alert in alerts):
            overall_status = "warning"

        log_system_health(
            "overall",
            overall_status,
            {
                "alerts_count": len(alerts),
                "critical_alerts": len([a for a in alerts if a["level"] == "critical"]),
                "warning_alerts": len([a for a in alerts if a["level"] == "warning"]),
            },
        )

        logger.info(
            f"Monitoring complete. Status: {overall_status}, Alerts: {len(alerts)}"
        )

        return all_metrics


# Global monitor instance
system_monitor = SystemMonitor()
