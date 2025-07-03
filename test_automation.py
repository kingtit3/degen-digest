#!/usr/bin/env python3
"""Test the automatic renaming functionality"""

from datetime import datetime
from pathlib import Path


def test_rename_function():
    """Test the rename_digest function"""
    print("🧪 Testing Automatic Renaming")
    print("=" * 40)

    # Check if rename_digest.py exists
    rename_script = Path("rename_digest.py")
    if not rename_script.exists():
        print("❌ rename_digest.py not found")
        return False

    # Check if output directory exists
    output_dir = Path("output")
    if not output_dir.exists():
        print("❌ output directory not found")
        return False

    # Check for digest files
    digest_files = list(output_dir.glob("digest*.md"))
    print(f"📄 Found {len(digest_files)} digest files:")
    for file in digest_files:
        size = file.stat().st_size
        mtime = datetime.fromtimestamp(file.stat().st_mtime)
        print(f"   - {file.name} ({size:,} bytes, {mtime.strftime('%Y-%m-%d %H:%M')})")

    # Test importing the function
    try:
        from rename_digest import rename_digest

        print("✅ Successfully imported rename_digest function")

        # Test calling the function
        print("🔄 Testing rename function...")
        rename_digest()
        print("✅ Rename function executed successfully")

        # Check results
        updated_files = list(output_dir.glob("digest*.md"))
        print(f"📄 After rename: {len(updated_files)} digest files:")
        for file in updated_files:
            size = file.stat().st_size
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            print(
                f"   - {file.name} ({size:,} bytes, {mtime.strftime('%Y-%m-%d %H:%M')})"
            )

        return True

    except Exception as e:
        print(f"❌ Error testing rename function: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_rename_function()
    print(f"\n{'✅ Test passed' if success else '❌ Test failed'}")
