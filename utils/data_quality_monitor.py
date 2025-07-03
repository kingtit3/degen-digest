#!/usr/bin/env python3
"""
Data Quality Monitoring System
Monitors and ensures high-quality data for viral prediction
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from utils.advanced_logging import get_logger

logger = get_logger(__name__)


class DataQualityMonitor:
    """Data quality monitoring system"""

    def __init__(self):
        self.quality_thresholds = {
            "completeness": 0.8,  # 80% of required fields present
            "accuracy": 0.9,  # 90% accuracy threshold
            "consistency": 0.85,  # 85% consistency threshold
            "timeliness": 3600,  # 1 hour max age for real-time data
            "validity": 0.95,  # 95% valid data threshold
        }

        self.quality_metrics = {}
        self.quality_alerts = []
        self.data_sources_status = {}

    def monitor_data_quality(self, data: list[dict], source: str) -> dict[str, Any]:
        """Monitor quality of incoming data"""

        logger.info(f"Monitoring data quality for {source}")

        quality_report = {
            "source": source,
            "timestamp": datetime.utcnow().isoformat(),
            "total_items": len(data),
            "metrics": {},
            "alerts": [],
            "overall_score": 0.0,
        }

        if not data:
            quality_report["alerts"].append("No data received")
            quality_report["overall_score"] = 0.0
            return quality_report

        # Calculate quality metrics
        completeness = self.calculate_completeness(data)
        accuracy = self.calculate_accuracy(data)
        consistency = self.calculate_consistency(data)
        timeliness = self.calculate_timeliness(data)
        validity = self.calculate_validity(data)

        quality_report["metrics"] = {
            "completeness": completeness,
            "accuracy": accuracy,
            "consistency": consistency,
            "timeliness": timeliness,
            "validity": validity,
        }

        # Calculate overall quality score
        overall_score = (
            completeness + accuracy + consistency + timeliness + validity
        ) / 5
        quality_report["overall_score"] = overall_score

        # Check for quality alerts
        alerts = self.check_quality_alerts(quality_report["metrics"])
        quality_report["alerts"] = alerts

        # Update source status
        self.data_sources_status[source] = {
            "last_check": datetime.utcnow().isoformat(),
            "quality_score": overall_score,
            "status": "healthy"
            if overall_score >= 0.8
            else "degraded"
            if overall_score >= 0.6
            else "critical",
        }

        # Store quality metrics
        self.quality_metrics[source] = quality_report

        logger.info(f"Data quality for {source}: {overall_score:.3f}")

        return quality_report

    def calculate_completeness(self, data: list[dict]) -> float:
        """Calculate data completeness score"""

        if not data:
            return 0.0

        required_fields = ["text", "timestamp", "source"]
        optional_fields = [
            "engagement_velocity",
            "viral_coefficient",
            "influence_score",
        ]

        total_required = len(required_fields) * len(data)
        total_optional = len(optional_fields) * len(data)

        required_present = 0
        optional_present = 0

        for item in data:
            # Check required fields
            for field in required_fields:
                if item.get(field) is not None and item.get(field) != "":
                    required_present += 1

            # Check optional fields
            for field in optional_fields:
                if item.get(field) is not None:
                    optional_present += 1

        required_score = required_present / total_required if total_required > 0 else 0
        optional_score = optional_present / total_optional if total_optional > 0 else 0

        # Weight required fields more heavily
        completeness = (required_score * 0.8) + (optional_score * 0.2)

        return min(completeness, 1.0)

    def calculate_accuracy(self, data: list[dict]) -> float:
        """Calculate data accuracy score"""

        if not data:
            return 0.0

        accuracy_checks = 0
        passed_checks = 0

        for item in data:
            # Check for reasonable engagement values
            engagement = item.get("engagement_velocity", 0)
            if isinstance(engagement, (int, float)) and engagement >= 0:
                passed_checks += 1
            accuracy_checks += 1

            # Check for reasonable viral coefficient
            viral_coef = item.get("viral_coefficient", 0)
            if isinstance(viral_coef, (int, float)) and 0 <= viral_coef <= 10:
                passed_checks += 1
            accuracy_checks += 1

            # Check for valid timestamps
            timestamp = (
                item.get("timestamp") or item.get("published") or item.get("created_at")
            )
            if timestamp and self.is_valid_timestamp(timestamp):
                passed_checks += 1
            accuracy_checks += 1

            # Check for reasonable text length
            text = (
                item.get("text", "") or item.get("title", "") or item.get("summary", "")
            )
            if isinstance(text, str) and 0 < len(text) < 10000:
                passed_checks += 1
            accuracy_checks += 1

        return passed_checks / accuracy_checks if accuracy_checks > 0 else 0.0

    def calculate_consistency(self, data: list[dict]) -> float:
        """Calculate data consistency score"""

        if not data:
            return 0.0

        consistency_checks = 0
        passed_checks = 0

        # Check for consistent data types
        for item in data:
            # Check engagement_velocity type consistency
            if "engagement_velocity" in item:
                if isinstance(item["engagement_velocity"], (int, float)):
                    passed_checks += 1
                consistency_checks += 1

            # Check viral_coefficient type consistency
            if "viral_coefficient" in item:
                if isinstance(item["viral_coefficient"], (int, float)):
                    passed_checks += 1
                consistency_checks += 1

            # Check source consistency
            if "source" in item:
                if isinstance(item["source"], str):
                    passed_checks += 1
                consistency_checks += 1

        return passed_checks / consistency_checks if consistency_checks > 0 else 0.0

    def calculate_timeliness(self, data: list[dict]) -> float:
        """Calculate data timeliness score"""

        if not data:
            return 0.0

        current_time = datetime.utcnow()
        total_items = len(data)
        timely_items = 0

        for item in data:
            timestamp = (
                item.get("timestamp") or item.get("published") or item.get("created_at")
            )

            if timestamp:
                try:
                    if isinstance(timestamp, str):
                        # Parse timestamp
                        if "T" in timestamp:
                            item_time = datetime.fromisoformat(
                                timestamp.replace("Z", "+00:00")
                            )
                        else:
                            item_time = datetime.fromisoformat(timestamp)
                    else:
                        item_time = timestamp

                    # Calculate age in seconds
                    age_seconds = (current_time - item_time).total_seconds()

                    # Check if within timeliness threshold
                    if age_seconds <= self.quality_thresholds["timeliness"]:
                        timely_items += 1

                except Exception as e:
                    logger.warning(f"Failed to parse timestamp {timestamp}: {e}")
                    continue

        return timely_items / total_items if total_items > 0 else 0.0

    def calculate_validity(self, data: list[dict]) -> float:
        """Calculate data validity score"""

        if not data:
            return 0.0

        valid_items = 0
        total_items = len(data)

        for item in data:
            is_valid = True

            # Check for required fields
            if (
                not item.get("text")
                and not item.get("title")
                and not item.get("summary")
            ):
                is_valid = False

            # Check for valid source
            if not item.get("source"):
                is_valid = False

            # Check for valid engagement metrics
            engagement = item.get("engagement_velocity", 0)
            if not isinstance(engagement, (int, float)) or engagement < 0:
                is_valid = False

            # Check for valid viral coefficient
            viral_coef = item.get("viral_coefficient", 0)
            if not isinstance(viral_coef, (int, float)) or viral_coef < 0:
                is_valid = False

            if is_valid:
                valid_items += 1

        return valid_items / total_items if total_items > 0 else 0.0

    def is_valid_timestamp(self, timestamp) -> bool:
        """Check if timestamp is valid"""

        try:
            if isinstance(timestamp, str):
                if "T" in timestamp:
                    datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                else:
                    datetime.fromisoformat(timestamp)
            elif isinstance(timestamp, datetime):
                return True
            else:
                return False
            return True
        except Exception:
            return False

    def check_quality_alerts(self, metrics: dict[str, float]) -> list[str]:
        """Check for quality alerts based on metrics"""

        alerts = []

        for metric_name, threshold in self.quality_thresholds.items():
            if metric_name in metrics:
                metric_value = metrics[metric_name]

                if metric_value < threshold:
                    alerts.append(
                        f"{metric_name} below threshold: {metric_value:.3f} < {threshold}"
                    )

        return alerts

    def get_quality_summary(self) -> dict[str, Any]:
        """Get overall quality summary"""

        if not self.quality_metrics:
            return {"status": "no_data", "overall_score": 0.0}

        # Calculate overall quality score
        total_score = 0
        source_count = 0

        for source, metrics in self.quality_metrics.items():
            if "overall_score" in metrics:
                total_score += metrics["overall_score"]
                source_count += 1

        overall_score = total_score / source_count if source_count > 0 else 0.0

        # Determine overall status
        if overall_score >= 0.8:
            status = "excellent"
        elif overall_score >= 0.6:
            status = "good"
        elif overall_score >= 0.4:
            status = "fair"
        else:
            status = "poor"

        return {
            "status": status,
            "overall_score": overall_score,
            "sources_monitored": source_count,
            "last_update": datetime.utcnow().isoformat(),
            "source_status": self.data_sources_status,
        }

    def save_quality_report(self, output_dir: str = "output/enhanced_pipeline"):
        """Save quality monitoring report"""

        try:
            report = {
                "quality_thresholds": self.quality_thresholds,
                "quality_metrics": self.quality_metrics,
                "data_sources_status": self.data_sources_status,
                "quality_summary": self.get_quality_summary(),
                "generated_at": datetime.utcnow().isoformat(),
            }

            output_path = Path(output_dir) / "data_quality_report.json"
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w") as f:
                json.dump(report, f, indent=2, default=str)

            logger.info(f"Quality report saved to {output_path}")

        except Exception as e:
            logger.error(f"Failed to save quality report: {e}")

    def get_recommendations(self) -> list[str]:
        """Get data quality improvement recommendations"""

        recommendations = []

        for source, metrics in self.quality_metrics.items():
            if "metrics" in metrics:
                source_metrics = metrics["metrics"]

                # Check completeness
                if source_metrics.get("completeness", 0) < 0.8:
                    recommendations.append(f"Improve data completeness for {source}")

                # Check accuracy
                if source_metrics.get("accuracy", 0) < 0.9:
                    recommendations.append(f"Improve data accuracy for {source}")

                # Check timeliness
                if source_metrics.get("timeliness", 0) < 0.8:
                    recommendations.append(f"Improve data timeliness for {source}")

        return recommendations


def main():
    """Test the data quality monitor"""

    monitor = DataQualityMonitor()

    # Sample data for testing
    sample_data = [
        {
            "text": "Bitcoin is going to the moon! 🚀",
            "timestamp": datetime.utcnow().isoformat(),
            "source": "twitter",
            "engagement_velocity": 10.5,
            "viral_coefficient": 0.8,
            "influence_score": 85.2,
        },
        {
            "text": "Ethereum merge is amazing!",
            "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "source": "reddit",
            "engagement_velocity": 5.2,
            "viral_coefficient": 0.3,
        },
    ]

    # Monitor quality
    quality_report = monitor.monitor_data_quality(sample_data, "test_source")

    print("Data Quality Report:")
    print(json.dumps(quality_report, indent=2))

    # Get summary
    summary = monitor.get_quality_summary()
    print("\nQuality Summary:")
    print(json.dumps(summary, indent=2))

    # Get recommendations
    recommendations = monitor.get_recommendations()
    print("\nRecommendations:")
    for rec in recommendations:
        print(f"- {rec}")


if __name__ == "__main__":
    main()
