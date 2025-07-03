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

    .tab-container {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
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
                cloud_path = f"data/{source}"
                blob = bucket.blob(cloud_path)

                if blob.exists():
                    try:
                        # Download to memory and parse
                        content = blob.download_as_text()
                        data[source.replace("_raw.json", "")] = json.loads(content)
                        st.sidebar.success(f"✅ Loaded {source} from GCS")
                    except Exception as e:
                        st.sidebar.warning(f"⚠️ Error loading {source} from GCS: {e}")
                        data[source.replace("_raw.json", "")] = []
                else:
                    data[source.replace("_raw.json", "")] = []

        except Exception as e:
            st.sidebar.warning(f"⚠️ GCS not available: {e}")
            # Fall back to local files

    # Fall back to local files if GCS failed or not available
    for source in sources:
        if (
            source.replace("_raw.json", "") not in data
            or not data[source.replace("_raw.json", "")]
        ):
            file_path = output_dir / source
            if file_path.exists():
                try:
                    with open(file_path, encoding="utf-8") as f:
                        data[source.replace("_raw.json", "")] = json.load(f)
                except:
                    data[source.replace("_raw.json", "")] = []
            else:
                data[source.replace("_raw.json", "")] = []

    return data


def generate_fresh_digest():
    """Generate a fresh digest"""
    try:
        # Import and run main digest generation
        from main import main as run_digest

        run_digest()
        return True, "Digest generated successfully!"
    except Exception as e:
        return False, f"Error generating digest: {str(e)}"


def create_analytics_charts(data):
    """Create analytics charts"""
    charts = {}

    # Source distribution
    source_counts = {}
    for source, items in data.items():
        if isinstance(items, list):
            source_counts[source.title()] = len(items)

    if source_counts:
        fig_source = px.pie(
            values=list(source_counts.values()),
            names=list(source_counts.keys()),
            title="Data Source Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        fig_source.update_layout(height=400)
        charts["source_distribution"] = fig_source

    # Engagement analysis (if available)
    all_items = []
    for source, items in data.items():
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    item["source"] = source
                    all_items.append(item)

    if all_items:
        # Engagement scores
        engagement_scores = [
            item.get("engagement_score", 0)
            for item in all_items
            if item.get("engagement_score")
        ]
        if engagement_scores:
            fig_engagement = px.histogram(
                x=engagement_scores,
                title="Engagement Score Distribution",
                nbins=20,
                color_discrete_sequence=["#667eea"],
            )
            fig_engagement.update_layout(
                height=400, xaxis_title="Engagement Score", yaxis_title="Count"
            )
            charts["engagement_distribution"] = fig_engagement

    return charts


def get_trending_content(data, limit=20):
    """Get trending content in Twitter-style format"""
    trending = []

    for source, items in data.items():
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    # Extract relevant information
                    text = item.get("text", item.get("title", item.get("content", "")))
                    if text:
                        trending.append(
                            {
                                "source": source,
                                "text": text[:200] + "..." if len(text) > 200 else text,
                                "engagement_score": item.get("engagement_score", 0),
                                "like_count": item.get(
                                    "likeCount", item.get("score", 0)
                                ),
                                "timestamp": item.get(
                                    "created_at", item.get("timestamp", "")
                                ),
                                "author": item.get("user", {}).get(
                                    "screen_name", item.get("author", "Unknown")
                                ),
                                "url": item.get("url", ""),
                                "sentiment": item.get("sentiment", {}).get(
                                    "compound", 0
                                ),
                            }
                        )

    # Sort by engagement score
    trending.sort(key=lambda x: x["engagement_score"], reverse=True)
    return trending[:limit]


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

    # Get current digest
    digest_content, digest_filename = get_latest_digest()

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📰 Current Digest", "📊 Analytics", "🔥 Trending", "🕷️ Solana Crawler Control"]
    )

    with tab1:
        st.markdown("### 📰 Current Digest")

        if digest_content:
            # Digest info
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
            st.markdown("---")
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

    with tab2:
        st.markdown("### 📊 Analytics Dashboard")

        # Get raw data for analytics
        data = get_raw_data()

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
            st.markdown(
                f"""
            <div class="metric-card">
                <div class="metric-value">{len(data.get('reddit', []))}</div>
                <div class="metric-label">Reddit Posts</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Charts
        charts = create_analytics_charts(data)

        if charts:
            col1, col2 = st.columns(2)

            with col1:
                if "source_distribution" in charts:
                    st.plotly_chart(
                        charts["source_distribution"], use_container_width=True
                    )

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
                    [
                        item
                        for item in items
                        if isinstance(item, dict) and item.get("text")
                    ]
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

    with tab3:
        st.markdown("### 🔥 Trending Content")

        # Get trending content
        data = get_raw_data()
        trending = get_trending_content(data, limit=30)

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

            # Display trending content
            for i, item in enumerate(filtered_trending):
                # Determine if viral
                is_viral = item["engagement_score"] > 80

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

    with tab4:
        st.markdown("### 🕷️ Solana Crawler Control")

        # Info about the cloud deployment
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

        # Get current status
        status_data = get_cloud_crawler_status()

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
            st.error(
                f"❌ **Status Error:** {status_data.get('message', 'Unknown error')}"
            )

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

        # Crawler information
        st.markdown("#### 📋 Crawler Information")

        st.markdown(
            """
        **🌐 Cloud Deployment Details:**
        - **Service URL:** https://solana-crawler-128671663649.us-central1.run.app
        - **Region:** us-central1
        - **Platform:** Google Cloud Run
        - **Architecture:** linux/amd64

        **🎯 Crawler Features:**
        - Solana-focused content collection
        - Followed accounts monitoring
        - For You page scanning
        - Saved post comments
        - Discovered user content

        **⏰ Automatic Schedule:**
        - Runs 18 hours per day
        - 6-hour maintenance window
        - Automatic restart on failure
        - Health monitoring enabled
        """
        )

        # Recent activity (if available)
        if status_data.get("status") == "running" and "recent_activity" in status_data:
            st.markdown("#### 📝 Recent Activity")

            for activity in status_data["recent_activity"][:5]:
                st.markdown(
                    f"""
                <div class="log-entry">
                    <strong>{activity.get('timestamp', 'Unknown')}</strong>: {activity.get('message', 'No message')}
                </div>
                """,
                    unsafe_allow_html=True,
                )


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


if __name__ == "__main__":
    main()
