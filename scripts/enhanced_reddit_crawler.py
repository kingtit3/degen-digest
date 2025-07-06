#!/usr/bin/env python3
"""
Enhanced Reddit Crawler with API Access
Uses Reddit API with developer app credentials for better data access
Deployed as Cloud Run service
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from google.cloud import storage

    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    print("Warning: Google Cloud Storage not available")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedRedditCrawler:
    def __init__(self):
        self.cloud_only = True
        self.gcs_bucket = os.getenv("BUCKET_NAME", "degen-digest-data")
        self.project_id = os.getenv("PROJECT_ID", "lucky-union-463615-t3")

        # Reddit API credentials from environment variables
        self.reddit_config = {
            "client_id": os.getenv("REDDIT_CLIENT_ID", "doW2qicqXIeszi2nTfUfQg"),
            "client_secret": os.getenv(
                "REDDIT_CLIENT_SECRET", "cGyFrR80N6bhJb1RYdhj3lIbT9Py9A"
            ),
            "user_agent": "DegenDigest/1.0 (by /u/degen_digest_bot)",
            "username": "degen_digest_bot",  # Optional: if you have a bot account
            "password": "",  # Optional: if you have a bot account
        }

        # Target subreddits for crypto content
        self.subreddits = [
            "CryptoCurrency",
            "Solana",
            "Bitcoin",
            "Ethereum",
            "defi",
            "altcoin",
            "CryptoMoonShots",
            "CryptoMarkets",
            "binance",
            "CoinBase",
        ]

    def get_gcs_client(self):
        """Get GCS client if available"""
        if not GCS_AVAILABLE:
            return None, None

        try:
            client = storage.Client(project=self.project_id)
            bucket = client.bucket(self.gcs_bucket)
            return client, bucket
        except Exception as e:
            logger.error(f"GCS connection failed: {e}")
            return None, None

    def upload_to_gcs(self, data: dict[str, Any]):
        """Upload data to GCS"""
        client, bucket = self.get_gcs_client()
        if not bucket:
            return False

        try:
            # Create timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reddit_data/reddit_api_{timestamp}.json"

            # Upload data
            blob = bucket.blob(filename)
            blob.upload_from_string(
                json.dumps(data, indent=2, ensure_ascii=False),
                content_type="application/json",
            )

            # Also upload as latest
            latest_filename = "reddit_data/reddit_api_latest.json"
            latest_blob = bucket.blob(latest_filename)
            latest_blob.upload_from_string(
                json.dumps(data, indent=2, ensure_ascii=False),
                content_type="application/json",
            )

            logger.info(f"✅ Uploaded Reddit API data to GCS: {filename}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to upload Reddit API data to GCS: {e}")
            return False

    def get_reddit_access_token(self) -> str:
        """Get Reddit API access token"""
        try:
            import requests

            auth_url = "https://www.reddit.com/api/v1/access_token"
            auth_data = {"grant_type": "client_credentials"}

            auth_response = requests.post(
                auth_url,
                data=auth_data,
                auth=(
                    self.reddit_config["client_id"],
                    self.reddit_config["client_secret"],
                ),
                headers={"User-Agent": self.reddit_config["user_agent"]},
                timeout=10,
            )

            if auth_response.status_code == 200:
                token_data = auth_response.json()
                return token_data.get("access_token")
            else:
                logger.error(f"Failed to get access token: {auth_response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error getting access token: {e}")
            return None

    async def fetch_subreddit_posts(
        self, subreddit: str, access_token: str, limit: int = 25
    ) -> list[dict[str, Any]]:
        """Fetch posts from a subreddit using Reddit API"""
        try:
            import requests

            # Reddit API endpoint for subreddit posts
            url = f"https://oauth.reddit.com/r/{subreddit}/hot"

            headers = {
                "Authorization": f"Bearer {access_token}",
                "User-Agent": self.reddit_config["user_agent"],
            }

            params = {
                "limit": limit,
                "t": "day",  # Time filter: day, week, month, year, all
            }

            response = requests.get(url, headers=headers, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()
                posts = []

                for post in data["data"]["children"]:
                    post_data = post["data"]

                    # Skip stickied posts and ads
                    if post_data.get("stickied") or post_data.get("promoted"):
                        continue

                    # Calculate engagement score
                    upvotes = post_data.get("ups", 0)
                    downvotes = post_data.get("downs", 0)
                    comments = post_data.get("num_comments", 0)
                    engagement_score = (upvotes - downvotes) + (comments * 2)

                    # Extract relevant data
                    post_info = {
                        "id": post_data.get("id"),
                        "title": post_data.get("title"),
                        "content": post_data.get("selftext", ""),
                        "author": post_data.get("author"),
                        "subreddit": subreddit,
                        "url": f"https://reddit.com{post_data.get('permalink')}",
                        "external_url": post_data.get("url"),
                        "score": post_data.get("score", 0),
                        "upvotes": upvotes,
                        "downvotes": downvotes,
                        "comments": comments,
                        "engagement_score": engagement_score,
                        "created_utc": post_data.get("created_utc"),
                        "published_at": datetime.fromtimestamp(
                            post_data.get("created_utc", 0), UTC
                        ).isoformat(),
                        "is_video": post_data.get("is_video", False),
                        "is_gallery": post_data.get("is_gallery", False),
                        "domain": post_data.get("domain"),
                        "over_18": post_data.get("over_18", False),
                        "spoiler": post_data.get("spoiler", False),
                        "locked": post_data.get("locked", False),
                        "archived": post_data.get("archived", False),
                        "stickied": post_data.get("stickied", False),
                        "gilded": post_data.get("gilded", 0),
                        "upvote_ratio": post_data.get("upvote_ratio", 0),
                        "total_awards_received": post_data.get(
                            "total_awards_received", 0
                        ),
                        "all_awardings": post_data.get("all_awardings", []),
                        "media": post_data.get("media"),
                        "preview": post_data.get("preview"),
                        "thumbnail": post_data.get("thumbnail"),
                        "raw_data": post_data,  # Keep original data for flexibility
                    }

                    posts.append(post_info)

                logger.info(f"  ✅ r/{subreddit}: {len(posts)} posts")
                return posts

            else:
                logger.warning(
                    f"  ⚠️ Failed to fetch r/{subreddit}: {response.status_code}"
                )
                return []

        except Exception as e:
            logger.error(f"  ❌ Error fetching r/{subreddit}: {e}")
            return []

    async def crawl_reddit_api(self) -> dict[str, Any]:
        """Crawl Reddit using official API"""
        try:
            logger.info("🔄 Starting Reddit API crawl...")

            # Get access token
            access_token = self.get_reddit_access_token()
            if not access_token:
                logger.error("❌ Failed to get Reddit access token")
                return {"error": "Failed to authenticate with Reddit API"}

            logger.info("✅ Got Reddit access token")

            all_posts = []
            total_engagement = 0

            # Fetch posts from each subreddit
            for subreddit in self.subreddits:
                try:
                    # Add delay to respect rate limits
                    await asyncio.sleep(2)

                    posts = await self.fetch_subreddit_posts(
                        subreddit, access_token, limit=25
                    )
                    all_posts.extend(posts)

                    # Calculate total engagement
                    subreddit_engagement = sum(
                        post.get("engagement_score", 0) for post in posts
                    )
                    total_engagement += subreddit_engagement

                    logger.info(
                        f"  📊 r/{subreddit}: {len(posts)} posts, {subreddit_engagement} engagement"
                    )

                except Exception as e:
                    logger.error(f"  ❌ Error processing r/{subreddit}: {e}")
                    continue

            # Sort posts by engagement score
            all_posts.sort(key=lambda x: x.get("engagement_score", 0), reverse=True)

            # Prepare response data
            response_data = {
                "metadata": {
                    "source": "reddit_api",
                    "crawled_at": datetime.now(UTC).isoformat(),
                    "subreddits": self.subreddits,
                    "total_posts": len(all_posts),
                    "total_engagement": total_engagement,
                    "average_engagement": total_engagement / len(all_posts)
                    if all_posts
                    else 0,
                    "api_used": True,
                    "access_token_obtained": True,
                },
                "data": all_posts,
                "top_posts": all_posts[:10],  # Top 10 by engagement
                "subreddit_stats": {},
            }

            # Calculate subreddit statistics
            subreddit_stats = {}
            for post in all_posts:
                subreddit = post.get("subreddit")
                if subreddit not in subreddit_stats:
                    subreddit_stats[subreddit] = {
                        "post_count": 0,
                        "total_engagement": 0,
                        "avg_engagement": 0,
                    }

                subreddit_stats[subreddit]["post_count"] += 1
                subreddit_stats[subreddit]["total_engagement"] += post.get(
                    "engagement_score", 0
                )

            # Calculate averages
            for subreddit, stats in subreddit_stats.items():
                stats["avg_engagement"] = (
                    stats["total_engagement"] / stats["post_count"]
                )

            response_data["subreddit_stats"] = subreddit_stats

            logger.info(
                f"✅ Reddit API crawl completed: {len(all_posts)} posts, {total_engagement} total engagement"
            )
            return response_data

        except Exception as e:
            logger.error(f"❌ Reddit API crawl failed: {e}")
            return {"error": str(e)}

    async def run_single_crawl(self):
        """Run a single Reddit crawl"""
        try:
            # Crawl Reddit
            data = await self.crawl_reddit_api()

            if "error" in data:
                logger.error(f"❌ Crawl failed: {data['error']}")
                return False

            # Upload to GCS
            if self.upload_to_gcs(data):
                logger.info("✅ Reddit crawl and upload completed successfully")
                return True
            else:
                logger.error("❌ Failed to upload data to GCS")
                return False

        except Exception as e:
            logger.error(f"❌ Single crawl failed: {e}")
            return False


# Cloud Run service functionality
async def handle_request():
    """Handle Cloud Run request"""
    crawler = EnhancedRedditCrawler()
    success = await crawler.run_single_crawl()

    if success:
        return {
            "status": "success",
            "message": "Reddit crawl completed successfully",
            "timestamp": datetime.now(UTC).isoformat(),
        }
    else:
        return {
            "status": "error",
            "message": "Reddit crawl failed",
            "timestamp": datetime.now(UTC).isoformat(),
        }


async def main():
    """Main function - handles both direct execution and Cloud Run"""
    if os.getenv("PORT"):
        # Running as Cloud Run service
        import uvicorn
        from fastapi import FastAPI

        app = FastAPI(title="Enhanced Reddit API Crawler")

        @app.get("/")
        async def root():
            return {"message": "Enhanced Reddit API Crawler", "status": "running"}

        @app.get("/health")
        async def health():
            return {"status": "healthy", "timestamp": datetime.now(UTC).isoformat()}

        @app.post("/crawl")
        async def crawl():
            return await handle_request()

        @app.get("/crawl")
        async def crawl_get():
            return await handle_request()

        port = int(os.getenv("PORT", 8080))
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        # Running directly
        crawler = EnhancedRedditCrawler()
        await crawler.run_single_crawl()


if __name__ == "__main__":
    asyncio.run(main())
