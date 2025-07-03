# Deployment Guide

This document provides comprehensive deployment information for the Degen Digest platform.

## Table of Contents

- [Overview](#overview)
- [Environment Setup](#environment-setup)
- [Local Development](#local-development)
- [Staging Deployment](#staging-deployment)
- [Production Deployment](#production-deployment)
- [Google Cloud Deployment](#google-cloud-deployment)
- [Docker Deployment](#docker-deployment)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Rollback Procedures](#rollback-procedures)
- [Troubleshooting](#troubleshooting)

## Overview

The Degen Digest platform supports multiple deployment environments and methods to accommodate different use cases and requirements.

### Deployment Environments

- **Local Development** - For development and testing
- **Staging** - For pre-production testing
- **Production** - Live environment for end users

### Deployment Methods

- **Local** - Direct Python execution
- **Docker** - Containerized deployment
- **Google Cloud Run** - Serverless cloud deployment
- **Kubernetes** - Container orchestration (future)

## Environment Setup

### Prerequisites

```bash
# System requirements
- Python 3.11+
- Docker (for containerized deployment)
- Google Cloud SDK (for cloud deployment)
- Git

# Python dependencies
- pip
- virtualenv or conda
```

### Environment Variables

```bash
# Core configuration
ENVIRONMENT=production                    # Environment (development, staging, production)
LOG_LEVEL=INFO                           # Logging level
LOG_FORMAT=json                          # Log format (json, console)
DATABASE_URL=sqlite:///output/degen_digest.db

# API keys
OPENROUTER_API_KEY=your_openrouter_key
TWITTER_USERNAME=your_twitter_username
TWITTER_PASSWORD=your_twitter_password

# Google Cloud configuration
GOOGLE_CLOUD_PROJECT=your_project_id
GCS_BUCKET_NAME=degen-digest-data
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# Service configuration
CRAWLER_SERVICE_URL=https://crawler-service-url
DASHBOARD_SERVICE_URL=https://dashboard-service-url
API_SERVICE_URL=https://api-service-url

# Logging configuration
ENABLE_CLOUD_LOGGING=true
ENABLE_AUDIT_LOGGING=true
ENABLE_PERFORMANCE_LOGGING=true
ENABLE_SECURITY_LOGGING=true
ENABLE_BUSINESS_LOGGING=true
ENABLE_DATA_QUALITY_LOGGING=true
ENABLE_API_LOGGING=true
ENABLE_DATABASE_LOGGING=true
ENABLE_CRAWLER_LOGGING=true
ENABLE_DASHBOARD_LOGGING=true
```

### Configuration Files

```yaml
# config/app_config.yaml
environment: production
logging:
  level: INFO
  format: json
  file_path: logs/degen_digest.log
  max_size_mb: 100
  backup_count: 5

database:
  url: sqlite:///output/degen_digest.db
  pool_size: 10
  max_overflow: 20

crawler:
  sources:
    - twitter
    - reddit
    - telegram
  interval_minutes: 30
  max_tweets_per_session: 1000

api:
  host: 0.0.0.0
  port: 8080
  workers: 4
  timeout: 30

dashboard:
  host: 0.0.0.0
  port: 8501
  theme: dark

security:
  enable_rate_limiting: true
  max_requests_per_minute: 100
  enable_cors: true
  allowed_origins:
    - https://farmchecker.xyz
    - https://www.farmchecker.xyz
```

## Local Development

### Setup Local Environment

```bash
# Clone repository
git clone https://github.com/your-org/degen-digest.git
cd degen-digest

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-crawler.txt
pip install -r requirements-streamlit.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python scripts/setup_database.py

# Run tests
python -m pytest tests/ -v
```

### Start Local Services

```bash
# Start crawler service
python crawler_server.py

# Start dashboard (in new terminal)
python dashboard/app.py

# Start API service (in new terminal)
python api_server.py
```

### Development Workflow

```bash
# Development workflow
1. Make code changes
2. Run tests: python -m pytest tests/ -v
3. Run linting: ruff check .
4. Run formatting: ruff format .
5. Test locally: python main.py
6. Commit changes: git commit -m "feat: add new feature"
7. Push to repository: git push origin feature-branch
```

## Staging Deployment

### Staging Environment Setup

```bash
# Create staging environment
mkdir staging
cd staging

# Clone repository
git clone https://github.com/your-org/degen-digest.git
cd degen-digest

# Checkout staging branch
git checkout staging

# Setup staging environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup staging configuration
cp .env.example .env.staging
# Edit .env.staging with staging configuration

# Initialize staging database
DATABASE_URL=sqlite:///staging/degen_digest.db python scripts/setup_database.py
```

### Staging Deployment Script

```bash
#!/bin/bash
# scripts/deploy_staging.sh

echo "Deploying to staging environment..."

# Set environment
export ENVIRONMENT=staging
export DATABASE_URL=sqlite:///staging/degen_digest.db
export LOG_LEVEL=DEBUG

# Pull latest changes
git pull origin staging

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

# Run linting
ruff check .

# Start services
echo "Starting staging services..."

# Start crawler service
nohup python crawler_server.py > staging_crawler.log 2>&1 &

# Start dashboard
nohup python dashboard/app.py > staging_dashboard.log 2>&1 &

# Start API service
nohup python api_server.py > staging_api.log 2>&1 &

echo "Staging deployment completed!"
echo "Crawler: http://localhost:8080"
echo "Dashboard: http://localhost:8501"
echo "API: http://localhost:8081"
```

### Staging Testing

```bash
# Test staging deployment
curl http://localhost:8080/health
curl http://localhost:8501
curl http://localhost:8081/api/digest

# Run integration tests against staging
ENVIRONMENT=staging python -m pytest tests/integration/ -v

# Load testing
locust -f tests/performance/locustfile.py --host=http://localhost:8081
```

## Production Deployment

### Production Environment Setup

```bash
# Production server setup
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
sudo apt-get install -y nginx supervisor

# Create production user
sudo useradd -m -s /bin/bash degen
sudo usermod -aG sudo degen

# Setup production directory
sudo mkdir -p /opt/degen-digest
sudo chown degen:degen /opt/degen-digest
```

### Production Deployment Script

```bash
#!/bin/bash
# scripts/deploy_production.sh

echo "Deploying to production environment..."

# Set environment
export ENVIRONMENT=production
export DATABASE_URL=sqlite:///production/degen_digest.db
export LOG_LEVEL=INFO

# Create backup
echo "Creating backup..."
cp -r /opt/degen-digest /opt/degen-digest.backup.$(date +%Y%m%d_%H%M%S)

# Pull latest changes
cd /opt/degen-digest
git pull origin main

# Install dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run database migrations
python scripts/migrate_database.py

# Restart services
echo "Restarting production services..."
sudo supervisorctl restart degen-crawler
sudo supervisorctl restart degen-dashboard
sudo supervisorctl restart degen-api

# Health check
echo "Performing health checks..."
sleep 10
curl -f http://localhost:8080/health || exit 1
curl -f http://localhost:8501 || exit 1
curl -f http://localhost:8081/api/digest || exit 1

echo "Production deployment completed successfully!"
```

### Production Configuration

```ini
# /etc/supervisor/conf.d/degen-digest.conf
[program:degen-crawler]
command=/opt/degen-digest/venv/bin/python /opt/degen-digest/crawler_server.py
directory=/opt/degen-digest
user=degen
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/degen-crawler.log
environment=ENVIRONMENT="production",LOG_LEVEL="INFO"

[program:degen-dashboard]
command=/opt/degen-digest/venv/bin/python /opt/degen-digest/dashboard/app.py
directory=/opt/degen-digest
user=degen
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/degen-dashboard.log
environment=ENVIRONMENT="production",LOG_LEVEL="INFO"

[program:degen-api]
command=/opt/degen-digest/venv/bin/python /opt/degen-digest/api_server.py
directory=/opt/degen-digest
user=degen
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/degen-api.log
environment=ENVIRONMENT="production",LOG_LEVEL="INFO"
```

```nginx
# /etc/nginx/sites-available/degen-digest
server {
    listen 80;
    server_name farmchecker.xyz www.farmchecker.xyz;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name farmchecker.xyz www.farmchecker.xyz;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/farmchecker.xyz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/farmchecker.xyz/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Dashboard
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # API
    location /api/ {
        proxy_pass http://localhost:8081;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Crawler
    location /crawler/ {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Google Cloud Deployment

### Google Cloud Setup

```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Initialize Google Cloud
gcloud init

# Set project
gcloud config set project your-project-id

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable monitoring.googleapis.com
```

### Cloud Run Deployment

```bash
#!/bin/bash
# scripts/deploy_cloud_run.sh

echo "Deploying to Google Cloud Run..."

# Set variables
PROJECT_ID=$(gcloud config get-value project)
REGION=us-central1
CRAWLER_SERVICE=degen-digest-crawler
DASHBOARD_SERVICE=degen-digest-dashboard
API_SERVICE=degen-digest-api

# Build and deploy crawler service
echo "Deploying crawler service..."
gcloud run deploy $CRAWLER_SERVICE \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars ENVIRONMENT=production,LOG_LEVEL=INFO \
    --memory 2Gi \
    --cpu 2 \
    --timeout 3600 \
    --concurrency 80

# Build and deploy dashboard service
echo "Deploying dashboard service..."
gcloud run deploy $DASHBOARD_SERVICE \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars ENVIRONMENT=production,LOG_LEVEL=INFO \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --concurrency 100

# Build and deploy API service
echo "Deploying API service..."
gcloud run deploy $API_SERVICE \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars ENVIRONMENT=production,LOG_LEVEL=INFO \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --concurrency 100

# Get service URLs
CRAWLER_URL=$(gcloud run services describe $CRAWLER_SERVICE --region=$REGION --format='value(status.url)')
DASHBOARD_URL=$(gcloud run services describe $DASHBOARD_SERVICE --region=$REGION --format='value(status.url)')
API_URL=$(gcloud run services describe $API_SERVICE --region=$REGION --format='value(status.url)')

echo "Deployment completed!"
echo "Crawler URL: $CRAWLER_URL"
echo "Dashboard URL: $DASHBOARD_URL"
echo "API URL: $API_URL"
```

### Cloud Storage Setup

```bash
# Create storage bucket
gsutil mb gs://degen-digest-data

# Set bucket permissions
gsutil iam ch allUsers:objectViewer gs://degen-digest-data

# Upload initial data
gsutil cp output/*.json gs://degen-digest-data/

# Setup lifecycle policy
cat > lifecycle.json << EOF
{
  "rule": [
    {
      "action": {"type": "Delete"},
      "condition": {
        "age": 365,
        "isLive": true
      }
    }
  ]
}
EOF

gsutil lifecycle set lifecycle.json gs://degen-digest-data
```

### Domain Mapping

```bash
# Map custom domain
gcloud run domain-mappings create \
    --service degen-digest-dashboard \
    --domain farmchecker.xyz \
    --region us-central1

# Verify domain mapping
gcloud run domain-mappings describe \
    --domain farmchecker.xyz \
    --region us-central1
```

## Docker Deployment

### Docker Configuration

```dockerfile
# Dockerfile.crawler
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt requirements-crawler.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt -r requirements-crawler.txt

# Copy application code
COPY . .

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Start crawler service
CMD ["python", "crawler_server.py"]
```

```dockerfile
# Dockerfile.dashboard
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt requirements-streamlit.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt -r requirements-streamlit.txt

# Copy application code
COPY . .

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501 || exit 1

# Expose port
EXPOSE 8501

# Start dashboard
CMD ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: "3.8"

services:
  crawler:
    build:
      context: .
      dockerfile: Dockerfile.crawler
    ports:
      - "8080:8080"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
      - DATABASE_URL=sqlite:///data/degen_digest.db
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  dashboard:
    build:
      context: .
      dockerfile: Dockerfile.dashboard
    ports:
      - "8501:8501"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
      - DATABASE_URL=sqlite:///data/degen_digest.db
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    depends_on:
      - crawler
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501"]
      interval: 30s
      timeout: 10s
      retries: 3

  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8081:8081"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
      - DATABASE_URL=sqlite:///data/degen_digest.db
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    depends_on:
      - crawler
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8081/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  data:
  logs:
```

### Docker Deployment Commands

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# Scale services
docker-compose up -d --scale crawler=3

# Backup data
docker-compose exec crawler tar -czf /app/backup.tar.gz /app/data
docker cp $(docker-compose ps -q crawler):/app/backup.tar.gz ./backup.tar.gz
```

## Monitoring & Maintenance

### Health Monitoring

```python
# scripts/health_monitor.py
import requests
import time
import smtplib
from email.mime.text import MIMEText
from utils.enterprise_logging import get_logger

logger = get_logger('health_monitor')

class HealthMonitor:
    """Health monitoring system"""

    def __init__(self):
        self.services = {
            'crawler': 'http://localhost:8080/health',
            'dashboard': 'http://localhost:8501',
            'api': 'http://localhost:8081/health'
        }
        self.alert_threshold = 3
        self.failure_counts = {service: 0 for service in self.services}

    def check_health(self):
        """Check health of all services"""
        for service, url in self.services.items():
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    logger.info(f"Service {service} is healthy")
                    self.failure_counts[service] = 0
                else:
                    self.handle_failure(service, f"HTTP {response.status_code}")
            except Exception as e:
                self.handle_failure(service, str(e))

    def handle_failure(self, service, error):
        """Handle service failure"""
        self.failure_counts[service] += 1
        logger.warning(f"Service {service} failure: {error}")

        if self.failure_counts[service] >= self.alert_threshold:
            self.send_alert(service, error)

    def send_alert(self, service, error):
        """Send alert for service failure"""
        message = f"Service {service} is down: {error}"
        logger.error(message)

        # Send email alert
        self.send_email_alert(message)

    def send_email_alert(self, message):
        """Send email alert"""
        # Email configuration
        sender = 'alerts@degen-digest.com'
        recipients = ['admin@degen-digest.com']

        msg = MIMEText(message)
        msg['Subject'] = 'Degen Digest Service Alert'
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)

        # Send email (configure SMTP settings)
        # smtp_server.send_message(msg)

if __name__ == "__main__":
    monitor = HealthMonitor()

    while True:
        monitor.check_health()
        time.sleep(60)  # Check every minute
```

### Log Monitoring

```bash
#!/bin/bash
# scripts/monitor_logs.sh

echo "Monitoring application logs..."

# Monitor crawler logs
tail -f logs/crawler.log | grep -E "(ERROR|CRITICAL)" | while read line; do
    echo "[$(date)] Crawler Error: $line"
    # Send alert
done

# Monitor dashboard logs
tail -f logs/dashboard.log | grep -E "(ERROR|CRITICAL)" | while read line; do
    echo "[$(date)] Dashboard Error: $line"
    # Send alert
done

# Monitor API logs
tail -f logs/api.log | grep -E "(ERROR|CRITICAL)" | while read line; do
    echo "[$(date)] API Error: $line"
    # Send alert
done
```

### Performance Monitoring

```python
# scripts/performance_monitor.py
import psutil
import time
from utils.enterprise_logging import get_logger

logger = get_logger('performance_monitor')

class PerformanceMonitor:
    """Performance monitoring system"""

    def __init__(self):
        self.thresholds = {
            'cpu_percent': 80,
            'memory_percent': 80,
            'disk_percent': 90
        }

    def check_performance(self):
        """Check system performance"""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > self.thresholds['cpu_percent']:
            logger.warning(f"High CPU usage: {cpu_percent}%")

        # Memory usage
        memory = psutil.virtual_memory()
        if memory.percent > self.thresholds['memory_percent']:
            logger.warning(f"High memory usage: {memory.percent}%")

        # Disk usage
        disk = psutil.disk_usage('/')
        if disk.percent > self.thresholds['disk_percent']:
            logger.warning(f"High disk usage: {disk.percent}%")

        # Log performance metrics
        logger.info(f"Performance metrics - CPU: {cpu_percent}%, Memory: {memory.percent}%, Disk: {disk.percent}%")

if __name__ == "__main__":
    monitor = PerformanceMonitor()

    while True:
        monitor.check_performance()
        time.sleep(300)  # Check every 5 minutes
```

## Rollback Procedures

### Rollback Script

```bash
#!/bin/bash
# scripts/rollback.sh

echo "Rolling back deployment..."

# Get current version
CURRENT_VERSION=$(git rev-parse HEAD)
echo "Current version: $CURRENT_VERSION"

# Get previous version
PREVIOUS_VERSION=$(git rev-parse HEAD~1)
echo "Rolling back to: $PREVIOUS_VERSION"

# Create backup
echo "Creating backup..."
BACKUP_DIR="/opt/degen-digest.backup.$(date +%Y%m%d_%H%M%S)"
cp -r /opt/degen-digest $BACKUP_DIR

# Checkout previous version
cd /opt/degen-digest
git checkout $PREVIOUS_VERSION

# Install dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart services
echo "Restarting services..."
sudo supervisorctl restart degen-crawler
sudo supervisorctl restart degen-dashboard
sudo supervisorctl restart degen-api

# Health check
echo "Performing health checks..."
sleep 10
curl -f http://localhost:8080/health || {
    echo "Health check failed, restoring from backup..."
    rm -rf /opt/degen-digest
    cp -r $BACKUP_DIR /opt/degen-digest
    sudo supervisorctl restart degen-crawler degen-dashboard degen-api
    exit 1
}

echo "Rollback completed successfully!"
```

### Database Rollback

```python
# scripts/rollback_database.py
import sqlite3
import shutil
import os
from datetime import datetime
from utils.enterprise_logging import get_logger

logger = get_logger('database_rollback')

def rollback_database():
    """Rollback database to previous state"""

    # Create backup
    backup_path = f"output/degen_digest.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy2("output/degen_digest.db", backup_path)
    logger.info(f"Database backed up to {backup_path}")

    # Restore from previous backup
    previous_backup = "output/degen_digest.backup.latest.db"
    if os.path.exists(previous_backup):
        shutil.copy2(previous_backup, "output/degen_digest.db")
        logger.info("Database rolled back to previous state")
    else:
        logger.error("No previous backup found")
        return False

    return True

if __name__ == "__main__":
    rollback_database()
```

## Troubleshooting

### Common Issues

#### 1. Service Won't Start

```bash
# Check logs
tail -f logs/degen_digest.log

# Check port availability
netstat -tulpn | grep :8080
netstat -tulpn | grep :8501
netstat -tulpn | grep :8081

# Check permissions
ls -la /opt/degen-digest/
ls -la logs/

# Check dependencies
python -c "import flask, streamlit, playwright"
```

#### 2. Database Issues

```bash
# Check database file
ls -la output/degen_digest.db

# Check database integrity
sqlite3 output/degen_digest.db "PRAGMA integrity_check;"

# Repair database
sqlite3 output/degen_digest.db "VACUUM;"
sqlite3 output/degen_digest.db "REINDEX;"
```

#### 3. Network Issues

```bash
# Check connectivity
curl -v http://localhost:8080/health
curl -v http://localhost:8501
curl -v http://localhost:8081/health

# Check firewall
sudo ufw status
sudo iptables -L

# Check DNS
nslookup farmchecker.xyz
```

#### 4. Performance Issues

```bash
# Check system resources
htop
df -h
free -h

# Check process status
ps aux | grep python
ps aux | grep streamlit

# Check memory usage
cat /proc/meminfo
```

### Debug Mode

```bash
# Enable debug mode
export LOG_LEVEL=DEBUG
export LOG_FORMAT=console

# Run with debug output
python main.py --debug

# Enable verbose logging
python -u main.py 2>&1 | tee debug.log
```

### Emergency Procedures

```bash
# Emergency stop all services
sudo supervisorctl stop all

# Emergency restart
sudo supervisorctl restart all

# Emergency rollback
./scripts/rollback.sh

# Emergency backup
tar -czf emergency_backup_$(date +%Y%m%d_%H%M%S).tar.gz output/ logs/ config/
```

This comprehensive deployment guide ensures reliable deployment across all environments with proper monitoring, maintenance, and troubleshooting procedures.
