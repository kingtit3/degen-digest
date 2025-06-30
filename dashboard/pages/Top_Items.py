import sys
from pathlib import Path
root_path = Path(__file__).resolve().parents[2]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

import streamlit as st
from sqlmodel import Session, select
from storage.db import engine
from processor.scorer import degen_score
import json
from utils.advanced_logging import get_logger

logger = get_logger(__name__)

OUTPUT_DIR = Path("output")

st.set_page_config(page_title="Top Items", layout="wide")
st.title("🔥 Top 50 Items by Degen Score")

# Load latest raw source files
items: list[dict] = []
for fname in ["twitter_raw.json", "reddit_raw.json", "telegram_raw.json", "coingecko_raw.json"]:
    path = OUTPUT_DIR / fname
    if path.exists():
        try:
            items.extend(json.loads(path.read_text()))
        except Exception as exc:
            logger.warning("Failed reading %s: %s", fname, exc)

# Compute scores quick (no LLM)
scored = []
for it in items:
    try:
        s = degen_score(it)
        scored.append({"score": s, **it})
    except Exception:
        continue

scored.sort(key=lambda x: x["score"], reverse=True)

if not scored:
    st.info("No items available. Run scrapers first.")
    st.stop()

import humanize

table_data = {
    "Score": [r["score"] for r in scored[:50]],
    "Text / Title": [r.get("full_text") or r.get("text") or r.get("title") for r in scored[:50]],
    "Source": [r.get("channel") or r.get("subreddit") or "tweet" for r in scored[:50]],
    "Likes": [r.get("likeCount", "-") for r in scored[:50]],
    "Retweets": [r.get("retweetCount", "-") for r in scored[:50]],
    "Link": [r.get("url") or r.get("link") for r in scored[:50]],
}

st.dataframe(table_data, use_container_width=True) 