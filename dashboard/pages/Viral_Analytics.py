#!/usr/bin/env python3
"""
Enhanced Viral Analytics Dashboard
Real-time virality prediction and trend analysis
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from utils.advanced_logging import get_logger

logger = get_logger(__name__)


def main():
    st.set_page_config(
        page_title="Viral Analytics - Degen Digest", page_icon="🚀", layout="wide"
    )

    st.title("🚀 Enhanced Viral Analytics")
    st.markdown("### Ultimate Crypto Virality Prediction & Analysis")

    # Sidebar controls
    st.sidebar.header("📊 Analytics Controls")

    # Data source selection
    data_source = st.sidebar.selectbox(
        "Data Source",
        ["All Sources", "Twitter", "Reddit", "Telegram", "News", "Market"],
        index=0,
    )

    # Time range selection
    time_range = st.sidebar.selectbox(
        "Time Range",
        ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "All Time"],
        index=0,
    )

    # Viral score threshold
    viral_threshold = st.sidebar.slider(
        "Viral Score Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1,
        help="Minimum viral score to display",
    )

    # Load data
    data = load_viral_data()

    if not data:
        st.warning(
            "No viral analytics data available. Run the enhanced data pipeline first."
        )
        st.info("To generate data, run: `python scripts/enhanced_data_pipeline.py`")
        return

    # Filter data based on selections
    filtered_data = filter_data(data, data_source, time_range, viral_threshold)

    # Main dashboard
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📈 Viral Prediction Overview")
        display_viral_overview(filtered_data)

    with col2:
        st.subheader("🎯 Quick Stats")
        display_quick_stats(filtered_data)

    # Detailed analysis
    st.subheader("🔍 Detailed Viral Analysis")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Predictions", "📈 Trends", "🎯 Top Viral Content", "🔬 Model Performance"]
    )

    with tab1:
        display_predictions_analysis(filtered_data)

    with tab2:
        display_trends_analysis(filtered_data)

    with tab3:
        display_top_viral_content(filtered_data)

    with tab4:
        display_model_performance()

    # Real-time monitoring
    st.subheader("⚡ Real-Time Monitoring")
    display_real_time_monitoring()


def load_viral_data():
    """Load viral analytics data"""

    try:
        # Load processed data
        processed_file = Path("output/enhanced_pipeline/processed_data.json")
        if processed_file.exists():
            with open(processed_file) as f:
                processed_data = json.load(f)
        else:
            processed_data = []

        # Load viral predictions
        predictions_file = Path("output/enhanced_pipeline/viral_predictions.json")
        if predictions_file.exists():
            with open(predictions_file) as f:
                viral_predictions = json.load(f)
        else:
            viral_predictions = []

        # Load trends analysis
        trends_file = Path("output/enhanced_pipeline/trends_analysis.json")
        if trends_file.exists():
            with open(trends_file) as f:
                trends_data = json.load(f)
        else:
            trends_data = {}

        return {
            "processed_data": processed_data,
            "viral_predictions": viral_predictions,
            "trends_data": trends_data,
        }

    except Exception as e:
        logger.error(f"Failed to load viral data: {e}")
        return None


def filter_data(data, data_source, time_range, viral_threshold):
    """Filter data based on user selections"""

    processed_data = data["processed_data"]
    viral_predictions = data["viral_predictions"]

    # Filter by data source
    if data_source != "All Sources":
        processed_data = [
            item for item in processed_data if item.get("source") == data_source.lower()
        ]
        viral_predictions = [
            pred
            for pred in viral_predictions
            if pred.get("source") == data_source.lower()
        ]

    # Filter by time range
    if time_range != "All Time":
        cutoff_time = get_cutoff_time(time_range)
        processed_data = [
            item
            for item in processed_data
            if parse_timestamp(item.get("processed_at", item.get("created_at", "")))
            > cutoff_time
        ]
        viral_predictions = [
            pred
            for pred in viral_predictions
            if parse_timestamp(pred.get("timestamp", "")) > cutoff_time
        ]

    # Filter by viral threshold
    viral_predictions = [
        pred
        for pred in viral_predictions
        if pred.get("prediction", {}).get("score", 0) >= viral_threshold
    ]

    return {
        "processed_data": processed_data,
        "viral_predictions": viral_predictions,
        "trends_data": data["trends_data"],
    }


def get_cutoff_time(time_range):
    """Get cutoff time based on time range selection"""

    now = datetime.utcnow()

    if time_range == "Last 24 Hours":
        return now - timedelta(days=1)
    elif time_range == "Last 7 Days":
        return now - timedelta(days=7)
    elif time_range == "Last 30 Days":
        return now - timedelta(days=30)
    else:
        return datetime.min


def parse_timestamp(timestamp_str):
    """Parse timestamp string to datetime object"""

    try:
        if timestamp_str:
            return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        return datetime.min
    except:
        return datetime.min


def display_viral_overview(data):
    """Display viral prediction overview"""

    viral_predictions = data["viral_predictions"]

    if not viral_predictions:
        st.info("No viral predictions available for the selected filters.")
        return

    # Create DataFrame for analysis
    df = pd.DataFrame(viral_predictions)
    df["viral_score"] = df["prediction"].apply(lambda x: x.get("score", 0))
    df["confidence"] = df["prediction"].apply(lambda x: x.get("confidence", 0))

    # Viral score distribution
    fig = px.histogram(
        df,
        x="viral_score",
        nbins=20,
        title="Viral Score Distribution",
        labels={"viral_score": "Viral Score", "count": "Number of Items"},
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Source breakdown
    source_counts = df["source"].value_counts()
    fig = px.pie(
        values=source_counts.values,
        names=source_counts.index,
        title="Viral Content by Source",
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def display_quick_stats(data):
    """Display quick statistics"""

    viral_predictions = data["viral_predictions"]
    processed_data = data["processed_data"]

    if not viral_predictions:
        st.info("No data available")
        return

    # Calculate statistics
    total_items = len(processed_data)
    viral_items = len(viral_predictions)
    avg_viral_score = np.mean([p["prediction"]["score"] for p in viral_predictions])
    high_viral_count = len(
        [p for p in viral_predictions if p["prediction"]["score"] > 0.7]
    )

    # Display metrics
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Items", total_items)
        st.metric("Viral Items", viral_items)

    with col2:
        st.metric("Avg Viral Score", f"{avg_viral_score:.3f}")
        st.metric("High Viral (>0.7)", high_viral_count)

    # Top sources
    if viral_predictions:
        source_counts = pd.DataFrame(viral_predictions)["source"].value_counts()
        st.write("**Top Sources:**")
        for source, count in source_counts.head(3).items():
            st.write(f"• {source.title()}: {count}")


def display_predictions_analysis(data):
    """Display detailed predictions analysis"""

    viral_predictions = data["viral_predictions"]

    if not viral_predictions:
        st.info("No predictions available")
        return

    df = pd.DataFrame(viral_predictions)
    df["viral_score"] = df["prediction"].apply(lambda x: x.get("score", 0))
    df["confidence"] = df["prediction"].apply(lambda x: x.get("confidence", 0))

    # Score vs Confidence scatter plot
    fig = px.scatter(
        df,
        x="viral_score",
        y="confidence",
        color="source",
        title="Viral Score vs Confidence by Source",
        labels={"viral_score": "Viral Score", "confidence": "Confidence"},
    )
    st.plotly_chart(fig, use_container_width=True)

    # Top predictions table
    st.subheader("Top Viral Predictions")

    top_predictions = df.nlargest(10, "viral_score")[
        ["source", "viral_score", "confidence", "content_preview"]
    ]
    top_predictions["viral_score"] = top_predictions["viral_score"].round(3)
    top_predictions["confidence"] = top_predictions["confidence"].round(3)

    st.dataframe(top_predictions, use_container_width=True)


def display_trends_analysis(data):
    """Display trends analysis"""

    trends_data = data["trends_data"]

    if not trends_data:
        st.info("No trends data available")
        return

    # Convert trends to DataFrame
    trends_df = pd.DataFrame(
        [
            {
                "source": source,
                "total_items": data.get("total_items", 0),
                "avg_engagement_velocity": data.get("avg_engagement_velocity", 0),
                "avg_viral_coefficient": data.get("avg_viral_coefficient", 0),
                "viral_items": data.get("viral_items", 0),
            }
            for source, data in trends_data.items()
        ]
    )

    if trends_df.empty:
        st.info("No trends data available")
        return

    # Engagement velocity by source
    fig = px.bar(
        trends_df,
        x="source",
        y="avg_engagement_velocity",
        title="Average Engagement Velocity by Source",
        labels={
            "avg_engagement_velocity": "Avg Engagement Velocity",
            "source": "Source",
        },
    )
    st.plotly_chart(fig, use_container_width=True)

    # Viral coefficient by source
    fig = px.bar(
        trends_df,
        x="source",
        y="avg_viral_coefficient",
        title="Average Viral Coefficient by Source",
        labels={"avg_viral_coefficient": "Avg Viral Coefficient", "source": "Source"},
    )
    st.plotly_chart(fig, use_container_width=True)

    # Top categories
    st.subheader("Top Content Categories")

    all_categories = []
    for source_data in trends_data.values():
        if "top_categories" in source_data:
            all_categories.extend(source_data["top_categories"])

    if all_categories:
        category_df = pd.DataFrame(all_categories)
        category_counts = (
            category_df.groupby("category")["count"].sum().sort_values(ascending=False)
        )

        fig = px.bar(
            x=category_counts.index,
            y=category_counts.values,
            title="Content Categories Distribution",
            labels={"x": "Category", "y": "Count"},
        )
        st.plotly_chart(fig, use_container_width=True)


def display_top_viral_content(data):
    """Display top viral content"""

    viral_predictions = data["viral_predictions"]

    if not viral_predictions:
        st.info("No viral content available")
        return

    # Sort by viral score
    sorted_predictions = sorted(
        viral_predictions, key=lambda x: x["prediction"]["score"], reverse=True
    )

    # Display top 10
    st.subheader("Top 10 Viral Content Items")

    for i, pred in enumerate(sorted_predictions[:10], 1):
        with st.expander(
            f"#{i} - Score: {pred['prediction']['score']:.3f} | {pred['source'].title()}"
        ):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.write("**Content:**")
                st.write(pred["content_preview"])

            with col2:
                st.write("**Metrics:**")
                st.write(f"Score: {pred['prediction']['score']:.3f}")
                st.write(f"Confidence: {pred['prediction']['confidence']:.3f}")
                st.write(f"Source: {pred['source']}")
                st.write(f"Model: {pred['prediction']['model']}")


def display_model_performance():
    """Display model performance metrics"""

    try:
        # Load model performance data
        model_file = Path("models/enhanced_viral_predictor.joblib")
        if model_file.exists():
            import joblib

            model_data = joblib.load(model_file)
            performance = model_data.get("model_performance", {})

            if performance:
                st.subheader("Model Performance Metrics")

                # Create performance DataFrame
                perf_df = pd.DataFrame(
                    [
                        {
                            "Model": model_name,
                            "MSE": metrics.get("mse", 0),
                            "MAE": metrics.get("mae", 0),
                            "R²": metrics.get("r2", 0),
                            "RMSE": metrics.get("rmse", 0),
                        }
                        for model_name, metrics in performance.items()
                    ]
                )

                # Display metrics
                st.dataframe(perf_df, use_container_width=True)

                # Performance visualization
                fig = px.bar(
                    perf_df,
                    x="Model",
                    y="R²",
                    title="Model Performance (R² Score)",
                    labels={"R²": "R² Score", "Model": "Model"},
                )
                st.plotly_chart(fig, use_container_width=True)

            else:
                st.info("No model performance data available")
        else:
            st.info("No trained model found. Train the model first.")

    except Exception as e:
        st.error(f"Failed to load model performance: {e}")


def display_real_time_monitoring():
    """Display real-time monitoring dashboard"""

    st.info("🔄 Real-time monitoring is being developed...")

    # Placeholder for real-time features
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Live Data Stream", "Active", delta="+5 items/min")

    with col2:
        st.metric("Model Accuracy", "87.3%", delta="+2.1%")

    with col3:
        st.metric("Prediction Latency", "0.3s", delta="-0.1s")

    # Real-time alerts placeholder
    st.subheader("🚨 Real-Time Alerts")

    alerts = [
        {
            "time": "2 min ago",
            "type": "High Viral Score",
            "content": "New Bitcoin tweet scored 0.89",
        },
        {
            "time": "5 min ago",
            "type": "Trending Topic",
            "content": "DeFi mentions increased 150%",
        },
        {
            "time": "8 min ago",
            "type": "Model Update",
            "content": "Model retrained with new data",
        },
    ]

    for alert in alerts:
        st.info(f"**{alert['time']}** - {alert['type']}: {alert['content']}")


if __name__ == "__main__":
    main()
