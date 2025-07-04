import json
import time
from pathlib import Path

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# Google Cloud Storage imports
try:
    from google.cloud import storage

    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    print(
        "Warning: Google Cloud Storage not available. Install with: pip install google-cloud-storage"
    )

# Page config
st.set_page_config(
    page_title="Degen Digest - Crypto Intelligence",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for clean design
st.markdown(
    """
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }

    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
        margin: 0.5rem 0;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }

    .metric-label {
        color: #666;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }

    .digest-container {
        background: white;
        border-radius: 10px;
        padding: 2rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }

    .tweet-card {
        background: white;
        border: 1px solid #e1e8ed;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }

    .tweet-card:hover {
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }

    .engagement-stats {
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
        font-size: 0.9rem;
        color: #666;
    }

    .engagement-stat {
        display: flex;
        align-items: center;
        gap: 0.3rem;
    }

    .viral-badge {
        background: linear-gradient(45deg, #ff6b6b, #ffa500);
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }

    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }

    .crawler-status {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }

    .crawler-controls {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }

    .log-entry {
        background: #f8f9fa;
        border-left: 3px solid #667eea;
        padding: 0.5rem;
        margin: 0.25rem 0;
        font-family: monospace;
        font-size: 0.9rem;
    }

    .section-header {
        background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 2rem 0 1rem 0;
        border-left: 4px solid #667eea;
    }

    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }

    .status-running {
        background-color: #28a745;
    }

    .status-stopped {
        background-color: #dc3545;
    }

    .status-unknown {
        background-color: #ffc107;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Standardized Cloud Configuration
GCS_CONFIG = {
    "project_id": "lucky-union-463615-t3",
    "bucket_name": "degen-digest-data",
    "data_structure": {
        "twitter": {
            "raw": "twitter_data/",
            "consolidated": "consolidated/twitter_consolidated.json",
            "latest": "consolidated/twitter_latest.json",
        },
        "reddit": {
            "raw": "reddit_data/",
            "consolidated": "consolidated/reddit_consolidated.json",
        },
        "telegram": {
            "raw": "telegram_data/",
            "consolidated": "consolidated/telegram_consolidated.json",
        },
        "news": {
            "raw": "news_data/",
            "consolidated": "consolidated/news_consolidated.json",
        },
        "crypto": {
            "raw": "crypto_data/",
            "consolidated": "consolidated/crypto_consolidated.json",
        },
        "analytics": {
            "stats": "analytics/crawler_stats.json",
            "metrics": "analytics/engagement_metrics.json",
        },
        "digests": {
            "latest": "digests/latest_digest.md",
            "archive": "digests/archive/",
        },
    },
}


def get_gcs_client():
    """Get Google Cloud Storage client"""
    if not GCS_AVAILABLE:
        return None, "Google Cloud Storage not available"

    try:
        client = storage.Client(project=GCS_CONFIG["project_id"])
        bucket = client.bucket(GCS_CONFIG["bucket_name"])
        return client, bucket
    except Exception as e:
        return None, f"GCS connection failed: {e}"


def load_consolidated_data(source_name):
    """Load consolidated data from GCS for a specific source"""
    client, bucket = get_gcs_client()
    if not bucket:
        return None

    try:
        consolidated_path = GCS_CONFIG["data_structure"][source_name]["consolidated"]
        blob = bucket.blob(consolidated_path)

        if blob.exists():
            content = blob.download_as_text()
            data = json.loads(content)
            st.success(f"✅ Loaded {source_name} data from GCS")
            return data
        else:
            st.warning(f"⚠️ No consolidated {source_name} data found in GCS")
            return None
    except Exception as e:
        st.error(f"❌ Error loading {source_name} data: {e}")
        return None


def get_raw_data():
    """Get raw data for analytics and trending content from GCS"""
    data = {}

    # Load from consolidated files in GCS
    sources = ["twitter", "reddit", "telegram", "news", "crypto"]

    for source in sources:
        source_data = load_consolidated_data(source)
        if source_data:
            # Extract tweets/posts from the consolidated structure
            if "tweets" in source_data:
                data[source] = source_data["tweets"]
            elif "posts" in source_data:
                data[source] = source_data["posts"]
            elif "messages" in source_data:
                data[source] = source_data["messages"]
            elif "articles" in source_data:
                data[source] = source_data["articles"]
            elif "data" in source_data:
                data[source] = source_data["data"]
            else:
                data[source] = source_data

    return data


def get_latest_digest():
    """Get the latest digest content from GCS"""
    client, bucket = get_gcs_client()
    if not bucket:
        return None, "GCS not available"

    try:
        # Try to get latest digest from GCS
        digest_path = GCS_CONFIG["data_structure"]["digests"]["latest"]
        blob = bucket.blob(digest_path)

        if blob.exists():
            content = blob.download_as_text()
            return content, "Latest Digest (GCS)"
        else:
            # Fallback to local file if GCS doesn't have digest
            output_dir = Path("output")
            digest_files = list(output_dir.glob("digest*.md"))
            if digest_files:
                latest_digest = max(digest_files, key=lambda x: x.stat().st_mtime)
                with open(latest_digest, encoding="utf-8") as f:
                    content = f.read()
                return content, latest_digest.name
            else:
                return None, "No digest found"
    except Exception as e:
        return None, f"Error reading digest: {str(e)}"


def get_crawler_analytics():
    """Get crawler analytics and statistics from GCS"""
    client, bucket = get_gcs_client()
    if not bucket:
        return None

    try:
        stats_path = GCS_CONFIG["data_structure"]["analytics"]["stats"]
        blob = bucket.blob(stats_path)

        if blob.exists():
            content = blob.download_as_text()
            return json.loads(content)
        else:
            return None
    except Exception as e:
        st.error(f"Error loading crawler analytics: {e}")
        return None


def get_engagement_metrics():
    """Get engagement metrics from GCS"""
    client, bucket = get_gcs_client()
    if not bucket:
        return None

    try:
        metrics_path = GCS_CONFIG["data_structure"]["analytics"]["metrics"]
        blob = bucket.blob(metrics_path)

        if blob.exists():
            content = blob.download_as_text()
            return json.loads(content)
        else:
            return None
    except Exception as e:
        st.error(f"Error loading engagement metrics: {e}")
        return None


def generate_fresh_digest():
    """Generate a fresh digest"""
    try:
        # This would call your digest generation script
        # For now, return success
        return True, "Digest generated successfully!"
    except Exception as e:
        return False, f"Error generating digest: {str(e)}"


def create_analytics_charts(data):
    """Create analytics charts from data"""
    charts = {}

    # Source distribution chart
    source_counts = {}
    for source, items in data.items():
        if isinstance(items, list):
            source_counts[source.title()] = len(items)

    if source_counts:
        df_source = pd.DataFrame(
            list(source_counts.items()), columns=["Source", "Count"]
        )
        fig_source = px.pie(
            df_source,
            values="Count",
            names="Source",
            title="Content Distribution by Source",
        )
        charts["source_distribution"] = fig_source

    # Engagement distribution (if available)
    engagement_scores = []
    for _source, items in data.items():
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict) and "engagement_score" in item:
                    engagement_scores.append(item["engagement_score"])

    if engagement_scores:
        df_engagement = pd.DataFrame(engagement_scores, columns=["Engagement Score"])
        fig_engagement = px.histogram(
            df_engagement,
            x="Engagement Score",
            title="Engagement Score Distribution",
            nbins=20,
        )
        charts["engagement_distribution"] = fig_engagement

    return charts


def get_trending_content(data, limit=20):
    """Get trending content from all sources"""
    trending = []

    for source, items in data.items():
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict) and item.get("text"):
                    # Calculate engagement score if not present
                    engagement_score = item.get("engagement_score", 0)
                    if not engagement_score:
                        # Simple scoring based on available metrics
                        likes = item.get("like_count", 0) or item.get("likes", 0)
                        retweets = item.get("retweet_count", 0) or item.get(
                            "retweets", 0
                        )
                        engagement_score = min(100, (likes + retweets * 2) / 10)

                    trending.append(
                        {
                            "text": item["text"][:200] + "..."
                            if len(item["text"]) > 200
                            else item["text"],
                            "author": item.get("author", "Unknown"),
                            "source": source,
                            "engagement_score": engagement_score,
                            "like_count": item.get("like_count", 0)
                            or item.get("likes", 0),
                            "sentiment": item.get("sentiment", 0),
                            "timestamp": item.get("timestamp", "Unknown"),
                        }
                    )

    # Sort by engagement score and return top items
    trending.sort(key=lambda x: x["engagement_score"], reverse=True)
    return trending[:limit]


def get_cloud_crawler_status():
    """Get crawler status from Cloud Run service"""
    try:
        response = requests.get(
            "https://solana-crawler-128671663649.us-central1.run.app/status", timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def start_cloud_crawler():
    """Start the crawler on Cloud Run"""
    try:
        response = requests.post(
            "https://solana-crawler-128671663649.us-central1.run.app/start", timeout=10
        )
        if response.status_code == 200:
            return True, "Crawler started successfully!"
        else:
            return False, f"Failed to start crawler: HTTP {response.status_code}"
    except Exception as e:
        return False, f"Error starting crawler: {str(e)}"


def stop_cloud_crawler():
    """Stop the crawler on Cloud Run"""
    try:
        response = requests.post(
            "https://solana-crawler-128671663649.us-central1.run.app/stop", timeout=10
        )
        if response.status_code == 200:
            return True, "Crawler stopped successfully!"
        else:
            return False, f"Failed to stop crawler: HTTP {response.status_code}"
    except Exception as e:
        return False, f"Error stopping crawler: {str(e)}"


def main():
    # Header
    st.markdown(
        """
    <div class="main-header">
        <h1>🚀 Degen Digest - Cloud Intelligence Platform</h1>
        <p>Your Daily Crypto Intelligence Dashboard - Powered by Google Cloud</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Get data from cloud sources
    digest_content, digest_filename = get_latest_digest()
    data = get_raw_data()
    trending = get_trending_content(data, limit=15)
    status_data = get_cloud_crawler_status()
    crawler_analytics = get_crawler_analytics()
    engagement_metrics = get_engagement_metrics()

    # System Status Section
    st.markdown(
        '<div class="section-header"><h2>📊 Cloud System Status</h2></div>',
        unsafe_allow_html=True,
    )

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)

    total_items = sum(
        len(items) if isinstance(items, list) else 0 for items in data.values()
    )

    with col1:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-value">{total_items:,}</div>
            <div class="metric-label">Total Items (GCS)</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        active_sources = len([k for k, v in data.items() if v])
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-value">{active_sources}</div>
            <div class="metric-label">Active Sources</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        twitter_count = len(data.get("twitter", []))
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-value">{twitter_count}</div>
            <div class="metric-label">Twitter Posts</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col4:
        # Crawler status indicator
        status_class = (
            "status-running"
            if status_data.get("status") == "running"
            else "status-stopped"
            if status_data.get("status") == "stopped"
            else "status-unknown"
        )
        status_text = (
            "Running"
            if status_data.get("status") == "running"
            else "Stopped"
            if status_data.get("status") == "stopped"
            else "Unknown"
        )

        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-value">
                <span class="status-indicator {status_class}"></span>{status_text}
            </div>
            <div class="metric-label">Cloud Crawler</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Crawler Analytics Section
    if crawler_analytics:
        st.markdown(
            '<div class="section-header"><h2>🤖 Crawler Analytics</h2></div>',
            unsafe_allow_html=True,
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_crawls = crawler_analytics.get("session_stats", {}).get(
                "total_crawls", 0
            )
            st.metric("Total Crawls", total_crawls)

        with col2:
            successful_crawls = crawler_analytics.get("session_stats", {}).get(
                "successful_crawls", 0
            )
            st.metric("Successful Crawls", successful_crawls)

        with col3:
            total_tweets = crawler_analytics.get("session_stats", {}).get(
                "total_tweets_collected", 0
            )
            st.metric("Tweets Collected", total_tweets)

        with col4:
            last_crawl = crawler_analytics.get("session_stats", {}).get(
                "last_crawl_time", "Unknown"
            )
            if last_crawl != "Unknown":
                st.metric("Last Crawl", last_crawl[:10])  # Show just the date
            else:
                st.metric("Last Crawl", "Unknown")

    # Data Sources Section
    st.markdown(
        '<div class="section-header"><h2>📡 Data Sources</h2></div>',
        unsafe_allow_html=True,
    )

    # Show data source status
    source_cols = st.columns(5)
    sources = ["twitter", "reddit", "telegram", "news", "crypto"]

    for i, source in enumerate(sources):
        with source_cols[i]:
            source_data = data.get(source, [])
            count = len(source_data) if isinstance(source_data, list) else 0
            status = "✅ Active" if count > 0 else "❌ No Data"

            st.markdown(
                f"""
            <div class="metric-card">
                <div class="metric-value">{count}</div>
                <div class="metric-label">{source.title()}</div>
                <div style="font-size: 0.8rem; color: {'green' if count > 0 else 'red'};">{status}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    # Current Digest Section
    st.markdown(
        '<div class="section-header"><h2>📰 Latest Digest</h2></div>',
        unsafe_allow_html=True,
    )

    if digest_content:
        st.markdown(
            f"""
        <div class="digest-container">
            <h3>📄 {digest_filename}</h3>
            <div style="max-height: 400px; overflow-y: auto;">
                {digest_content}
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        st.warning("No digest content available")

    # Trending Content Section
    if trending:
        st.markdown(
            '<div class="section-header"><h2>🔥 Trending Content</h2></div>',
            unsafe_allow_html=True,
        )

        for i, item in enumerate(trending[:10]):
            engagement_color = (
                "#ff6b6b"
                if item["engagement_score"] > 50
                else "#ffa500"
                if item["engagement_score"] > 20
                else "#28a745"
            )

            st.markdown(
                f"""
            <div class="tweet-card">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <strong>@{item['author']}</strong> • <span style="color: #666;">{item['source'].title()}</span>
                        <div style="margin-top: 0.5rem;">{item['text']}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: {engagement_color}; font-weight: bold; font-size: 1.2rem;">
                            {item['engagement_score']:.1f}
                        </div>
                        <div style="font-size: 0.8rem; color: #666;">Engagement</div>
                    </div>
                </div>
                <div class="engagement-stats">
                    <div class="engagement-stat">
                        ❤️ {item['like_count']}
                    </div>
                    <div class="engagement-stat">
                        📊 {item.get('sentiment', 0):.2f}
                    </div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    # Crawler Controls Section
    st.markdown(
        '<div class="section-header"><h2>🎮 Crawler Controls</h2></div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🟢 Start Crawler", use_container_width=True):
            success, message = start_cloud_crawler()
            if success:
                st.success(message)
            else:
                st.error(message)

    with col2:
        if st.button("🔴 Stop Crawler", use_container_width=True):
            success, message = stop_cloud_crawler()
            if success:
                st.success(message)
            else:
                st.error(message)

    with col3:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()

    # Analytics Charts Section
    if data:
        st.markdown(
            '<div class="section-header"><h2>📈 Analytics</h2></div>',
            unsafe_allow_html=True,
        )

        charts = create_analytics_charts(data)

        if "source_distribution" in charts:
            st.plotly_chart(charts["source_distribution"], use_container_width=True)

        if "engagement_distribution" in charts:
            st.plotly_chart(charts["engagement_distribution"], use_container_width=True)

    # Footer
    st.markdown(
        """
    <div style="text-align: center; margin-top: 3rem; padding: 2rem; background: #f8f9fa; border-radius: 10px;">
        <p><strong>🚀 Degen Digest</strong> - Powered by Google Cloud Platform</p>
        <p style="font-size: 0.9rem; color: #666;">
            Data sourced from Twitter, Reddit, Telegram, News APIs, and CoinGecko
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
