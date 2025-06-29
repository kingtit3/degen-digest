import os
from typing import List, Dict, Any
import logging
from utils.logger import setup_logging
from storage.db import add_tweets

import httpx
from dotenv import load_dotenv

load_dotenv()

APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
APIFY_TWEET_SCRAPER_ACTOR = "kaitoeasyapi~twitter-x-data-tweet-scraper-pay-per-result-cheapest"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
setup_logging()

def run_tweet_scraper(accounts: List[str], search_terms: List[str], max_tweets: int = 200,
                      min_likes: int = 50, min_retweets: int = 20) -> List[Dict[str, Any]]:
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
        "addUserInfo": False,
    }

    logger.info("Starting Apify run for %s accounts, %s keywords", len(accounts), len(search_terms))

    # Create actor run (token in Authorization header)
    url = f"https://api.apify.com/v2/acts/{APIFY_TWEET_SCRAPER_ACTOR}/runs"
    headers = {"Authorization": f"Bearer {APIFY_API_TOKEN}", "Content-Type": "application/json"}
    response = httpx.post(url, json=input_payload, headers=headers, timeout=60)
    response.raise_for_status()
    run_info = response.json()
    run_id = run_info["data"]["id"]
    logger.info("Apify run started with id %s", run_id)

    # Poll for finish
    status_url = f"https://api.apify.com/v2/actor-runs/{run_id}"
    while True:
        status_resp = httpx.get(status_url, headers=headers, timeout=30)
        status_resp.raise_for_status()
        status = status_resp.json()["data"]["status"]
        if status in {"SUCCEEDED", "FAILED", "TIMED-OUT", "ABORTED"}:
            break
        logger.debug("Run %s status %s. Waiting...", run_id, status)
        import time
        time.sleep(10)

    if status != "SUCCEEDED":
        raise RuntimeError(f"Apify run failed with status {status}")

    # Get dataset items
    dataset_id = status_resp.json()["data"]["defaultDatasetId"]
    dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?format=json"
    dataset_resp = httpx.get(dataset_url, headers=headers, timeout=60)
    dataset_resp.raise_for_status()
    tweets = dataset_resp.json()
    logger.info("Retrieved %d tweets", len(tweets))

    add_tweets(tweets)

    return tweets


def main():
    import json
    from pathlib import Path

    influencers = json.loads(Path("config/influencers.json").read_text())
    keywords = json.loads(Path("config/keywords.json").read_text())

    tweets = run_tweet_scraper(accounts=influencers, search_terms=keywords["twitter_search"], max_tweets=200)
    out_path = Path("output/twitter_raw.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(tweets, indent=2))
    logger.info("Saved raw tweets to %s", out_path)


if __name__ == "__main__":
    main() 