# Database Migration Plan for DegenDigest

## Overview

Migrate from JSON files in GCS to a hybrid SQL + GCS architecture for better analytics and performance.

## Current Data Structure

- **519 files** (~20MB) across multiple sources
- **Time-series data** with timestamped collections
- **Well-organized** GCS structure by source type

## Proposed Hybrid Architecture

### 1. SQL Database (Primary Analytics)

- **Cloud SQL (PostgreSQL)** or **BigQuery** for analytics
- Store processed, normalized data for queries
- Maintain data relationships and metadata

### 2. GCS (Primary Storage)

- Keep raw JSON files for backup and reprocessing
- Store large media content (images, videos)
- Maintain historical archives

## Database Schema Design

### Core Tables

#### 1. `data_sources`

```sql
CREATE TABLE data_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL, -- 'twitter', 'reddit', 'news', etc.
    display_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 2. `data_collections`

```sql
CREATE TABLE data_collections (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES data_sources(id),
    collection_timestamp TIMESTAMP NOT NULL,
    file_path VARCHAR(500) NOT NULL, -- GCS path
    record_count INTEGER DEFAULT 0,
    file_size_bytes BIGINT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'processed', -- 'raw', 'processed', 'error'
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 3. `content_items`

```sql
CREATE TABLE content_items (
    id SERIAL PRIMARY KEY,
    collection_id INTEGER REFERENCES data_collections(id),
    source_id INTEGER REFERENCES data_sources(id),
    external_id VARCHAR(255), -- Original ID from source
    title TEXT,
    content TEXT,
    author VARCHAR(255),
    url VARCHAR(1000),
    published_at TIMESTAMP,
    engagement_score DECIMAL(10,4),
    virality_score DECIMAL(10,4),
    sentiment_score DECIMAL(5,4),
    raw_data JSONB, -- Store original JSON for flexibility
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 4. `crypto_tokens`

```sql
CREATE TABLE crypto_tokens (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(100),
    network VARCHAR(50),
    contract_address VARCHAR(255),
    market_cap DECIMAL(20,2),
    price_usd DECIMAL(20,8),
    volume_24h DECIMAL(20,2),
    price_change_24h DECIMAL(10,4),
    first_seen_at TIMESTAMP DEFAULT NOW(),
    last_updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 5. `token_mentions`

```sql
CREATE TABLE token_mentions (
    id SERIAL PRIMARY KEY,
    content_item_id INTEGER REFERENCES content_items(id),
    token_id INTEGER REFERENCES crypto_tokens(id),
    mention_count INTEGER DEFAULT 1,
    sentiment_score DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 6. `trending_topics`

```sql
CREATE TABLE trending_topics (
    id SERIAL PRIMARY KEY,
    topic_name VARCHAR(255) NOT NULL,
    source_id INTEGER REFERENCES data_sources(id),
    mention_count INTEGER DEFAULT 0,
    engagement_score DECIMAL(10,4),
    trend_period_start TIMESTAMP,
    trend_period_end TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Migration Strategy

### Phase 1: Database Setup & Schema

1. Set up Cloud SQL PostgreSQL instance
2. Create database schema
3. Set up connection pooling and monitoring

### Phase 2: Data Migration

1. **Backfill existing data** from GCS
2. **Process consolidated files** first
3. **Migrate historical data** in batches
4. **Validate data integrity**

### Phase 3: Hybrid Integration

1. **Update crawlers** to write to both GCS and SQL
2. **Modify digest generator** to use SQL for queries
3. **Update dashboard** to query SQL database
4. **Maintain GCS sync** for backup

### Phase 4: Optimization

1. **Add indexes** for common queries
2. **Implement data retention policies**
3. **Set up automated backups**
4. **Performance monitoring**

## Implementation Benefits

### Immediate Benefits

- **Faster dashboard queries** (sub-second vs minutes)
- **Advanced analytics** (trends, correlations, patterns)
- **Better data relationships** (token mentions across sources)
- **Real-time insights** (live data processing)

### Long-term Benefits

- **Scalability** (handles millions of records)
- **Data quality** (constraints and validation)
- **Advanced ML features** (training data preparation)
- **Business intelligence** (custom reports and dashboards)

## Cost Considerations

- **Cloud SQL**: ~$25-50/month for small instance
- **Storage**: Minimal (data stays in GCS)
- **Processing**: One-time migration cost
- **ROI**: Significant performance and analytics improvements

## Next Steps

1. **Approve migration plan**
2. **Set up Cloud SQL instance**
3. **Create migration scripts**
4. **Test with subset of data**
5. **Full migration execution**

## Risk Mitigation

- **Keep GCS as backup** during migration
- **Test thoroughly** before switching
- **Rollback plan** if issues arise
- **Gradual migration** by data source
