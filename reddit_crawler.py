#!/usr/bin/env python3
"""
Standalone Reddit Crawler Service
Deployed as a separate Cloud Run service for better isolation
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.append(str(Path(__file__).parent))

try:
    from google.cloud import storage

    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    print("Warning: Google Cloud Storage not available")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class RedditCrawler:
    def __init__(self):
        self.cloud_only = True
        self.gcs_bucket = "degen-digest-data"
        self.project_id = "lucky-union-463615-t3"

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
            filename = f"reddit_data/reddit_{timestamp}.json"

            # Upload data
            blob = bucket.blob(filename)
            blob.upload_from_string(
                json.dumps(data, indent=2, ensure_ascii=False),
                content_type="application/json",
            )

            # Also upload as latest
            latest_filename = "reddit_data/reddit_latest.json"
            latest_blob = bucket.blob(latest_filename)
            latest_blob.upload_from_string(
                json.dumps(data, indent=2, ensure_ascii=False),
                content_type="application/json",
            )

            logger.info(f"✅ Uploaded reddit data to GCS: {filename}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to upload reddit data to GCS: {e}")
            return False

    async def crawl_reddit(self) -> dict[str, Any]:
        """Crawl Reddit RSS feeds"""
        try:
            logger.info("🔄 Starting Reddit crawl...")

            import requests

            # Reddit RSS feeds
            feeds = [
                "https://www.reddit.com/r/CryptoCurrency/new/.rss",
                "https://www.reddit.com/r/Solana/new/.rss",
                "https://www.reddit.com/r/Bitcoin/new/.rss",
                "https://www.reddit.com/r/Ethereum/new/.rss",
            ]

            # Proper headers to avoid being blocked
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }

            all_posts = []

            for feed_url in feeds:
                try:
                    # Add delay between requests to be respectful
                    await asyncio.sleep(1)

                    response = requests.get(feed_url, headers=headers, timeout=15)
                    if response.status_code == 200:
                        # Parse XML properly using xml.etree
                        import xml.etree.ElementTree as ET

                        try:
                            # Parse the XML content
                            root = ET.fromstring(response.text)

                            # Find all entry elements (posts)
                            entries = root.findall(
                                ".//{http://www.w3.org/2005/Atom}entry"
                            )

                            posts = []
                            for entry in entries[:5]:  # Limit to 5 posts per subreddit
                                title_elem = entry.find(
                                    ".//{http://www.w3.org/2005/Atom}title"
                                )
                                link_elem = entry.find(
                                    ".//{http://www.w3.org/2005/Atom}link"
                                )
                                published_elem = entry.find(
                                    ".//{http://www.w3.org/2005/Atom}published"
                                )

                                if title_elem is not None and link_elem is not None:
                                    title = title_elem.text
                                    link = (
                                        link_elem.get("href")
                                        if link_elem.get("href")
                                        else link_elem.text
                                    )
                                    published = (
                                        published_elem.text
                                        if published_elem is not None
                                        else datetime.now(UTC).isoformat()
                                    )

                                    posts.append(
                                        {
                                            "title": title,
                                            "link": link,
                                            "subreddit": feed_url.split("/r/")[1].split(
                                                "/"
                                            )[0],
                                            "published": published,
                                        }
                                    )

                            all_posts.extend(posts)
                            logger.info(f"  ✅ {feed_url}: {len(posts)} posts")

                        except ET.ParseError as e:
                            logger.warning(
                                f"  ⚠️ Failed to parse XML from {feed_url}: {e}"
                            )
                            # Fallback to simple regex parsing
                            content = response.text
                            import re

                            titles = re.findall(r"<title>(.*?)</title>", content)
                            links = re.findall(r"<link>(.*?)</link>", content)

                            posts = []
                            for i, title in enumerate(titles):
                                if i < len(links) and "reddit.com/r/" in links[i]:
                                    posts.append(
                                        {
                                            "title": title,
                                            "link": links[i],
                                            "subreddit": feed_url.split("/r/")[1].split(
                                                "/"
                                            )[0],
                                            "published": datetime.now(UTC).isoformat(),
                                        }
                                    )

                            all_posts.extend(posts[:5])
                            logger.info(
                                f"  ✅ {feed_url}: {len(posts)} posts (regex fallback)"
                            )

                    else:
                        logger.warning(
                            f"  ⚠️ Failed to fetch {feed_url}: HTTP {response.status_code}"
                        )

                except Exception as e:
                    logger.warning(f"  ⚠️ Failed to fetch {feed_url}: {e}")

            data = {
                "posts": all_posts,
                "metadata": {
                    "source": "reddit",
                    "crawled_at": datetime.now(UTC).isoformat(),
                    "count": len(all_posts),
                    "status": "success",
                },
            }

            logger.info(f"✅ Reddit crawl completed: {len(all_posts)} posts")
            return data

        except Exception as e:
            logger.error(f"❌ Reddit crawl failed: {e}")
            return {
                "posts": [],
                "metadata": {
                    "source": "reddit",
                    "crawled_at": datetime.now(UTC).isoformat(),
                    "count": 0,
                    "status": "error",
                    "error": str(e),
                },
            }

    async def run_single_crawl(self):
        """Run a single Reddit crawl session"""
        logger.info("🔄 Running Reddit crawl session...")

        # Crawl Reddit
        reddit_data = await self.crawl_reddit()

        # Upload to GCS
        if self.upload_to_gcs(reddit_data):
            logger.info("✅ Reddit crawl session completed successfully")
        else:
            logger.error("❌ Failed to upload Reddit data")

        return reddit_data


async def main():
    """Main function for standalone Reddit crawler"""
    crawler = RedditCrawler()

    # Run single crawl
    result = await crawler.run_single_crawl()

    logger.info("📊 Crawl Summary:")
    logger.info(f"  - Reddit: {len(result['posts'])} posts")

    return result


if __name__ == "__main__":
    asyncio.run(main())
