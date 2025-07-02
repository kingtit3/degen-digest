import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import hashlib
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

from storage.db import add_tweets
from utils.advanced_logging import get_logger
from utils.logger import setup_logging

load_dotenv()

APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
APIFY_TWEET_SCRAPER_ACTOR = (
    "kaitoeasyapi~twitter-x-data-tweet-scraper-pay-per-result-cheapest"
)

logger = get_logger(__name__)
logging.basicConfig(level=logging.INFO)
setup_logging()

# ------------------------------------------------------------
#   Simple cache to avoid paying for identical Apify runs
# ------------------------------------------------------------

CACHE_FILE = Path("output/apify_cache.json")


def _cache_key(
    accounts: list[str],
    search_terms: list[str],
    max_tweets: int,
    min_likes: int,
    min_retweets: int,
) -> str:
    """Return an md5 hash that uniquely represents the scraper parameters."""
    h = hashlib.md5()
    payload = json.dumps(
        {
            "accounts": sorted(accounts),
            "keywords": sorted(search_terms),
            "max": max_tweets,
            "likes": min_likes,
            "rts": min_retweets,
        },
        sort_keys=True,
    ).encode()
    h.update(payload)
    return h.hexdigest()


def _load_cache() -> dict:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text())
        except Exception:
            pass
    return {}


def _save_cache(cache: dict):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=2))


def run_tweet_scraper(
    accounts: list[str],
    search_terms: list[str],
    max_tweets: int = 200,
    min_likes: int = 50,
    min_retweets: int = 20,
) -> list[dict[str, Any]]:
    """Run Apify Twitter tweet scraper.

    Args:
        accounts (List[str]): Accounts to scrape.
        search_terms (List[str]): Additional free-text search terms.
        max_tweets (int): Maximum tweets to return.
        min_likes (int): Minimum likes filter.
        min_retweets (int): Minimum retweets filter.

    Returns:
        List[Dict[str, Any]]: List of tweet JSON objects.
    """
    if APIFY_API_TOKEN is None:
        raise ValueError("APIFY_API_TOKEN not set in environment.")

    input_payload = {
        "mode": "SCRAPE",
        "usernames": accounts,
        "searchTerms": search_terms,
        "tweetsDesired": max_tweets,
        "tweetFilters": {
            "minLikes": min_likes,
            "minRetweets": min_retweets,
            "includeRetweets": False,
            "includeReplies": False,
        },
        "includeMetrics": True,
        "addUserInfo": True,
    }

    logger.info("apify run start", accounts=len(accounts), keywords=len(search_terms))

    # --- cache check ------------------------------------------------------
    key = _cache_key(accounts, search_terms, max_tweets, min_likes, min_retweets)
    cache = _load_cache()
    cached_entry = cache.get(key)
    if cached_entry:
        ts = datetime.fromisoformat(cached_entry["timestamp"])
        if datetime.utcnow() - ts < timedelta(hours=2):  # still fresh
            dataset_id = cached_entry["dataset_id"]
            logger.info("Using cached Apify dataset", dataset_id=dataset_id)
            dataset_url = (
                f"https://api.apify.com/v2/datasets/{dataset_id}/items?format=json"
            )
            dataset_resp = httpx.get(
                dataset_url,
                headers={"Authorization": f"Bearer {APIFY_API_TOKEN}"},
                timeout=60,
            )
            dataset_resp.raise_for_status()
            tweets = dataset_resp.json()
            logger.info("tweets retrieved (cached)", count=len(tweets))
            add_tweets(tweets)
            return tweets

    # ---------------------------------------------------------------------

    # Create actor run (token in Authorization header)
    url = f"https://api.apify.com/v2/acts/{APIFY_TWEET_SCRAPER_ACTOR}/runs"
    headers = {
        "Authorization": f"Bearer {APIFY_API_TOKEN}",
        "Content-Type": "application/json",
    }
    response = httpx.post(url, json=input_payload, headers=headers, timeout=60)
    response.raise_for_status()
    run_info = response.json()
    run_id = run_info["data"]["id"]
    logger.info("apify run id", run_id=run_id)

    # Poll for finish
    status_url = f"https://api.apify.com/v2/actor-runs/{run_id}"
    while True:
        status_resp = httpx.get(status_url, headers=headers, timeout=30)
        status_resp.raise_for_status()
        status = status_resp.json()["data"]["status"]
        if status in {"SUCCEEDED", "FAILED", "TIMED-OUT", "ABORTED"}:
            break
        logger.debug("apify run poll", run_id=run_id, status=status)
        import time

        time.sleep(10)

    if status != "SUCCEEDED":
        raise RuntimeError(f"Apify run failed with status {status}")

    # Get dataset items
    dataset_id = status_resp.json()["data"]["defaultDatasetId"]

    # update cache
    cache[key] = {"dataset_id": dataset_id, "timestamp": datetime.utcnow().isoformat()}
    _save_cache(cache)

    dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?format=json"
    dataset_resp = httpx.get(dataset_url, headers=headers, timeout=60)
    dataset_resp.raise_for_status()
    tweets = dataset_resp.json()
    logger.info("tweets retrieved", count=len(tweets))

    add_tweets(tweets)

    return tweets


def main():
    import json
    from pathlib import Path

    influencers = json.loads(Path("config/influencers.json").read_text())
    keywords = json.loads(Path("config/keywords.json").read_text())

    tweets = run_tweet_scraper(
        accounts=influencers, search_terms=keywords["twitter_search"], max_tweets=200
    )
    out_path = Path("output/twitter_raw.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(tweets, indent=2))
    logger.info("raw tweets saved", path=str(out_path))


if __name__ == "__main__":
    main()
