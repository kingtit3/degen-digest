import sys
from pathlib import Path
# Ensure project root is on PYTHONPATH when Streamlit launches from inside dashboard/
root_path = Path(__file__).resolve().parents[1]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
import json
from storage.db import engine, Tweet, RedditPost, Digest, get_month_usage, LLMUsage
from sqlmodel import Session, select, func
from sqlalchemy import desc, and_
import humanize
from utils.health_monitor import health_monitor
from utils.advanced_logging import get_logger

logger = get_logger(__name__)

# Page configuration with modern theme
st.set_page_config(
    page_title="Degen Digest - Crypto Intelligence Hub",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for futuristic design
st.markdown("""
<style>
    /* Modern futuristic theme */
    .main {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    /* Custom metric cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* Gradient text */
    .gradient-text {
        background: linear-gradient(45deg, #00d4ff, #ff6b6b, #4ecdc4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: bold;
    }
    
    /* Animated cards */
    .animated-card {
        transition: all 0.3s ease;
    }
    
    .animated-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
    }
    
    /* Custom sidebar */
    .css-1d391kg {
        background: rgba(15, 15, 35, 0.9);
    }
    
    /* Data table styling */
    .dataframe {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 10px !important;
    }
    
    .dataframe th {
        background: rgba(0, 212, 255, 0.2) !important;
        color: #00d4ff !important;
        font-weight: bold !important;
    }
    
    .dataframe td {
        color: #ffffff !important;
    }
    
    /* Chart containers */
    .chart-container {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 class="gradient-text">🚀 Degen Digest</h1>
        <p style="color: #888; font-size: 14px;">Crypto Intelligence Hub</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    st.markdown("### 📊 Navigation")
    page = st.selectbox(
        "Choose a page:",
        ["Dashboard", "Live Feed", "Analytics", "Health Monitor", "Digests", "Digest Archive", "Sources"],
        label_visibility="collapsed"
    )
    
    # Filters
    st.markdown("### 🔍 Filters")
    date_range = st.date_input(
        "Date Range",
        value=(datetime.now(timezone.utc) - timedelta(days=7), datetime.now(timezone.utc)),
        max_value=datetime.now(timezone.utc)
    )
    
    source_filter = st.multiselect(
        "Data Sources",
        ["Twitter", "Reddit", "Telegram", "NewsAPI", "CoinGecko"],
        default=["Twitter", "Reddit"]
    )
    
    # Sort options
    st.markdown("### 📈 Sort Options")
    sort_by = st.selectbox(
        "Sort by",
        ["Engagement Score", "Date", "Source", "Viral Prediction"]
    )
    
    # Display options
    st.markdown("### ⚙️ Display")
    show_duplicates = st.checkbox("Show Duplicates", value=False)
    items_per_page = st.slider("Items per page", 10, 100, 25)

# Main content based on selected page
if page == "Dashboard":
    st.markdown("""
    <div style="text-align: center; margin-bottom: 40px;">
        <h1 class="gradient-text">🚀 Degen Digest Dashboard</h1>
        <p style="color: #888; font-size: 18px;">Real-time crypto intelligence and market insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics row
    with Session(engine) as sess:
        tweet_count = sess.exec(select(func.count()).select_from(Tweet)).one()
        reddit_count = sess.exec(select(func.count()).select_from(RedditPost)).one()
        digest_count = sess.exec(select(func.count()).select_from(Digest)).one()
        
        # Get recent activity
        recent_tweets = sess.exec(
            select(Tweet).order_by(desc(Tweet.created_at)).limit(1)
        ).first()
        
        # Calculate engagement metrics
        avg_engagement = sess.exec(
            select(func.avg(Tweet.like_count + Tweet.retweet_count * 2 + Tweet.reply_count * 3))
        ).one() or 0

    # Metrics cards with modern design
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card animated-card">
            <h3 style="color: #00d4ff; margin: 0;">📊 Total Data</h3>
            <h2 style="color: #ffffff; margin: 10px 0;">{:,}</h2>
            <p style="color: #888; margin: 0;">Tweets & Posts</p>
        </div>
        """.format(tweet_count + reddit_count), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card animated-card">
            <h3 style="color: #ff6b6b; margin: 0;">📈 Engagement</h3>
            <h2 style="color: #ffffff; margin: 10px 0;">{:.0f}</h2>
            <p style="color: #888; margin: 0;">Avg Engagement</p>
        </div>
        """.format(avg_engagement), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card animated-card">
            <h3 style="color: #4ecdc4; margin: 0;">📋 Digests</h3>
            <h2 style="color: #ffffff; margin: 10px 0;">{}</h2>
            <p style="color: #888; margin: 0;">Generated Reports</p>
        </div>
        """.format(digest_count), unsafe_allow_html=True)
    
    # LLM spend metric
    month_str = datetime.now(timezone.utc).strftime("%Y-%m")
    usage = get_month_usage(month_str)
    spend = usage.cost_usd if usage else 0.0
    
    with col4:
        st.markdown("""
        <div class="metric-card animated-card">
            <h3 style="color: #f39c12; margin: 0;">💰 LLM Cost</h3>
            <h2 style="color: #ffffff; margin: 10px 0;">${:.2f}</h2>
            <p style="color: #888; margin: 0;">This Month</p>
        </div>
        """.format(spend), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📊 Data Source Distribution")
        
        # Create pie chart for data sources
        source_data = {
            'Twitter': tweet_count,
            'Reddit': reddit_count,
            'Telegram': 0,  # Add actual count when available
            'NewsAPI': 0,   # Add actual count when available
        }
        
        fig = px.pie(
            values=list(source_data.values()),
            names=list(source_data.keys()),
            color_discrete_sequence=['#00d4ff', '#ff6b6b', '#4ecdc4', '#f39c12']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📈 Engagement Trends")
        
        # Get engagement data over time
        with Session(engine) as sess:
            engagement_data = sess.exec(
                select(
                    Tweet.created_at,
                    func.sum(Tweet.like_count + Tweet.retweet_count * 2 + Tweet.reply_count * 3).label('engagement')
                )
                .group_by(func.date(Tweet.created_at))
                .order_by(func.date(Tweet.created_at))
                .limit(30)
            ).all()
        
        if engagement_data:
            dates = [str(row[0].date()) for row in engagement_data]
            engagement = [row[1] for row in engagement_data]
            
            fig = px.line(
                x=dates,
                y=engagement,
                title="Daily Engagement",
                color_discrete_sequence=['#00d4ff']
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No engagement data available yet")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Recent activity section
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("🕒 Recent Activity")
    
    # Get recent tweets with engagement
    with Session(engine) as sess:
        recent_activity = sess.exec(
            select(Tweet)
            .order_by(desc(Tweet.created_at))
            .limit(10)
        ).all()
    
    if recent_activity:
        activity_data = []
        for tweet in recent_activity:
            engagement = (tweet.like_count or 0) + (tweet.retweet_count or 0) * 2 + (tweet.reply_count or 0) * 3
            activity_data.append({
                'Content': tweet.full_text[:100] + "..." if len(tweet.full_text) > 100 else tweet.full_text,
                'Engagement': engagement,
                'Likes': tweet.like_count or 0,
                'Retweets': tweet.retweet_count or 0,
                'Replies': tweet.reply_count or 0,
                'Date': tweet.created_at.strftime("%Y-%m-%d %H:%M")
            })
        
        df = pd.DataFrame(activity_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No recent activity available")
    
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Live Feed":
    # Import and run the live feed page
    import pages.Live_Feed as live_feed_page
    live_feed_page.main()

elif page == "Analytics":
    # Import and run the analytics page
    import pages.Analytics as analytics_page
    analytics_page.main()

elif page == "Health Monitor":
    # Import and run the health monitor page
    import pages.Health_Monitor as health_page
    health_page.main()

elif page == "Digests":
    # Import and run the digests page
    import pages.Digests as digests_page
    digests_page.main()

elif page == "Digest Archive":
    # Import the digest archive functionality
    import pages.Digest_Archive as digest_archive_page
    digest_archive_page.main()

elif page == "Sources":
    # Import and run the sources page
    import pages.Sources as sources_page
    sources_page.main()

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 50px; padding: 20px; border-top: 1px solid rgba(255,255,255,0.1);">
    <p style="color: #888; font-size: 12px;">
        🚀 Degen Digest v2.0 | Powered by AI | Real-time Crypto Intelligence
    </p>
</div>
""", unsafe_allow_html=True)

def main():
    """Main function to run the Streamlit app"""
    # The app code is already structured to run when imported
    # This function is for compatibility
    pass

if __name__ == "__main__":
    main() 