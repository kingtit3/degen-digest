import sys
from pathlib import Path

root_path = Path(__file__).resolve().parents[2]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

from datetime import datetime

import streamlit as st


def get_digest_content():
    """Get the latest digest content directly"""
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
        page_title="Degen Digest - Latest Crypto Intelligence",
        page_icon="🚀",
        layout="wide",
    )

    # Get digest content
    content, filename = get_digest_content()

    if content is None:
        st.error(f"❌ {filename}")
        st.info(
            "💡 Try refreshing the page or check if the digest generation is working."
        )
        return

    # Display the digest
    st.markdown(
        f"""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: #00d4ff; font-size: 2.5em;">🚀 Degen Digest</h1>
        <p style="color: #888; font-size: 1.2em;">Latest Crypto Intelligence</p>
        <p style="color: #666; font-size: 0.9em;">File: {filename} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Display the content
    st.markdown(content)

    # Add a refresh button
    if st.button("🔄 Refresh Digest"):
        st.rerun()

    # Add debug info in expander
    with st.expander("🔧 Technical Info", expanded=False):
        st.write(f"Current directory: {Path.cwd()}")
        st.write(f"Digest file: {filename}")
        st.write(f"Content length: {len(content)} characters")
        st.write(
            f"Last modified: {datetime.fromtimestamp(Path('output/digest.md').stat().st_mtime) if Path('output/digest.md').exists() else 'Unknown'}"
        )


if __name__ == "__main__":
    main()
