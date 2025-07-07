# FarmChecker.xyz - Enterprise Documentation

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [System Components](#system-components)
4. [API Documentation](#api-documentation)
5. [Database Schema](#database-schema)
6. [Deployment Guide](#deployment-guide)
7. [Monitoring & Logging](#monitoring--logging)
8. [Security](#security)
9. [Development Guide](#development-guide)
10. [Troubleshooting](#troubleshooting)

## Project Overview

FarmChecker.xyz is a comprehensive crypto intelligence platform that aggregates real-time data from multiple sources including Twitter, Reddit, news outlets, and cryptocurrency exchanges. The platform provides analytics, market insights, and trending information for cryptocurrency traders and enthusiasts.

### Key Features

- **Real-time Data Aggregation**: Collects data from Twitter, Reddit, CoinGecko, DexScreener, and DexPaprika
- **Live Market Data**: Displays current prices, market caps, and 24h changes
- **Social Media Analytics**: Tracks engagement metrics and trending topics
- **Responsive Web Interface**: Modern, mobile-friendly design with dark mode
- **Enterprise Logging**: Comprehensive structured logging and monitoring
- **Scalable Architecture**: Microservices-based deployment on Google Cloud

### Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python 3.11, Flask
- **Database**: PostgreSQL (Cloud SQL)
- **Cloud Platform**: Google Cloud Platform
- **Deployment**: Google Cloud Run
- **Monitoring**: Custom enterprise logging system
- **Crawlers**: Python with async/await patterns

## Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │   API Gateway   │    │   Database      │
│   (Cloud Run)   │◄──►│   (Cloud Run)   │◄──►│   (Cloud SQL)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ CoinGecko       │    │ DexScreener     │    │ DexPaprika      │
│ Crawler         │    │ Crawler         │    │ Crawler         │
│ (Cloud Run)     │    │ (Cloud Run)     │    │ (Cloud Run)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Flow

1. **Data Collection**: Crawlers run every 7 minutes to collect data from various sources
2. **Data Processing**: Raw data is cleaned, validated, and stored in PostgreSQL
3. **API Serving**: Flask API serves processed data to the frontend
4. **Frontend Display**: Modern web interface displays data with real-time updates

## System Components

### 1. Web Application (`farmchecker-website`)

**Purpose**: Main user interface for the platform

**Features**:
- Responsive design with dark mode
- Real-time data display
- Interactive charts and analytics
- Mobile-friendly navigation

**Technology**: HTML5, CSS3, JavaScript, Chart.js

**Deployment**: Google Cloud Run

### 2. API Gateway (`server.py`)

**Purpose**: RESTful API for serving data to the frontend

**Endpoints**:
- `/api/stats` - System statistics
- `/api/crypto/top-gainers` - Top performing cryptocurrencies
- `/api/crypto/trending` - Trending cryptocurrencies
- `/api/crypto/market-data` - Market overview data
- `/api/twitter-posts` - Twitter posts with engagement metrics
- `/api/reddit-posts` - Reddit posts with engagement metrics
- `/api/latest-digest` - Latest digest information
- `/api/system-status` - System health status

**Technology**: Python Flask, PostgreSQL

### 3. Data Crawlers

#### CoinGecko Crawler (`enhanced-coingecko-crawler`)

**Purpose**: Collects cryptocurrency data from CoinGecko API

**Data Collected**:
- Token prices and market caps
- 24h price changes
- Trading volumes
- Market rankings

**Schedule**: Every 7 minutes

#### DexScreener Crawler (`dexscreener-crawler`)

**Purpose**: Collects DEX trading data from DexScreener

**Data Collected**:
- DEX token prices
- Liquidity information
- Trading pairs
- Volume data

**Schedule**: Every 7 minutes

#### DexPaprika Crawler (`dexpaprika-crawler`)

**Purpose**: Collects additional DEX data from DexPaprika

**Data Collected**:
- Alternative DEX prices
- Cross-platform comparisons
- Additional market data

**Schedule**: Every 7 minutes

### 4. Database (`crypto_tokens` table)

**Schema**:
```sql
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
```

## API Documentation

### Authentication

Currently, the API is public and doesn't require authentication. Rate limiting is implemented to prevent abuse.

### Endpoints

#### GET /api/stats

Returns system statistics including data counts from various sources.

**Response**:
```json
{
  "crypto": 210,
  "dexpaprika": 100,
  "dexscreener": 2400,
  "news": 2058,
  "reddit": 420,
  "total_engagement": "0",
  "twitter": 294
}
```

#### GET /api/crypto/top-gainers

Returns top performing cryptocurrencies based on 24h price change.

**Response**:
```json
[
  {
    "id": 2,
    "symbol": "ETH",
    "name": "Ethereum",
    "price": "$3,200.00",
    "price_change_24h": "+3.10%",
    "price_change_percentage_24h": 3.1,
    "market_cap": "$380.00B",
    "volume_24h": "$15.00B",
    "rank": 0,
    "image": "",
    "source": "ethereum",
    "updated_at": "2025-07-06T03:37:45.876012"
  }
]
```

#### GET /api/crypto/trending

Returns trending cryptocurrencies.

**Response**: Same format as top-gainers

#### GET /api/crypto/market-data

Returns market overview data.

**Response**:
```json
{
  "total_tokens": 2710,
  "sources": {
    "crypto": 210,
    "dexpaprika": 100,
    "dexscreener": 2400
  },
  "market_sentiment": "bullish"
}
```

#### GET /api/system-status

Returns system health status for all services.

**Response**:
```json
{
  "coingecko_crawler": {
    "status": "online",
    "last_run_ago": "2 minutes ago"
  },
  "dexscreener_crawler": {
    "status": "online", 
    "last_run_ago": "3 minutes ago"
  },
  "dexpaprika_crawler": {
    "status": "online",
    "last_run_ago": "4 minutes ago"
  }
}
```

## Database Schema

### Tables

#### crypto_tokens

Main table storing cryptocurrency data from all sources.

```sql
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

-- Indexes for performance
CREATE INDEX idx_crypto_tokens_symbol ON crypto_tokens(symbol);
CREATE INDEX idx_crypto_tokens_source ON crypto_tokens(source);
CREATE INDEX idx_crypto_tokens_updated_at ON crypto_tokens(updated_at);
CREATE INDEX idx_crypto_tokens_price_change ON crypto_tokens(price_change_percentage_24h DESC);
```

#### content_items (Legacy)

Legacy table for storing social media and news content.

```sql
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
```

## Deployment Guide

### Prerequisites

1. Google Cloud Platform account
2. Google Cloud CLI installed
3. Docker installed
4. Python 3.11+

### Environment Setup

1. **Set up Google Cloud Project**:
```bash
gcloud config set project YOUR_PROJECT_ID
gcloud auth login
```

2. **Enable required APIs**:
```bash
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

3. **Set up Cloud SQL**:
```bash
# Create PostgreSQL instance
gcloud sql instances create farmchecker-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=YOUR_PASSWORD

# Create database
gcloud sql databases create farmchecker --instance=farmchecker-db
```

### Deployment Steps

1. **Deploy Web Application**:
```bash
cd farmchecker_new
gcloud run deploy farmchecker-website \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 5000
```

2. **Deploy Crawlers**:
```bash
# Deploy CoinGecko crawler
gcloud run deploy enhanced-coingecko-crawler \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated

# Deploy DexScreener crawler  
gcloud run deploy dexscreener-crawler \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated

# Deploy DexPaprika crawler
gcloud run deploy dexpaprika-crawler \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

3. **Set up Domain Mapping**:
```bash
gcloud beta run domain-mappings create \
    --service farmchecker-website \
    --domain farmchecker.xyz \
    --region us-central1
```

4. **Configure Environment Variables**:
```bash
# Set database connection
gcloud run services update farmchecker-website \
    --set-env-vars DATABASE_URL=postgresql://user:pass@host:port/db \
    --region us-central1
```

### Monitoring Setup

1. **Enable Cloud Monitoring**:
```bash
gcloud services enable monitoring.googleapis.com
```

2. **Set up Logging**:
```bash
# Create log bucket
gsutil mb gs://farmchecker-logs

# Configure log export
gcloud logging sinks create farmchecker-logs \
    storage.googleapis.com/farmchecker-logs \
    --log-filter="resource.type=cloud_run_revision"
```

## Monitoring & Logging

### Enterprise Logging System

The platform uses a custom enterprise logging system (`utils/enterprise_logger.py`) that provides:

- **Structured JSON Logging**: All logs are in JSON format for easy parsing
- **Performance Monitoring**: Track response times, memory usage, and CPU usage
- **Audit Trails**: Complete audit trail for all system events
- **Error Tracking**: Detailed error logging with stack traces
- **Business Metrics**: Track business KPIs and user behavior

### Log Levels

- **DEBUG**: Detailed debugging information
- **INFO**: General information about system operation
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failed operations
- **CRITICAL**: Critical system failures
- **AUDIT**: Security and compliance audit events
- **SECURITY**: Security-related events
- **PERFORMANCE**: Performance metrics and monitoring
- **BUSINESS**: Business metrics and KPIs

### Monitoring Dashboards

Create monitoring dashboards in Google Cloud Console for:

1. **System Health**: Service uptime, response times, error rates
2. **Data Quality**: Data freshness, completeness, accuracy
3. **Performance**: API response times, database query performance
4. **Business Metrics**: User engagement, data volume, trending topics

### Alerting

Set up alerts for:

- Service downtime
- High error rates (>5%)
- Slow response times (>2 seconds)
- Data freshness issues (>10 minutes old)
- High memory/CPU usage

## Security

### Security Measures

1. **HTTPS Only**: All services use HTTPS with TLS 1.3
2. **Input Validation**: All API inputs are validated and sanitized
3. **Rate Limiting**: API rate limiting to prevent abuse
4. **CORS Configuration**: Proper CORS headers for web security
5. **Database Security**: Cloud SQL with encrypted connections
6. **Logging Security**: Sensitive data is not logged

### Security Best Practices

1. **Regular Updates**: Keep all dependencies updated
2. **Secret Management**: Use Google Secret Manager for sensitive data
3. **Access Control**: Implement proper IAM roles and permissions
4. **Monitoring**: Monitor for suspicious activities
5. **Backup**: Regular database backups

### Compliance

- **GDPR**: Data privacy compliance for EU users
- **SOC 2**: Security and availability controls
- **PCI DSS**: Payment card industry compliance (if applicable)

## Development Guide

### Local Development Setup

1. **Clone Repository**:
```bash
git clone https://github.com/your-org/farmchecker.git
cd farmchecker/farmchecker_new
```

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up Local Database**:
```bash
# Install PostgreSQL locally or use Docker
docker run --name farmchecker-db \
    -e POSTGRES_PASSWORD=password \
    -e POSTGRES_DB=farmchecker \
    -p 5432:5432 \
    -d postgres:14
```

4. **Configure Environment**:
```bash
export DATABASE_URL=postgresql://postgres:password@localhost:5432/farmchecker
export ENVIRONMENT=development
```

5. **Run Application**:
```bash
python server.py
```

### Code Standards

1. **Python**: Follow PEP 8 style guide
2. **JavaScript**: Use ESLint with Airbnb config
3. **CSS**: Use consistent naming conventions (BEM methodology)
4. **Documentation**: All functions must have docstrings
5. **Testing**: Maintain >80% code coverage

### Testing

1. **Unit Tests**:
```bash
python -m pytest tests/ -v
```

2. **Integration Tests**:
```bash
python -m pytest tests/integration/ -v
```

3. **API Tests**:
```bash
python -m pytest tests/api/ -v
```

### Code Review Process

1. Create feature branch from main
2. Implement changes with tests
3. Submit pull request
4. Code review by team member
5. Address feedback
6. Merge to main branch

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues

**Symptoms**: API returns 500 errors, database connection timeouts

**Solutions**:
- Check Cloud SQL instance status
- Verify connection string
- Check firewall rules
- Monitor connection pool

#### 2. Crawler Failures

**Symptoms**: No new data, crawler services showing offline

**Solutions**:
- Check crawler logs: `gcloud run services logs read SERVICE_NAME`
- Verify API rate limits
- Check network connectivity
- Monitor resource usage

#### 3. High Response Times

**Symptoms**: Slow website loading, API timeouts

**Solutions**:
- Check database query performance
- Monitor Cloud Run scaling
- Review caching strategy
- Optimize database indexes

#### 4. Memory Issues

**Symptoms**: Service crashes, out of memory errors

**Solutions**:
- Increase Cloud Run memory allocation
- Optimize data processing
- Implement pagination
- Review memory leaks

### Debug Commands

```bash
# Check service status
gcloud run services list --region us-central1

# View service logs
gcloud run services logs read SERVICE_NAME --region us-central1

# Check database connections
gcloud sql instances describe farmchecker-db

# Monitor resource usage
gcloud monitoring metrics list --filter="metric.type:run.googleapis.com"

# Test API endpoints
curl -X GET https://farmchecker.xyz/api/stats
```

### Performance Optimization

1. **Database Optimization**:
   - Add appropriate indexes
   - Optimize queries
   - Use connection pooling
   - Implement caching

2. **API Optimization**:
   - Implement pagination
   - Use compression
   - Cache frequently accessed data
   - Optimize response payloads

3. **Frontend Optimization**:
   - Minimize bundle size
   - Use CDN for static assets
   - Implement lazy loading
   - Optimize images

### Maintenance Tasks

1. **Daily**:
   - Monitor service health
   - Check error rates
   - Review performance metrics

2. **Weekly**:
   - Update dependencies
   - Review security logs
   - Backup verification

3. **Monthly**:
   - Performance review
   - Security audit
   - Capacity planning

## Support

For technical support and questions:

- **Email**: support@farmchecker.xyz
- **Documentation**: https://docs.farmchecker.xyz
- **GitHub Issues**: https://github.com/your-org/farmchecker/issues
- **Slack**: #farmchecker-support

---

**Last Updated**: July 6, 2025  
**Version**: 1.0.0  
**Maintainer**: FarmChecker.xyz Development Team 