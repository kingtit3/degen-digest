import sys
from pathlib import Path
# Ensure project root is on PYTHONPATH when Streamlit launches from inside dashboard/
root_path = Path(__file__).resolve().parents[1]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

import streamlit as st
from storage.db import engine, Tweet, RedditPost, Digest, get_month_usage, LLMUsage
from sqlmodel import Session, select
from datetime import datetime
from sqlalchemy import func
import humanize

st.set_page_config(page_title="Degen Digest Dashboard", layout="wide")

st.title("📈 Degen Digest Dashboard")

with Session(engine) as sess:
    tweet_count = sess.exec(select(func.count()).select_from(Tweet)).one()
    reddit_count = sess.exec(select(func.count()).select_from(RedditPost)).one()
    digest_count = sess.exec(select(func.count()).select_from(Digest)).one()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Tweets scraped", humanize.intcomma(tweet_count))
col2.metric("Reddit posts", humanize.intcomma(reddit_count))
col3.metric("Digests", humanize.intcomma(digest_count))

# LLM spend metric
month_str = datetime.utcnow().strftime("%Y-%m")
usage = get_month_usage(month_str)
spend = usage.cost_usd if usage else 0.0
col4.metric("LLM spend (this month)", f"${spend:,.2f}")

# Recent token usage table
with Session(engine) as sess:
    recent_usage = sess.exec(select(LLMUsage).order_by(LLMUsage.month.desc()).limit(3)).all()

if recent_usage:
    st.subheader("Recent LLM token usage")
    st.table({
        "Month": [u.month for u in recent_usage],
        "Tokens": [humanize.intcomma(u.tokens) for u in recent_usage],
        "Cost $": [f"{u.cost_usd:,.2f}" for u in recent_usage],
    })

st.subheader("Recent Digests")
with Session(engine) as sess:
    digests = sess.exec(select(Digest).order_by(Digest.date.desc()).limit(10)).all()

for d in digests:
    with st.expander(datetime.fromisoformat(d.date).strftime("%B %d, %Y")):
        st.markdown(Path(d.markdown_path).read_text())
        if d.pdf_path:
            st.download_button("PDF", Path(d.pdf_path).read_bytes(), file_name=Path(d.pdf_path).name) 