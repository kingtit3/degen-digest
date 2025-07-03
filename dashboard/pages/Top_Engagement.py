import sys
from pathlib import Path

root_path = Path(__file__).resolve().parents[2]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

import json

import humanize
import streamlit as st

from utils.advanced_logging import get_logger

logger = get_logger(__name__)

OUTPUT_DIR = Path("output")


def load_tweets():
    tw_path = OUTPUT_DIR / "twitter_raw.json"
    if not tw_path.exists():
        return []
    try:
        return json.loads(tw_path.read_text())
    except Exception as exc:
        logger.warning("failed reading twitter_raw.json: %s", exc)
        return []


def engagement_score(tw: dict) -> int:
    likes = tw.get("likeCount", 0)
    rts = tw.get("retweetCount", 0)
    replies = tw.get("replyCount", 0)
    quotes = tw.get("quoteCount", 0)
    bookmarks = tw.get("bookmarkCount", 0)
    # simple weighted sum
    return likes + 2 * rts + replies + 3 * quotes + bookmarks


st.set_page_config(page_title="Top Engagement", layout="wide")
st.title("🐳 Tweets with highest engagement")

tweets = load_tweets()
if not tweets:
    st.info("No tweets scraped yet. Run twitter scraper first.")
    st.stop()

for tw in tweets:
    tw["_eng"] = engagement_score(tw)

tweets.sort(key=lambda x: x["_eng"], reverse=True)

show = tweets[:100]

import pandas as pd

rows = []
for t in show:
    rows.append(
        {
            "Engagement": humanize.intcomma(t["_eng"]),
            "Likes": humanize.intcomma(t.get("likeCount", 0)),
            "RTs": humanize.intcomma(t.get("retweetCount", 0)),
            "Quotes": t.get("quoteCount", "-"),
            "Bookmarks": t.get("bookmarkCount", "-"),
            "Text": (t.get("full_text") or t.get("text") or "")[:140],
            "Link": t.get("url") or t.get("twitterUrl"),
        }
    )

df = pd.DataFrame(rows)
# make link clickable
st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
