#!/usr/bin/env python3
"""
Top Items Dashboard Page
Shows top engagement tweets for the last 24 hours in a Twitter-like interface.
"""

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
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

logger = get_logger(__name__)

OUTPUT_DIR = Path("output")

# Page config
st.set_page_config(
    page_title="Top Items - Degen Digest",
    page_icon="🔥",
    layout="wide"
)

# Custom CSS for Twitter-like styling
st.markdown("""
<style>
.tweet-container {
    background-color: #ffffff;
    border: 1px solid #e1e8ed;
    border-radius: 12px;
    padding: 16px;
    margin: 12px 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    transition: all 0.2s ease;
}

.tweet-container:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    transform: translateY(-2px);
}

.tweet-header {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
}

.tweet-author {
    font-weight: 700;
    color: #14171a;
    margin-right: 8px;
}

.tweet-username {
    color: #657786;
    font-size: 14px;
}

.tweet-verified {
    color: #1da1f2;
    margin-left: 4px;
}

.tweet-time {
    color: #657786;
    font-size: 14px;
    margin-left: auto;
}

.tweet-content {
    color: #14171a;
    font-size: 16px;
    line-height: 1.4;
    margin-bottom: 12px;
    word-wrap: break-word;
}

.tweet-stats {
    display: flex;
    justify-content: space-between;
    color: #657786;
    font-size: 14px;
    border-top: 1px solid #e1e8ed;
    padding-top: 12px;
}

.tweet-stat {
    display: flex;
    align-items: center;
    gap: 4px;
}

.engagement-score {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
}

.rank-badge {
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
    color: white;
    padding: 4px 8px;
    border-radius: 50%;
    font-size: 12px;
    font-weight: 700;
    min-width: 24px;
    text-align: center;
}

.source-badge {
    background: #e8f5e8;
    color: #2d5a2d;
    padding: 2px 6px;
    border-radius: 8px;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
}

.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 16px;
    border-radius: 12px;
    text-align: center;
    margin: 8px 0;
}

.metric-value {
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 4px;
}

.metric-label {
    font-size: 12px;
    opacity: 0.9;
}
</style>
""", unsafe_allow_html=True)

st.title("🔥 Top Engagement Items")

# Load consolidated data
@st.cache_data(ttl=300)
def load_top_items_data():
    """Load data for top items analysis"""
    # Try consolidated data first
    consolidated_file = Path("output/consolidated_data.json")
    if consolidated_file.exists():
        try:
            with open(consolidated_file, 'r') as f:
                data = json.load(f)
            
            items = []
            
            # Process tweets
            for tweet in data.get('tweets', []):
                items.append({
                    'text': tweet.get('full_text', tweet.get('text', '')),
                    'author': tweet.get('userScreenName', 'Unknown'),
                    'username': tweet.get('userScreenName', ''),
                    'verified': tweet.get('userVerified', False),
                    'published': tweet.get('createdAt', ''),
                    'likeCount': tweet.get('likeCount', 0),
                    'retweetCount': tweet.get('retweetCount', 0),
                    'replyCount': tweet.get('replyCount', 0),
                    'viewCount': tweet.get('viewCount', 0),
                    'userFollowersCount': tweet.get('userFollowersCount', 0),
                    'engagement_score': tweet.get('engagement_score', 0),
                    'source': 'twitter',
                    'url': f"https://twitter.com/{tweet.get('userScreenName', '')}/status/{tweet.get('id', '')}",
                    'id': tweet.get('id', '')
                })
            
            # Process Reddit posts
            for post in data.get('reddit_posts', []):
                items.append({
                    'text': post.get('title', ''),
                    'author': post.get('author', 'Unknown'),
                    'username': f"u/{post.get('author', '')}",
                    'verified': False,
                    'published': post.get('published', ''),
                    'likeCount': post.get('score', 0),
                    'retweetCount': 0,
                    'replyCount': post.get('num_comments', 0),
                    'viewCount': 0,
                    'userFollowersCount': 0,
                    'engagement_score': post.get('score', 0) * 0.1,  # Simple scoring
                    'source': 'reddit',
                    'url': post.get('url', ''),
                    'id': post.get('id', '')
                })
            
            return items
            
        except Exception as e:
            st.error(f"Error loading consolidated data: {e}")
            return []
    
    # Fallback to raw data files
    items = []
    
    # Load Twitter data
    twitter_file = Path("output/twitter_raw.json")
    if twitter_file.exists():
        try:
            with open(twitter_file, 'r') as f:
                tweets = json.load(f)
            
            for tweet in tweets:
                items.append({
                    'text': tweet.get('full_text', tweet.get('text', '')),
                    'author': tweet.get('userScreenName', 'Unknown'),
                    'username': tweet.get('userScreenName', ''),
                    'verified': tweet.get('userVerified', False),
                    'published': tweet.get('createdAt', ''),
                    'likeCount': tweet.get('likeCount', 0),
                    'retweetCount': tweet.get('retweetCount', 0),
                    'replyCount': tweet.get('replyCount', 0),
                    'viewCount': tweet.get('viewCount', 0),
                    'userFollowersCount': tweet.get('userFollowersCount', 0),
                    'engagement_score': tweet.get('engagement_score', 0),
                    'source': 'twitter',
                    'url': f"https://twitter.com/{tweet.get('userScreenName', '')}/status/{tweet.get('id', '')}",
                    'id': tweet.get('id', '')
                })
        except Exception as e:
            st.error(f"Error loading Twitter data: {e}")
    
    return items

# Load data
items = load_top_items_data()

if not items:
    st.warning("No data available. Please run scrapers first.")
    st.stop()

# Sidebar controls
st.sidebar.header("🔥 Top Items Controls")

# Time filter
st.sidebar.subheader("Time Range")
time_filter = st.sidebar.selectbox(
    "Show items from:",
    ["Last 24 hours", "Last 7 days", "Last 30 days", "All time"],
    index=0
)

# Source filter
st.sidebar.subheader("Source Filter")
all_sources = list(set(item.get('source', 'unknown') for item in items))
selected_sources = st.sidebar.multiselect(
    "Select sources:",
    all_sources,
    default=all_sources
)

# Sort by
st.sidebar.subheader("Sort By")
sort_by = st.sidebar.selectbox(
    "Sort by:",
    ["Engagement Score", "Likes", "Retweets", "Views", "Replies"],
    index=0
)

# Apply filters
now = datetime.now()
if time_filter == "Last 24 hours":
    cutoff_time = now - timedelta(hours=24)
elif time_filter == "Last 7 days":
    cutoff_time = now - timedelta(days=7)
elif time_filter == "Last 30 days":
    cutoff_time = now - timedelta(days=30)
else:
    cutoff_time = datetime.min

# Filter items
filtered_items = []
for item in items:
    # Time filter
    if item.get('published'):
        try:
            item_time = datetime.fromisoformat(item['published'].replace('Z', '+00:00'))
            if item_time < cutoff_time:
                continue
        except:
            pass
    
    # Source filter
    if item.get('source') not in selected_sources:
        continue
    
    filtered_items.append(item)

# Sort items
sort_key_map = {
    "Engagement Score": "engagement_score",
    "Likes": "likeCount",
    "Retweets": "retweetCount",
    "Views": "viewCount",
    "Replies": "replyCount"
}

sort_key = sort_key_map.get(sort_by, "engagement_score")
filtered_items.sort(key=lambda x: x.get(sort_key, 0), reverse=True)

# Top items metrics
st.sidebar.metric("Items Found", len(filtered_items))
if filtered_items:
    st.sidebar.metric("Top Engagement", f"{filtered_items[0].get('engagement_score', 0):.0f}")
    st.sidebar.metric("Total Likes", sum(item.get('likeCount', 0) for item in filtered_items))

# Main content
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader(f"🔥 Top {len(filtered_items)} Items ({time_filter})")
    
    if not filtered_items:
        st.info("No items found for the selected filters.")
    else:
        # Display top items in Twitter-like format
        for i, item in enumerate(filtered_items[:50]):  # Show top 50
            # Create Twitter-like card
            st.markdown(f"""
            <div class="tweet-container">
                <div class="tweet-header">
                    <span class="rank-badge">{i+1}</span>
                    <span class="tweet-author">{item.get('author', 'Unknown')}</span>
                    <span class="tweet-username">@{item.get('username', '')}</span>
                    {'<span class="tweet-verified">✓</span>' if item.get('verified') else ''}
                    <span class="source-badge">{item.get('source', 'unknown')}</span>
                    <span class="tweet-time">{item.get('published', '')[:19]}</span>
                </div>
                <div class="tweet-content">{item.get('text', '')[:280]}{'...' if len(item.get('text', '')) > 280 else ''}</div>
                <div class="tweet-stats">
                    <div class="tweet-stat">
                        <span>❤️</span>
                        <span>{item.get('likeCount', 0):,}</span>
                    </div>
                    <div class="tweet-stat">
                        <span>🔄</span>
                        <span>{item.get('retweetCount', 0):,}</span>
                    </div>
                    <div class="tweet-stat">
                        <span>💬</span>
                        <span>{item.get('replyCount', 0):,}</span>
                    </div>
                    <div class="tweet-stat">
                        <span>👁️</span>
                        <span>{item.get('viewCount', 0):,}</span>
                    </div>
                    <div class="engagement-score">
                        Score: {item.get('engagement_score', 0):.0f}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Add expandable details
            with st.expander(f"📊 Details for #{i+1}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Engagement Score", f"{item.get('engagement_score', 0):.0f}")
                    st.metric("Likes", f"{item.get('likeCount', 0):,}")
                
                with col2:
                    st.metric("Retweets", f"{item.get('retweetCount', 0):,}")
                    st.metric("Replies", f"{item.get('replyCount', 0):,}")
                
                with col3:
                    st.metric("Views", f"{item.get('viewCount', 0):,}")
                    st.metric("Followers", f"{item.get('userFollowersCount', 0):,}")
                
                if item.get('url'):
                    st.markdown(f"**Link:** [{item['url']}]({item['url']})")

with col2:
    st.subheader("📊 Quick Stats")
    
    if filtered_items:
        # Engagement distribution
        engagement_scores = [item.get('engagement_score', 0) for item in filtered_items]
        
        fig = px.histogram(
            x=engagement_scores,
            title="Engagement Score Distribution",
            labels={'x': 'Engagement Score', 'y': 'Count'},
            nbins=20
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Source breakdown
        source_counts = {}
        for item in filtered_items:
            source = item.get('source', 'unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        if source_counts:
            fig = px.pie(
                values=list(source_counts.values()),
                names=list(source_counts.keys()),
                title="Items by Source"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Top authors
        author_counts = {}
        for item in filtered_items:
            author = item.get('author', 'Unknown')
            author_counts[author] = author_counts.get(author, 0) + 1
        
        top_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        st.subheader("👥 Top Authors")
        for author, count in top_authors:
            st.write(f"• **{author}**: {count} items")

# Footer
st.markdown("---")
st.markdown("*Top engagement items from the last 24 hours - Twitter-like interface*") 