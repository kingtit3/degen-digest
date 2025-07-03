import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, func, select

from storage.db import Digest, RedditPost, Tweet, engine
from utils.advanced_logging import get_logger
from utils.monitoring import system_monitor

logger = get_logger(__name__)


def load_metrics_data():
    """Load metrics from files and database"""
    metrics_file = Path("output/system_metrics.json")
    alerts_file = Path("output/system_alerts.json")

    metrics = {}
    alerts = []

    if metrics_file.exists():
        try:
            with open(metrics_file) as f:
                metrics = json.load(f)
        except Exception as e:
            st.error(f"Error loading metrics: {e}")

    if alerts_file.exists():
        try:
            with open(alerts_file) as f:
                alerts = json.load(f)
        except Exception as e:
            st.error(f"Error loading alerts: {e}")

    return metrics, alerts


def get_database_metrics():
    """Get real-time database metrics"""
    try:
        with Session(engine) as session:
            # Get counts
            tweet_count = session.exec(select(func.count()).select_from(Tweet)).one()
            reddit_count = session.exec(
                select(func.count()).select_from(RedditPost)
            ).one()
            digest_count = session.exec(select(func.count()).select_from(Digest)).one()

            # Get recent activity (last 24 hours)
            cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
            recent_tweets = session.exec(
                select(func.count())
                .select_from(Tweet)
                .where(Tweet.created_at >= cutoff)
            ).one()

            recent_reddit = session.exec(
                select(func.count())
                .select_from(RedditPost)
                .where(RedditPost.created_at >= cutoff)
            ).one()

            # Get latest data timestamp
            latest_tweet = session.exec(
                select(Tweet).order_by(Tweet.created_at.desc()).limit(1)
            ).first()

            latest_reddit = session.exec(
                select(RedditPost).order_by(RedditPost.created_at.desc()).limit(1)
            ).first()

            # Calculate data freshness
            tweet_freshness = None
            reddit_freshness = None

            if latest_tweet:
                tweet_freshness = (
                    datetime.now(timezone.utc) - latest_tweet.created_at
                ).total_seconds() / 3600

            if latest_reddit:
                reddit_freshness = (
                    datetime.now(timezone.utc) - latest_reddit.created_at
                ).total_seconds() / 3600

            return {
                "tweet_count": tweet_count,
                "reddit_count": reddit_count,
                "digest_count": digest_count,
                "recent_tweets_24h": recent_tweets,
                "recent_reddit_24h": recent_reddit,
                "tweet_freshness_hours": tweet_freshness,
                "reddit_freshness_hours": reddit_freshness,
            }
    except Exception as e:
        st.error(f"Database error: {e}")
        return {}


def run_system_monitoring():
    """Run comprehensive system monitoring"""
    try:
        with st.spinner("Running system monitoring..."):
            metrics = system_monitor.run_comprehensive_monitoring()
        return metrics
    except Exception as e:
        st.error(f"Monitoring failed: {e}")
        return {}


def display_system_overview(metrics):
    """Display system overview with key metrics"""
    st.header("🖥️ System Overview")

    if not metrics:
        st.warning("No system metrics available")
        return

    # Create overview cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if "system" in metrics:
            cpu = metrics["system"].get("cpu_percent", 0)
            st.metric("CPU Usage", f"{cpu:.1f}%")

            # Color based on usage
            if cpu > 80:
                st.error("High CPU usage detected")
            elif cpu > 60:
                st.warning("Moderate CPU usage")
            else:
                st.success("Normal CPU usage")

    with col2:
        if "system" in metrics:
            memory = metrics["system"].get("memory_percent", 0)
            st.metric("Memory Usage", f"{memory:.1f}%")

            if memory > 85:
                st.error("High memory usage detected")
            elif memory > 70:
                st.warning("Moderate memory usage")
            else:
                st.success("Normal memory usage")

    with col3:
        if "database" in metrics:
            status = metrics["database"].get("overall_status", "unknown")
            st.metric("Database Status", status.title())

            if status == "critical":
                st.error("Critical database issues")
            elif status == "warning":
                st.warning("Database warnings")
            else:
                st.success("Database healthy")

    with col4:
        if "cloud_function" in metrics:
            func_status = metrics["cloud_function"].get("function_status", "unknown")
            st.metric("Cloud Function", func_status.title())

            if func_status == "error":
                st.error("Cloud function errors")
            elif func_status == "unhealthy":
                st.warning("Cloud function issues")
            else:
                st.success("Cloud function healthy")


def display_performance_metrics(metrics):
    """Display performance metrics with charts"""
    st.header("📊 Performance Metrics")

    if not metrics:
        st.warning("No performance data available")
        return

    # System performance chart
    if "system" in metrics:
        st.subheader("System Resources")

        # Create performance chart
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=("CPU Usage", "Memory Usage", "Disk Usage", "Network I/O"),
            specs=[
                [{"type": "indicator"}, {"type": "indicator"}],
                [{"type": "indicator"}, {"type": "bar"}],
            ],
        )

        # CPU gauge
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=metrics["system"].get("cpu_percent", 0),
                title={"text": "CPU %"},
                gauge={
                    "axis": {"range": [None, 100]},
                    "bar": {"color": "darkblue"},
                    "steps": [
                        {"range": [0, 50], "color": "lightgray"},
                        {"range": [50, 80], "color": "yellow"},
                        {"range": [80, 100], "color": "red"},
                    ],
                },
            ),
            row=1,
            col=1,
        )

        # Memory gauge
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=metrics["system"].get("memory_percent", 0),
                title={"text": "Memory %"},
                gauge={
                    "axis": {"range": [None, 100]},
                    "bar": {"color": "darkgreen"},
                    "steps": [
                        {"range": [0, 70], "color": "lightgray"},
                        {"range": [70, 85], "color": "yellow"},
                        {"range": [85, 100], "color": "red"},
                    ],
                },
            ),
            row=1,
            col=2,
        )

        # Disk gauge
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=metrics["system"].get("disk_percent", 0),
                title={"text": "Disk %"},
                gauge={
                    "axis": {"range": [None, 100]},
                    "bar": {"color": "darkred"},
                    "steps": [
                        {"range": [0, 80], "color": "lightgray"},
                        {"range": [80, 90], "color": "yellow"},
                        {"range": [90, 100], "color": "red"},
                    ],
                },
            ),
            row=2,
            col=1,
        )

        # Network I/O
        network_sent = metrics["system"].get("network_bytes_sent", 0) / (1024**2)  # MB
        network_recv = metrics["system"].get("network_bytes_recv", 0) / (1024**2)  # MB

        fig.add_trace(
            go.Bar(
                x=["Sent", "Received"],
                y=[network_sent, network_recv],
                name="Network I/O (MB)",
                marker_color=["blue", "green"],
            ),
            row=2,
            col=2,
        )

        fig.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)


def display_database_health(metrics):
    """Display database health metrics"""
    st.header("🗄️ Database Health")

    db_metrics = get_database_metrics()

    if not db_metrics:
        st.warning("No database metrics available")
        return

    # Database overview
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Tweets", f"{db_metrics.get('tweet_count', 0):,}")

    with col2:
        st.metric("Total Reddit Posts", f"{db_metrics.get('reddit_count', 0):,}")

    with col3:
        st.metric("Total Digests", f"{db_metrics.get('digest_count', 0):,}")

    with col4:
        recent_total = db_metrics.get("recent_tweets_24h", 0) + db_metrics.get(
            "recent_reddit_24h", 0
        )
        st.metric("Recent Activity (24h)", f"{recent_total:,}")

    # Data freshness
    st.subheader("Data Freshness")

    col1, col2 = st.columns(2)

    with col1:
        tweet_freshness = db_metrics.get("tweet_freshness_hours")
        if tweet_freshness is not None:
            st.metric("Tweet Data Age", f"{tweet_freshness:.1f} hours")

            if tweet_freshness > 24:
                st.error("Tweet data is stale (>24 hours)")
            elif tweet_freshness > 6:
                st.warning("Tweet data is getting old (>6 hours)")
            else:
                st.success("Tweet data is fresh")

    with col2:
        reddit_freshness = db_metrics.get("reddit_freshness_hours")
        if reddit_freshness is not None:
            st.metric("Reddit Data Age", f"{reddit_freshness:.1f} hours")

            if reddit_freshness > 24:
                st.error("Reddit data is stale (>24 hours)")
            elif reddit_freshness > 6:
                st.warning("Reddit data is getting old (>6 hours)")
            else:
                st.success("Reddit data is fresh")

    # Recent activity chart
    st.subheader("Recent Activity")

    activity_data = {
        "Source": ["Tweets", "Reddit Posts"],
        "Count (24h)": [
            db_metrics.get("recent_tweets_24h", 0),
            db_metrics.get("recent_reddit_24h", 0),
        ],
    }

    df_activity = pd.DataFrame(activity_data)

    fig = px.bar(
        df_activity,
        x="Source",
        y="Count (24h)",
        title="Data Collection Activity (Last 24 Hours)",
        color="Source",
        color_discrete_map={"Tweets": "blue", "Reddit Posts": "orange"},
    )

    st.plotly_chart(fig, use_container_width=True)


def display_alerts(alerts):
    """Display system alerts"""
    st.header("🚨 System Alerts")

    if not alerts:
        st.success("No active alerts - system is healthy!")
        return

    # Filter alerts by severity
    critical_alerts = [a for a in alerts if a.get("level") == "critical"]
    warning_alerts = [a for a in alerts if a.get("level") == "warning"]

    # Display critical alerts first
    if critical_alerts:
        st.error("🚨 Critical Alerts")
        for alert in critical_alerts:
            with st.expander(f"Critical: {alert.get('message', 'Unknown error')}"):
                st.write(f"**Category:** {alert.get('category', 'Unknown')}")
                st.write(f"**Time:** {alert.get('timestamp', 'Unknown')}")
                st.write(
                    f"**Recommendation:** {alert.get('recommendation', 'No recommendation')}"
                )

    # Display warning alerts
    if warning_alerts:
        st.warning("⚠️ Warning Alerts")
        for alert in warning_alerts:
            with st.expander(f"Warning: {alert.get('message', 'Unknown warning')}"):
                st.write(f"**Category:** {alert.get('category', 'Unknown')}")
                st.write(f"**Time:** {alert.get('timestamp', 'Unknown')}")
                st.write(
                    f"**Recommendation:** {alert.get('recommendation', 'No recommendation')}"
                )


def display_api_health(metrics):
    """Display API health status"""
    st.header("🔌 API Health")

    if "apis" not in metrics or "apis" not in metrics["apis"]:
        st.warning("No API health data available")
        return

    api_data = metrics["apis"]["apis"]

    # Create API status table
    api_status_data = []
    for api_name, api_info in api_data.items():
        status = api_info.get("status", "unknown")
        response_time = api_info.get("response_time_ms", 0)
        status_code = api_info.get("status_code", 0)

        api_status_data.append(
            {
                "API": api_name.title(),
                "Status": status.title(),
                "Response Time (ms)": f"{response_time:.1f}",
                "Status Code": status_code,
            }
        )

    df_api = pd.DataFrame(api_status_data)

    # Color code the status
    def color_status(val):
        if val == "Healthy":
            return "background-color: lightgreen"
        elif val == "Unhealthy":
            return "background-color: lightcoral"
        else:
            return "background-color: lightyellow"

    st.dataframe(
        df_api.style.applymap(color_status, subset=["Status"]), use_container_width=True
    )


def display_data_quality(metrics):
    """Display data quality metrics"""
    st.header("📈 Data Quality")

    if "data_quality" not in metrics:
        st.warning("No data quality metrics available")
        return

    dq_metrics = metrics["data_quality"]

    # Data quality score
    quality_score = dq_metrics.get("data_quality_score", 100)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Data Quality Score", f"{quality_score:.1f}/100")

        if quality_score < 70:
            st.error("Low data quality detected")
        elif quality_score < 85:
            st.warning("Moderate data quality")
        else:
            st.success("High data quality")

    with col2:
        duplicate_count = dq_metrics.get("duplicate_tweets", 0)
        st.metric("Duplicate Tweets", duplicate_count)

        if duplicate_count > 10:
            st.warning("High number of duplicates")

    with col3:
        malformed_count = dq_metrics.get("malformed_tweets", 0)
        st.metric("Malformed Tweets", malformed_count)

        if malformed_count > 5:
            st.warning("Data quality issues detected")

    # Data quality chart
    quality_data = {
        "Metric": ["Quality Score", "Duplicates", "Malformed"],
        "Value": [
            quality_score,
            dq_metrics.get("duplicate_tweets", 0),
            dq_metrics.get("malformed_tweets", 0),
        ],
    }

    df_quality = pd.DataFrame(quality_data)

    fig = px.bar(
        df_quality,
        x="Metric",
        y="Value",
        title="Data Quality Metrics",
        color="Metric",
        color_discrete_map={
            "Quality Score": "green",
            "Duplicates": "orange",
            "Malformed": "red",
        },
    )

    st.plotly_chart(fig, use_container_width=True)


def main():
    st.set_page_config(
        page_title="Health Monitor - Degen Digest", page_icon="🏥", layout="wide"
    )

    st.title("🏥 System Health Monitor")
    st.markdown("Comprehensive monitoring and alerting for the Degen Digest system")

    # Sidebar controls
    st.sidebar.header("Monitoring Controls")

    auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)", value=False)
    refresh_button = st.sidebar.button("🔄 Refresh Now")

    # Load metrics
    metrics, alerts = load_metrics_data()

    # Manual refresh
    if refresh_button:
        metrics = run_system_monitoring()
        alerts = []  # Will be populated by monitoring

    # Auto-refresh
    if auto_refresh:
        time.sleep(30)
        st.rerun()

    # Display sections
    display_system_overview(metrics)

    # Create tabs for different monitoring aspects
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📊 Performance", "🗄️ Database", "🚨 Alerts", "🔌 APIs", "📈 Data Quality"]
    )

    with tab1:
        display_performance_metrics(metrics)

    with tab2:
        display_database_health(metrics)

    with tab3:
        display_alerts(alerts)

    with tab4:
        display_api_health(metrics)

    with tab5:
        display_data_quality(metrics)

    # Footer with last update time
    st.markdown("---")
    st.markdown(
        f"*Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}*"
    )


if __name__ == "__main__":
    main()
