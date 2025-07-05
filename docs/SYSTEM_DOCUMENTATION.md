# DegenDigest System Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Components](#components)
4. [Data Flow](#data-flow)
5. [Configuration](#configuration)
6. [Deployment](#deployment)
7. [Monitoring & Logging](#monitoring--logging)
8. [Security](#security)
9. [Troubleshooting](#troubleshooting)
10. [API Reference](#api-reference)
11. [Development Guide](#development-guide)

## System Overview

DegenDigest is a comprehensive cryptocurrency data aggregation and analysis platform that collects, processes, and analyzes data from multiple sources to generate daily digests of market trends, viral content, and trading opportunities.

### Key Features

- **Multi-Source Data Collection**: Twitter, Reddit, DexScreener, DexPaprika, News APIs
- **Real-time Processing**: Continuous data collection and processing
- **Intelligent Analysis**: AI-powered content analysis and virality prediction
- **Automated Digest Generation**: Daily automated digest creation
- **Cloud-Native Architecture**: Scalable cloud deployment
- **Comprehensive Monitoring**: Enterprise-grade logging and monitoring

### System Goals

- Provide real-time cryptocurrency market intelligence
- Identify viral content and trending topics
- Generate actionable trading insights
- Maintain high data quality and reliability
- Ensure system scalability and performance

## Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │    │   Data Storage  │    │   Analytics     │
│                 │    │                 │    │                 │
│ • Twitter       │───▶│ • GCS Buckets   │───▶│ • AI Analysis   │
│ • Reddit        │    │ • Cloud SQL     │    │ • Virality      │
│ • DexScreener   │    │ • BigQuery      │    │ • Classification│
│ • DexPaprika    │    │ • Firestore     │    │ • Summarization │
│ • News APIs     │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Crawlers      │    │   Processors    │    │   Dashboards    │
│                 │    │                 │    │                 │
│ • Cloud Run     │    │ • Data Pipeline │    │ • Streamlit     │
│ • Cloud Tasks   │    │ • Enrichment    │    │ • Analytics     │
│ • Systemd       │    │ • Deduplication │    │ • Monitoring    │
│ • VMs           │    │ • Quality Check │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Architecture

#### Data Collection Layer

- **Twitter Crawler**: Playwright-based web scraping with login support
- **Reddit Crawler**: RSS feed and API-based collection
- **Crypto Crawlers**: DexScreener and DexPaprika API integration
- **News Crawler**: NewsAPI integration for headlines

#### Processing Layer

- **Data Aggregator**: Centralized data collection and processing
- **Content Processor**: Text analysis, classification, and enrichment
- **Virality Predictor**: ML-based content virality prediction
- **Quality Monitor**: Data quality validation and monitoring

#### Storage Layer

- **Google Cloud Storage**: Raw data and processed files
- **Cloud SQL**: Structured data and metadata
- **BigQuery**: Analytics and reporting data
- **Firestore**: Real-time data and configuration

#### Presentation Layer

- **Streamlit Dashboard**: Interactive analytics and monitoring
- **API Endpoints**: RESTful APIs for data access
- **Cloud Functions**: Serverless processing and triggers

## Components

### 1. Data Crawlers

#### Twitter Crawler (`twitter_crawler_server.py`)

- **Purpose**: Collect tweets from multiple Twitter sources
- **Technology**: Playwright for web automation
- **Features**:
  - Multi-source collection (Following, For You, Explore, Search)
  - Login support for authenticated access
  - Rate limiting and error handling
  - Continuous operation with systemd
- **Configuration**: See `config/app_config.yaml`
- **Deployment**: Cloud Run, VM with systemd

#### Reddit Crawler (`reddit_crawler_server.py`)

- **Purpose**: Collect posts and comments from cryptocurrency subreddits
- **Technology**: RSS feeds and Reddit API
- **Features**:
  - Multiple subreddit monitoring
  - Comment collection and analysis
  - Sentiment analysis integration
- **Configuration**: Subreddit list in `config/app_config.yaml`

#### Crypto Crawlers

- **DexScreener Crawler** (`cloud_tasks_dexscreener.py`)

  - Collects token data, prices, and trading information
  - Monitors multiple blockchain networks
  - Tracks trending tokens and pairs

- **DexPaprika Crawler** (`cloud_tasks_dexpaprika.py`)
  - Collects network data and token information
  - Price tracking and historical data
  - Market cap and volume analysis

#### News Crawler (`news_crawler_server.py`)

- **Purpose**: Collect cryptocurrency news headlines
- **Technology**: NewsAPI integration
- **Features**:
  - Keyword-based filtering
  - Sentiment analysis
  - Source credibility scoring

### 2. Data Processing

#### Data Aggregator (`data_aggregator_server.py`)

- **Purpose**: Centralized data collection and processing
- **Features**:
  - Multi-source data integration
  - Data validation and cleaning
  - Deduplication and merging
  - Quality monitoring

#### Content Processor (`processor/`)

- **Text Classification** (`classifier.py`)

  - Categorizes content by type and sentiment
  - Uses pre-trained models for accuracy

- **Virality Prediction** (`viral_predictor.py`)

  - ML-based content virality scoring
  - Feature extraction and model training

- **Content Summarization** (`summarizer.py`)
  - AI-powered content summarization
  - Key point extraction and condensation

#### Data Quality Monitor (`utils/data_quality_monitor.py`)

- **Purpose**: Monitor and validate data quality
- **Features**:
  - Schema validation
  - Completeness checks
  - Consistency monitoring
  - Anomaly detection

### 3. Storage Systems

#### Google Cloud Storage

- **Buckets**:
  - `degen-digest-data`: Raw and processed data
  - `degen-digest-backups`: System backups
  - `degen-digest-logs`: Log files and monitoring data

#### Cloud SQL

- **Tables**:
  - `tweets`: Twitter data storage
  - `reddit_posts`: Reddit data storage
  - `crypto_data`: Cryptocurrency data
  - `digests`: Generated digest metadata
  - `system_metrics`: Performance and health data

#### BigQuery

- **Datasets**:
  - `analytics`: Processed analytics data
  - `reports`: Generated reports and insights
  - `monitoring`: System monitoring data

### 4. Analytics and Dashboards

#### Streamlit Dashboard (`dashboard/`)

- **Pages**:
  - **Live Feed**: Real-time data visualization
  - **Analytics**: Historical data analysis
  - **Health Monitor**: System health and performance
  - **Data Sources**: Source management and monitoring
  - **Digest Archive**: Historical digest access

#### Analytics Components

- **Buzz Heatmap**: Trending topic visualization
- **Viral Analytics**: Content virality analysis
- **Top Engagement**: High-engagement content tracking
- **Prediction vs Actual**: Model performance analysis

### 5. Cloud Infrastructure

#### Cloud Run Services

- **dexscreener-crawler**: DexScreener data collection
- **dexpaprika-crawler**: DexPaprika data collection
- **twitter-crawler**: Twitter data collection
- **data-aggregator**: Centralized data processing
- **dashboard**: Streamlit dashboard hosting

#### Cloud Functions

- **Digest Generation**: Automated digest creation
- **Data Processing**: Serverless data transformation
- **Monitoring**: Health checks and alerts

#### Cloud Scheduler

- **Crawler Triggers**: Periodic data collection
- **Digest Generation**: Daily digest creation
- **Maintenance Tasks**: System maintenance and cleanup

## Data Flow

### 1. Data Collection Flow

```
Data Sources → Crawlers → Raw Storage → Processing → Enriched Storage → Analytics
```

1. **Source Monitoring**: Crawlers continuously monitor data sources
2. **Data Collection**: Raw data collected and stored in GCS
3. **Initial Processing**: Basic validation and formatting
4. **Enrichment**: AI analysis, classification, and scoring
5. **Storage**: Processed data stored in structured databases
6. **Analytics**: Data analyzed for insights and trends

### 2. Digest Generation Flow

```
Scheduled Trigger → Data Aggregation → Content Analysis → Digest Creation → Distribution
```

1. **Scheduler Trigger**: Cloud Scheduler initiates daily digest generation
2. **Data Aggregation**: Collect and merge data from all sources
3. **Content Analysis**: AI-powered analysis and scoring
4. **Digest Creation**: Generate formatted digest with insights
5. **Distribution**: Store and make digest available via dashboard

### 3. Real-time Processing Flow

```
Live Data → Stream Processing → Real-time Analysis → Dashboard Updates
```

1. **Live Collection**: Real-time data collection from sources
2. **Stream Processing**: Immediate processing and analysis
3. **Real-time Updates**: Dashboard updates with live data
4. **Alerting**: Notifications for significant events

## Configuration

### Environment Variables

```bash
# API Keys
APIFY_API_TOKEN=your_apify_token
TELEGRAM_API_ID=your_telegram_api_id
TELEGRAM_API_HASH=your_telegram_api_hash
OPENROUTER_API_KEY=your_openrouter_key
NEWSAPI_KEY=your_newsapi_key

# Twitter Credentials
TWITTER_USERNAME=your_twitter_username
TWITTER_PASSWORD=your_twitter_password

# Cloud Configuration
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_APPLICATION_CREDENTIALS=path_to_credentials.json

# Database Configuration
DATABASE_URL=your_database_url
BIGQUERY_DATASET=your_dataset_name

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
ENABLE_CLOUD_LOGGING=true
```

### Configuration Files

#### `config/app_config.yaml`

```yaml
# Crawler Configuration
crawlers:
  twitter:
    enabled: true
    sources: ["following", "for_you", "explore", "search"]
    interval_minutes: 30

  reddit:
    enabled: true
    subreddits: ["cryptocurrency", "bitcoin", "ethereum"]
    interval_minutes: 60

  crypto:
    dexscreener:
      enabled: true
      interval_minutes: 120
    dexpaprika:
      enabled: true
      interval_minutes: 120

# Processing Configuration
processing:
  batch_size: 1000
  max_workers: 4
  timeout_seconds: 300

# Storage Configuration
storage:
  gcs_bucket: "degen-digest-data"
  backup_bucket: "degen-digest-backups"
  retention_days: 30
```

#### `config/cloud_config.yaml`

```yaml
# Cloud Run Configuration
cloud_run:
  region: "us-central1"
  memory: "1Gi"
  cpu: "1"
  timeout: "300s"
  max_instances: 10

# Cloud Scheduler Configuration
scheduler:
  digest_generation: "0 6 * * *" # Daily at 6 AM
  data_cleanup: "0 2 * * *" # Daily at 2 AM

# Monitoring Configuration
monitoring:
  enabled: true
  metrics_interval: 60
  alert_threshold: 0.95
```

## Deployment

### Local Development

1. **Environment Setup**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configuration**:

   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Database Setup**:

   ```bash
   python recreate_db.py
   ```

4. **Run Services**:

   ```bash
   # Start dashboard
   streamlit run dashboard/main.py

   # Start crawler
   python twitter_crawler_server.py

   # Start data aggregator
   python data_aggregator_server.py
   ```

### Cloud Deployment

#### 1. Google Cloud Setup

```bash
# Authenticate with Google Cloud
gcloud auth login
gcloud config set project your-project-id

# Enable required APIs
gcloud services enable cloudrun.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable cloudtasks.googleapis.com
```

#### 2. Deploy Services

```bash
# Deploy all services
./deploy_all_services.sh

# Or deploy individual services
./deploy_cloud_tasks.sh
./deploy_twitter_crawler.sh
./deploy_data_aggregator.sh
```

#### 3. VM Deployment

```bash
# Deploy to VM
./deploy_crawler_to_gcloud.sh

# Setup systemd services
sudo cp *.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable continuous-twitter-crawler
sudo systemctl start continuous-twitter-crawler
```

### Deployment Verification

```bash
# Check service status
gcloud run services list --region=us-central1

# Check logs
gcloud logging read 'resource.type=cloud_run_revision' --limit=50

# Test endpoints
curl -X GET https://your-service-url
```

## Monitoring & Logging

### Logging System

The system uses a comprehensive enterprise logging system (`utils/enterprise_logging.py`) with the following features:

#### Log Types

- **Application Logs**: General application events
- **Performance Logs**: Timing and performance metrics
- **Error Logs**: Error tracking and debugging
- **Security Logs**: Security events and access logs
- **Audit Logs**: User actions and system changes
- **Business Logs**: Business events and metrics

#### Log Formats

- **Console**: Human-readable colored output
- **JSON**: Structured logging for analysis
- **File**: Rotated log files with compression
- **Cloud Logging**: Google Cloud Logging integration

#### Usage Example

```python
from utils.enterprise_logging import get_logger

logger = get_logger("my_service")

# Basic logging
logger.info("Service started", service_name="my_service")

# Performance logging
with logger.operation_context("data_processing", request_id="123"):
    # Process data
    logger.log_performance("data_processing", 1500.5)

# API call logging
logger.log_api_call("GET", "/api/data", 200, 250.3)

# Security logging
logger.log_security_event("login_attempt", "medium", user_id="user123")
```

### Monitoring Dashboard

The system includes a comprehensive monitoring dashboard with:

#### Health Monitoring

- **Service Health**: Real-time service status
- **Performance Metrics**: Response times and throughput
- **Error Rates**: Error tracking and alerting
- **Resource Usage**: CPU, memory, and storage monitoring

#### Data Quality Monitoring

- **Data Completeness**: Missing data detection
- **Data Consistency**: Schema validation
- **Data Freshness**: Timestamp monitoring
- **Anomaly Detection**: Statistical anomaly detection

#### Business Metrics

- **Content Volume**: Data collection volumes
- **Engagement Metrics**: User engagement tracking
- **Digest Performance**: Digest generation metrics
- **Trend Analysis**: Trending topic tracking

### Alerting

The system includes automated alerting for:

- **Service Failures**: Service downtime alerts
- **Data Quality Issues**: Data quality degradation
- **Performance Degradation**: Slow response times
- **Security Events**: Security incident alerts
- **Resource Exhaustion**: Resource usage alerts

## Security

### Authentication & Authorization

#### API Security

- **API Keys**: Secure API key management
- **Rate Limiting**: Request rate limiting
- **Input Validation**: Comprehensive input validation
- **CORS Configuration**: Cross-origin resource sharing

#### Data Security

- **Encryption at Rest**: Data encryption in storage
- **Encryption in Transit**: TLS/SSL encryption
- **Access Control**: Role-based access control
- **Audit Logging**: Comprehensive audit trails

### Security Best Practices

1. **Credential Management**

   - Use environment variables for sensitive data
   - Rotate credentials regularly
   - Use least privilege principle

2. **Network Security**

   - VPC configuration for cloud resources
   - Firewall rules and security groups
   - DDoS protection

3. **Application Security**

   - Input validation and sanitization
   - SQL injection prevention
   - XSS protection
   - CSRF protection

4. **Monitoring & Alerting**
   - Security event monitoring
   - Intrusion detection
   - Automated threat response

## Troubleshooting

### Common Issues

#### 1. Crawler Failures

**Symptoms**: No data being collected
**Diagnosis**:

```bash
# Check crawler logs
gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=twitter-crawler'

# Check service status
gcloud run services describe twitter-crawler --region=us-central1
```

**Solutions**:

- Verify API credentials
- Check rate limiting
- Review error logs for specific issues
- Restart service if needed

#### 2. Database Connection Issues

**Symptoms**: Database errors in logs
**Diagnosis**:

```bash
# Check database connectivity
python -c "from storage.db import get_db; print(get_db().execute('SELECT 1').fetchone())"
```

**Solutions**:

- Verify database credentials
- Check network connectivity
- Review connection pool settings
- Restart database if needed

#### 3. Performance Issues

**Symptoms**: Slow response times
**Diagnosis**:

```bash
# Check performance logs
tail -f logs/performance.log

# Monitor resource usage
gcloud monitoring metrics list
```

**Solutions**:

- Scale up resources
- Optimize queries
- Review caching strategy
- Check for bottlenecks

### Debugging Tools

#### 1. Log Analysis

```bash
# Search for specific errors
grep "ERROR" logs/*.log

# Analyze performance
grep "PERF" logs/performance.log

# Check recent activity
tail -100 logs/main.log
```

#### 2. Database Debugging

```python
# Check database schema
from storage.db import get_db
db = get_db()
tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print(tables)

# Check data quality
from utils.data_quality_monitor import DataQualityMonitor
monitor = DataQualityMonitor()
report = monitor.generate_report()
print(report)
```

#### 3. API Testing

```bash
# Test API endpoints
curl -X GET https://your-service-url/health
curl -X POST https://your-service-url/trigger
```

### Recovery Procedures

#### 1. Service Recovery

```bash
# Restart failed service
gcloud run services update service-name --region=us-central1

# Check service health
gcloud run services describe service-name --region=us-central1
```

#### 2. Data Recovery

```bash
# Restore from backup
gsutil cp gs://backup-bucket/backup.sql ./backup.sql
python restore_from_backup.py backup.sql
```

#### 3. Configuration Recovery

```bash
# Restore configuration
git checkout HEAD -- config/
python setup_project.py
```

## API Reference

### REST API Endpoints

#### Health Check

```
GET /health
Response: {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}
```

#### Data Collection

```
POST /collect/twitter
POST /collect/reddit
POST /collect/crypto
Response: {"status": "success", "records_collected": 100}
```

#### Digest Generation

```
POST /generate/digest
Response: {"status": "success", "digest_id": "digest_20240101"}
```

#### Analytics

```
GET /analytics/trends
GET /analytics/viral
GET /analytics/performance
```

### Cloud Function Triggers

#### Scheduled Triggers

- **Digest Generation**: Daily at 6 AM UTC
- **Data Cleanup**: Daily at 2 AM UTC
- **Health Checks**: Every 5 minutes

#### Event Triggers

- **Data Collection**: Triggered by Cloud Scheduler
- **Processing**: Triggered by new data arrival
- **Alerting**: Triggered by error conditions

### Database Schema

#### Core Tables

```sql
-- Tweets table
CREATE TABLE tweets (
    id INTEGER PRIMARY KEY,
    tweet_id TEXT UNIQUE,
    username TEXT,
    content TEXT,
    created_at TIMESTAMP,
    engagement_score REAL,
    virality_score REAL,
    source TEXT,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reddit posts table
CREATE TABLE reddit_posts (
    id INTEGER PRIMARY KEY,
    post_id TEXT UNIQUE,
    subreddit TEXT,
    title TEXT,
    content TEXT,
    score INTEGER,
    created_at TIMESTAMP,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crypto data table
CREATE TABLE crypto_data (
    id INTEGER PRIMARY KEY,
    token_address TEXT,
    token_name TEXT,
    price REAL,
    market_cap REAL,
    volume_24h REAL,
    source TEXT,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Digests table
CREATE TABLE digests (
    id INTEGER PRIMARY KEY,
    digest_date DATE,
    content TEXT,
    summary TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Development Guide

### Development Environment Setup

1. **Prerequisites**:

   - Python 3.11+
   - Node.js 18+ (for some tools)
   - Docker (for containerization)
   - Git

2. **Local Setup**:

   ```bash
   git clone https://github.com/your-repo/degen-digest.git
   cd degen-digest
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configuration**:

   ```bash
   cp .env.example .env
   # Edit .env with your development credentials
   ```

4. **Database Setup**:
   ```bash
   python recreate_db.py
   ```

### Development Workflow

#### 1. Feature Development

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes
# Test locally
python -m pytest tests/

# Commit changes
git add .
git commit -m "Add new feature"

# Push and create PR
git push origin feature/new-feature
```

#### 2. Testing

```bash
# Run all tests
python -m pytest

# Run specific test
python -m pytest tests/test_crawler.py

# Run with coverage
python -m pytest --cov=.

# Run integration tests
python -m pytest tests/integration/
```

#### 3. Code Quality

```bash
# Run linting
flake8 .
black .
isort .

# Run type checking
mypy .

# Run security checks
bandit -r .
```

### Contributing Guidelines

#### Code Standards

- Follow PEP 8 style guide
- Use type hints for all functions
- Write comprehensive docstrings
- Include unit tests for new features

#### Commit Messages

- Use conventional commit format
- Include issue numbers when applicable
- Write descriptive commit messages

#### Pull Request Process

1. Create feature branch
2. Make changes with tests
3. Update documentation
4. Create pull request
5. Address review comments
6. Merge after approval

### Performance Optimization

#### 1. Database Optimization

- Use indexes for frequently queried columns
- Implement connection pooling
- Use batch operations for bulk data
- Monitor query performance

#### 2. Caching Strategy

- Implement Redis for session storage
- Use in-memory caching for frequently accessed data
- Cache API responses where appropriate
- Implement cache invalidation strategies

#### 3. Resource Management

- Use async/await for I/O operations
- Implement proper error handling
- Monitor memory usage
- Use connection pooling

### Security Considerations

#### 1. Input Validation

- Validate all user inputs
- Sanitize data before processing
- Use parameterized queries
- Implement rate limiting

#### 2. Authentication

- Use secure authentication methods
- Implement proper session management
- Use HTTPS for all communications
- Implement proper error handling

#### 3. Data Protection

- Encrypt sensitive data
- Implement proper access controls
- Regular security audits
- Monitor for security events

---

This documentation provides a comprehensive overview of the DegenDigest system. For specific implementation details, refer to the individual component documentation and source code comments.
