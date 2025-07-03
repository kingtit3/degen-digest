#!/usr/bin/env python3
"""Rename digest.md to include today's date"""

import shutil
from datetime import datetime
from pathlib import Path


def rename_digest():
    """Rename digest.md to digest-YYYY-MM-DD.md"""

    output_dir = Path("output")
    digest_file = output_dir / "digest.md"

    if not digest_file.exists():
        print("❌ digest.md not found")
        return

    # Create new filename with today's date
    today = datetime.now()
    new_filename = f"digest-{today.strftime('%Y-%m-%d')}.md"
    new_filepath = output_dir / new_filename

    # Copy the file with new name
    shutil.copy2(digest_file, new_filepath)

    print(f"✅ Renamed digest.md to {new_filename}")
    print(f"📁 Original: {digest_file}")
    print(f"📁 New: {new_filepath}")

    # Show file sizes
    print(f"📊 Original size: {digest_file.stat().st_size} bytes")
    print(f"📊 New file size: {new_filepath.stat().st_size} bytes")

    # List all digest files now
    print("\n📄 All digest files in output:")
    for file in output_dir.glob("digest*.md"):
        print(f"   - {file.name} ({file.stat().st_size} bytes)")


if __name__ == "__main__":
    rename_digest()
