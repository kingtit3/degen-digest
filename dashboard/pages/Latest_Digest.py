import sys
from pathlib import Path

root_path = Path(__file__).resolve().parents[2]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

from datetime import datetime

import streamlit as st


def get_latest_digest():
    """Get the latest digest content"""
    # Try multiple possible output directory paths
    possible_paths = [
        Path("output"),
        Path("../output"),
        Path("../../output"),
        Path("/app/output"),
        Path.cwd() / "output",
    ]

    output_dir = None
    for path in possible_paths:
        if path.exists():
            output_dir = path
            break

    if not output_dir:
        return None, "Could not find output directory"

    # Look for the main digest file
    digest_file = output_dir / "digest.md"
    if not digest_file.exists():
        # Try the most recent dated digest
        md_files = list(output_dir.glob("digest-*.md"))
        if md_files:
            digest_file = max(md_files, key=lambda p: p.stat().st_mtime)
        else:
            return None, "No digest files found"

    try:
        with open(digest_file, encoding="utf-8") as f:
            content = f.read()
        return content, digest_file.name
    except Exception as e:
        return None, f"Error reading digest: {str(e)}"


def main():
    st.set_page_config(
        page_title="Latest Digest - Degen Digest", page_icon="📰", layout="wide"
    )

    # Clean header
    st.markdown(
        """
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1>📰 Latest Digest</h1>
        <p style="color: #6c757d; font-size: 1.1rem;">Your daily crypto intelligence</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Get digest content
    content, filename = get_latest_digest()

    if content is None:
        st.error(f"❌ {filename}")
        st.info(
            "💡 Try refreshing the page or check if the digest generation is working."
        )

        # Add a generate button
        if st.button("🚀 Generate New Digest"):
            st.info("Generating new digest... This may take a few minutes.")
            # Add digest generation logic here
        return

    # Display file info
    st.markdown(
        f"""
    <div style="background: #f8f9fa; padding: 1rem; border-radius: 6px; margin-bottom: 2rem;">
        <strong>File:</strong> {filename} |
        <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
        <strong>Size:</strong> {len(content)} characters
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Refresh"):
            st.rerun()
    with col2:
        if st.button("📥 Download"):
            st.download_button(
                "Download Digest", content, file_name=filename, mime="text/markdown"
            )
    with col3:
        if st.button("🏠 Back to Dashboard"):
            st.switch_page("app.py")

    st.markdown("---")

    # Display the content in a clean format
    st.markdown(
        """
    <style>
        .digest-content {
            background: #ffffff;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 2rem;
            margin: 1rem 0;
            line-height: 1.6;
        }
        .digest-content h1 {
            color: #1a1a1a;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 1rem;
            text-align: center;
        }
        .digest-content h2 {
            color: #2c3e50;
            font-size: 1.5rem;
            font-weight: 600;
            margin-top: 2rem;
            margin-bottom: 1rem;
            border-bottom: 2px solid #3498db;
            padding-bottom: 0.5rem;
        }
        .digest-content h3 {
            color: #34495e;
            font-size: 1.2rem;
            font-weight: 600;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
        }
        .digest-content p {
            margin-bottom: 1rem;
        }
        .digest-content ul, .digest-content ol {
            margin-bottom: 1rem;
            padding-left: 2rem;
        }
        .digest-content li {
            margin-bottom: 0.5rem;
        }
        .digest-content strong {
            color: #2c3e50;
        }
        .digest-content em {
            color: #6c757d;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Display content in a clean container
    st.markdown(
        f"""
    <div class="digest-content">
        {content}
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Footer
    st.markdown("---")
    st.markdown(
        """
    <div style="text-align: center; color: #6c757d; font-size: 0.9rem;">
        🚀 Degen Digest - Your daily crypto intelligence companion
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
