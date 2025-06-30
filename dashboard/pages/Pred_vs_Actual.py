import sys
from pathlib import Path
root_path = Path(__file__).resolve().parents[2]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

import streamlit as st
import numpy as np
import pandas as pd
from sqlmodel import Session, select
from storage.db import engine, Tweet, TweetMetrics
from processor.scorer import degen_score
from utils.advanced_logging import get_logger

logger = get_logger(__name__)

st.set_page_config(page_title="Pred vs Actual", layout="wide")
st.title("📊 Predicted vs Actual 1-h Like Growth")

# build data
rows = []
with Session(engine) as sess:
    tweets = {t.id: t for t in sess.exec(select(Tweet)).all()}
    metrics = sess.exec(select(TweetMetrics)).all()
    first_snap = {}
    for m in metrics:
        if m.tweet_id not in first_snap or m.captured_at < first_snap[m.tweet_id].captured_at:
            first_snap[m.tweet_id] = m

for tid, m in first_snap.items():
    tw = tweets.get(tid)
    if not tw:
        continue
    actual = m.like_count - (tw.like_count or 0)
    if actual < 0:
        continue
    pred = degen_score({
        "full_text": tw.text,
        "likeCount": tw.like_count,
        "retweetCount": tw.retweet_count,
        "replyCount": tw.reply_count,
    })  # 0-100
    rows.append({"pred": pred, "actual": actual, "text": tw.text[:100], "link": f"https://twitter.com/i/web/status/{tid}"})

if not rows:
    st.info("Need metrics & model: run refresh + training steps first.")
    st.stop()

df = pd.DataFrame(rows)
st.scatter_chart(df, x="pred", y="actual", size=5)

st.subheader("Undervalued (High pred, low actual)")
underval = df.sort_values(by="pred", ascending=False).head(20)
st.table(underval[["pred", "actual", "text", "link"]]) 