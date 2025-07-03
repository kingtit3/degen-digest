#!/usr/bin/env python3
"""
Data Sync Dashboard Page
Shows data synchronization status and allows merging local/cloud data.
"""

import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# Page config
st.set_page_config(page_title="Data Sync - Degen Digest", page_icon="🔄", layout="wide")

st.title("🔄 Data Synchronization & Merging")


# Load consolidated data
@st.cache_data(ttl=300)
def load_consolidated_data():
    """Load consolidated data from the merger"""
    consolidated_file = Path("output/consolidated_data.json")
    if not consolidated_file.exists():
        return None

    try:
        with open(consolidated_file) as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading consolidated data: {e}")
        return None


# Load merge report
@st.cache_data(ttl=300)
def load_merge_report():
    """Load merge report"""
    report_file = Path("output/merge_report.json")
    if not report_file.exists():
        return None

    try:
        with open(report_file) as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading merge report: {e}")
        return None


# Load processed data for dashboard
@st.cache_data(ttl=300)
def load_dashboard_data():
    """Load processed data for dashboard"""
    dashboard_file = Path("output/dashboard_processed_data.json")
    if not dashboard_file.exists():
        return None

    try:
        with open(dashboard_file) as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading dashboard data: {e}")
        return None


# Main content
consolidated_data = load_consolidated_data()
merge_report = load_merge_report()
dashboard_data = load_dashboard_data()

if not consolidated_data:
    st.warning("No consolidated data found. Run the data merger first.")
    st.stop()

# Sidebar controls
st.sidebar.header("🔄 Sync Controls")

# Data overview
st.sidebar.subheader("📊 Data Overview")
if consolidated_data and "metadata" in consolidated_data:
    metadata = consolidated_data["metadata"]
    st.sidebar.metric("Total Items", metadata.get("total_items", 0))
    st.sidebar.metric("Sources", len(metadata.get("sources", [])))
    st.sidebar.metric("Last Updated", metadata.get("last_updated", "Unknown"))

# Sync actions
st.sidebar.subheader("🔄 Sync Actions")

if st.sidebar.button("🔄 Run Data Merger"):
    with st.spinner("Running data merger..."):
        import subprocess

        try:
            result = subprocess.run(
                ["python", "scripts/merge_local_cloud_data.py"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                st.success("Data merger completed successfully!")
                st.rerun()
            else:
                st.error(f"Data merger failed: {result.stderr}")
        except Exception as e:
            st.error(f"Error running data merger: {e}")

if st.sidebar.button("☁️ Upload to Cloud"):
    with st.spinner("Uploading to cloud..."):
        import subprocess

        try:
            result = subprocess.run(
                ["python", "scripts/cloud_storage_sync.py", "--direction", "upload"],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                st.success("Upload to cloud completed!")
            else:
                st.error(f"Upload failed: {result.stderr}")
        except Exception as e:
            st.error(f"Error uploading to cloud: {e}")

if st.sidebar.button("⬇️ Download from Cloud"):
    with st.spinner("Downloading from cloud..."):
        import subprocess

        try:
            result = subprocess.run(
                ["python", "scripts/cloud_storage_sync.py", "--direction", "download"],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                st.success("Download from cloud completed!")
                st.rerun()
            else:
                st.error(f"Download failed: {result.stderr}")
        except Exception as e:
            st.error(f"Error downloading from cloud: {e}")

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Data Overview", "🔄 Sync Status", "📈 Analytics", "🔧 Manual Sync"]
)

with tab1:
    st.subheader("📊 Consolidated Data Overview")

    # Data sources summary
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        tweets = consolidated_data.get("tweets", [])
        st.metric("Tweets", len(tweets))

    with col2:
        reddit_posts = consolidated_data.get("reddit_posts", [])
        st.metric("Reddit Posts", len(reddit_posts))

    with col3:
        telegram_messages = consolidated_data.get("telegram_messages", [])
        st.metric("Telegram Messages", len(telegram_messages))

    with col4:
        news_articles = consolidated_data.get("news_articles", [])
        st.metric("News Articles", len(news_articles))

    # Data timeline
    st.subheader("📅 Data Timeline")

    # Create timeline data
    timeline_data = []

    for tweet in tweets[:100]:  # Sample for performance
        if "createdAt" in tweet:
            try:
                date = pd.to_datetime(tweet["createdAt"]).date()
                timeline_data.append({"date": date, "source": "Twitter", "count": 1})
            except:
                pass

    for post in reddit_posts:
        if "published" in post:
            try:
                date = pd.to_datetime(post["published"]).date()
                timeline_data.append({"date": date, "source": "Reddit", "count": 1})
            except:
                pass

    if timeline_data:
        df_timeline = pd.DataFrame(timeline_data)
        daily_counts = df_timeline.groupby(["date", "source"]).count().reset_index()

        fig = px.line(
            daily_counts,
            x="date",
            y="count",
            color="source",
            title="Daily Data Volume by Source",
        )
        st.plotly_chart(fig, use_container_width=True)

    # Source distribution
    st.subheader("📊 Source Distribution")

    source_counts = {
        "Twitter": len(tweets),
        "Reddit": len(reddit_posts),
        "Telegram": len(telegram_messages),
        "News": len(news_articles),
        "Crypto": len(consolidated_data.get("crypto_data", [])),
    }

    fig = px.pie(
        values=list(source_counts.values()),
        names=list(source_counts.keys()),
        title="Data Distribution by Source",
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("🔄 Synchronization Status")

    if merge_report:
        st.json(merge_report)
    else:
        st.warning("No merge report found. Run the data merger first.")

    # File status
    st.subheader("📁 File Status")

    important_files = [
        "twitter_raw.json",
        "reddit_raw.json",
        "telegram_raw.json",
        "newsapi_raw.json",
        "coingecko_raw.json",
        "consolidated_data.json",
        "dashboard_processed_data.json",
        "degen_digest.db",
    ]

    file_status = []
    for filename in important_files:
        file_path = Path(f"output/{filename}")
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            file_status.append(
                {
                    "File": filename,
                    "Status": "✅ Present",
                    "Size (MB)": f"{size_mb:.2f}",
                    "Last Modified": datetime.fromtimestamp(
                        file_path.stat().st_mtime
                    ).strftime("%Y-%m-%d %H:%M"),
                }
            )
        else:
            file_status.append(
                {
                    "File": filename,
                    "Status": "❌ Missing",
                    "Size (MB)": "0.00",
                    "Last Modified": "N/A",
                }
            )

    df_status = pd.DataFrame(file_status)
    st.dataframe(df_status, use_container_width=True)

with tab3:
    st.subheader("📈 Enhanced Analytics")

    if dashboard_data:
        # Viral predictions analysis
        st.subheader("🔮 Viral Predictions")

        viral_scores = []
        for item in dashboard_data:
            if "viral_score" in item:
                viral_scores.append(item["viral_score"])

        if viral_scores:
            col1, col2 = st.columns(2)

            with col1:
                fig = px.histogram(
                    x=viral_scores,
                    title="Viral Score Distribution",
                    labels={"x": "Viral Score", "y": "Count"},
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.metric(
                    "Average Viral Score", f"{sum(viral_scores)/len(viral_scores):.2f}"
                )
                st.metric("Max Viral Score", f"{max(viral_scores):.2f}")
                st.metric("Min Viral Score", f"{min(viral_scores):.2f}")

        # Top viral content
        st.subheader("🔥 Top Viral Content")

        top_viral = sorted(
            dashboard_data, key=lambda x: x.get("viral_score", 0), reverse=True
        )[:10]

        for i, item in enumerate(top_viral[:5]):
            with st.expander(f"#{i+1} - {item.get('title', 'No title')[:50]}..."):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Viral Score:** {item.get('viral_score', 0):.2f}")
                    st.write(f"**Source:** {item.get('source', 'unknown')}")
                    st.write(f"**Engagement:** {item.get('engagement_score', 0):.2f}")
                with col2:
                    st.write(f"**Text:** {item.get('text', '')[:200]}...")
                    if item.get("url"):
                        st.write(f"**URL:** {item['url']}")
    else:
        st.warning("No enhanced dashboard data found. Run the enhanced pipeline first.")

with tab4:
    st.subheader("🔧 Manual Data Operations")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📤 Export Data")

        if st.button("Export Consolidated Data"):
            if consolidated_data:
                # Create download link
                import io

                buffer = io.StringIO()
                json.dump(consolidated_data, buffer, indent=2, default=str)

                st.download_button(
                    label="Download Consolidated Data (JSON)",
                    data=buffer.getvalue(),
                    file_name=f"consolidated_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                )

        if st.button("Export as CSV"):
            if dashboard_data:
                df = pd.DataFrame(dashboard_data)
                csv = df.to_csv(index=False)

                st.download_button(
                    label="Download as CSV",
                    data=csv,
                    file_name=f"dashboard_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                )

    with col2:
        st.subheader("🗑️ Clean Data")

        if st.button("Clear Cache"):
            st.cache_data.clear()
            st.success("Cache cleared!")
            st.rerun()

        if st.button("Regenerate Consolidated Data"):
            with st.spinner("Regenerating..."):
                import subprocess

                try:
                    result = subprocess.run(
                        ["python", "scripts/merge_local_cloud_data.py"],
                        capture_output=True,
                        text=True,
                        timeout=60,
                    )
                    if result.returncode == 0:
                        st.success("Data regenerated!")
                        st.rerun()
                    else:
                        st.error(f"Regeneration failed: {result.stderr}")
                except Exception as e:
                    st.error(f"Error regenerating data: {e}")

# Footer
st.markdown("---")
st.markdown("*Data synchronization and merging tools for Degen Digest*")
