#!/usr/bin/env python3
"""
Test script to verify digest generation works after fixing LLM batch processing error.
"""

import json
from datetime import datetime
from pathlib import Path


def test_digest_generation():
    """Test if digest generation works"""
    print("🧪 Testing Digest Generation")
    print("=" * 40)

    # Check if we have raw data
    output_dir = Path("output")
    raw_files = ["twitter_raw.json", "reddit_raw.json", "newsapi_raw.json"]

    has_data = False
    for file in raw_files:
        if (output_dir / file).exists():
            with open(output_dir / file) as f:
                data = json.load(f)
                if data:
                    print(f"✅ Found {len(data)} items in {file}")
                    has_data = True
                else:
                    print(f"⚠️ {file} is empty")
        else:
            print(f"❌ {file} not found")

    if not has_data:
        print("\n❌ No data available for digest generation")
        print("💡 Run scrapers first or use manual_data_refresh.py")
        return False

    # Try to generate digest
    print("\n📄 Attempting digest generation...")
    try:
        # Import and run main digest generation
        from main import main as run_digest

        run_digest()
        print("✅ Digest generation completed successfully!")

        # Check if digest was created
        digest_files = list(output_dir.glob("digest*.md"))
        if digest_files:
            latest_digest = max(digest_files, key=lambda x: x.stat().st_mtime)
            print(f"📄 Digest created: {latest_digest}")

            # Show preview
            with open(latest_digest, encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")[:10]
                print("\n📋 Digest Preview:")
                for line in lines:
                    print(f"   {line}")
                if len(content.split("\n")) > 10:
                    print("   ...")

            return True
        else:
            print("❌ No digest files found")
            return False

    except Exception as e:
        print(f"❌ Digest generation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_llm_functionality():
    """Test if LLM functionality works"""
    print("\n🤖 Testing LLM Functionality")
    print("=" * 40)

    try:
        from processor.summarizer import rewrite_content

        # Test with a simple content
        test_item = {
            "full_text": "Bitcoin price reaches new highs as institutional adoption increases."
        }

        result = rewrite_content(test_item)
        print(f"✅ LLM test successful: {result.get('headline', 'No headline')}")
        return True

    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        return False


def main():
    """Main test function"""
    print("🚀 Degen Digest System Test")
    print("=" * 50)
    print(f"⏰ Tested at: {datetime.now()}")

    # Test LLM functionality first
    llm_works = test_llm_functionality()

    if llm_works:
        # Test digest generation
        digest_works = test_digest_generation()

        if digest_works:
            print("\n🎉 All tests passed! System is working correctly.")
            print("📊 Check the dashboard at https://farmchecker.xyz")
        else:
            print("\n⚠️ Digest generation failed, but LLM is working.")
            print("💡 Check data availability and try manual_data_refresh.py")
    else:
        print("\n❌ LLM functionality is broken.")
        print("💡 Check API keys and network connectivity")


if __name__ == "__main__":
    main()
