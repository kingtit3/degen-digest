import sys, subprocess, json
from pathlib import Path
root_path = Path(__file__).resolve().parents[2]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

import streamlit as st
from sqlmodel import Session, select
from storage.db import engine, Tweet, RedditPost
import pandas as pd

def main():
    st.set_page_config(page_title="⛓️ Sources Browser", layout="wide")
    st.title("🔎 Source Browser & Refresh")

    if st.button("🔄 Refresh ALL data"):
        with st.spinner("Running scrapers – this may take a few minutes..."):
            code = subprocess.call(["python", "scripts/run_all.py"])
            if code == 0:
                st.success("Data refreshed!")
            else:
                st.error(f"Scraper run failed (exit {code})")

    source_tabs = st.tabs(["Twitter", "Reddit", "Telegram", "NewsAPI", "CoinGecko"])

    # --- Twitter --------------------------------------------------------------
    with source_tabs[0]:
        st.subheader("Twitter Items")
        with Session(engine) as sess:
            rows = sess.exec(select(Tweet).order_by(Tweet.scraped_at.desc()).limit(1000)).all()
        if rows:
            df = pd.DataFrame([{
                "Date": t.created_at,
                "User": t.author,
                "Likes": t.like_count,
                "Retweets": t.retweet_count,
                "Quotes": t.quote_count,
                "Replies": t.reply_count,
                "Followers": t.follower_count,
                "Text": t.text,
                "Link": f"https://twitter.com/i/web/status/{t.tweet_id}",
            } for t in rows])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No tweets in database.")

    # --- Reddit ---------------------------------------------------------------
    with source_tabs[1]:
        st.subheader("Reddit Posts")
        with Session(engine) as sess:
            rows = sess.exec(select(RedditPost).order_by(RedditPost.published.desc()).limit(1000)).all()
        if rows:
            df = pd.DataFrame([{
                "Date": r.published,
                "Title": r.title,
                "Subreddit": r.subreddit,
                "Link": r.link,
                "Summary": r.summary,
            } for r in rows])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No reddit data.")

    # --- Telegram -------------------------------------------------------------
    with source_tabs[2]:
        st.subheader("Telegram Messages")
        tg_path = Path("output/telegram_raw.json")
        if tg_path.exists():
            msgs = json.loads(tg_path.read_text())
            df = pd.DataFrame(msgs)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No telegram data file yet.")

    # --- NewsAPI --------------------------------------------------------------
    with source_tabs[3]:
        st.subheader("NewsAPI Headlines")
        news_path = Path("output/newsapi_raw.json")
        if news_path.exists():
            headlines = json.loads(news_path.read_text())
            df = pd.DataFrame(headlines)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No NewsAPI data yet.")

    # --- CoinGecko ------------------------------------------------------------
    with source_tabs[4]:
        st.subheader("CoinGecko Top Gainers")
        cg_path = Path("output/coingecko_raw.json")
        if cg_path.exists():
            coins = json.loads(cg_path.read_text())
            df = pd.DataFrame(coins)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No CoinGecko data yet.") 