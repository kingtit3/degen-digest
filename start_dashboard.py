#!/usr/bin/env python3
"""
Simple startup script for the new Degen Digest Dashboard
"""

import os
import sys
from pathlib import Path


def setup_environment():
    """Setup the environment for the dashboard"""
    # Add the current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))

    # Set environment variables (use PORT env var for Cloud Run compatibility)
    port = os.environ.get("PORT", "8501")
    os.environ["STREAMLIT_SERVER_PORT"] = port
    os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"


def main():
    """Start the dashboard"""
    print("🚀 Starting Degen Digest Dashboard...")

    # Setup environment
    setup_environment()

    # Check if output directory exists
    output_dir = Path("output")
    if not output_dir.exists():
        print("📁 Creating output directory...")
        output_dir.mkdir(exist_ok=True)

    # Check if we have any digest files
    digest_files = list(output_dir.glob("digest*.md"))
    if not digest_files:
        print("⚠️  No digest files found. You may want to generate a digest first.")
        print("💡 Run: python3 main.py")

    port = os.environ.get("PORT", "8501")
    print(f"🌐 Dashboard will be available at: http://localhost:{port}")
    print("📱 Press Ctrl+C to stop the dashboard")

    # Start Streamlit
    import subprocess

    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                "dashboard/app.py",
                "--server.port",
                port,
                "--server.address",
                "0.0.0.0",
                "--server.headless",
                "true",
            ]
        )
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped.")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")


if __name__ == "__main__":
    main()
