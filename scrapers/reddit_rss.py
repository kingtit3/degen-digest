import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json
import logging
from pathlib import Path

import feedparser
import httpx
from dateutil import parser as dateparser

from storage.db import add_reddit_posts
from utils.advanced_logging import get_logger
from utils.logger import setup_logging

logger = get_logger(__name__)
logging.basicConfig(level=logging.INFO)
setup_logging()

REDDIT_FEEDS = [
    "https://www.reddit.com/r/CryptoCurrency/new/.rss",
    "https://www.reddit.com/r/shitcoin/new/.rss",
    "https://www.reddit.com/r/Solana/new/.rss",
    # Added mainstream and niche crypto subs (2025-06-29)
    "https://www.reddit.com/r/Bitcoin/new/.rss",
    "https://www.reddit.com/r/Ethereum/new/.rss",
    "https://www.reddit.com/r/CryptoMarkets/new/.rss",
    "https://www.reddit.com/r/defi/new/.rss",
    "https://www.reddit.com/r/NFT/new/.rss",
    # High-volume crypto subs
    "https://www.reddit.com/r/cryptostreetbets/new/.rss",
    "https://www.reddit.com/r/altcoin/new/.rss",
    "https://www.reddit.com/r/cryptomoonshots/new/.rss",
    "https://www.reddit.com/r/cryptonews/new/.rss",
    "https://www.reddit.com/r/ethtrader/new/.rss",
    "https://www.reddit.com/r/cryptocurrencymemes/new/.rss",
    "https://www.reddit.com/r/cryptotrading/new/.rss",
    "https://www.reddit.com/r/cryptosignals/new/.rss",
    "https://www.reddit.com/r/cryptomemes/new/.rss",
]


async def parse_reddit_feed_async(url: str, keyword_filters: list[str]) -> list[dict]:
    """Fetch RSS feed and filter entries by keywords (async)."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=30)
            resp.raise_for_status()
        feed = feedparser.parse(resp.content)
        entries = []
        for item in feed.entries:
            title = item.get("title", "")
            summary = item.get("summary", "")
            content = f"{title} {summary}".lower()
            if any(k.lower() in content for k in keyword_filters):
                # Parse published date to datetime
                published_str = item.get("published")
                published_dt = None
                if published_str:
                    try:
                        published_dt = dateparser.parse(published_str)
                        if published_dt.tzinfo is None:
                            from datetime import timezone

                            published_dt = published_dt.replace(tzinfo=timezone.utc)
                        else:
                            published_dt = published_dt.astimezone(dateparser.tz.UTC)
                    except Exception:
                        published_dt = None
                entries.append(
                    {
                        "title": title,
                        "link": item.get("link"),
                        "published": published_dt,
                        "summary": summary,
                        "subreddit": url.split("/")[4] if "/r/" in url else None,
                    }
                )
        return entries
    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        return []


def scrape_reddit(keyword_filters: list[str]):
    """Scrape multiple Reddit RSS feeds concurrently and return filtered items."""
    all_entries = []

    async def worker(url):
        logger.info("scrape start", url=url)
        return await parse_reddit_feed_async(url, keyword_filters)

    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(
        asyncio.gather(*[worker(u) for u in REDDIT_FEEDS])
    )
    for entries in results:
        all_entries.extend(entries)
    # Sort by published date (string) but there might be inconsistent format; keep as is
    logger.info("scrape complete", total=len(all_entries))
    return all_entries[:20]


def main():
    keywords = json.loads(Path("config/keywords.json").read_text())
    items = scrape_reddit(keywords["reddit"])
    add_reddit_posts(items)
    out_path = Path("output/reddit_raw.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(items, indent=2))
    logger.info("reddit items saved", count=len(items))


if __name__ == "__main__":
    main()
