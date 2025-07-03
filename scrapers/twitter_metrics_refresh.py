import json
from datetime import datetime
from pathlib import Path

from storage.db import add_tweet_metrics, recent_tweet_ids
from utils.advanced_logging import get_logger
from utils.logger import setup_logging

setup_logging()
logger = get_logger(__name__)

RAW_PATH = Path("output/twitter_raw.json")


def load_current_raw():
    if RAW_PATH.exists():
        return {
            str(t.get("id") or t.get("tweetId")): t
            for t in json.loads(RAW_PATH.read_text())
        }
    return {}


def main():
    ids = recent_tweet_ids(2)
    if not ids:
        logger.info("no recent tweets to refresh")
        return

    raw_map = load_current_raw()
    metrics_rows = []
    for tid in ids:
        tw = raw_map.get(str(tid))
        if not tw:
            continue
        metrics_rows.append(
            {
                "tweet_id": str(tid),
                "captured_at": datetime.utcnow(),
                "like_count": tw.get("likeCount", 0),
                "retweet_count": tw.get("retweetCount", 0),
                "reply_count": tw.get("replyCount", 0),
                "quote_count": tw.get("quoteCount"),
                "bookmark_count": tw.get("bookmarkCount"),
            }
        )
    add_tweet_metrics(metrics_rows)
    logger.info("tweet metrics stored", count=len(metrics_rows))


if __name__ == "__main__":
    main()
