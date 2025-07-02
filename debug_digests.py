#!/usr/bin/env python3
"""Debug script to check digest files and path resolution"""

import os
from pathlib import Path


def debug_digest_files():
    """Debug digest file loading"""
    print("🔍 Debugging Digest Files")
    print("=" * 50)

    # Check current working directory
    print(f"📁 Current working directory: {os.getcwd()}")

    # Check if output directory exists
    output_dir = Path("output")
    print(f"📁 Output directory exists: {output_dir.exists()}")
    print(f"📁 Output directory path: {output_dir.absolute()}")

    if output_dir.exists():
        print("📁 Output directory contents:")
        for item in output_dir.iterdir():
            print(f"   - {item.name} ({'dir' if item.is_dir() else 'file'})")

    # Check for digest files specifically
    print("\n🔍 Looking for digest files:")
    digest_patterns = ["digest*.md", "digest*.txt", "*.md"]

    for pattern in digest_patterns:
        files = list(output_dir.glob(pattern))
        print(f"📄 Pattern '{pattern}': {len(files)} files found")
        for file in files:
            print(f"   - {file.name} ({file.stat().st_size} bytes)")

    # Test the path resolution from dashboard/pages/
    print("\n🔍 Testing path resolution from dashboard/pages/:")
    test_paths = [
        Path("../../output"),
        Path("../output"),
        Path("output"),
        Path("../../../output"),
    ]

    for test_path in test_paths:
        print(f"📁 Testing path: {test_path}")
        print(f"   Absolute: {test_path.absolute()}")
        print(f"   Exists: {test_path.exists()}")
        if test_path.exists():
            digest_files = list(test_path.glob("digest*.md"))
            print(f"   Digest files: {len(digest_files)}")
            for file in digest_files:
                print(f"     - {file.name}")

    # Check if there are any .md files at all
    print("\n🔍 All .md files in output:")
    if output_dir.exists():
        md_files = list(output_dir.glob("*.md"))
        print(f"📄 Found {len(md_files)} .md files:")
        for file in md_files:
            print(f"   - {file.name} ({file.stat().st_size} bytes)")
            # Try to read first few lines
            try:
                with open(file, encoding="utf-8") as f:
                    first_line = f.readline().strip()
                    print(f"     First line: {first_line[:50]}...")
            except Exception as e:
                print(f"     Error reading: {e}")


def create_test_digest():
    """Create a test digest file"""
    print("\n🔧 Creating test digest file...")

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    test_content = """# 🚀 Degen Digest - Test

**Date:** 2025-06-30 | **Edition:** Test Report

---

## 📋 Executive Summary

This is a test digest for debugging purposes.

---

## 🎯 Key Takeaways

Test content for debugging.

---

*Generated for testing*
"""

    test_file = output_dir / "digest-test.md"
    test_file.write_text(test_content)
    print(f"✅ Created test digest: {test_file}")
    print(f"📁 File size: {test_file.stat().st_size} bytes")


if __name__ == "__main__":
    debug_digest_files()
    create_test_digest()
    print("\n🎯 Debug complete! Check the output above for issues.")
