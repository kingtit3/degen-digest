import feedparser
import json
import logging
from pathlib import Path
from typing import List, Dict
from utils.logger import setup_logging
from storage.db import add_reddit_posts
import asyncio
import httpx

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
setup_logging()

REDDIT_FEEDS = [
    "https://www.reddit.com/r/CryptoCurrency/new/.rss",
    "https://www.reddit.com/r/shitcoin/new/.rss",
    "https://www.reddit.com/r/Solana/new/.rss",
]


async def parse_reddit_feed_async(url: str, keyword_filters: List[str]) -> List[Dict]:
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
            entries.append({
                "title": title,
                "link": item.get("link"),
                "published": item.get("published"),
                "summary": summary,
            })
    return entries


def scrape_reddit(keyword_filters: List[str]):
    all_entries = []
    async def worker(url):
        logger.info("Scraping %s", url)
        return await parse_reddit_feed_async(url, keyword_filters)

    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(asyncio.gather(*[worker(u) for u in REDDIT_FEEDS]))
    for entries in results:
        all_entries.extend(entries)
    # Sort by published date (string) but there might be inconsistent format; keep as is
    return all_entries[:20]


def main():
    keywords = json.loads(Path("config/keywords.json").read_text())
    items = scrape_reddit(keywords["reddit"])
    add_reddit_posts(items)
    out_path = Path("output/reddit_raw.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(items, indent=2))
    logger.info("Saved %d Reddit items", len(items))


if __name__ == "__main__":
    main() 