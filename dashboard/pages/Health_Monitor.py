import sys
from pathlib import Path
root_path = Path(__file__).resolve().parents[2]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import pandas as pd
from datetime import datetime, timedelta
from utils.health_monitor import health_monitor
from utils.advanced_logging import get_logger

logger = get_logger(__name__)

st.set_page_config(page_title="Health Monitor", layout="wide")

st.title("🏥 System Health Monitor")

# Run health check
with st.spinner("Running health check..."):
    health_data = health_monitor.run_health_check()
    summary = health_monitor.get_health_summary()

# Overall Health Score
col1, col2, col3, col4 = st.columns(4)

score = summary["overall_score"]
status = summary["status"]

# Color coding for health score
if score >= 80:
    color = "green"
    emoji = "🟢"
elif score >= 60:
    color = "orange"
    emoji = "🟡"
else:
    color = "red"
    emoji = "🔴"

col1.metric(
    "Overall Health Score", 
    f"{emoji} {score}/100",
    delta=f"{status.title()}"
)

col2.metric(
    "Active Alerts",
    summary["active_alerts"],
    delta="Critical Issues" if summary["active_alerts"] > 0 else "All Good"
)

col3.metric(
    "Warnings",
    summary["warnings"],
    delta="Needs Attention" if summary["warnings"] > 0 else "Clear"
)

col4.metric(
    "Last Check",
    datetime.fromisoformat(summary["last_check"]).strftime("%H:%M:%S"),
    delta="Just Now"
)

st.markdown("---")

# System Metrics
st.subheader("📊 System Performance")

if health_data["system"]:
    sys_data = health_data["system"]
    
    # Create subplot for system metrics
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("CPU Usage", "Memory Usage", "Disk Usage", "Process Count"),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # CPU Usage
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=sys_data.get("cpu_percent", 0),
            title={"text": "CPU %"},
            gauge={"axis": {"range": [None, 100]},
                   "bar": {"color": "darkblue"},
                   "steps": [{"range": [0, 50], "color": "lightgray"},
                            {"range": [50, 80], "color": "yellow"},
                            {"range": [80, 100], "color": "red"}]},
            domain={"row": 0, "column": 0}
        ),
        row=1, col=1
    )
    
    # Memory Usage
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=sys_data.get("memory_percent", 0),
            title={"text": "Memory %"},
            gauge={"axis": {"range": [None, 100]},
                   "bar": {"color": "darkblue"},
                   "steps": [{"range": [0, 60], "color": "lightgray"},
                            {"range": [60, 85], "color": "yellow"},
                            {"range": [85, 100], "color": "red"}]},
            domain={"row": 0, "column": 1}
        ),
        row=1, col=2
    )
    
    # Disk Usage
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=sys_data.get("disk_percent", 0),
            title={"text": "Disk %"},
            gauge={"axis": {"range": [None, 100]},
                   "bar": {"color": "darkblue"},
                   "steps": [{"range": [0, 70], "color": "lightgray"},
                            {"range": [70, 90], "color": "yellow"},
                            {"range": [90, 100], "color": "red"}]},
            domain={"row": 1, "column": 0}
        ),
        row=2, col=1
    )
    
    # Process Count
    fig.add_trace(
        go.Indicator(
            mode="number",
            value=sys_data.get("process_count", 0),
            title={"text": "Processes"},
            domain={"row": 1, "column": 1}
        ),
        row=2, col=2
    )
    
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # System details
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Available Memory", f"{sys_data.get('memory_available_gb', 0):.1f} GB")
        st.metric("Free Disk Space", f"{sys_data.get('disk_free_gb', 0):.1f} GB")
    
    with col2:
        st.metric("Uptime", f"{sys_data.get('uptime_seconds', 0) / 3600:.1f} hours")
        st.metric("Timestamp", datetime.fromisoformat(sys_data.get("timestamp", "")).strftime("%Y-%m-%d %H:%M:%S"))

st.markdown("---")

# Data Freshness
st.subheader("📁 Data Freshness")

if health_data["data_freshness"]:
    data_df = []
    for filename, status in health_data["data_freshness"].items():
        data_df.append({
            "File": filename,
            "Exists": "✅" if status["exists"] else "❌",
            "Fresh": "✅" if status.get("is_fresh", False) else "❌",
            "Age (hours)": f"{status.get('age_hours', 0):.1f}" if status.get('age_hours') else "N/A",
            "Size (KB)": f"{status.get('size_bytes', 0) / 1024:.1f}" if status.get('size_bytes') else "0"
        })
    
    df = pd.DataFrame(data_df)
    st.dataframe(df, use_container_width=True)

st.markdown("---")

# Database Health
st.subheader("🗄️ Database Health")

if health_data["database"]:
    db_data = health_data["database"]
    
    col1, col2, col3, col4 = st.columns(4)
    
    status_icon = "✅" if db_data.get("connected", False) else "❌"
    col1.metric("Connection", f"{status_icon} Connected" if db_data.get("connected") else "❌ Disconnected")
    
    col2.metric("Tweet Count", f"{db_data.get('tweet_count', 0):,}")
    col3.metric("Reddit Posts", f"{db_data.get('reddit_count', 0):,}")
    col4.metric("DB Size", f"{db_data.get('database_size_mb', 0):.1f} MB")
    
    if db_data.get("last_tweet_age_hours"):
        st.info(f"Last tweet was {db_data['last_tweet_age_hours']:.1f} hours ago")

st.markdown("---")

# LLM Health
st.subheader("🤖 LLM Service Health")

if health_data["llm"]:
    llm_data = health_data["llm"]
    
    col1, col2, col3, col4 = st.columns(4)
    
    api_status = "✅ Available" if llm_data.get("api_available", False) else "❌ Unavailable"
    col1.metric("API Status", api_status)
    
    col2.metric("Monthly Tokens", f"{llm_data.get('monthly_tokens', 0):,}")
    col3.metric("Monthly Cost", f"${llm_data.get('monthly_cost_usd', 0):.2f}")
    
    budget_remaining = llm_data.get("budget_remaining_usd", 10.0)
    budget_color = "green" if budget_remaining > 5 else "orange" if budget_remaining > 1 else "red"
    col4.metric("Budget Remaining", f"${budget_remaining:.2f}", delta_color=budget_color)

st.markdown("---")

# Recent Alerts
st.subheader("🚨 Recent Alerts")

alerts_file = Path("output/health_alerts.json")
if alerts_file.exists():
    try:
        alerts = json.loads(alerts_file.read_text())
        if alerts:
            # Show last 10 alerts
            recent_alerts = alerts[-10:]
            
            for alert in reversed(recent_alerts):
                level = alert.get("level", "info")
                category = alert.get("category", "unknown")
                message = alert.get("message", "No message")
                timestamp = alert.get("timestamp", "")
                
                if level == "error":
                    st.error(f"**{category.upper()}** - {message}")
                elif level == "warning":
                    st.warning(f"**{category.upper()}** - {message}")
                else:
                    st.info(f"**{category.upper()}** - {message}")
                
                if timestamp:
                    st.caption(f"Time: {datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.success("No alerts in the system! 🎉")
    except Exception as e:
        st.error(f"Error loading alerts: {e}")
else:
    st.info("No alerts file found. System may be running for the first time.")

# Manual refresh button
if st.button("🔄 Refresh Health Check"):
    st.rerun()

# Auto-refresh
st.markdown("---")
st.caption("This page auto-refreshes every 5 minutes. Last updated: " + 
          datetime.fromisoformat(summary["last_check"]).strftime("%Y-%m-%d %H:%M:%S")) 