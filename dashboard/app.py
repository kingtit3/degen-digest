import streamlit as st
from storage.db import engine, Tweet, RedditPost, Digest
from sqlmodel import Session, select
from datetime import datetime
from pathlib import Path

st.set_page_config(page_title="Degen Digest Dashboard", layout="wide")

st.title("📈 Degen Digest Dashboard")

with Session(engine) as sess:
    tweet_count = sess.exec(select(Tweet).count()).one()
    reddit_count = sess.exec(select(RedditPost).count()).one()
    digest_count = sess.exec(select(Digest).count()).one()

col1, col2, col3 = st.columns(3)
col1.metric("Tweets scraped", tweet_count)
col2.metric("Reddit posts", reddit_count)
col3.metric("Digests", digest_count)

st.subheader("Recent Digests")
with Session(engine) as sess:
    digests = sess.exec(select(Digest).order_by(Digest.date.desc()).limit(10)).all()

for d in digests:
    with st.expander(d.date):
        st.markdown(Path(d.markdown_path).read_text())
        if d.pdf_path:
            st.download_button("PDF", Path(d.pdf_path).read_bytes(), file_name=Path(d.pdf_path).name) 