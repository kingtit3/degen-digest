#!/usr/bin/env python3
"""
Data Cleanup Dashboard Page
Manages data deduplication and cleanup operations.
"""

import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Page config
st.set_page_config(
    page_title="Data Cleanup - Degen Digest", page_icon="🧹", layout="wide"
)

st.title("🧹 Data Cleanup & Deduplication")


# Load deduplication report
@st.cache_data(ttl=300)
def load_deduplication_report():
    """Load deduplication report if it exists"""
    report_file = Path("output/deduplicated/deduplication_report.json")
    if not report_file.exists():
        return None

    try:
        with open(report_file) as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading deduplication report: {e}")
        return None


# Load original data stats
@st.cache_data(ttl=300)
def load_original_data_stats():
    """Load statistics about original data files"""
    stats = {}

    files_to_check = [
        ("twitter_raw.json", "Twitter"),
        ("reddit_raw.json", "Reddit"),
        ("telegram_raw.json", "Telegram"),
        ("newsapi_raw.json", "News"),
        ("consolidated_data.json", "Consolidated"),
    ]

    for filename, source in files_to_check:
        file_path = Path(f"output/{filename}")
        if file_path.exists():
            try:
                with open(file_path) as f:
                    data = json.load(f)

                if isinstance(data, list):
                    count = len(data)
                elif isinstance(data, dict):
                    # Count items in consolidated data
                    count = sum(
                        len(data.get(key, []))
                        for key in [
                            "tweets",
                            "reddit_posts",
                            "telegram_messages",
                            "news_articles",
                        ]
                    )
                else:
                    count = 0

                size_mb = file_path.stat().st_size / (1024 * 1024)
                stats[source] = {
                    "count": count,
                    "size_mb": size_mb,
                    "last_modified": datetime.fromtimestamp(
                        file_path.stat().st_mtime
                    ).strftime("%Y-%m-%d %H:%M"),
                }
            except Exception as e:
                st.error(f"Error loading {filename}: {e}")

    return stats


# Load deduplicated data stats
@st.cache_data(ttl=300)
def load_deduplicated_data_stats():
    """Load statistics about deduplicated data files"""
    stats = {}

    deduplicated_dir = Path("output/deduplicated")
    if not deduplicated_dir.exists():
        return stats

    files_to_check = [
        ("twitter_deduplicated.json", "Twitter"),
        ("reddit_deduplicated.json", "Reddit"),
        ("telegram_deduplicated.json", "Telegram"),
        ("news_deduplicated.json", "News"),
        ("consolidated_data_deduplicated.json", "Consolidated"),
    ]

    for filename, source in files_to_check:
        file_path = deduplicated_dir / filename
        if file_path.exists():
            try:
                with open(file_path) as f:
                    data = json.load(f)

                if isinstance(data, list):
                    count = len(data)
                elif isinstance(data, dict):
                    # Count items in consolidated data
                    count = sum(
                        len(data.get(key, []))
                        for key in [
                            "tweets",
                            "reddit_posts",
                            "telegram_messages",
                            "news_articles",
                        ]
                    )
                else:
                    count = 0

                size_mb = file_path.stat().st_size / (1024 * 1024)
                stats[source] = {
                    "count": count,
                    "size_mb": size_mb,
                    "last_modified": datetime.fromtimestamp(
                        file_path.stat().st_mtime
                    ).strftime("%Y-%m-%d %H:%M"),
                }
            except Exception as e:
                st.error(f"Error loading deduplicated {filename}: {e}")

    return stats


# Main content
original_stats = load_original_data_stats()
deduplicated_stats = load_deduplicated_data_stats()
deduplication_report = load_deduplication_report()

# Sidebar controls
st.sidebar.header("🧹 Cleanup Controls")

# Run deduplication
if st.sidebar.button("🔄 Run Data Deduplication"):
    with st.spinner("Running deduplication..."):
        import subprocess

        try:
            result = subprocess.run(
                ["python", "scripts/deduplicate_data.py"],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                st.success("Deduplication completed successfully!")
                st.rerun()
            else:
                st.error(f"Deduplication failed: {result.stderr}")
        except Exception as e:
            st.error(f"Error running deduplication: {e}")

# Clear cache
if st.sidebar.button("🗑️ Clear Cache"):
    st.cache_data.clear()
    st.success("Cache cleared!")
    st.rerun()

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 Data Overview",
        "🔍 Deduplication Report",
        "📁 File Management",
        "⚙️ Cleanup Tools",
    ]
)

with tab1:
    st.subheader("📊 Data Overview")

    if original_stats:
        col1, col2, col3, col4 = st.columns(4)

        total_items = sum(stats["count"] for stats in original_stats.values())
        total_size = sum(stats["size_mb"] for stats in original_stats.values())

        with col1:
            st.metric("Total Items", f"{total_items:,}")
        with col2:
            st.metric("Total Size", f"{total_size:.1f} MB")
        with col3:
            st.metric("Data Sources", len(original_stats))
        with col4:
            if deduplication_report:
                duplicates_removed = deduplication_report["summary"][
                    "total_duplicates_removed"
                ]
                st.metric("Duplicates Removed", f"{duplicates_removed:,}")
            else:
                st.metric("Duplicates Removed", "Not run")

        # Data source breakdown
        st.subheader("📈 Data by Source")

        source_data = []
        for source, stats in original_stats.items():
            source_data.append(
                {
                    "Source": source,
                    "Items": stats["count"],
                    "Size (MB)": stats["size_mb"],
                    "Last Modified": stats["last_modified"],
                }
            )

        df_sources = pd.DataFrame(source_data)

        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(df_sources, x="Source", y="Items", title="Items by Source")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.pie(
                df_sources,
                values="Items",
                names="Source",
                title="Distribution by Source",
            )
            st.plotly_chart(fig, use_container_width=True)

        # Data table
        st.subheader("📋 Detailed Data Statistics")
        st.dataframe(df_sources, use_container_width=True)
    else:
        st.warning("No data files found. Please run scrapers first.")

with tab2:
    st.subheader("🔍 Deduplication Report")

    if deduplication_report:
        # Summary metrics
        summary = deduplication_report["summary"]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Original Items", f"{summary['total_original_items']:,}")
        with col2:
            st.metric("Final Items", f"{summary['total_final_items']:,}")
        with col3:
            st.metric("Duplicates Removed", f"{summary['total_duplicates_removed']:,}")
        with col4:
            st.metric("Deduplication Rate", f"{summary['deduplication_rate']:.1f}%")

        # Before vs After comparison
        st.subheader("📊 Before vs After Comparison")

        comparison_data = []
        for source, data in deduplication_report["by_source"].items():
            comparison_data.append(
                {
                    "Source": source.title(),
                    "Original": data["original_count"],
                    "Final": data["final_count"],
                    "Removed": data["duplicates_removed"],
                    "Rate (%)": data["deduplication_rate"],
                }
            )

        df_comparison = pd.DataFrame(comparison_data)

        col1, col2 = st.columns(2)

        with col1:
            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    name="Original",
                    x=df_comparison["Source"],
                    y=df_comparison["Original"],
                )
            )
            fig.add_trace(
                go.Bar(
                    name="Final", x=df_comparison["Source"], y=df_comparison["Final"]
                )
            )
            fig.update_layout(
                title="Items Before vs After Deduplication", barmode="group"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(
                df_comparison,
                x="Source",
                y="Rate (%)",
                title="Deduplication Rate by Source",
            )
            st.plotly_chart(fig, use_container_width=True)

        # Detailed table
        st.subheader("📋 Detailed Deduplication Results")
        st.dataframe(df_comparison, use_container_width=True)

        # Recommendations
        if deduplication_report.get("recommendations"):
            st.subheader("💡 Recommendations")
            for rec in deduplication_report["recommendations"]:
                st.info(rec)

        # Report metadata
        st.subheader("📅 Report Information")
        st.write(
            f"**Deduplication Date:** {deduplication_report['deduplication_date']}"
        )

    else:
        st.info(
            "No deduplication report found. Run the deduplication process to see results."
        )

with tab3:
    st.subheader("📁 File Management")

    # Original files
    st.subheader("📂 Original Data Files")

    if original_stats:
        original_files_data = []
        for source, stats in original_stats.items():
            original_files_data.append(
                {
                    "File": f"{source.lower()}_raw.json",
                    "Source": source,
                    "Items": stats["count"],
                    "Size (MB)": f"{stats['size_mb']:.2f}",
                    "Last Modified": stats["last_modified"],
                    "Status": "✅ Present",
                }
            )

        df_original = pd.DataFrame(original_files_data)
        st.dataframe(df_original, use_container_width=True)
    else:
        st.warning("No original data files found.")

    # Deduplicated files
    st.subheader("🧹 Deduplicated Data Files")

    if deduplicated_stats:
        deduplicated_files_data = []
        for source, stats in deduplicated_stats.items():
            deduplicated_files_data.append(
                {
                    "File": f"{source.lower()}_deduplicated.json",
                    "Source": source,
                    "Items": stats["count"],
                    "Size (MB)": f"{stats['size_mb']:.2f}",
                    "Last Modified": stats["last_modified"],
                    "Status": "✅ Present",
                }
            )

        df_deduplicated = pd.DataFrame(deduplicated_files_data)
        st.dataframe(df_deduplicated, use_container_width=True)
    else:
        st.info("No deduplicated files found. Run deduplication to create them.")

    # File size comparison
    if original_stats and deduplicated_stats:
        st.subheader("📊 File Size Comparison")

        comparison_data = []
        for source in original_stats.keys():
            if source in deduplicated_stats:
                original_size = original_stats[source]["size_mb"]
                deduplicated_size = deduplicated_stats[source]["size_mb"]
                size_reduction = (
                    ((original_size - deduplicated_size) / original_size * 100)
                    if original_size > 0
                    else 0
                )

                comparison_data.append(
                    {
                        "Source": source,
                        "Original Size (MB)": original_size,
                        "Deduplicated Size (MB)": deduplicated_size,
                        "Size Reduction (%)": size_reduction,
                    }
                )

        if comparison_data:
            df_size_comparison = pd.DataFrame(comparison_data)

            fig = px.bar(
                df_size_comparison,
                x="Source",
                y=["Original Size (MB)", "Deduplicated Size (MB)"],
                title="File Size Comparison",
                barmode="group",
            )
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(df_size_comparison, use_container_width=True)

with tab4:
    st.subheader("⚙️ Cleanup Tools")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🗑️ Data Cleanup")

        if st.button("Clear Old Cache Files"):
            with st.spinner("Clearing cache..."):
                import shutil
                from pathlib import Path

                cache_dirs = [
                    Path.home() / ".streamlit" / "cache",
                    Path("output") / ".cache",
                    Path("output") / "llm_cache.sqlite",
                ]

                cleared_count = 0
                for cache_dir in cache_dirs:
                    if cache_dir.exists():
                        if cache_dir.is_file():
                            cache_dir.unlink()
                        else:
                            shutil.rmtree(cache_dir)
                        cleared_count += 1

                st.success(f"Cleared {cleared_count} cache locations!")

        if st.button("Backup Original Data"):
            with st.spinner("Creating backup..."):
                import shutil
                from datetime import datetime

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_dir = Path(f"output/backup_{timestamp}")
                backup_dir.mkdir(exist_ok=True)

                # Copy original files
                files_to_backup = [
                    "twitter_raw.json",
                    "reddit_raw.json",
                    "telegram_raw.json",
                    "newsapi_raw.json",
                    "consolidated_data.json",
                ]

                copied_count = 0
                for filename in files_to_backup:
                    src = Path(f"output/{filename}")
                    if src.exists():
                        shutil.copy2(src, backup_dir / filename)
                        copied_count += 1

                st.success(f"Backup created: {backup_dir} ({copied_count} files)")

    with col2:
        st.subheader("📊 Data Analysis")

        if st.button("Analyze Data Quality"):
            with st.spinner("Analyzing data quality..."):
                # This would run data quality analysis
                st.info("Data quality analysis would run here")

        if st.button("Generate Data Report"):
            with st.spinner("Generating report..."):
                # This would generate a comprehensive data report
                st.info("Data report generation would run here")

    # Data export
    st.subheader("📤 Export Clean Data")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Export Deduplicated Data"):
            if deduplicated_stats:
                # Create download link for deduplicated consolidated data
                deduplicated_file = Path(
                    "output/deduplicated/consolidated_data_deduplicated.json"
                )
                if deduplicated_file.exists():
                    with open(deduplicated_file) as f:
                        data = f.read()

                    st.download_button(
                        label="Download Deduplicated Data (JSON)",
                        data=data,
                        file_name=f"deduplicated_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                    )
                else:
                    st.warning("Deduplicated data not found. Run deduplication first.")
            else:
                st.warning("No deduplicated data available.")

    with col2:
        if st.button("Export Deduplication Report"):
            if deduplication_report:
                report_json = json.dumps(deduplication_report, indent=2)

                st.download_button(
                    label="Download Deduplication Report (JSON)",
                    data=report_json,
                    file_name=f"deduplication_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                )
            else:
                st.warning("No deduplication report available.")

# Footer
st.markdown("---")
st.markdown("*Data cleanup and deduplication tools for Degen Digest*")
