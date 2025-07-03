import sys
from pathlib import Path

root_path = Path(__file__).resolve().parents[2]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

import hashlib
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import and_, desc, or_
from sqlmodel import Session, select

from storage.db import RedditPost, Tweet, engine
from utils.advanced_logging import get_logger

logger = get_logger(__name__)


def calculate_engagement_score(tweet):
    """Calculate engagement score for a tweet"""
    likes = tweet.like_count or 0
    retweets = tweet.retweet_count or 0
    replies = tweet.reply_count or 0
    views = tweet.view_count or 0

    # Weighted engagement score
    return likes + (retweets * 2) + (replies * 3) + (views * 0.1)


def remove_duplicates(data, similarity_threshold=0.8):
    """Remove duplicate content based on similarity"""
    if not data:
        return data

    # Create content hashes for quick comparison
    content_hashes = []
    unique_data = []

    for item in data:
        # Create a hash of the content (normalized)
        content = (item.get("full_text", "") or item.get("text", "") or "").lower()
        content_hash = hashlib.md5(content.encode()).hexdigest()

        if content_hash not in content_hashes:
            content_hashes.append(content_hash)
            unique_data.append(item)

    return unique_data


def main():
    st.markdown(
        """
    <div style="text-align: center; margin-bottom: 40px;">
        <h1 class="gradient-text">📡 Live Feed</h1>
        <p style="color: #888; font-size: 18px;">Real-time crypto content with advanced filtering and analytics</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Advanced filters sidebar
    with st.sidebar:
        st.markdown("### 🔍 Advanced Filters")

        # Date range filter
        st.markdown("**📅 Date Range**")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("From", value=datetime.now() - timedelta(days=7))
        with col2:
            end_date = st.date_input("To", value=datetime.now())

        # Source filter
        st.markdown("**📊 Data Sources**")
        sources = st.multiselect(
            "Select sources",
            ["Twitter", "Reddit", "Telegram", "NewsAPI", "CoinGecko"],
            default=["Twitter", "Reddit"],
        )

        # Engagement filter
        st.markdown("**📈 Engagement Filter**")
        min_engagement = st.slider("Minimum Engagement", 0, 10000, 0)

        # Content type filter
        st.markdown("**📝 Content Type**")
        content_types = st.multiselect(
            "Content types",
            ["News", "Analysis", "Meme", "Price Update", "Project Update", "Opinion"],
            default=["News", "Analysis", "Price Update"],
        )

        # Keyword filter
        st.markdown("**🔍 Keywords**")
        keywords = st.text_input("Search keywords (comma separated)")

        # Duplicate handling
        st.markdown("**🔄 Duplicate Handling**")
        remove_dups = st.checkbox("Remove Duplicates", value=True)
        similarity_threshold = st.slider("Similarity Threshold", 0.5, 1.0, 0.8)

        # Sort options
        st.markdown("**📊 Sort Options**")
        sort_by = st.selectbox(
            "Sort by",
            [
                "Engagement Score",
                "Date (Newest)",
                "Date (Oldest)",
                "Source",
                "Content Length",
            ],
        )

        # Display options
        st.markdown("**⚙️ Display Options**")
        items_per_page = st.slider("Items per page", 10, 100, 25)
        show_metrics = st.checkbox("Show Engagement Metrics", value=True)
        show_charts = st.checkbox("Show Analytics Charts", value=True)

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        # Data loading and processing
        with st.spinner("Loading data..."):
            data = []

            # Load Twitter data
            if "Twitter" in sources:
                with Session(engine) as sess:
                    twitter_query = select(Tweet).where(
                        and_(
                            Tweet.created_at >= start_date,
                            Tweet.created_at <= end_date + timedelta(days=1),
                        )
                    )

                    if keywords:
                        keyword_list = [k.strip().lower() for k in keywords.split(",")]
                        keyword_filters = [
                            Tweet.full_text.ilike(f"%{k}%") for k in keyword_list
                        ]
                        twitter_query = twitter_query.where(or_(*keyword_filters))

                    tweets = sess.exec(
                        twitter_query.order_by(desc(Tweet.created_at)).limit(1000)
                    ).all()

                    for tweet in tweets:
                        engagement = calculate_engagement_score(tweet)
                        if engagement >= min_engagement:
                            data.append(
                                {
                                    "id": tweet.id,
                                    "source": "Twitter",
                                    "content": tweet.full_text,
                                    "engagement": engagement,
                                    "likes": tweet.like_count or 0,
                                    "retweets": tweet.retweet_count or 0,
                                    "replies": tweet.reply_count or 0,
                                    "views": tweet.view_count or 0,
                                    "date": tweet.created_at,
                                    "author": tweet.author_username or "Unknown",
                                    "url": f"https://twitter.com/user/status/{tweet.tweet_id}"
                                    if tweet.tweet_id
                                    else None,
                                }
                            )

            # Load Reddit data
            if "Reddit" in sources:
                with Session(engine) as sess:
                    reddit_query = select(RedditPost).where(
                        and_(
                            RedditPost.created_at >= start_date,
                            RedditPost.created_at <= end_date + timedelta(days=1),
                        )
                    )

                    if keywords:
                        keyword_list = [k.strip().lower() for k in keywords.split(",")]
                        keyword_filters = [
                            RedditPost.title.ilike(f"%{k}%") for k in keyword_list
                        ]
                        reddit_query = reddit_query.where(or_(*keyword_filters))

                    reddit_posts = sess.exec(
                        reddit_query.order_by(desc(RedditPost.created_at)).limit(500)
                    ).all()

                    for post in reddit_posts:
                        engagement = (post.score or 0) + (post.numComments or 0) * 2
                        if engagement >= min_engagement:
                            data.append(
                                {
                                    "id": post.id,
                                    "source": "Reddit",
                                    "content": f"{post.title}",
                                    "engagement": engagement,
                                    "likes": post.score or 0,
                                    "retweets": 0,
                                    "replies": post.numComments or 0,
                                    "views": 0,
                                    "date": post.created_at,
                                    "author": post.author or "Unknown",
                                    "url": post.url or None,
                                }
                            )

        # Remove duplicates if requested
        if remove_dups and data:
            original_count = len(data)
            data = remove_duplicates(data, similarity_threshold)
            st.info(f"Removed {original_count - len(data)} duplicates")

        # Sort data
        if sort_by == "Engagement Score":
            data.sort(key=lambda x: x["engagement"], reverse=True)
        elif sort_by == "Date (Newest)":
            data.sort(key=lambda x: x["date"], reverse=True)
        elif sort_by == "Date (Oldest)":
            data.sort(key=lambda x: x["date"])
        elif sort_by == "Source":
            data.sort(key=lambda x: x["source"])
        elif sort_by == "Content Length":
            data.sort(key=lambda x: len(x["content"]), reverse=True)

        # Pagination
        total_items = len(data)
        total_pages = (total_items + items_per_page - 1) // items_per_page

        if total_pages > 1:
            page = st.selectbox(f"Page (1-{total_pages})", range(1, total_pages + 1))
            start_idx = (page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            current_data = data[start_idx:end_idx]
        else:
            current_data = data[:items_per_page]

        # Display data
        st.markdown(f"### 📊 Showing {len(current_data)} of {total_items} items")

        for i, item in enumerate(current_data):
            with st.container():
                st.markdown(
                    """
                <div style="
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 10px;
                    padding: 15px;
                    margin: 10px 0;
                    backdrop-filter: blur(10px);
                ">
                """,
                    unsafe_allow_html=True,
                )

                # Header with source and date
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.markdown(f"**{item['source']}** • {item['author']}")
                with col2:
                    st.markdown(f"📅 {item['date'].strftime('%Y-%m-%d %H:%M')}")
                with col3:
                    if item["url"]:
                        st.markdown(f"[🔗 Link]({item['url']})")

                # Content
                st.markdown(
                    f"**{item['content'][:200]}{'...' if len(item['content']) > 200 else ''}**"
                )

                # Engagement metrics
                if show_metrics:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Engagement", f"{item['engagement']:,}")
                    with col2:
                        st.metric("Likes", f"{item['likes']:,}")
                    with col3:
                        st.metric("Retweets", f"{item['retweets']:,}")
                    with col4:
                        st.metric("Replies", f"{item['replies']:,}")

                st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        # Analytics sidebar
        if show_charts and data:
            st.markdown("### 📈 Analytics")

            # Engagement distribution
            engagement_values = [item["engagement"] for item in data]
            fig = px.histogram(
                x=engagement_values,
                nbins=20,
                title="Engagement Distribution",
                color_discrete_sequence=["#00d4ff"],
            )
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
            )
            st.plotly_chart(fig, use_container_width=True)

            # Source distribution
            source_counts = {}
            for item in data:
                source_counts[item["source"]] = source_counts.get(item["source"], 0) + 1

            if source_counts:
                fig = px.pie(
                    values=list(source_counts.values()),
                    names=list(source_counts.keys()),
                    title="Data Source Distribution",
                    color_discrete_sequence=["#00d4ff", "#ff6b6b", "#4ecdc4"],
                )
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="white"),
                )
                st.plotly_chart(fig, use_container_width=True)

            # Time series
            if len(data) > 1:
                df = pd.DataFrame(data)
                df["date_only"] = df["date"].dt.date
                daily_engagement = (
                    df.groupby("date_only")["engagement"].sum().reset_index()
                )

                fig = px.line(
                    daily_engagement,
                    x="date_only",
                    y="engagement",
                    title="Daily Engagement Trend",
                    color_discrete_sequence=["#00d4ff"],
                )
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="white"),
                    xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
                    yaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
                )
                st.plotly_chart(fig, use_container_width=True)

        # Quick stats
        if data:
            st.markdown("### 📊 Quick Stats")
            st.metric("Total Items", len(data))
            st.metric(
                "Avg Engagement",
                f"{np.mean([item['engagement'] for item in data]):.0f}",
            )
            st.metric(
                "Top Engagement", f"{max([item['engagement'] for item in data]):,}"
            )

            # Top sources
            source_counts = {}
            for item in data:
                source_counts[item["source"]] = source_counts.get(item["source"], 0) + 1

            st.markdown("**Top Sources:**")
            for source, count in sorted(
                source_counts.items(), key=lambda x: x[1], reverse=True
            ):
                st.markdown(f"• {source}: {count}")


if __name__ == "__main__":
    main()
