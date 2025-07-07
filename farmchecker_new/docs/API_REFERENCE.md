# FarmChecker.xyz API Reference

## Overview

The FarmChecker.xyz API provides access to real-time cryptocurrency data, social media analytics, and market insights. All endpoints return JSON responses and use standard HTTP status codes.

**Base URL**: `https://farmchecker.xyz/api`

## Authentication

Currently, the API is public and doesn't require authentication. Rate limiting is implemented to prevent abuse.

**Rate Limits**:
- 100 requests per minute per IP address
- 1000 requests per hour per IP address

## Response Format

All API responses follow this standard format:

```json
{
  "data": {...},
  "timestamp": "2025-07-06T04:00:00Z",
  "status": "success"
}
```

Error responses:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {...}
  },
  "timestamp": "2025-07-06T04:00:00Z",
  "status": "error"
}
```

## Endpoints

### System Statistics

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

**Fields**:
- `crypto`: Number of tokens from CoinGecko
- `dexpaprika`: Number of tokens from DexPaprika
- `dexscreener`: Number of tokens from DexScreener
- `news`: Number of news articles
- `reddit`: Number of Reddit posts
- `twitter`: Number of Twitter posts
- `total_engagement`: Total engagement across all social media

### Cryptocurrency Data

#### GET /api/crypto/top-gainers

Returns top performing cryptocurrencies based on 24h price change.

**Query Parameters**:
- `limit` (optional): Number of results to return (default: 10, max: 100)
- `source` (optional): Filter by data source (coingecko, dexscreener, dexpaprika)

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

**Fields**:
- `id`: Unique identifier
- `symbol`: Token symbol (e.g., "ETH")
- `name`: Token name (e.g., "Ethereum")
- `price`: Current price formatted as string
- `price_change_24h`: 24h price change as percentage string
- `price_change_percentage_24h`: 24h price change as decimal
- `market_cap`: Market capitalization
- `volume_24h`: 24h trading volume
- `rank`: Market rank (0 if not ranked)
- `image`: Token image URL
- `source`: Data source
- `updated_at`: Last update timestamp

#### GET /api/crypto/trending

Returns trending cryptocurrencies.

**Query Parameters**:
- `limit` (optional): Number of results to return (default: 10, max: 100)
- `source` (optional): Filter by data source

**Response**: Same format as `/api/crypto/top-gainers`

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

**Fields**:
- `total_tokens`: Total number of tracked tokens
- `sources`: Token counts by data source
- `market_sentiment`: Overall market sentiment (bullish/bearish/neutral)

#### GET /api/crypto/search

Search for cryptocurrencies by symbol or name.

**Query Parameters**:
- `q` (required): Search query
- `limit` (optional): Number of results (default: 10, max: 50)

**Response**:
```json
[
  {
    "id": 1,
    "symbol": "BTC",
    "name": "Bitcoin",
    "price": "$45,000.00",
    "price_change_24h": "+2.85%",
    "price_change_percentage_24h": 2.85,
    "market_cap": "$850.00B",
    "volume_24h": "$25.00B",
    "rank": 1,
    "image": "",
    "source": "bitcoin",
    "updated_at": "2025-07-06T03:37:45.301178"
  }
]
```

### Social Media Data

#### GET /api/twitter-posts

Returns Twitter posts with engagement metrics.

**Query Parameters**:
- `limit` (optional): Number of results (default: 10, max: 100)
- `sort` (optional): Sort order (engagement, recent, likes, retweets)
- `min_engagement` (optional): Minimum engagement score

**Response**:
```json
[
  {
    "id": 1,
    "title": "Bitcoin reaches new all-time high",
    "content": "Bitcoin has reached a new all-time high of $75,000...",
    "author": "crypto_analyst",
    "engagement_score": 1250,
    "published_at": "2025-07-05T20:30:00Z",
    "likes": 850,
    "replies": 400,
    "retweets": 200,
    "views": 50000
  }
]
```

**Fields**:
- `id`: Unique identifier
- `title`: Post title
- `content`: Post content
- `author`: Twitter username
- `engagement_score`: Calculated engagement score
- `published_at`: Publication timestamp
- `likes`: Number of likes
- `replies`: Number of replies
- `retweets`: Number of retweets
- `views`: Number of views

#### GET /api/reddit-posts

Returns Reddit posts with engagement metrics.

**Query Parameters**:
- `limit` (optional): Number of results (default: 10, max: 100)
- `sort` (optional): Sort order (engagement, recent, upvotes, comments)
- `min_score` (optional): Minimum score

**Response**:
```json
[
  {
    "id": 1,
    "title": "Ethereum 2.0 Update Discussion",
    "content": "What do you think about the latest Ethereum 2.0 developments?",
    "author": "eth_enthusiast",
    "engagement_score": 850,
    "published_at": "2025-07-05T19:30:00Z",
    "upvotes": 650,
    "comments": 200,
    "score": 850
  }
]
```

**Fields**:
- `id`: Unique identifier
- `title`: Post title
- `content`: Post content
- `author`: Reddit username
- `engagement_score`: Calculated engagement score
- `published_at`: Publication timestamp
- `upvotes`: Number of upvotes
- `comments`: Number of comments
- `score`: Post score

### System Status

#### GET /api/system-status

Returns system health status for all services.

**Response**:
```json
{
  "coingecko_crawler": {
    "status": "online",
    "last_run_ago": "2 minutes ago",
    "last_run": "2025-07-06T03:58:00Z",
    "uptime": "99.9%",
    "errors_last_24h": 0
  },
  "dexscreener_crawler": {
    "status": "online",
    "last_run_ago": "3 minutes ago",
    "last_run": "2025-07-06T03:57:00Z",
    "uptime": "99.8%",
    "errors_last_24h": 1
  },
  "dexpaprika_crawler": {
    "status": "online",
    "last_run_ago": "4 minutes ago",
    "last_run": "2025-07-06T03:56:00Z",
    "uptime": "99.7%",
    "errors_last_24h": 0
  },
  "web_app": {
    "status": "online",
    "response_time_ms": 150,
    "uptime": "100%",
    "errors_last_24h": 0
  },
  "database": {
    "status": "online",
    "connection_count": 5,
    "uptime": "100%",
    "slow_queries_last_24h": 0
  }
}
```

**Status Values**:
- `online`: Service is running normally
- `offline`: Service is down
- `stale`: Service hasn't updated recently
- `error`: Service is experiencing errors

### Latest Digest

#### GET /api/latest-digest

Returns the latest digest information.

**Response**:
```json
{
  "title": "Daily Crypto Digest - July 6, 2025",
  "content": "Today's top stories include Bitcoin's new ATH, Ethereum upgrades, and DeFi innovations...",
  "created_at": "2025-07-06T04:00:00Z",
  "summary": "Market summary and key insights...",
  "top_tokens": ["BTC", "ETH", "SOL"],
  "trending_topics": ["DeFi", "NFTs", "Layer 2"]
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `RATE_LIMIT_EXCEEDED` | Rate limit exceeded |
| `INVALID_PARAMETER` | Invalid query parameter |
| `RESOURCE_NOT_FOUND` | Requested resource not found |
| `INTERNAL_ERROR` | Internal server error |
| `SERVICE_UNAVAILABLE` | Service temporarily unavailable |
| `VALIDATION_ERROR` | Request validation failed |

## Rate Limiting

Rate limits are enforced per IP address:

- **100 requests per minute**
- **1000 requests per hour**

When rate limited, the API returns:

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again later.",
    "retry_after": 60
  },
  "timestamp": "2025-07-06T04:00:00Z",
  "status": "error"
}
```

## CORS

The API supports CORS for web applications:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

## SDKs and Libraries

### JavaScript/TypeScript

```javascript
// Example usage
const response = await fetch('https://farmchecker.xyz/api/crypto/top-gainers');
const data = await response.json();
console.log(data);
```

### Python

```python
import requests

# Example usage
response = requests.get('https://farmchecker.xyz/api/crypto/top-gainers')
data = response.json()
print(data)
```

### cURL

```bash
# Example usage
curl -X GET "https://farmchecker.xyz/api/crypto/top-gainers?limit=5"
```

## Webhooks

Webhook support is planned for future releases to notify subscribers of:

- New trending tokens
- Significant price movements
- System status changes
- Data updates

## Versioning

API versioning is handled through URL paths:

- Current version: `/api/`
- Future versions: `/api/v2/`, `/api/v3/`, etc.

Breaking changes will be announced with 6 months notice.

## Support

For API support:

- **Email**: api-support@farmchecker.xyz
- **Documentation**: https://docs.farmchecker.xyz/api
- **Status Page**: https://status.farmchecker.xyz

---

**Last Updated**: July 6, 2025  
**API Version**: 1.0.0 