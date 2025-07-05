#!/usr/bin/env python3
"""
Enhanced Monitoring Configuration for DegenDigest
Ensures every aspect of the project has comprehensive monitoring and logging
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List


class EnhancedMonitoringConfig:
    """
    Comprehensive monitoring configuration that covers all aspects of the project
    """

    def __init__(self):
        self.config = self._create_comprehensive_config()
        self._save_configs()

    def _create_comprehensive_config(self) -> dict[str, Any]:
        """Create comprehensive monitoring configuration"""
        return {
            "logging": {
                "global": {
                    "level": "INFO",
                    "format": "json",
                    "directory": "logs",
                    "max_file_size_mb": 100,
                    "backup_count": 10,
                    "retention_days": 30,
                },
                "services": {
                    "crawler": {
                        "level": "DEBUG",
                        "enable_performance_logging": True,
                        "enable_api_logging": True,
                        "enable_error_tracking": True,
                    },
                    "dashboard": {
                        "level": "INFO",
                        "enable_user_activity_logging": True,
                        "enable_performance_logging": True,
                    },
                    "processor": {
                        "level": "DEBUG",
                        "enable_ai_logging": True,
                        "enable_data_processing_logging": True,
                    },
                    "cloud_function": {
                        "level": "INFO",
                        "enable_execution_logging": True,
                        "enable_cost_tracking": True,
                    },
                    "database": {
                        "level": "DEBUG",
                        "enable_query_logging": True,
                        "enable_connection_logging": True,
                    },
                },
                "structured_fields": [
                    "service_name",
                    "operation",
                    "request_id",
                    "user_id",
                    "session_id",
                    "duration_ms",
                    "status_code",
                    "error_code",
                    "metadata",
                ],
            },
            "monitoring": {
                "health_checks": {
                    "interval_seconds": 60,
                    "timeout_seconds": 30,
                    "retry_count": 3,
                    "components": {
                        "system": {
                            "enabled": True,
                            "checks": ["cpu", "memory", "disk", "network", "processes"],
                        },
                        "database": {
                            "enabled": True,
                            "checks": ["connectivity", "performance", "size", "backup"],
                        },
                        "services": {
                            "enabled": True,
                            "checks": ["crawler", "dashboard", "cloud_function", "api"],
                        },
                        "apis": {
                            "enabled": True,
                            "checks": [
                                "twitter",
                                "reddit",
                                "news",
                                "crypto",
                                "openrouter",
                            ],
                        },
                        "data_quality": {
                            "enabled": True,
                            "checks": [
                                "completeness",
                                "accuracy",
                                "consistency",
                                "timeliness",
                            ],
                        },
                        "security": {
                            "enabled": True,
                            "checks": [
                                "authentication",
                                "authorization",
                                "rate_limits",
                                "suspicious_activity",
                            ],
                        },
                    },
                },
                "metrics": {
                    "collection_interval_seconds": 30,
                    "retention_hours": 168,  # 7 days
                    "categories": {
                        "system": ["cpu", "memory", "disk", "network", "load"],
                        "application": [
                            "requests",
                            "response_time",
                            "error_rate",
                            "throughput",
                        ],
                        "business": [
                            "crawls",
                            "tweets_collected",
                            "digests_generated",
                            "user_engagement",
                        ],
                        "cost": [
                            "api_calls",
                            "llm_usage",
                            "storage_usage",
                            "compute_usage",
                        ],
                    },
                },
                "alerting": {
                    "enabled": True,
                    "channels": {
                        "webhook": {
                            "enabled": True,
                            "url": os.environ.get("MONITORING_WEBHOOK_URL"),
                            "timeout_seconds": 10,
                        },
                        "slack": {
                            "enabled": True,
                            "webhook_url": os.environ.get("MONITORING_SLACK_WEBHOOK"),
                            "channel": "#monitoring",
                        },
                        "email": {
                            "enabled": True,
                            "recipients": os.environ.get("MONITORING_EMAILS", "").split(
                                ","
                            ),
                            "smtp_config": {
                                "host": os.environ.get("SMTP_HOST"),
                                "port": int(os.environ.get("SMTP_PORT", "587")),
                                "username": os.environ.get("SMTP_USERNAME"),
                                "password": os.environ.get("SMTP_PASSWORD"),
                            },
                        },
                    },
                    "rules": {
                        "critical": {
                            "cpu_usage": 90,
                            "memory_usage": 95,
                            "disk_usage": 95,
                            "error_rate": 0.1,
                            "response_time_ms": 5000,
                            "crawler_stopped": True,
                            "database_unavailable": True,
                        },
                        "warning": {
                            "cpu_usage": 80,
                            "memory_usage": 85,
                            "disk_usage": 90,
                            "error_rate": 0.05,
                            "response_time_ms": 2000,
                            "data_freshness_hours": 2,
                            "quality_score": 0.8,
                        },
                    },
                },
            },
            "data_quality": {
                "monitoring": {
                    "enabled": True,
                    "check_interval_seconds": 300,
                    "thresholds": {
                        "completeness": 0.8,
                        "accuracy": 0.9,
                        "consistency": 0.85,
                        "timeliness": 3600,
                        "validity": 0.95,
                    },
                    "sources": {
                        "twitter": {
                            "required_fields": [
                                "text",
                                "timestamp",
                                "source",
                                "engagement_velocity",
                            ],
                            "validation_rules": [
                                "text_length > 0",
                                "timestamp_valid",
                                "engagement_velocity >= 0",
                            ],
                        },
                        "reddit": {
                            "required_fields": [
                                "title",
                                "url",
                                "author",
                                "created_utc",
                            ],
                            "validation_rules": [
                                "title_length > 0",
                                "url_valid",
                                "created_utc_valid",
                            ],
                        },
                        "news": {
                            "required_fields": [
                                "title",
                                "url",
                                "publishedAt",
                                "source",
                            ],
                            "validation_rules": [
                                "title_length > 0",
                                "url_valid",
                                "publishedAt_valid",
                            ],
                        },
                    },
                }
            },
            "performance": {
                "tracking": {
                    "enabled": True,
                    "operations": {
                        "crawl_operation": {
                            "enabled": True,
                            "threshold_ms": 300000,  # 5 minutes
                            "track_memory": True,
                            "track_cpu": True,
                        },
                        "digest_generation": {
                            "enabled": True,
                            "threshold_ms": 60000,  # 1 minute
                            "track_memory": True,
                            "track_cpu": True,
                        },
                        "ai_processing": {
                            "enabled": True,
                            "threshold_ms": 30000,  # 30 seconds
                            "track_tokens": True,
                            "track_cost": True,
                        },
                        "database_operations": {
                            "enabled": True,
                            "threshold_ms": 1000,  # 1 second
                            "track_queries": True,
                            "track_connections": True,
                        },
                    },
                }
            },
            "security": {
                "monitoring": {
                    "enabled": True,
                    "events": {
                        "authentication": {
                            "enabled": True,
                            "track_failures": True,
                            "track_success": True,
                            "alert_threshold": 5,
                        },
                        "authorization": {
                            "enabled": True,
                            "track_access_denied": True,
                            "track_permission_changes": True,
                        },
                        "rate_limiting": {
                            "enabled": True,
                            "track_violations": True,
                            "alert_threshold": 10,
                        },
                        "suspicious_activity": {
                            "enabled": True,
                            "patterns": [
                                "multiple_failed_logins",
                                "unusual_api_usage",
                                "data_access_patterns",
                            ],
                        },
                    },
                }
            },
            "cost_tracking": {
                "enabled": True,
                "providers": {
                    "openrouter": {
                        "enabled": True,
                        "track_requests": True,
                        "track_tokens": True,
                        "track_costs": True,
                        "alert_threshold_usd": 10.0,
                    },
                    "google_cloud": {
                        "enabled": True,
                        "track_storage": True,
                        "track_compute": True,
                        "track_network": True,
                        "alert_threshold_usd": 50.0,
                    },
                    "apify": {
                        "enabled": True,
                        "track_credits": True,
                        "track_runs": True,
                        "alert_threshold_credits": 100,
                    },
                },
            },
            "reporting": {
                "enabled": True,
                "reports": {
                    "daily": {
                        "enabled": True,
                        "schedule": "0 0 * * *",  # Daily at midnight
                        "include": [
                            "system_health",
                            "data_quality",
                            "cost_summary",
                            "alerts",
                        ],
                    },
                    "weekly": {
                        "enabled": True,
                        "schedule": "0 0 * * 0",  # Weekly on Sunday
                        "include": [
                            "trends",
                            "performance_analysis",
                            "capacity_planning",
                        ],
                    },
                    "monthly": {
                        "enabled": True,
                        "schedule": "0 0 1 * *",  # Monthly on 1st
                        "include": [
                            "comprehensive_analysis",
                            "recommendations",
                            "cost_optimization",
                        ],
                    },
                },
                "retention": {
                    "daily_reports_days": 30,
                    "weekly_reports_days": 90,
                    "monthly_reports_days": 365,
                },
            },
        }

    def _save_configs(self):
        """Save monitoring configurations to files"""
        config_dir = Path("config/monitoring")
        config_dir.mkdir(parents=True, exist_ok=True)

        # Save main configuration
        with open(config_dir / "enhanced_monitoring_config.json", "w") as f:
            json.dump(self.config, f, indent=2)

        # Save individual component configurations
        for component, config in self.config.items():
            with open(config_dir / f"{component}_config.json", "w") as f:
                json.dump(config, f, indent=2)

        # Create environment-specific configurations
        self._create_environment_configs()

    def _create_environment_configs(self):
        """Create environment-specific monitoring configurations"""
        environments = {
            "development": {
                "logging": {"level": "DEBUG"},
                "monitoring": {"health_checks": {"interval_seconds": 30}},
                "alerting": {"enabled": False},
            },
            "staging": {
                "logging": {"level": "INFO"},
                "monitoring": {"health_checks": {"interval_seconds": 60}},
                "alerting": {
                    "enabled": True,
                    "channels": {"email": {"enabled": False}},
                },
            },
            "production": {
                "logging": {"level": "INFO"},
                "monitoring": {"health_checks": {"interval_seconds": 60}},
                "alerting": {"enabled": True},
            },
        }

        config_dir = Path("config/monitoring")

        for env, overrides in environments.items():
            env_config = self._merge_config(self.config, overrides)
            with open(config_dir / f"config_{env}.json", "w") as f:
                json.dump(env_config, f, indent=2)

    def _merge_config(
        self, base_config: dict[str, Any], overrides: dict[str, Any]
    ) -> dict[str, Any]:
        """Merge configuration overrides with base configuration"""
        import copy

        merged = copy.deepcopy(base_config)

        def merge_dict(base, override):
            for key, value in override.items():
                if (
                    key in base
                    and isinstance(base[key], dict)
                    and isinstance(value, dict)
                ):
                    merge_dict(base[key], value)
                else:
                    base[key] = value

        merge_dict(merged, overrides)
        return merged

    def get_config(
        self, component: str = None, environment: str = "production"
    ) -> dict[str, Any]:
        """Get monitoring configuration"""
        if component:
            return self.config.get(component, {})
        return self.config

    def validate_config(self) -> list[str]:
        """Validate monitoring configuration"""
        errors = []

        # Check required environment variables
        required_env_vars = [
            "MONITORING_WEBHOOK_URL",
            "MONITORING_SLACK_WEBHOOK",
            "MONITORING_EMAILS",
        ]

        for var in required_env_vars:
            if not os.environ.get(var):
                errors.append(f"Missing environment variable: {var}")

        # Check configuration structure
        required_components = [
            "logging",
            "monitoring",
            "data_quality",
            "performance",
            "security",
        ]
        for component in required_components:
            if component not in self.config:
                errors.append(f"Missing configuration component: {component}")

        # Check monitoring thresholds
        thresholds = (
            self.config.get("monitoring", {}).get("alerting", {}).get("rules", {})
        )
        if not thresholds.get("critical") or not thresholds.get("warning"):
            errors.append("Missing alerting thresholds")

        return errors

    def generate_monitoring_script(self) -> str:
        """Generate monitoring startup script"""
        script = '''#!/usr/bin/env python3
"""
Enhanced Monitoring Startup Script
Automatically starts comprehensive monitoring for all project components
"""

import os
import sys
import subprocess
from pathlib import Path

def start_monitoring():
    """Start all monitoring components"""
    print("🚀 Starting Enhanced DegenDigest Monitoring...")

    # Start continuous monitoring service
    subprocess.Popen([sys.executable, "continuous_monitoring_service.py"])

    # Start health monitoring dashboard
    subprocess.Popen([sys.executable, "-m", "streamlit", "run", "dashboard/main.py"])

    # Start log monitoring
    subprocess.Popen([sys.executable, "scripts/monitor_logs.py"])

    print("✅ All monitoring components started")

if __name__ == "__main__":
    start_monitoring()
'''
        return script


def main():
    """Main function to setup enhanced monitoring"""
    print("🔧 Setting up Enhanced Monitoring Configuration")
    print("=" * 50)

    # Create enhanced monitoring configuration
    config = EnhancedMonitoringConfig()

    # Validate configuration
    errors = config.validate_config()

    if errors:
        print("❌ Configuration validation errors:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease fix the above errors before proceeding.")
        return

    print("✅ Configuration created successfully")
    print("\n📁 Generated files:")
    print("  - config/monitoring/enhanced_monitoring_config.json")
    print("  - config/monitoring/logging_config.json")
    print("  - config/monitoring/monitoring_config.json")
    print("  - config/monitoring/data_quality_config.json")
    print("  - config/monitoring/performance_config.json")
    print("  - config/monitoring/security_config.json")
    print("  - config/monitoring/cost_tracking_config.json")
    print("  - config/monitoring/reporting_config.json")
    print("  - config/monitoring/config_development.json")
    print("  - config/monitoring/config_staging.json")
    print("  - config/monitoring/config_production.json")

    print("\n🚀 Next steps:")
    print("  1. Review the generated configurations")
    print("  2. Set required environment variables")
    print("  3. Start the continuous monitoring service")
    print("  4. Access the monitoring dashboard")

    # Save monitoring startup script
    script_content = config.generate_monitoring_script()
    with open("start_monitoring.py", "w") as f:
        f.write(script_content)

    print("\n📝 Created start_monitoring.py script")
    print("   Run: python start_monitoring.py")


if __name__ == "__main__":
    main()
