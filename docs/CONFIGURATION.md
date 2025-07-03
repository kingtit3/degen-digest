# Configuration Guide

This document provides comprehensive configuration information for the Degen Digest platform.

## Table of Contents

- [Environment Variables](#environment-variables)
- [Application Configuration](#application-configuration)
- [Database Configuration](#database-configuration)
- [Cloud Configuration](#cloud-configuration)
- [API Configuration](#api-configuration)
- [Security Configuration](#security-configuration)
- [Monitoring Configuration](#monitoring-configuration)

## Environment Variables

### Core Application

| Variable      | Required | Default       | Description                                          |
| ------------- | -------- | ------------- | ---------------------------------------------------- |
| `ENVIRONMENT` | No       | `development` | Environment: development, staging, production        |
| `LOG_LEVEL`   | No       | `INFO`        | Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `LOG_FORMAT`  | No       | `console`     | Log format: console, json                            |
| `TIMEZONE`    | No       | `UTC`         | Application timezone                                 |

### Database Configuration

| Variable                | Required | Default | Description                                         |
| ----------------------- | -------- | ------- | --------------------------------------------------- |
| `DATABASE_URL`          | Yes      | -       | SQLite database URL or PostgreSQL connection string |
| `DATABASE_POOL_SIZE`    | No       | `10`    | Database connection pool size                       |
| `DATABASE_MAX_OVERFLOW` | No       | `20`    | Database connection pool max overflow               |
| `DATABASE_ECHO`         | No       | `false` | Enable SQL query logging                            |

### Google Cloud Configuration

| Variable                         | Required | Default             | Description                      |
| -------------------------------- | -------- | ------------------- | -------------------------------- |
| `GOOGLE_CLOUD_PROJECT`           | Yes      | -                   | Google Cloud project ID          |
| `GOOGLE_CLOUD_REGION`            | No       | `us-central1`       | Google Cloud region              |
| `GCS_BUCKET_NAME`                | No       | `degen-digest-data` | Google Cloud Storage bucket name |
| `GOOGLE_APPLICATION_CREDENTIALS` | Yes\*    | -                   | Path to service account key file |

\*Required for local development, auto-configured in Cloud Run

### API Configuration

#### OpenRouter (LLM)

| Variable                     | Required | Default                        | Description               |
| ---------------------------- | -------- | ------------------------------ | ------------------------- |
| `OPENROUTER_API_KEY`         | Yes      | -                              | OpenRouter API key        |
| `OPENROUTER_API_BASE`        | No       | `https://openrouter.ai/api/v1` | OpenRouter API base URL   |
| `OPENROUTER_MODEL`           | No       | `google/gemini-2.0-flash-001`  | Default LLM model         |
| `LLM_BUDGET_MONTHLY_USD`     | No       | `10.0`                         | Monthly LLM budget in USD |
| `OPENROUTER_COST_PER_1K_USD` | No       | `0.005`                        | Cost per 1K tokens in USD |

#### Twitter/X Configuration

| Variable           | Required | Default | Description                              |
| ------------------ | -------- | ------- | ---------------------------------------- |
| `TWITTER_USERNAME` | Yes      | -       | Twitter username for crawler             |
| `TWITTER_PASSWORD` | Yes      | -       | Twitter password for crawler             |
| `APIFY_API_TOKEN`  | No       | -       | Apify API token for alternative scraping |

#### Other APIs

| Variable             | Required | Default | Description                     |
| -------------------- | -------- | ------- | ------------------------------- |
| `NEWSAPI_API_KEY`    | No       | -       | NewsAPI key for news collection |
| `TELEGRAM_API_ID`    | No       | -       | Telegram API ID                 |
| `TELEGRAM_API_HASH`  | No       | -       | Telegram API hash               |
| `NOTION_TOKEN`       | No       | -       | Notion integration token        |
| `NOTION_DATABASE_ID` | No       | -       | Notion database ID              |

### Crawler Configuration

| Variable                   | Required | Default | Description                         |
| -------------------------- | -------- | ------- | ----------------------------------- |
| `CRAWLER_START_HOUR`       | No       | `6`     | Crawler start hour (24-hour format) |
| `CRAWLER_END_HOUR`         | No       | `0`     | Crawler end hour (24-hour format)   |
| `CRAWLER_INTERVAL_MINUTES` | No       | `30`    | Crawler interval in minutes         |
| `CRAWLER_MAX_RETRIES`      | No       | `3`     | Maximum retry attempts for crawler  |
| `CRAWLER_HEADLESS`         | No       | `true`  | Run crawler in headless mode        |

### Dashboard Configuration

| Variable                               | Required | Default   | Description                    |
| -------------------------------------- | -------- | --------- | ------------------------------ |
| `STREAMLIT_SERVER_PORT`                | No       | `8501`    | Streamlit server port          |
| `STREAMLIT_SERVER_ADDRESS`             | No       | `0.0.0.0` | Streamlit server address       |
| `STREAMLIT_SERVER_HEADLESS`            | No       | `true`    | Run Streamlit in headless mode |
| `STREAMLIT_BROWSER_GATHER_USAGE_STATS` | No       | `false`   | Disable usage statistics       |

### Security Configuration

| Variable              | Required | Default | Description                           |
| --------------------- | -------- | ------- | ------------------------------------- |
| `SECRET_KEY`          | Yes      | -       | Application secret key                |
| `ALLOWED_HOSTS`       | No       | `*`     | Comma-separated list of allowed hosts |
| `CORS_ORIGINS`        | No       | `*`     | Comma-separated list of CORS origins  |
| `RATE_LIMIT_REQUESTS` | No       | `100`   | Rate limit requests per minute        |
| `RATE_LIMIT_WINDOW`   | No       | `60`    | Rate limit window in seconds          |

### Monitoring Configuration

| Variable                | Required | Default | Description                      |
| ----------------------- | -------- | ------- | -------------------------------- |
| `ENABLE_HEALTH_CHECKS`  | No       | `true`  | Enable health check endpoints    |
| `HEALTH_CHECK_INTERVAL` | No       | `300`   | Health check interval in seconds |
| `METRICS_ENABLED`       | No       | `true`  | Enable metrics collection        |
| `ALERT_EMAIL`           | No       | -       | Email for system alerts          |
| `SLACK_WEBHOOK_URL`     | No       | -       | Slack webhook for alerts         |

## Application Configuration

### Configuration Files

The application uses YAML configuration files located in the `config/` directory:

#### `config/app_config.yaml`

```yaml
# Application-wide settings
app:
  name: "Degen Digest"
  version: "2.0.0"
  environment: "production"

# Data processing settings
processing:
  max_items_per_batch: 1000
  batch_timeout_seconds: 300
  retry_attempts: 3
  retry_delay_seconds: 60

# Crawler settings
crawler:
  max_concurrent_crawls: 5
  crawl_timeout_seconds: 1800
  rate_limit_delay_seconds: 2
  user_agent: "Mozilla/5.0 (compatible; DegenDigest/2.0)"

# AI/ML settings
ai:
  model_name: "google/gemini-2.0-flash-001"
  max_tokens: 1000
  temperature: 0.7
  batch_size: 10

# Dashboard settings
dashboard:
  refresh_interval_seconds: 30
  max_items_per_page: 50
  enable_real_time_updates: true

# Monitoring settings
monitoring:
  health_check_interval_seconds: 300
  metrics_collection_interval_seconds: 60
  alert_thresholds:
    cpu_usage_percent: 80
    memory_usage_percent: 85
    disk_usage_percent: 90
    error_rate_percent: 5
```

#### `config/keywords.py`

```python
# Keywords for content filtering and categorization
KEYWORDS = {
    "solana": [
        "sol", "solana", "phantom", "saga", "jupiter", "raydium",
        "serum", "orca", "saber", "mercurial", "mango", "synthetify"
    ],
    "defi": [
        "defi", "yield", "liquidity", "amm", "dex", "swap", "farm",
        "stake", "governance", "dao", "lending", "borrowing"
    ],
    "nft": [
        "nft", "mint", "floor", "rarity", "opensea", "magiceden",
        "collection", "metadata", "royalties", "marketplace"
    ]
}
```

#### `config/influencers.py`

```python
# Influential accounts to monitor
INFLUENCERS = {
    "solana": [
        "solana", "solanalabs", "sbf", "rajgokal", "anatoly",
        "jupiter", "raydium", "phantom", "saga"
    ],
    "defi": [
        "defipulse", "defillama", "coingecko", "coinmarketcap",
        "thedefiant", "defiprime"
    ],
    "general": [
        "cz_binance", "saylor", "elonmusk", "vitalikbuterin",
        "chamath", "naval"
    ]
}
```

## Database Configuration

### SQLite (Development)

```bash
DATABASE_URL=sqlite:///output/degen_digest.db
```

### PostgreSQL (Production)

```bash
DATABASE_URL=postgresql://username:password@host:port/database
```

### Connection Pool Settings

```python
# Recommended production settings
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600
```

## Cloud Configuration

### Google Cloud Run

```yaml
# service.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: degen-digest
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "1"
        autoscaling.knative.dev/maxScale: "10"
    spec:
      containerConcurrency: 80
      timeoutSeconds: 300
      containers:
        - image: gcr.io/PROJECT_ID/degen-digest:latest
          env:
            - name: ENVIRONMENT
              value: "production"
            - name: GOOGLE_CLOUD_PROJECT
              value: "PROJECT_ID"
          resources:
            limits:
              cpu: "2"
              memory: "4Gi"
            requests:
              cpu: "1"
              memory: "2Gi"
```

### Google Cloud Storage

```bash
# Bucket configuration
gsutil mb -l us-central1 gs://degen-digest-data
gsutil iam ch allUsers:objectViewer gs://degen-digest-data
```

## API Configuration

### Rate Limiting

```python
# Rate limiting configuration
RATE_LIMITS = {
    "default": {
        "requests": 100,
        "window": 60  # seconds
    },
    "crawler": {
        "requests": 10,
        "window": 60
    },
    "api": {
        "requests": 1000,
        "window": 3600
    }
}
```

### API Endpoints

```python
# API endpoint configuration
API_ENDPOINTS = {
    "health": "/health",
    "status": "/status",
    "metrics": "/metrics",
    "crawler": {
        "start": "/start",
        "stop": "/stop",
        "status": "/status"
    },
    "dashboard": {
        "data": "/api/data",
        "analytics": "/api/analytics",
        "digest": "/api/digest"
    }
}
```

## Security Configuration

### Environment Security

```bash
# Production security checklist
- [ ] All secrets stored in environment variables
- [ ] No hardcoded credentials in code
- [ ] HTTPS enabled for all endpoints
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Input validation implemented
- [ ] SQL injection protection
- [ ] XSS protection
- [ ] CSRF protection
```

### Access Control

```python
# Access control configuration
ACCESS_CONTROL = {
    "admin_emails": [
        "admin@farmchecker.xyz",
        "dev@farmchecker.xyz"
    ],
    "allowed_ips": [
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16"
    ],
    "api_keys": {
        "read": ["key1", "key2"],
        "write": ["admin_key1"],
        "admin": ["super_admin_key"]
    }
}
```

## Monitoring Configuration

### Health Checks

```python
# Health check configuration
HEALTH_CHECKS = {
    "database": {
        "enabled": True,
        "timeout": 5,
        "interval": 60
    },
    "external_apis": {
        "enabled": True,
        "timeout": 10,
        "interval": 300
    },
    "storage": {
        "enabled": True,
        "timeout": 5,
        "interval": 120
    },
    "crawler": {
        "enabled": True,
        "timeout": 30,
        "interval": 300
    }
}
```

### Alerting

```python
# Alert configuration
ALERTS = {
    "email": {
        "enabled": True,
        "recipients": ["alerts@farmchecker.xyz"],
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587
    },
    "slack": {
        "enabled": True,
        "webhook_url": "https://hooks.slack.com/...",
        "channel": "#alerts"
    },
    "pagerduty": {
        "enabled": False,
        "service_key": "..."
    }
}
```

## Configuration Validation

### Environment Validation

```python
# config/validator.py
import os
from typing import Dict, List, Optional

class ConfigValidator:
    """Validates configuration settings"""

    @staticmethod
    def validate_required_vars(required_vars: List[str]) -> Dict[str, str]:
        """Validate required environment variables"""
        missing = []
        for var in required_vars:
            if not os.getenv(var):
                missing.append(var)

        if missing:
            raise ValueError(f"Missing required environment variables: {missing}")

        return {var: os.getenv(var) for var in required_vars}

    @staticmethod
    def validate_database_url(url: str) -> bool:
        """Validate database URL format"""
        if not url:
            return False

        if url.startswith("sqlite:///"):
            return True
        elif url.startswith("postgresql://"):
            return True
        else:
            return False
```

### Usage Example

```python
# Example configuration validation
from config.validator import ConfigValidator

# Validate required variables
required_vars = [
    "GOOGLE_CLOUD_PROJECT",
    "OPENROUTER_API_KEY",
    "TWITTER_USERNAME",
    "TWITTER_PASSWORD"
]

try:
    config = ConfigValidator.validate_required_vars(required_vars)
    print("✅ Configuration validation passed")
except ValueError as e:
    print(f"❌ Configuration validation failed: {e}")
    exit(1)
```

## Configuration Best Practices

### 1. Environment-Specific Configs

```bash
# Development
cp .env.example .env.development

# Staging
cp .env.example .env.staging

# Production
cp .env.example .env.production
```

### 2. Secret Management

```bash
# Use Google Secret Manager for production
gcloud secrets create openrouter-api-key --data-file=-
gcloud secrets create twitter-credentials --data-file=-

# Reference in deployment
gcloud run services update degen-digest \
  --update-secrets=OPENROUTER_API_KEY=openrouter-api-key:latest \
  --update-secrets=TWITTER_PASSWORD=twitter-credentials:latest
```

### 3. Configuration Validation

```python
# Always validate configuration on startup
def validate_configuration():
    """Validate all configuration settings"""
    validators = [
        validate_database_config,
        validate_api_config,
        validate_cloud_config,
        validate_security_config
    ]

    for validator in validators:
        validator()
```

### 4. Configuration Documentation

- Document all configuration options
- Provide examples for each environment
- Include validation rules
- Maintain configuration templates
- Version control configuration schemas

---

_For more information, see the [Deployment Guide](DEPLOYMENT.md) and [Security Guide](SECURITY.md)._
