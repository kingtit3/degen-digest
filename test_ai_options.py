#!/usr/bin/env python3
"""Test script to compare OpenRouter vs Google Cloud AI options"""

import os

from dotenv import load_dotenv

load_dotenv()


def test_openrouter():
    """Test OpenRouter configuration"""
    print("🔍 Testing OpenRouter Configuration:")
    print("-" * 40)

    api_key = os.getenv("OPENROUTER_API_KEY")
    api_base = os.getenv("OPENROUTER_API_BASE")
    model = os.getenv("OPENROUTER_MODEL")

    print(f"API Key: {'✅ Found' if api_key else '❌ Missing'}")
    print(f"API Base: {api_base or 'Default'}")
    print(f"Model: {model or 'Default'}")

    if api_key:
        print("✅ OpenRouter is configured!")
        return True
    else:
        print("❌ OpenRouter needs configuration")
        return False


def test_google_ai():
    """Test Google Cloud AI configuration"""
    print("\n🔍 Testing Google Cloud AI Configuration:")
    print("-" * 40)

    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

    print(f"Project ID: {'✅ Found' if project_id else '❌ Missing'}")
    print(f"Location: {location}")

    if project_id:
        print("✅ Google Cloud AI is configured!")
        return True
    else:
        print("❌ Google Cloud AI needs configuration")
        return False


def main():
    """Main test function"""
    print("🤖 AI Provider Configuration Test")
    print("=" * 50)

    openrouter_ok = test_openrouter()
    google_ai_ok = test_google_ai()

    print("\n📊 Summary:")
    print("-" * 20)

    if openrouter_ok and google_ai_ok:
        print("✅ Both providers configured!")
        print("💡 OpenRouter will be used by default")
        print("💡 To switch to Google AI, comment out OPENROUTER_API_KEY in .env")
    elif openrouter_ok:
        print("✅ OpenRouter configured - ready to use!")
    elif google_ai_ok:
        print("✅ Google Cloud AI configured - ready to use!")
    else:
        print("❌ No AI providers configured")
        print("\n🔧 Setup Options:")
        print("1. OpenRouter: Get API key from https://openrouter.ai/keys")
        print("2. Google Cloud AI: Run 'python google_ai_setup.py' for instructions")


if __name__ == "__main__":
    main()
