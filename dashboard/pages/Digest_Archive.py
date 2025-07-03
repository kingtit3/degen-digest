import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st


def load_digest_files():
    """Load all digest files from the output directory"""
    # More robust path resolution

    # Try multiple possible paths
    possible_paths = [
        Path("../../output"),  # From dashboard/pages/
        Path("../output"),  # From dashboard/
        Path("output"),  # From project root
        Path(
            os.path.join(os.path.dirname(__file__), "../../output")
        ),  # Absolute from this file
        Path(os.path.join(os.getcwd(), "output")),  # From current working directory
    ]

    output_dir = None
    for path in possible_paths:
        if path.exists():
            output_dir = path
            break

    if not output_dir:
        st.error(
            f"Could not find output directory. Tried paths: {[str(p) for p in possible_paths]}"
        )
        return []

    st.info(f"📁 Found output directory: {output_dir.absolute()}")

    digest_files = []

    # Look for digest files - include both digest-*.md and digest.md
    digest_patterns = ["digest*.md", "digest.md"]

    for pattern in digest_patterns:
        for file_path in output_dir.glob(pattern):
            # Skip if we already processed this file
            if any(d["path"] == file_path for d in digest_files):
                continue

            try:
                # Extract date from filename or file content
                content = file_path.read_text(encoding="utf-8")

                # Try to extract date from filename first
                filename = file_path.stem
                if "digest-" in filename:
                    date_str = filename.split("digest-")[1]
                    try:
                        date = datetime.strptime(date_str, "%Y-%m-%d")
                    except Exception:
                        # Fallback to current file modification time
                        date = datetime.fromtimestamp(file_path.stat().st_mtime)
                else:
                    # Try to extract date from content
                    lines = content.split("\n")
                    date = None
                    for line in lines:
                        if "Date:" in line or "Generated:" in line:
                            # Extract date from line
                            import re

                            date_match = re.search(r"(\d{4}-\d{2}-\d{2})", line)
                            if date_match:
                                try:
                                    date = datetime.strptime(
                                        date_match.group(1), "%Y-%m-%d"
                                    )
                                    break
                                except Exception:
                                    continue

                    if not date:
                        date = datetime.fromtimestamp(file_path.stat().st_mtime)

                digest_files.append(
                    {
                        "filename": file_path.name,
                        "date": date,
                        "content": content,
                        "size": file_path.stat().st_size,
                        "path": file_path,
                    }
                )

            except Exception as e:
                st.error(f"Error loading {file_path}: {e}")

    # Sort by date (newest first)
    digest_files.sort(key=lambda x: x["date"], reverse=True)

    st.success(f"📄 Loaded {len(digest_files)} digest files")
    return digest_files


def display_digest_archive():
    """Display the digest archive page"""
    st.markdown(
        """
    <div style="text-align: center; margin-bottom: 40px;">
        <h1 class="gradient-text">📚 Digest Archive</h1>
        <p style="color: #888; font-size: 18px;">All historical Degen Digest reports</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Load all digest files
    digest_files = load_digest_files()

    if not digest_files:
        st.warning("No digest files found in the output directory.")
        st.info("Generate your first digest by running: `python main.py`")
        return

    # Search and filter options
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        search_term = st.text_input(
            "🔍 Search digests", placeholder="Search for keywords..."
        )

    with col2:
        date_filter = st.selectbox(
            "📅 Filter by period",
            ["All Time", "Last 7 days", "Last 30 days", "Last 90 days", "This year"],
        )

    with col3:
        sort_by = st.selectbox(
            "📊 Sort by", ["Date (Newest)", "Date (Oldest)", "File Size"]
        )

    # Apply filters
    filtered_digests = digest_files.copy()

    # Date filter
    if date_filter != "All Time":
        now = datetime.now()
        if date_filter == "Last 7 days":
            cutoff = now - pd.Timedelta(days=7)
        elif date_filter == "Last 30 days":
            cutoff = now - pd.Timedelta(days=30)
        elif date_filter == "Last 90 days":
            cutoff = now - pd.Timedelta(days=90)
        elif date_filter == "This year":
            cutoff = datetime(now.year, 1, 1)

        filtered_digests = [d for d in filtered_digests if d["date"] >= cutoff]

    # Search filter
    if search_term:
        filtered_digests = [
            d for d in filtered_digests if search_term.lower() in d["content"].lower()
        ]

    # Sort
    if sort_by == "Date (Oldest)":
        filtered_digests.sort(key=lambda x: x["date"])
    elif sort_by == "File Size":
        filtered_digests.sort(key=lambda x: x["size"], reverse=True)

    # Display results
    st.markdown(f"### 📋 Found {len(filtered_digests)} digests")

    if not filtered_digests:
        st.info("No digests match your search criteria.")
        return

    # Create a dataframe for better display
    df_data = []
    for digest in filtered_digests:
        # Extract summary from content
        lines = digest["content"].split("\n")
        summary = ""
        for line in lines:
            if line.startswith("## 📋 Executive Summary") or line.startswith(
                "## 🎯 Key Takeaways"
            ):
                # Get next few lines as summary
                start_idx = lines.index(line)
                summary_lines = lines[start_idx + 1 : start_idx + 6]
                summary = " ".join(
                    [
                        l.strip()
                        for l in summary_lines
                        if l.strip() and not l.startswith("---")
                    ]
                )
                break

        df_data.append(
            {
                "Date": digest["date"].strftime("%Y-%m-%d"),
                "Time": digest["date"].strftime("%H:%M"),
                "Filename": digest["filename"],
                "Size (KB)": round(digest["size"] / 1024, 1),
                "Summary": summary[:200] + "..." if len(summary) > 200 else summary,
            }
        )

    df = pd.DataFrame(df_data)

    # Display as interactive table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
            "Time": st.column_config.TextColumn("Time"),
            "Filename": st.column_config.TextColumn("File"),
            "Size (KB)": st.column_config.NumberColumn("Size (KB)", format="%.1f"),
            "Summary": st.column_config.TextColumn("Summary", width="large"),
        },
    )

    # Individual digest viewer
    st.markdown("### 📖 Read Digests")

    if filtered_digests:
        selected_digest = st.selectbox(
            "Choose a digest to read:",
            options=[
                f"{d['date'].strftime('%Y-%m-%d')} - {d['filename']}"
                for d in filtered_digests
            ],
            index=0,
        )

        # Find the selected digest
        selected_date = selected_digest.split(" - ")[0]
        selected_filename = selected_digest.split(" - ")[1]

        for digest in filtered_digests:
            if (
                digest["date"].strftime("%Y-%m-%d") == selected_date
                and digest["filename"] == selected_filename
            ):
                # Display digest content
                st.markdown("---")
                st.markdown(
                    f"### 📄 {digest['date'].strftime('%B %d, %Y')} - {digest['filename']}"
                )

                # Add download button
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.download_button(
                        label="📥 Download Digest",
                        data=digest["content"],
                        file_name=digest["filename"],
                        mime="text/markdown",
                    )

                with col2:
                    st.info(f"📊 File size: {round(digest['size'] / 1024, 1)} KB")

                # Display content in a scrollable container
                st.markdown("#### 📖 Full Content:")

                # Simple, clean display of the content
                with st.expander(
                    "📄 Click to expand full digest content", expanded=True
                ):
                    st.markdown(digest["content"])

                # Alternative: Show as text for better readability
                st.markdown("#### 📝 Raw Text View:")
                with st.container():
                    st.text_area(
                        "Digest Content (Read-only)",
                        value=digest["content"],
                        height=400,
                        disabled=True,
                        help="This is the raw content of the digest file",
                    )
                break
    else:
        st.info("No digests available to read.")


def main():
    """Main function for the digest archive page"""
    display_digest_archive()


if __name__ == "__main__":
    main()
