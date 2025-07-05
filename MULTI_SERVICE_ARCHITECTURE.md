# Multi-Service Crawler Architecture

## Overview

Split the current monolithic crawler into separate Cloud Run services for better isolation, debugging, and resource management.

## Proposed Services

### 1. Twitter Crawler Service

- **Service Name**: `twitter-crawler`
- **Purpose**: Handle Twitter data collection with Playwright
- **Requirements**:
  - Twitter credentials
  - Playwright browser
  - Higher memory (2Gi) for browser
- **Output**: Uploads to `twitter_data/` in GCS

### 2. Reddit Crawler Service

- **Service Name**: `reddit-crawler`
- **Purpose**: Handle Reddit RSS feeds
- **Requirements**:
  - Simple HTTP requests
  - Minimal resources (512Mi memory)
- **Output**: Uploads to `reddit_data/` in GCS

### 3. News Crawler Service

- **Service Name**: `news-crawler`
- **Purpose**: Handle News API requests
- **Requirements**:
  - News API key
  - HTTP requests
  - Minimal resources (512Mi memory)
- **Output**: Uploads to `news_data/` in GCS

### 4. Crypto Crawler Service

- **Service Name**: `crypto-crawler`
- **Purpose**: Handle CoinGecko, DEX Screener, DexPaprika
- **Requirements**:
  - API requests to crypto services
  - Minimal resources (512Mi memory)
- **Output**: Uploads to `crypto_data/` in GCS

### 5. Data Aggregator Service

- **Service Name**: `data-aggregator`
- **Purpose**: Consolidate data from all crawlers
- **Requirements**:
  - Read from all GCS data folders
  - Process and deduplicate
  - Generate digests
- **Output**: Consolidated data and digests

### 6. Orchestrator Service (Optional)

- **Service Name**: `crawler-orchestrator`
- **Purpose**: Trigger crawlers on schedule
- **Requirements**:
  - Cloud Scheduler integration
  - HTTP requests to trigger other services
- **Output**: Orchestration logs

## Benefits

1. **Isolation**: Twitter issues won't affect other crawlers
2. **Debugging**: Easy to identify which service has problems
3. **Scaling**: Each service scales independently
4. **Resource Optimization**: Twitter gets more resources, others get less
5. **Deployment**: Deploy fixes to individual services
6. **Monitoring**: Separate logs and metrics per service

## Implementation Plan

### Phase 1: Create Individual Crawler Services

1. Create `twitter-crawler` service
2. Create `reddit-crawler` service
3. Create `news-crawler` service
4. Create `crypto-crawler` service

### Phase 2: Create Data Aggregator

1. Create `data-aggregator` service
2. Implement data consolidation logic
3. Test aggregation pipeline

### Phase 3: Create Orchestrator (Optional)

1. Create `crawler-orchestrator` service
2. Set up Cloud Scheduler
3. Test end-to-end pipeline

## Current Status

- Enhanced multi-source crawler is deployed but failing due to Twitter credentials
- All crawlers are running in one service, making debugging difficult
- Need to split into separate services for better management
