# FarmChecker.xyz Deployment & Operations Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Setup](#database-setup)
4. [Service Deployment](#service-deployment)
5. [Domain Configuration](#domain-configuration)
6. [Monitoring Setup](#monitoring-setup)
7. [Backup & Recovery](#backup--recovery)
8. [Scaling & Performance](#scaling--performance)
9. [Security Hardening](#security-hardening)
10. [Maintenance Procedures](#maintenance-procedures)

## Prerequisites

### Required Accounts & Tools

1. **Google Cloud Platform Account**
   - Active GCP project with billing enabled
   - Owner or Editor permissions

2. **Command Line Tools**
   ```bash
   # Install Google Cloud CLI
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   gcloud init
   
   # Install Docker
   curl -fsSL https://get.docker.com | sh
   sudo usermod -aG docker $USER
   
   # Install kubectl (optional, for advanced deployments)
   gcloud components install kubectl
   ```

3. **Domain & DNS**
   - Registered domain (e.g., farmchecker.xyz)
   - Access to DNS management

### Required APIs

Enable the following Google Cloud APIs:

```bash
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

## Environment Setup

### 1. Project Configuration

```bash
# Set your project ID
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Set default region and zone
gcloud config set compute/region us-central1
gcloud config set compute/zone us-central1-a
```

### 2. Service Account Setup

```bash
# Create service account for deployments
gcloud iam service-accounts create farmchecker-deployer \
    --display-name="FarmChecker Deployer"

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:farmchecker-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:farmchecker-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudbuild.builds.builder"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:farmchecker-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### 3. Environment Variables

Create a `.env` file for local development:

```bash
# Database
DATABASE_URL=postgresql://username:password@host:port/database
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# API Keys (store in Secret Manager for production)
COINGECKO_API_KEY=your_coingecko_api_key
DEXSCREENER_API_KEY=your_dexscreener_api_key

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
ENABLE_METRICS=true

# Security
CORS_ORIGINS=https://farmchecker.xyz,https://www.farmchecker.xyz
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

## Database Setup

### 1. Cloud SQL Instance

```bash
# Create PostgreSQL instance
gcloud sql instances create farmchecker-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password="$(openssl rand -base64 32)" \
    --storage-type=SSD \
    --storage-size=10GB \
    --backup-start-time=02:00 \
    --enable-point-in-time-recovery \
    --maintenance-window-day=SUN \
    --maintenance-window-hour=03

# Create database
gcloud sql databases create farmchecker --instance=farmchecker-db

# Create user for application
gcloud sql users create farmchecker-app \
    --instance=farmchecker-db \
    --password="$(openssl rand -base64 32)"
```

### 2. Database Schema

```sql
-- Connect to database and run schema
\c farmchecker

-- Create crypto_tokens table
CREATE TABLE crypto_tokens (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(20,8),
    price_change_24h VARCHAR(20),
    price_change_percentage_24h DECIMAL(10,4),
    market_cap VARCHAR(50),
    volume_24h VARCHAR(50),
    rank INTEGER,
    image TEXT,
    source VARCHAR(50),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_crypto_tokens_symbol ON crypto_tokens(symbol);
CREATE INDEX idx_crypto_tokens_source ON crypto_tokens(source);
CREATE INDEX idx_crypto_tokens_updated_at ON crypto_tokens(updated_at);
CREATE INDEX idx_crypto_tokens_price_change ON crypto_tokens(price_change_percentage_24h DESC);

-- Create content_items table (legacy)
CREATE TABLE content_items (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    author VARCHAR(100),
    source VARCHAR(50),
    published_at TIMESTAMP,
    engagement_score INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create system_logs table for enterprise logging
CREATE TABLE system_logs (
    id SERIAL PRIMARY KEY,
    log_id UUID NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    level VARCHAR(20) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    service VARCHAR(50) NOT NULL,
    message TEXT,
    context JSONB,
    data JSONB,
    performance JSONB,
    error JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for logs
CREATE INDEX idx_system_logs_timestamp ON system_logs(timestamp);
CREATE INDEX idx_system_logs_level ON system_logs(level);
CREATE INDEX idx_system_logs_service ON system_logs(service);
CREATE INDEX idx_system_logs_event_type ON system_logs(event_type);
```

### 3. Connection Security

```bash
# Get connection info
gcloud sql instances describe farmchecker-db

# Configure authorized networks (if needed)
gcloud sql instances patch farmchecker-db \
    --authorized-networks=YOUR_IP_ADDRESS/32
```

## Service Deployment

### 1. Web Application

```bash
# Deploy web application
cd farmchecker_new

gcloud run deploy farmchecker-website \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 5000 \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10 \
    --min-instances 1 \
    --set-env-vars ENVIRONMENT=production \
    --set-env-vars LOG_LEVEL=INFO \
    --set-env-vars DATABASE_URL="postgresql://farmchecker-app:password@host:port/farmchecker"
```

### 2. Data Crawlers

```bash
# Deploy CoinGecko crawler
gcloud run deploy enhanced-coingecko-crawler \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 256Mi \
    --cpu 0.5 \
    --max-instances 5 \
    --min-instances 0 \
    --set-env-vars ENVIRONMENT=production \
    --set-env-vars CRAWLER_INTERVAL=420 \
    --set-env-vars DATABASE_URL="postgresql://farmchecker-app:password@host:port/farmchecker"

# Deploy DexScreener crawler
gcloud run deploy dexscreener-crawler \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 256Mi \
    --cpu 0.5 \
    --max-instances 5 \
    --min-instances 0 \
    --set-env-vars ENVIRONMENT=production \
    --set-env-vars CRAWLER_INTERVAL=420 \
    --set-env-vars DATABASE_URL="postgresql://farmchecker-app:password@host:port/farmchecker"

# Deploy DexPaprika crawler
gcloud run deploy dexpaprika-crawler \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 256Mi \
    --cpu 0.5 \
    --max-instances 5 \
    --min-instances 0 \
    --set-env-vars ENVIRONMENT=production \
    --set-env-vars CRAWLER_INTERVAL=420 \
    --set-env-vars DATABASE_URL="postgresql://farmchecker-app:password@host:port/farmchecker"
```

### 3. Cloud Scheduler Setup

```bash
# Create scheduler jobs for crawlers
gcloud scheduler jobs create http coingecko-crawler-job \
    --schedule="*/7 * * * *" \
    --uri="https://enhanced-coingecko-crawler-xxx.run.app/trigger" \
    --http-method=POST \
    --location=us-central1

gcloud scheduler jobs create http dexscreener-crawler-job \
    --schedule="*/7 * * * *" \
    --uri="https://dexscreener-crawler-xxx.run.app/trigger" \
    --http-method=POST \
    --location=us-central1

gcloud scheduler jobs create http dexpaprika-crawler-job \
    --schedule="*/7 * * * *" \
    --uri="https://dexpaprika-crawler-xxx.run.app/trigger" \
    --http-method=POST \
    --location=us-central1
```

## Domain Configuration

### 1. Domain Mapping

```bash
# Map custom domain to web service
gcloud beta run domain-mappings create \
    --service farmchecker-website \
    --domain farmchecker.xyz \
    --region us-central1

# Map www subdomain
gcloud beta run domain-mappings create \
    --service farmchecker-website \
    --domain www.farmchecker.xyz \
    --region us-central1
```

### 2. SSL Certificate

SSL certificates are automatically provisioned by Google Cloud Run.

### 3. DNS Configuration

Configure your DNS provider with the following records:

```
# A record for root domain
farmchecker.xyz.  A   [Cloud Run IP]

# CNAME for www subdomain  
www.farmchecker.xyz.  CNAME  farmchecker.xyz.

# TXT record for domain verification
farmchecker.xyz.  TXT  google-site-verification=...
```

## Monitoring Setup

### 1. Cloud Monitoring

```bash
# Enable monitoring
gcloud services enable monitoring.googleapis.com

# Create monitoring workspace
gcloud monitoring workspaces create \
    --display-name="FarmChecker Monitoring"
```

### 2. Logging Configuration

```bash
# Create log bucket
gsutil mb gs://farmchecker-logs-$PROJECT_ID

# Configure log export
gcloud logging sinks create farmchecker-logs \
    storage.googleapis.com/farmchecker-logs-$PROJECT_ID \
    --log-filter="resource.type=cloud_run_revision"

# Create log-based metrics
gcloud logging metrics create api-errors \
    --description="API Error Rate" \
    --log-filter='resource.type="cloud_run_revision" AND severity>=ERROR'
```

### 3. Alerting Policies

```bash
# Create alerting policy for high error rate
gcloud alpha monitoring policies create \
    --policy-from-file=alerting-policy.yaml
```

Example `alerting-policy.yaml`:
```yaml
displayName: "High Error Rate Alert"
conditions:
  - displayName: "Error rate is high"
    conditionThreshold:
      filter: 'metric.type="logging.googleapis.com/log_entry_count" AND resource.type="cloud_run_revision"'
      comparison: COMPARISON_GREATER_THAN
      thresholdValue: 0.05
      duration: 300s
```

## Backup & Recovery

### 1. Database Backups

```bash
# Enable automated backups (already configured)
# Manual backup
gcloud sql backups create --instance=farmchecker-db

# Export data
gcloud sql export sql farmchecker-db \
    gs://farmchecker-backups/backup-$(date +%Y%m%d).sql \
    --database=farmchecker
```

### 2. Disaster Recovery Plan

1. **Database Recovery**:
   ```bash
   # Restore from backup
   gcloud sql import sql farmchecker-db \
       gs://farmchecker-backups/backup-20250706.sql \
       --database=farmchecker
   ```

2. **Service Recovery**:
   ```bash
   # Redeploy services
   ./deploy_all_services.sh
   ```

### 3. Backup Verification

```bash
# Test backup restoration
gcloud sql instances create farmchecker-test \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1

gcloud sql import sql farmchecker-test \
    gs://farmchecker-backups/backup-20250706.sql \
    --database=farmchecker
```

## Scaling & Performance

### 1. Auto-scaling Configuration

```bash
# Update web service with better scaling
gcloud run services update farmchecker-website \
    --region us-central1 \
    --max-instances 20 \
    --min-instances 2 \
    --cpu-throttling \
    --concurrency 80
```

### 2. Performance Optimization

1. **Database Optimization**:
   ```sql
   -- Analyze table statistics
   ANALYZE crypto_tokens;
   
   -- Update statistics
   VACUUM ANALYZE crypto_tokens;
   ```

2. **Caching Strategy**:
   - Implement Redis for session storage
   - Use Cloud CDN for static assets
   - Cache API responses

3. **Connection Pooling**:
   ```python
   # Configure database connection pool
   DATABASE_POOL_SIZE = 20
   DATABASE_MAX_OVERFLOW = 30
   ```

### 3. Load Testing

```bash
# Install artillery for load testing
npm install -g artillery

# Run load test
artillery run load-test.yml
```

Example `load-test.yml`:
```yaml
config:
  target: 'https://farmchecker.xyz'
  phases:
    - duration: 60
      arrivalRate: 10
    - duration: 120
      arrivalRate: 50
scenarios:
  - name: "API Load Test"
    requests:
      - get:
          url: "/api/stats"
      - get:
          url: "/api/crypto/top-gainers"
```

## Security Hardening

### 1. Secret Management

```bash
# Store sensitive data in Secret Manager
echo -n "your-database-password" | \
gcloud secrets create database-password --data-file=-

# Grant access to service account
gcloud secrets add-iam-policy-binding database-password \
    --member="serviceAccount:farmchecker-app@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### 2. Network Security

```bash
# Configure VPC connector for private services
gcloud compute networks vpc-access connectors create farmchecker-connector \
    --network=default \
    --region=us-central1 \
    --range=10.8.0.0/28
```

### 3. IAM Security

```bash
# Create custom roles with minimal permissions
gcloud iam roles create farmchecker.crawler \
    --project=$PROJECT_ID \
    --title="FarmChecker Crawler" \
    --description="Minimal permissions for crawler services" \
    --permissions="cloudsql.client.connect,cloudsql.client.getSslCert"
```

## Maintenance Procedures

### 1. Daily Maintenance

```bash
#!/bin/bash
# daily-maintenance.sh

# Check service health
gcloud run services list --region us-central1

# Check database connections
gcloud sql instances describe farmchecker-db

# Review error logs
gcloud logging read 'severity>=ERROR' --limit=50

# Check disk usage
gcloud sql instances describe farmchecker-db --format="value(settings.dataDiskSizeGb)"
```

### 2. Weekly Maintenance

```bash
#!/bin/bash
# weekly-maintenance.sh

# Update dependencies
pip install --upgrade -r requirements.txt

# Database maintenance
gcloud sql instances patch farmchecker-db \
    --maintenance-window-day=SUN \
    --maintenance-window-hour=03

# Review performance metrics
gcloud monitoring metrics list --filter="metric.type:run.googleapis.com"
```

### 3. Monthly Maintenance

```bash
#!/bin/bash
# monthly-maintenance.sh

# Security audit
gcloud projects get-iam-policy $PROJECT_ID

# Cost optimization review
gcloud billing accounts list

# Performance review
gcloud monitoring metrics list --filter="metric.type:run.googleapis.com/request_count"
```

### 4. Emergency Procedures

1. **Service Outage**:
   ```bash
   # Check service status
   gcloud run services describe SERVICE_NAME --region us-central1
   
   # Restart service
   gcloud run services replace SERVICE_NAME --region us-central1
   ```

2. **Database Issues**:
   ```bash
   # Check database status
   gcloud sql instances describe farmchecker-db
   
   # Restart database
   gcloud sql instances restart farmchecker-db
   ```

3. **High Load**:
   ```bash
   # Scale up services
   gcloud run services update SERVICE_NAME \
       --max-instances 50 \
       --region us-central1
   ```

## Deployment Scripts

### 1. Automated Deployment

```bash
#!/bin/bash
# deploy.sh

set -e

echo "Starting deployment..."

# Deploy web application
gcloud run deploy farmchecker-website \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 5000

# Deploy crawlers
gcloud run deploy enhanced-coingecko-crawler \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated

gcloud run deploy dexscreener-crawler \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated

gcloud run deploy dexpaprika-crawler \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated

echo "Deployment completed successfully!"
```

### 2. Rollback Script

```bash
#!/bin/bash
# rollback.sh

SERVICE_NAME=$1
REVISION=$2

if [ -z "$SERVICE_NAME" ] || [ -z "$REVISION" ]; then
    echo "Usage: ./rollback.sh SERVICE_NAME REVISION"
    exit 1
fi

echo "Rolling back $SERVICE_NAME to revision $REVISION..."

gcloud run services update-traffic $SERVICE_NAME \
    --to-revisions=$REVISION=100 \
    --region us-central1

echo "Rollback completed!"
```

---

**Last Updated**: July 6, 2025  
**Version**: 1.0.0  
**Maintainer**: FarmChecker.xyz Operations Team 