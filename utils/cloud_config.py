"""
Cloud Configuration Manager
Loads and manages centralized configuration for all cloud-based components.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class CloudConfig:
    """Centralized cloud configuration manager"""

    def __init__(self, config_path: str | None = None):
        """Initialize configuration manager"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "cloud_config.yaml"

        self.config_path = Path(config_path)
        self._config = None
        self._load_config()

    def _load_config(self):
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, encoding="utf-8") as f:
                self._config = yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Error loading config from {self.config_path}: {e}")
            self._config = self._get_default_config()

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration if file loading fails"""
        return {
            "google_cloud": {
                "project_id": "lucky-union-463615-t3",
                "region": "us-central1",
                "bucket_name": "degen-digest-data",
            },
            "services": {
                "crawler": {
                    "name": "solana-crawler",
                    "url": "https://solana-crawler-128671663649.us-central1.run.app",
                },
                "dashboard": {
                    "name": "farmchecker",
                    "url": "https://farmchecker-128671663649.us-central1.run.app",
                },
            },
        }

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'google_cloud.project_id')"""
        keys = key_path.split(".")
        value = self._config

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def get_gcs_config(self) -> dict[str, str]:
        """Get Google Cloud Storage configuration"""
        return {
            "project_id": self.get("google_cloud.project_id"),
            "bucket_name": self.get("google_cloud.bucket_name"),
            "region": self.get("google_cloud.region"),
        }

    def get_service_url(self, service_name: str) -> str | None:
        """Get service URL by name"""
        return self.get(f"services.{service_name}.url")

    def get_data_path(self, data_type: str, source: str) -> str | None:
        """Get data path for specific type and source"""
        return self.get(f"data_structure.{data_type}.{source}")

    def get_file_pattern(self, source: str, pattern_type: str = "raw") -> str | None:
        """Get file naming pattern for source"""
        return self.get(f"file_naming.patterns.{source}_{pattern_type}")

    def get_consolidated_path(self, source: str) -> str:
        """Get consolidated data path for source"""
        return self.get(
            f"data_structure.consolidated.{source}",
            f"consolidated/{source}_consolidated.json",
        )

    def get_raw_data_path(self, source: str) -> str:
        """Get raw data path for source"""
        return self.get(f"data_structure.raw_data.{source}", f"{source}_data/")

    def get_analytics_path(self, analytics_type: str) -> str:
        """Get analytics path for type"""
        return self.get(
            f"data_structure.analytics.{analytics_type}",
            f"analytics/{analytics_type}.json",
        )

    def get_digest_path(self, digest_type: str = "latest") -> str:
        """Get digest path for type"""
        return self.get(
            f"data_structure.digests.{digest_type}", f"digests/{digest_type}_digest.md"
        )

    def get_quality_settings(self) -> dict[str, Any]:
        """Get data quality settings"""
        return self.get("data_processing.quality", {})

    def get_engagement_settings(self) -> dict[str, Any]:
        """Get engagement scoring settings"""
        return self.get("data_processing.engagement", {})

    def get_monitoring_config(self) -> dict[str, Any]:
        """Get monitoring configuration"""
        return self.get("monitoring", {})

    def get_logging_config(self) -> dict[str, Any]:
        """Get logging configuration"""
        return self.get("logging", {})

    def get_security_config(self) -> dict[str, Any]:
        """Get security configuration"""
        return self.get("security", {})

    def validate_config(self) -> bool:
        """Validate that required configuration is present"""
        required_keys = [
            "google_cloud.project_id",
            "google_cloud.bucket_name",
            "services.crawler.url",
            "services.dashboard.url",
        ]

        for key in required_keys:
            if self.get(key) is None:
                print(f"❌ Missing required config key: {key}")
                return False

        print("✅ Configuration validation passed")
        return True

    def print_summary(self):
        """Print configuration summary"""
        print("📋 Cloud Configuration Summary")
        print("=" * 40)
        print(f"Project: {self.get('project.name', 'Degen Digest')}")
        print(f"Version: {self.get('project.version', 'Unknown')}")
        print(f"GCS Project: {self.get('google_cloud.project_id')}")
        print(f"GCS Bucket: {self.get('google_cloud.bucket_name')}")
        print(f"Crawler URL: {self.get('services.crawler.url')}")
        print(f"Dashboard URL: {self.get('services.dashboard.url')}")
        print("=" * 40)


# Global configuration instance
config = CloudConfig()


def get_config() -> CloudConfig:
    """Get global configuration instance"""
    return config


def get_gcs_client_config() -> dict[str, str]:
    """Get GCS client configuration"""
    return config.get_gcs_config()


def get_service_url(service_name: str) -> str | None:
    """Get service URL by name"""
    return config.get_service_url(service_name)


def get_data_path(data_type: str, source: str) -> str | None:
    """Get data path for specific type and source"""
    return config.get_data_path(data_type, source)


def get_consolidated_path(source: str) -> str:
    """Get consolidated data path for source"""
    return config.get_consolidated_path(source)


def get_raw_data_path(source: str) -> str:
    """Get raw data path for source"""
    return config.get_raw_data_path(source)


def get_analytics_path(analytics_type: str) -> str:
    """Get analytics path for type"""
    return config.get_analytics_path(analytics_type)


def get_digest_path(digest_type: str = "latest") -> str:
    """Get digest path for type"""
    return config.get_digest_path(digest_type)


# Convenience functions for common configurations
def get_twitter_config() -> dict[str, str]:
    """Get Twitter-specific configuration"""
    return {
        "raw_path": get_raw_data_path("twitter"),
        "consolidated_path": get_consolidated_path("twitter"),
        "latest_path": get_data_path("latest", "twitter"),
        "file_pattern": config.get_file_pattern("twitter", "raw"),
    }


def get_crawler_config() -> dict[str, Any]:
    """Get crawler-specific configuration"""
    return {
        "url": get_service_url("crawler"),
        "schedule": config.get("services.crawler.schedule", {}),
        "health_check": config.get("monitoring.health_checks.crawler", "/status"),
    }


def get_dashboard_config() -> dict[str, Any]:
    """Get dashboard-specific configuration"""
    return {
        "url": get_service_url("dashboard"),
        "port": config.get("services.dashboard.port", 8501),
        "health_check": config.get(
            "monitoring.health_checks.dashboard", "/_stcore/health"
        ),
    }


if __name__ == "__main__":
    # Test configuration loading
    config.print_summary()
    config.validate_config()
