import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from datetime import datetime, timezone
from pathlib import Path

import httpx

from storage.db import add_reddit_posts  # acts as generic saver (title/link fields).
from utils.advanced_logging import get_logger
from utils.logger import setup_logging

setup_logging()
logger = get_logger(__name__)

API_URL = "https://api.coingecko.com/api/v3/coins/markets"


def fetch_top_gainers(limit: int = 20) -> list[dict]:
    params = {
        "vs_currency": "usd",
        "order": "price_change_percentage_24h_desc",
        "per_page": limit,
        "page": 1,
        "price_change_percentage": "24h",
    }
    logger.info("coingecko request", limit=limit)
    resp = httpx.get(API_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    items = []
    for coin in data:
        pct = coin.get("price_change_percentage_24h")
        title = f"{coin['symbol'].upper()} +{pct:.1f}% in 24h"
        summary = f"{coin['name']} pumped {pct:.1f}% in the last 24h. Price now ${coin['current_price']:.4g}."
        items.append(
            {
                "title": title,
                "summary": summary,
                "link": f"https://www.coingecko.com/en/coins/{coin['id']}",
                "published": datetime.now(timezone.utc).isoformat(),
            }
        )
    return items


def main():
    items = fetch_top_gainers(20)

    # store to DB using RedditPost schema for now (id = link)
    try:
        add_reddit_posts([{**it, "subreddit": "coingecko"} for it in items])
    except Exception:
        pass

    out_path = Path("output/coingecko_raw.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(items, indent=2))
    logger.info("coingecko gainers saved", count=len(items))


if __name__ == "__main__":
    main()
