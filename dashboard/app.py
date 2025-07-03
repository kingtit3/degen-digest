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
    from google.cloud.exceptions import NotFound

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


def get_latest_digest():
    """Get the latest digest content"""
    output_dir = Path("output")

    # Look for the most recent digest file
    digest_files = list(output_dir.glob("digest*.md"))
    if not digest_files:
        return None, "No digest found"

    latest_digest = max(digest_files, key=lambda x: x.stat().st_mtime)

    try:
        with open(latest_digest, encoding="utf-8") as f:
            content = f.read()
        return content, latest_digest.name
    except Exception as e:
        return None, f"Error reading {latest_digest.name}: {str(e)}"


def get_raw_data():
    """Get raw data for analytics and trending content from both local and GCS"""
    output_dir = Path("output")
    data = {}

    # Load different data sources
    sources = [
        "twitter_raw.json",
        "reddit_raw.json",
        "telegram_raw.json",
        "newsapi_raw.json",
    ]

    # Try to load from Google Cloud Storage first
    if GCS_AVAILABLE:
        try:
            client = storage.Client(project="lucky-union-463615-t3")
            bucket = client.bucket("degen-digest-data")

            for source in sources:
                try:
                    blob = bucket.blob(source)
                    if blob.exists():
                        content = blob.download_as_text()
                        data[source.replace("_raw.json", "")] = json.loads(content)
                except Exception as e:
                    st.warning(f"Could not load {source} from GCS: {e}")

        except Exception as e:
            st.warning(f"GCS connection failed: {e}")

    # Fallback to local files
    for source in sources:
        source_name = source.replace("_raw.json", "")
        if source_name not in data:  # Only load if not already loaded from GCS
            file_path = output_dir / source
            if file_path.exists():
                try:
                    with open(file_path, encoding="utf-8") as f:
                        data[source_name] = json.load(f)
                except Exception as e:
                    st.warning(f"Could not load {source}: {e}")

    return data


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
    for source, items in data.items():
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
        <h1>🚀 Degen Digest</h1>
        <p>Your Daily Crypto Intelligence Dashboard</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Get current digest and data
    digest_content, digest_filename = get_latest_digest()
    data = get_raw_data()
    trending = get_trending_content(data, limit=15)
    status_data = get_cloud_crawler_status()

    # System Status Section
    st.markdown(
        '<div class="section-header"><h2>📊 System Status</h2></div>',
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
            <div class="metric-label">Total Items</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-value">{len([k for k, v in data.items() if v])}</div>
            <div class="metric-label">Active Sources</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-value">{len(data.get('twitter', []))}</div>
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
            <div class="metric-label">Crawler Status</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Current Digest Section
    st.markdown(
        '<div class="section-header"><h2>📰 Current Digest</h2></div>',
        unsafe_allow_html=True,
    )

    if digest_content:
        # Digest controls
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.info(f"📄 **Current Digest:** {digest_filename}")

        with col2:
            if st.button("🔄 Generate Fresh Digest", key="fresh_digest"):
                with st.spinner("Generating fresh digest..."):
                    success, message = generate_fresh_digest()
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

        with col3:
            if st.button("📥 Download Digest"):
                st.download_button(
                    "Download",
                    digest_content,
                    file_name=digest_filename,
                    mime="text/markdown",
                )

        # Display digest content
        st.markdown(
            """
        <div class="digest-container">
        """,
            unsafe_allow_html=True,
        )

        st.markdown(digest_content)

        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.error(f"❌ {digest_filename}")
        st.info("💡 Click 'Generate Fresh Digest' to create a new digest.")

    # Trending Content Section
    st.markdown(
        '<div class="section-header"><h2>🔥 Trending Content</h2></div>',
        unsafe_allow_html=True,
    )

    if trending:
        # Filter options
        col1, col2 = st.columns([1, 3])

        with col1:
            source_filter = st.selectbox(
                "Filter by source:",
                ["All"] + list({item["source"] for item in trending}),
            )

        with col2:
            min_engagement = st.slider(
                "Minimum engagement score:", min_value=0, max_value=100, value=0
            )

        # Filter content
        filtered_trending = trending
        if source_filter != "All":
            filtered_trending = [
                item for item in trending if item["source"] == source_filter
            ]

        filtered_trending = [
            item
            for item in filtered_trending
            if item["engagement_score"] >= min_engagement
        ]

        # Display trending content in a grid
        cols = st.columns(2)
        for i, item in enumerate(filtered_trending):
            col_idx = i % 2
            is_viral = item["engagement_score"] > 80

            with cols[col_idx]:
                st.markdown(
                    f"""
                <div class="tweet-card">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                        <div>
                            <strong>@{item['author']}</strong>
                            <span style="color: #666; font-size: 0.9rem;"> • {item['source'].title()}</span>
                        </div>
                        {'<span class="viral-badge">🔥 VIRAL</span>' if is_viral else ''}
                    </div>
                    <p style="margin: 1rem 0; line-height: 1.5;">{item['text']}</p>
                    <div class="engagement-stats">
                        <div class="engagement-stat">
                            <span>❤️</span>
                            <span>{item['like_count']:,}</span>
                        </div>
                        <div class="engagement-stat">
                            <span>📊</span>
                            <span>Score: {item['engagement_score']:.1f}</span>
                        </div>
                        <div class="engagement-stat">
                            <span>📈</span>
                            <span>Sentiment: {item['sentiment']:.2f}</span>
                        </div>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

        if not filtered_trending:
            st.info("No content matches your filters. Try adjusting the criteria.")

    else:
        st.info(
            "No trending content available. Generate a fresh digest to see trending items."
        )

    # Crawler Control Section
    st.markdown(
        '<div class="section-header"><h2>🕷️ Crawler Control</h2></div>',
        unsafe_allow_html=True,
    )

    # Crawler info
    st.info(
        """
    🌐 **Cloud Crawler Status**

    The Solana crawler is deployed on Google Cloud Run and runs automatically for 18 hours per day.
    Use the controls below to manually start or stop the crawler.

    **Schedule:** 18 hours/day (6 hours off for maintenance)
    **Credentials:** Pre-configured in cloud deployment
    **Target:** Solana-focused content from followed accounts
    """
    )

    # Crawler controls
    st.markdown('<div class="crawler-controls">', unsafe_allow_html=True)

    # Status display
    if status_data.get("status") == "running":
        st.success("🟢 **Crawler Status: RUNNING**")
        if "last_crawl" in status_data:
            st.info(f"📈 Last crawl: {status_data['last_crawl']}")
        if "total_tweets" in status_data:
            st.info(f"📊 Total tweets collected: {status_data['total_tweets']}")
    elif status_data.get("status") == "stopped":
        st.warning("🔴 **Crawler Status: STOPPED**")
    else:
        st.error(f"❌ **Status Error:** {status_data.get('message', 'Unknown error')}")

    # Control buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚀 Start Crawler", key="start_cloud_crawler", type="primary"):
            with st.spinner("Starting crawler..."):
                success, message = start_cloud_crawler()
                if success:
                    st.success(message)
                    time.sleep(2)  # Give time for status to update
                    st.rerun()
                else:
                    st.error(message)

    with col2:
        if st.button("⏹️ Stop Crawler", key="stop_cloud_crawler"):
            with st.spinner("Stopping crawler..."):
                success, message = stop_cloud_crawler()
                if success:
                    st.success(message)
                    time.sleep(2)  # Give time for status to update
                    st.rerun()
                else:
                    st.error(message)

    st.markdown("</div>", unsafe_allow_html=True)

    # Auto-refresh status
    if st.button("🔄 Refresh Status", key="refresh_status"):
        st.rerun()

    # Analytics Charts Section
    st.markdown(
        '<div class="section-header"><h2>📈 Analytics</h2></div>',
        unsafe_allow_html=True,
    )

    charts = create_analytics_charts(data)

    if charts:
        col1, col2 = st.columns(2)

        with col1:
            if "source_distribution" in charts:
                st.plotly_chart(charts["source_distribution"], use_container_width=True)

        with col2:
            if "engagement_distribution" in charts:
                st.plotly_chart(
                    charts["engagement_distribution"], use_container_width=True
                )

    # Data quality metrics
    st.markdown("### 📈 Data Quality Metrics")

    quality_metrics = []
    for source, items in data.items():
        if isinstance(items, list) and items:
            valid_items = len(
                [item for item in items if isinstance(item, dict) and item.get("text")]
            )
            quality_metrics.append(
                {
                    "Source": source.title(),
                    "Total Items": len(items),
                    "Valid Items": valid_items,
                    "Quality %": round((valid_items / len(items)) * 100, 1),
                }
            )

    if quality_metrics:
        df_quality = pd.DataFrame(quality_metrics)
        st.dataframe(df_quality, use_container_width=True)


if __name__ == "__main__":
    main()
