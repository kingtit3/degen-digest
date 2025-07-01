# Degen Digest System Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Components](#components)
4. [Deployment](#deployment)
5. [Monitoring & Logging](#monitoring--logging)
6. [Troubleshooting](#troubleshooting)
7. [API Documentation](#api-documentation)
8. [Database Schema](#database-schema)
9. [Configuration](#configuration)
10. [Security](#security)

## System Overview

Degen Digest is a comprehensive crypto content aggregation and analysis platform deployed on Google Cloud Platform. The system automatically collects, processes, and analyzes social media content related to cryptocurrency and blockchain projects.

### Key Features
- **Multi-source data collection**: Twitter, Reddit, Telegram, Discord, News APIs
- **AI-powered content analysis**: Sentiment analysis, viral prediction, content classification
- **Automated digest generation**: Daily summaries with engagement metrics
- **Real-time monitoring**: System health, data quality, and performance metrics
- **Cloud-native architecture**: Scalable, fault-tolerant deployment

### System Status
- **Dashboard**: https://farmchecker.xyz
- **Cloud Function**: https://us-central1-lucky-union-463615-t3.cloudfunctions.net/farmchecker-data-refresh
- **Scheduler**: Automated digest generation every 6 hours

## Architecture

### High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │    │  Cloud Function │    │   Dashboard     │
│                 │    │                 │    │                 │
│ • Twitter API   │───▶│ • Data Collection│───▶│ • Streamlit App │
│ • Reddit API    │    │ • Processing     │    │ • Analytics     │
│ • Telegram      │    │ • Analysis       │    │ • Monitoring    │
│ • Discord       │    │ • Digest Gen     │    │                 │
│ • News APIs     │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   SQLite DB     │
                       │                 │
                       │ • Tweets        │
                       │ • Reddit Posts  │
                       │ • Digests       │
                       │ • Metrics       │
                       └─────────────────┘
```

### Component Interaction Flow
1. **Data Collection**: Cloud Function triggers data collection from multiple sources
2. **Processing**: Raw data is cleaned, classified, and scored
3. **Analysis**: AI models analyze sentiment and predict virality
4. **Storage**: Processed data stored in SQLite database
5. **Digest Generation**: Automated creation of daily summaries
6. **Dashboard**: Real-time visualization and monitoring

## Components

### 1. Cloud Function (`cloud_function/main.py`)
**Purpose**: Core data processing and digest generation engine

**Key Functions**:
- `main()`: Entry point for HTTP triggers
- `collect_all_data()`: Orchestrates data collection from all sources
- `generate_digest()`: Creates daily digest summaries
- `process_data()`: Handles data cleaning and analysis

**Configuration**:
- Environment variables for API keys
- Rate limiting and error handling
- Automatic retry mechanisms

**Logging**: Comprehensive structured logging with performance metrics

### 2. Dashboard (`dashboard/app.py`)
**Purpose**: Web-based monitoring and analytics interface

**Features**:
- Real-time data visualization
- System health monitoring
- Performance metrics
- Data quality reports
- Manual digest generation

**Pages**:
- **Digests**: View and manage generated digests
- **Analytics**: Engagement and trend analysis
- **Live Feed**: Real-time data stream
- **Health Monitor**: System status and alerts
- **Sources**: Data source management

### 3. Data Processors (`processor/`)
**Purpose**: AI-powered content analysis and processing

**Components**:
- `classifier.py`: Content categorization
- `scorer.py`: Engagement scoring
- `viral_predictor.py`: Virality prediction
- `summarizer.py`: Content summarization
- `content_clustering.py`: Topic clustering

### 4. Scrapers (`scrapers/`)
**Purpose**: Data collection from various sources

**Components**:
- `twitter_apify.py`: Twitter data via Apify
- `reddit_rss.py`: Reddit data via RSS
- `telegram_telethon.py`: Telegram channel monitoring
- `discord_scraper.py`: Discord server monitoring
- `newsapi_headlines.py`: News API integration

### 5. Storage (`storage/db.py`)
**Purpose**: Database management and data persistence

**Features**:
- SQLite database with SQLModel ORM
- Automatic schema management
- Data validation and constraints
- Backup and recovery mechanisms

## Deployment

### Cloud Function Deployment
```bash
# Deploy to Google Cloud Functions
gcloud functions deploy farmchecker-data-refresh \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --memory 2GB \
  --timeout 540s \
  --set-env-vars "ENVIRONMENT=production"
```

### Dashboard Deployment
```bash
# Deploy to Streamlit Cloud
streamlit deploy dashboard/app.py
```

### Scheduler Setup
```bash
# Create Cloud Scheduler job
gcloud scheduler jobs create http degen-digest-scheduler \
  --schedule="0 */6 * * *" \
  --uri="https://us-central1-lucky-union-463615-t3.cloudfunctions.net/farmchecker-data-refresh" \
  --http-method=POST
```

## Monitoring & Logging

### Logging System
**Location**: `utils/advanced_logging.py`

**Features**:
- Structured JSON logging
- Performance metrics tracking
- Error correlation
- Function call tracing
- Database operation logging

**Log Levels**:
- `DEBUG`: Detailed debugging information
- `INFO`: General operational information
- `WARNING`: Potential issues
- `ERROR`: Error conditions
- `CRITICAL`: System failures

### Monitoring System
**Location**: `utils/monitoring.py`

**Metrics Collected**:
- System resources (CPU, memory, disk)
- Database health and performance
- API response times and availability
- Data quality metrics
- Business metrics (engagement, costs)

**Alerts**:
- High resource usage (>80% CPU/memory)
- Database connectivity issues
- Data quality degradation
- API failures
- System errors

### Health Checks
```python
# Run comprehensive monitoring
from utils.monitoring import system_monitor
metrics = system_monitor.run_comprehensive_monitoring()
```

## Troubleshooting

### Common Issues

#### 1. Cloud Function Timeout
**Symptoms**: Function fails after 540 seconds
**Causes**: Large data processing, slow API responses
**Solutions**:
- Increase memory allocation
- Implement batch processing
- Add timeout handling

#### 2. Database Connection Errors
**Symptoms**: SQLAlchemy OperationalError
**Causes**: Schema mismatch, corrupted database
**Solutions**:
```bash
# Recreate database
python recreate_db.py
```

#### 3. Import Errors
**Symptoms**: ModuleNotFoundError
**Causes**: Missing dependencies
**Solutions**:
```bash
# Install missing packages
pip install -r requirements.txt
```

#### 4. API Rate Limiting
**Symptoms**: 429 errors, data collection failures
**Causes**: Exceeding API rate limits
**Solutions**:
- Implement exponential backoff
- Add rate limiting
- Use multiple API keys

### Debug Commands
```bash
# Check system logs
tail -f logs/degen_digest.log

# Monitor system metrics
python -c "from utils.monitoring import system_monitor; system_monitor.run_comprehensive_monitoring()"

# Test cloud function
curl -X POST https://us-central1-lucky-union-463615-t3.cloudfunctions.net/farmchecker-data-refresh

# Check database health
python -c "from storage.db import engine; from sqlmodel import Session; print('DB OK' if Session(engine) else 'DB Error')"
```

### Performance Optimization
1. **Database Indexing**: Ensure proper indexes on frequently queried columns
2. **Caching**: Implement Redis caching for expensive operations
3. **Batch Processing**: Process data in batches to reduce memory usage
4. **Connection Pooling**: Reuse database connections
5. **Async Processing**: Use async/await for I/O operations

## API Documentation

### Cloud Function Endpoints

#### POST /farmchecker-data-refresh
Triggers data collection and digest generation

**Request**:
```json
{
  "force_refresh": false,
  "generate_digest": true
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Data collection and digest generation completed",
  "metrics": {
    "tweets_collected": 150,
    "reddit_posts": 45,
    "processing_time": 120.5
  }
}
```

### Dashboard API Endpoints

#### GET /api/health
Returns system health status

#### GET /api/metrics
Returns performance metrics

#### POST /api/generate-digest
Manually trigger digest generation

## Database Schema

### Tables

#### tweets
```sql
CREATE TABLE tweets (
    id INTEGER PRIMARY KEY,
    tweet_id TEXT UNIQUE,
    user_screen_name TEXT,
    full_text TEXT,
    created_at DATETIME,
    like_count INTEGER,
    retweet_count INTEGER,
    reply_count INTEGER,
    quote_count INTEGER,
    engagement_score REAL,
    sentiment_score REAL,
    viral_score REAL,
    category TEXT,
    processed_at DATETIME
);
```

#### reddit_posts
```sql
CREATE TABLE reddit_posts (
    id INTEGER PRIMARY KEY,
    post_id TEXT UNIQUE,
    title TEXT,
    selftext TEXT,
    subreddit TEXT,
    author TEXT,
    created_at DATETIME,
    score INTEGER,
    num_comments INTEGER,
    engagement_score REAL,
    sentiment_score REAL,
    viral_score REAL,
    category TEXT,
    processed_at DATETIME
);
```

#### digests
```sql
CREATE TABLE digests (
    id INTEGER PRIMARY KEY,
    date TEXT,
    content TEXT,
    summary TEXT,
    top_tweets TEXT,
    top_reddit_posts TEXT,
    metrics TEXT,
    created_at DATETIME
);
```

#### llm_usage
```sql
CREATE TABLE llm_usage (
    id INTEGER PRIMARY KEY,
    month TEXT,
    tokens_used INTEGER,
    cost_usd REAL,
    created_at DATETIME
);
```

## Configuration

### Environment Variables
```bash
# API Keys
TWITTER_BEARER_TOKEN=your_twitter_token
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_secret
NEWSAPI_KEY=your_newsapi_key
TELEGRAM_API_ID=your_telegram_api_id
TELEGRAM_API_HASH=your_telegram_hash

# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
PROJECT_ID=lucky-union-463615-t3

# Database
DATABASE_URL=sqlite:///output/degen_digest.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/degen_digest.log
```

### Configuration Files

#### `config/app_config.yaml`
```yaml
data_collection:
  twitter:
    enabled: true
    rate_limit: 100
  reddit:
    enabled: true
    subreddits: ["cryptocurrency", "bitcoin"]
  telegram:
    enabled: true
    channels: ["@cryptosignals"]

processing:
  batch_size: 100
  max_workers: 4
  timeout_seconds: 300

analysis:
  min_engagement_score: 0.1
  viral_threshold: 0.7
  sentiment_threshold: 0.5
```

## Security

### API Security
- Rate limiting on all endpoints
- Input validation and sanitization
- CORS configuration
- Authentication for sensitive operations

### Data Security
- Encrypted API keys
- Secure database connections
- Regular security audits
- Access control and logging

### Cloud Security
- IAM role-based access control
- VPC network isolation
- Cloud audit logging
- Security scanning

### Best Practices
1. **Never commit API keys** to version control
2. **Use environment variables** for sensitive data
3. **Implement proper error handling** to avoid information leakage
4. **Regular security updates** for dependencies
5. **Monitor for suspicious activity**

## Maintenance

### Daily Tasks
- Monitor system health metrics
- Review error logs
- Check data quality reports
- Verify digest generation

### Weekly Tasks
- Performance optimization review
- Database maintenance
- Security audit
- Backup verification

### Monthly Tasks
- System architecture review
- Cost optimization
- Feature planning
- Documentation updates

## Support

### Getting Help
1. Check this documentation first
2. Review system logs in `logs/degen_digest.log`
3. Run monitoring diagnostics
4. Check GitHub issues for known problems

### Emergency Contacts
- **System Admin**: [Your Contact]
- **Cloud Provider**: Google Cloud Support
- **Documentation**: This file and inline code comments

---

*Last Updated: December 2024*
*Version: 1.0* 