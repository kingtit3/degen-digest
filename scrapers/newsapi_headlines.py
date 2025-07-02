import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import logging
from pathlib import Path

import requests
from dotenv import load_dotenv

from utils.advanced_logging import get_logger
from utils.logger import setup_logging

# DB insertion optional – only if table/model exists. Import guarded.
try:
    from storage.db import add_news_items  # type: ignore
except ImportError:
    add_news_items = None  # type: ignore

load_dotenv()

NEWSAPI_KEY = (
    os.getenv("NEWSAPI_KEY") or os.getenv("NEWSAPI_API_KEY") or os.getenv("NEWSAPI")
)

logger = get_logger(__name__)
logging.basicConfig(level=logging.INFO)
setup_logging()


API_URL = "https://newsapi.org/v2/everything"

# Query parameters tuned for crypto / markets coverage
PARAMS = {
    "q": "crypto OR bitcoin OR ethereum OR solana OR defi OR nft OR blockchain OR cryptocurrency OR altcoin OR token OR coin OR trading OR market",
    "language": "en",
    "pageSize": 100,
    "sortBy": "publishedAt",
    "from": "2025-06-29",  # Last 24 hours
}


def fetch_headlines() -> list[dict]:
    if not NEWSAPI_KEY:
        raise ValueError("NEWSAPI_KEY not set in environment (.env)")

    headers = {"X-Api-Key": NEWSAPI_KEY}
    logger.info("newsapi request", params=PARAMS)
    resp = requests.get(API_URL, headers=headers, params=PARAMS, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("status") != "ok":
        raise RuntimeError(f"NewsAPI error: {data}")

    items: list[dict] = []
    for art in data.get("articles", []):
        items.append(
            {
                "title": art.get("title"),
                "summary": art.get("description") or "",  # "summary" for downstream
                "published": art.get("publishedAt"),
                "link": art.get("url"),
                "source": art.get("source", {}).get("name"),
            }
        )
    logger.info("newsapi items", count=len(items))
    return items


def main():
    items = fetch_headlines()
    # optional DB integration if schema present
    if add_news_items:
        try:
            add_news_items(items)  # type: ignore
        except Exception:
            pass

    out_path = Path("output/newsapi_raw.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(items, indent=2))
    logger.info("newsapi raw saved", path=str(out_path))


if __name__ == "__main__":
    main()
