# API Documentation

This document provides comprehensive API documentation for the Degen Digest platform.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Base URL](#base-url)
- [Endpoints](#endpoints)
- [Request/Response Formats](#requestresponse-formats)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)
- [SDKs](#sdks)

## Overview

The Degen Digest API provides programmatic access to all platform functionality including data collection, processing, and digest generation.

### API Features

- **RESTful Design** - Standard HTTP methods and status codes
- **JSON Responses** - All responses in JSON format
- **Authentication** - API key-based authentication
- **Rate Limiting** - Built-in rate limiting for API protection
- **Versioning** - API versioning for backward compatibility
- **Documentation** - Comprehensive documentation and examples

### API Versions

| Version | Status  | Release Date | End of Life |
| ------- | ------- | ------------ | ----------- |
| v1      | Current | 2025-01-01   | -           |
| v2      | Planned | 2025-06-01   | -           |

## Authentication

### API Key Authentication

All API requests require authentication using an API key.

```bash
# Include API key in headers
curl -H "X-API-Key: your_api_key_here" \
     https://api.farmchecker.xyz/v1/health
```

### Getting an API Key

1. Contact the platform administrator
2. Provide your use case and expected usage
3. Receive your API key via secure channel
4. Store the API key securely

### Security Best Practices

```bash
# Store API key securely
export DEGEN_API_KEY="your_api_key_here"

# Use in requests
curl -H "X-API-Key: $DEGEN_API_KEY" \
     https://api.farmchecker.xyz/v1/health
```

## Base URL

### Production

```
https://api.farmchecker.xyz/v1
```

### Staging

```
https://staging-api.farmchecker.xyz/v1
```

### Development

```
http://localhost:8081/v1
```

## Endpoints

### Health Check

#### GET /health

Check the health status of the API service.

**Request:**

```bash
curl -H "X-API-Key: your_api_key" \
     https://api.farmchecker.xyz/v1/health
```

**Response:**

```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2025-07-03T10:00:00Z",
    "version": "2.0.0",
    "uptime_seconds": 86400,
    "services": {
      "crawler": "healthy",
      "database": "healthy",
      "storage": "healthy"
    }
  },
  "metadata": {
    "request_id": "req_12345",
    "response_time_ms": 15
  }
}
```

#### GET /health/detailed

Get detailed health information including system metrics.

**Request:**

```bash
curl -H "X-API-Key: your_api_key" \
     https://api.farmchecker.xyz/v1/health/detailed
```

**Response:**

```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2025-07-03T10:00:00Z",
    "version": "2.0.0",
    "system_metrics": {
      "cpu_usage_percent": 25.5,
      "memory_usage_percent": 45.2,
      "disk_usage_percent": 30.1,
      "active_connections": 15
    },
    "service_health": {
      "crawler": {
        "status": "healthy",
        "last_check": "2025-07-03T09:55:00Z",
        "response_time_ms": 50
      },
      "database": {
        "status": "healthy",
        "last_check": "2025-07-03T09:55:00Z",
        "response_time_ms": 5
      },
      "storage": {
        "status": "healthy",
        "last_check": "2025-07-03T09:55:00Z",
        "response_time_ms": 100
      }
    }
  },
  "metadata": {
    "request_id": "req_12346",
    "response_time_ms": 25
  }
}
```

### Crawler Management

#### POST /crawler/start

Start the crawler service.

**Request:**

```bash
curl -X POST \
     -H "X-API-Key: your_api_key" \
     -H "Content-Type: application/json" \
     -d '{"sources": ["twitter", "reddit"]}' \
     https://api.farmchecker.xyz/v1/crawler/start
```

**Request Body:**

```json
{
  "sources": ["twitter", "reddit"],
  "options": {
    "max_items": 1000,
    "timeout_minutes": 60
  }
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "message": "Crawler started successfully",
    "crawler_id": "crawler_12345",
    "sources": ["twitter", "reddit"],
    "start_time": "2025-07-03T10:00:00Z",
    "estimated_duration_minutes": 30
  },
  "metadata": {
    "request_id": "req_12347",
    "response_time_ms": 150
  }
}
```

#### POST /crawler/stop

Stop the crawler service.

**Request:**

```bash
curl -X POST \
     -H "X-API-Key: your_api_key" \
     https://api.farmchecker.xyz/v1/crawler/stop
```

**Response:**

```json
{
  "success": true,
  "data": {
    "message": "Crawler stopped successfully",
    "crawler_id": "crawler_12345",
    "stop_time": "2025-07-03T10:30:00Z",
    "items_collected": 850,
    "duration_minutes": 30
  },
  "metadata": {
    "request_id": "req_12348",
    "response_time_ms": 50
  }
}
```

#### GET /crawler/status

Get the current status of the crawler service.

**Request:**

```bash
curl -H "X-API-Key: your_api_key" \
     https://api.farmchecker.xyz/v1/crawler/status
```

**Response:**

```json
{
  "success": true,
  "data": {
    "crawler_running": true,
    "crawler_id": "crawler_12345",
    "start_time": "2025-07-03T10:00:00Z",
    "current_source": "twitter",
    "items_collected": 450,
    "progress_percent": 45,
    "estimated_completion": "2025-07-03T10:30:00Z",
    "sources": {
      "twitter": {
        "status": "running",
        "items_collected": 300,
        "last_item_time": "2025-07-03T10:15:00Z"
      },
      "reddit": {
        "status": "pending",
        "items_collected": 0,
        "last_item_time": null
      }
    }
  },
  "metadata": {
    "request_id": "req_12349",
    "response_time_ms": 20
  }
}
```

#### GET /crawler/logs

Get crawler logs.

**Request:**

```bash
curl -H "X-API-Key: your_api_key" \
     "https://api.farmchecker.xyz/v1/crawler/logs?limit=100&level=INFO"
```

**Query Parameters:**

- `limit` (optional): Number of log entries to return (default: 50, max: 1000)
- `level` (optional): Log level filter (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `start_time` (optional): Start time for log filtering (ISO 8601 format)
- `end_time` (optional): End time for log filtering (ISO 8601 format)

**Response:**

```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "timestamp": "2025-07-03T10:15:00Z",
        "level": "INFO",
        "message": "Crawled 50 tweets from Twitter",
        "source": "twitter",
        "items_collected": 50
      },
      {
        "timestamp": "2025-07-03T10:14:00Z",
        "level": "INFO",
        "message": "Crawled 45 tweets from Twitter",
        "source": "twitter",
        "items_collected": 45
      }
    ],
    "total_count": 150,
    "has_more": true
  },
  "metadata": {
    "request_id": "req_12350",
    "response_time_ms": 30
  }
}
```

### Data Access

#### GET /data/tweets

Get tweets from the database.

**Request:**

```bash
curl -H "X-API-Key: your_api_key" \
     "https://api.farmchecker.xyz/v1/data/tweets?limit=50&source=twitter"
```

**Query Parameters:**

- `limit` (optional): Number of tweets to return (default: 20, max: 1000)
- `offset` (optional): Number of tweets to skip (default: 0)
- `source` (optional): Filter by source (twitter, reddit, telegram)
- `user` (optional): Filter by user
- `start_date` (optional): Start date for filtering (ISO 8601 format)
- `end_date` (optional): End date for filtering (ISO 8601 format)
- `classification` (optional): Filter by classification
- `min_engagement_score` (optional): Minimum engagement score
- `sort_by` (optional): Sort field (timestamp, engagement_score, viral_score)
- `sort_order` (optional): Sort order (asc, desc)

**Response:**

```json
{
  "success": true,
  "data": {
    "tweets": [
      {
        "id": "1234567890",
        "text": "This is a sample tweet about crypto",
        "user": "crypto_user",
        "timestamp": "2025-07-03T10:00:00Z",
        "likes": 150,
        "retweets": 25,
        "replies": 10,
        "source": "twitter",
        "classification": "crypto_news",
        "engagement_score": 0.85,
        "viral_score": 0.72,
        "cluster_id": "cluster_123"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 50,
      "total": 1250,
      "pages": 25,
      "has_next": true,
      "has_prev": false
    }
  },
  "metadata": {
    "request_id": "req_12351",
    "response_time_ms": 45
  }
}
```

#### GET /data/tweets/{id}

Get a specific tweet by ID.

**Request:**

```bash
curl -H "X-API-Key: your_api_key" \
     https://api.farmchecker.xyz/v1/data/tweets/1234567890
```

**Response:**

```json
{
  "success": true,
  "data": {
    "id": "1234567890",
    "text": "This is a sample tweet about crypto",
    "user": "crypto_user",
    "timestamp": "2025-07-03T10:00:00Z",
    "likes": 150,
    "retweets": 25,
    "replies": 10,
    "source": "twitter",
    "classification": "crypto_news",
    "engagement_score": 0.85,
    "viral_score": 0.72,
    "cluster_id": "cluster_123",
    "metadata": {
      "hashtags": ["#crypto", "#bitcoin"],
      "mentions": ["@elonmusk"],
      "urls": ["https://example.com"]
    }
  },
  "metadata": {
    "request_id": "req_12352",
    "response_time_ms": 15
  }
}
```

#### POST /data/tweets

Create a new tweet record.

**Request:**

```bash
curl -X POST \
     -H "X-API-Key: your_api_key" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "New tweet content",
       "user": "new_user",
       "source": "twitter"
     }' \
     https://api.farmchecker.xyz/v1/data/tweets
```

**Request Body:**

```json
{
  "text": "New tweet content",
  "user": "new_user",
  "source": "twitter",
  "likes": 0,
  "retweets": 0,
  "replies": 0,
  "metadata": {
    "hashtags": ["#test"],
    "mentions": [],
    "urls": []
  }
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "id": "1234567891",
    "text": "New tweet content",
    "user": "new_user",
    "timestamp": "2025-07-03T10:30:00Z",
    "likes": 0,
    "retweets": 0,
    "replies": 0,
    "source": "twitter",
    "classification": null,
    "engagement_score": null,
    "viral_score": null,
    "cluster_id": null
  },
  "metadata": {
    "request_id": "req_12353",
    "response_time_ms": 25
  }
}
```

#### DELETE /data/tweets/{id}

Delete a tweet by ID.

**Request:**

```bash
curl -X DELETE \
     -H "X-API-Key: your_api_key" \
     https://api.farmchecker.xyz/v1/data/tweets/1234567890
```

**Response:**

```json
{
  "success": true,
  "data": {
    "message": "Tweet deleted successfully",
    "deleted_id": "1234567890"
  },
  "metadata": {
    "request_id": "req_12354",
    "response_time_ms": 20
  }
}
```

### Digest Management

#### POST /digest/generate

Generate a new digest.

**Request:**

```bash
curl -X POST \
     -H "X-API-Key: your_api_key" \
     -H "Content-Type: application/json" \
     -d '{"date": "2025-07-03", "sources": ["twitter", "reddit"], "format": "json"}' \
     https://api.farmchecker.xyz/v1/digest/generate
```

**Request Body:**

```json
{
  "date": "2025-07-03",
  "sources": ["twitter", "reddit"],
  "format": "json",
  "options": {
    "max_items": 100,
    "min_engagement_score": 0.5,
    "include_analytics": true
  }
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "digest_id": "digest_12345",
    "date": "2025-07-03",
    "sources": ["twitter", "reddit"],
    "format": "json",
    "content": {
      "summary": "Daily crypto digest for 2025-07-03",
      "sections": [
        {
          "title": "Crypto News",
          "items": [
            {
              "id": "1234567890",
              "text": "Bitcoin reaches new all-time high",
              "user": "crypto_user",
              "source": "twitter",
              "engagement_score": 0.95
            }
          ]
        }
      ],
      "analytics": {
        "total_items": 85,
        "sources_breakdown": {
          "twitter": 60,
          "reddit": 25
        },
        "engagement_summary": {
          "avg_engagement_score": 0.72,
          "top_classification": "crypto_news"
        }
      }
    },
    "generated_at": "2025-07-03T11:00:00Z",
    "generation_time_seconds": 45
  },
  "metadata": {
    "request_id": "req_12355",
    "response_time_ms": 47000
  }
}
```

#### GET /digest/{date}

Get digest by date.

**Request:**

```bash
curl -H "X-API-Key: your_api_key" \
     https://api.farmchecker.xyz/v1/digest/2025-07-03
```

**Response:**

```json
{
  "success": true,
  "data": {
    "digest_id": "digest_12345",
    "date": "2025-07-03",
    "sources": ["twitter", "reddit"],
    "format": "json",
    "content": {
      "summary": "Daily crypto digest for 2025-07-03",
      "sections": [
        {
          "title": "Crypto News",
          "items": [
            {
              "id": "1234567890",
              "text": "Bitcoin reaches new all-time high",
              "user": "crypto_user",
              "source": "twitter",
              "engagement_score": 0.95
            }
          ]
        }
      ]
    },
    "generated_at": "2025-07-03T11:00:00Z"
  },
  "metadata": {
    "request_id": "req_12356",
    "response_time_ms": 25
  }
}
```

#### GET /digest/list

List available digests.

**Request:**

```bash
curl -H "X-API-Key: your_api_key" \
     "https://api.farmchecker.xyz/v1/digest/list?limit=20&start_date=2025-07-01"
```

**Query Parameters:**

- `limit` (optional): Number of digests to return (default: 20, max: 100)
- `offset` (optional): Number of digests to skip (default: 0)
- `start_date` (optional): Start date for filtering (ISO 8601 format)
- `end_date` (optional): End date for filtering (ISO 8601 format)
- `sources` (optional): Filter by sources (comma-separated)

**Response:**

```json
{
  "success": true,
  "data": {
    "digests": [
      {
        "digest_id": "digest_12345",
        "date": "2025-07-03",
        "sources": ["twitter", "reddit"],
        "content_count": 85,
        "generated_at": "2025-07-03T11:00:00Z",
        "generation_time_seconds": 45
      },
      {
        "digest_id": "digest_12344",
        "date": "2025-07-02",
        "sources": ["twitter", "reddit"],
        "content_count": 92,
        "generated_at": "2025-07-02T11:00:00Z",
        "generation_time_seconds": 52
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 150,
      "pages": 8,
      "has_next": true,
      "has_prev": false
    }
  },
  "metadata": {
    "request_id": "req_12357",
    "response_time_ms": 30
  }
}
```

#### DELETE /digest/{id}

Delete a digest by ID.

**Request:**

```bash
curl -X DELETE \
     -H "X-API-Key: your_api_key" \
     https://api.farmchecker.xyz/v1/digest/digest_12345
```

**Response:**

```json
{
  "success": true,
  "data": {
    "message": "Digest deleted successfully",
    "deleted_id": "digest_12345"
  },
  "metadata": {
    "request_id": "req_12358",
    "response_time_ms": 20
  }
}
```

### Analytics

#### GET /analytics/metrics

Get platform metrics.

**Request:**

```bash
curl -H "X-API-Key: your_api_key" \
     "https://api.farmchecker.xyz/v1/analytics/metrics?period=7d"
```

**Query Parameters:**

- `period` (optional): Time period (1d, 7d, 30d, 90d, 1y)
- `start_date` (optional): Start date (ISO 8601 format)
- `end_date` (optional): End date (ISO 8601 format)

**Response:**

```json
{
  "success": true,
  "data": {
    "period": "7d",
    "start_date": "2025-06-26",
    "end_date": "2025-07-03",
    "metrics": {
      "total_tweets": 12500,
      "total_digests": 7,
      "avg_engagement_score": 0.72,
      "top_sources": {
        "twitter": 8500,
        "reddit": 3200,
        "telegram": 800
      },
      "top_classifications": {
        "crypto_news": 4500,
        "market_analysis": 3200,
        "trading_signals": 2800,
        "project_updates": 1200,
        "community_discussion": 800
      },
      "daily_breakdown": [
        {
          "date": "2025-07-03",
          "tweets": 1800,
          "digests": 1,
          "avg_engagement": 0.75
        }
      ]
    }
  },
  "metadata": {
    "request_id": "req_12359",
    "response_time_ms": 40
  }
}
```

#### GET /analytics/trends

Get trending topics and patterns.

**Request:**

```bash
curl -H "X-API-Key: your_api_key" \
     "https://api.farmchecker.xyz/v1/analytics/trends?period=7d&limit=10"
```

**Query Parameters:**

- `period` (optional): Time period (1d, 7d, 30d, 90d)
- `limit` (optional): Number of trends to return (default: 10, max: 50)
- `type` (optional): Trend type (hashtags, mentions, topics)

**Response:**

```json
{
  "success": true,
  "data": {
    "period": "7d",
    "trends": {
      "hashtags": [
        {
          "hashtag": "#bitcoin",
          "count": 1250,
          "growth_percent": 15.5,
          "engagement_score": 0.85
        },
        {
          "hashtag": "#ethereum",
          "count": 980,
          "growth_percent": 8.2,
          "engagement_score": 0.78
        }
      ],
      "mentions": [
        {
          "mention": "@elonmusk",
          "count": 450,
          "growth_percent": 25.0,
          "engagement_score": 0.92
        }
      ],
      "topics": [
        {
          "topic": "DeFi protocols",
          "count": 320,
          "growth_percent": 12.5,
          "engagement_score": 0.81
        }
      ]
    }
  },
  "metadata": {
    "request_id": "req_12360",
    "response_time_ms": 35
  }
}
```

#### GET /analytics/insights

Get AI-generated insights from the data.

**Request:**

```bash
curl -H "X-API-Key: your_api_key" \
     "https://api.farmchecker.xyz/v1/analytics/insights?period=7d"
```

**Response:**

```json
{
  "success": true,
  "data": {
    "period": "7d",
    "insights": [
      {
        "type": "trending_topic",
        "title": "Bitcoin ETF Approval Hype",
        "description": "Bitcoin ETF approval discussions increased by 45% this week",
        "confidence": 0.92,
        "supporting_data": {
          "mention_count": 1250,
          "engagement_increase": 0.25
        }
      },
      {
        "type": "sentiment_shift",
        "title": "Positive Sentiment in DeFi",
        "description": "DeFi-related content shows 30% increase in positive sentiment",
        "confidence": 0.88,
        "supporting_data": {
          "sentiment_score": 0.75,
          "previous_score": 0.58
        }
      }
    ]
  },
  "metadata": {
    "request_id": "req_12361",
    "response_time_ms": 120
  }
}
```

## Request/Response Formats

### Standard Request Format

All requests should include:

- `X-API-Key` header for authentication
- `Content-Type: application/json` for POST/PUT requests
- JSON body for POST/PUT requests

### Standard Response Format

All responses follow this structure:

```json
{
  "success": true,
  "data": {
    // Response data
  },
  "metadata": {
    "timestamp": "2025-07-03T10:00:00Z",
    "version": "2.0.0",
    "request_id": "req_12345",
    "response_time_ms": 25
  },
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "date",
      "issue": "Date format is invalid"
    }
  },
  "metadata": {
    "timestamp": "2025-07-03T10:00:00Z",
    "version": "2.0.0",
    "request_id": "req_12345",
    "response_time_ms": 15
  }
}
```

## Error Handling

### HTTP Status Codes

| Code | Description           |
| ---- | --------------------- |
| 200  | Success               |
| 201  | Created               |
| 400  | Bad Request           |
| 401  | Unauthorized          |
| 403  | Forbidden             |
| 404  | Not Found             |
| 429  | Rate Limited          |
| 500  | Internal Server Error |

### Error Codes

| Code                   | Description                     |
| ---------------------- | ------------------------------- |
| `VALIDATION_ERROR`     | Input validation failed         |
| `AUTHENTICATION_ERROR` | Invalid API key                 |
| `AUTHORIZATION_ERROR`  | Insufficient permissions        |
| `RATE_LIMIT_EXCEEDED`  | Rate limit exceeded             |
| `RESOURCE_NOT_FOUND`   | Requested resource not found    |
| `INTERNAL_ERROR`       | Internal server error           |
| `SERVICE_UNAVAILABLE`  | Service temporarily unavailable |

### Error Handling Examples

```python
import requests

try:
    response = requests.get(
        "https://api.farmchecker.xyz/v1/health",
        headers={"X-API-Key": "your_api_key"}
    )

    if response.status_code == 200:
        data = response.json()
        print("Success:", data["data"])
    elif response.status_code == 401:
        print("Authentication failed")
    elif response.status_code == 429:
        print("Rate limit exceeded")
    else:
        error_data = response.json()
        print("Error:", error_data["error"]["message"])

except requests.exceptions.RequestException as e:
    print("Request failed:", e)
```

## Rate Limiting

### Rate Limits

| Endpoint          | Limit         | Window   |
| ----------------- | ------------- | -------- |
| Health checks     | 1000 requests | 1 minute |
| Data retrieval    | 500 requests  | 1 minute |
| Digest generation | 10 requests   | 1 hour   |
| Crawler control   | 100 requests  | 1 minute |

### Rate Limit Headers

Response headers include rate limit information:

```
X-RateLimit-Limit: 500
X-RateLimit-Remaining: 450
X-RateLimit-Reset: 1640995200
```

### Rate Limit Handling

```python
import requests
import time

def make_request_with_retry(url, headers):
    max_retries = 3
    retry_delay = 60  # seconds

    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
            wait_time = max(reset_time - time.time(), retry_delay)
            print(f"Rate limited. Waiting {wait_time} seconds...")
            time.sleep(wait_time)
        else:
            raise Exception(f"Request failed: {response.status_code}")

    raise Exception("Max retries exceeded")
```

## Examples

### Python SDK Example

```python
from degen_digest_api import DegenDigestAPI

# Initialize client
api = DegenDigestAPI(api_key="your_api_key")

# Check health
health = api.health.check()
print(f"API Status: {health['status']}")

# Start crawler
crawler = api.crawler.start(sources=["twitter", "reddit"])
print(f"Crawler ID: {crawler['crawler_id']}")

# Get tweets
tweets = api.data.get_tweets(limit=50, source="twitter")
for tweet in tweets['tweets']:
    print(f"Tweet: {tweet['text'][:100]}...")

# Generate digest
digest = api.digest.generate(
    date="2025-07-03",
    sources=["twitter", "reddit"],
    format="json"
)
print(f"Digest generated: {digest['digest_id']}")

# Get analytics
metrics = api.analytics.get_metrics(period="7d")
print(f"Total tweets: {metrics['total_tweets']}")
```

### JavaScript Example

```javascript
const DegenDigestAPI = require("degen-digest-api");

// Initialize client
const api = new DegenDigestAPI("your_api_key");

// Check health
api.health
  .check()
  .then((health) => {
    console.log(`API Status: ${health.status}`);
  })
  .catch((error) => {
    console.error("Error:", error.message);
  });

// Start crawler
api.crawler
  .start({ sources: ["twitter", "reddit"] })
  .then((crawler) => {
    console.log(`Crawler ID: ${crawler.crawler_id}`);
  })
  .catch((error) => {
    console.error("Error:", error.message);
  });

// Get tweets
api.data
  .getTweets({ limit: 50, source: "twitter" })
  .then((response) => {
    response.tweets.forEach((tweet) => {
      console.log(`Tweet: ${tweet.text.substring(0, 100)}...`);
    });
  })
  .catch((error) => {
    console.error("Error:", error.message);
  });
```

### cURL Examples

```bash
# Check API health
curl -H "X-API-Key: your_api_key" \
     https://api.farmchecker.xyz/v1/health

# Start crawler
curl -X POST \
     -H "X-API-Key: your_api_key" \
     -H "Content-Type: application/json" \
     -d '{"sources": ["twitter", "reddit"]}' \
     https://api.farmchecker.xyz/v1/crawler/start

# Get tweets
curl -H "X-API-Key: your_api_key" \
     "https://api.farmchecker.xyz/v1/data/tweets?limit=50&source=twitter"

# Generate digest
curl -X POST \
     -H "X-API-Key: your_api_key" \
     -H "Content-Type: application/json" \
     -d '{"date": "2025-07-03", "sources": ["twitter"], "format": "json"}' \
     https://api.farmchecker.xyz/v1/digest/generate
```

## SDKs

### Python SDK

```bash
pip install degen-digest-api
```

```python
from degen_digest_api import DegenDigestAPI

api = DegenDigestAPI(api_key="your_api_key")

# All API methods are available
health = api.health.check()
tweets = api.data.get_tweets()
digest = api.digest.generate()
```

### JavaScript SDK

```bash
npm install degen-digest-api
```

```javascript
const DegenDigestAPI = require("degen-digest-api");

const api = new DegenDigestAPI("your_api_key");

// All API methods are available
api.health.check().then((health) => console.log(health));
```

### Go SDK

```bash
go get github.com/degen-digest/api-go
```

```go
package main

import (
    "fmt"
    "github.com/degen-digest/api-go"
)

func main() {
    client := api.NewClient("your_api_key")

    health, err := client.Health.Check()
    if err != nil {
        fmt.Printf("Error: %v\n", err)
        return
    }

    fmt.Printf("Status: %s\n", health.Status)
}
```

This comprehensive API documentation provides all the information needed to integrate with the Degen Digest platform programmatically.
