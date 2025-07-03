#!/usr/bin/env python3
"""Test script to verify OpenRouter API key is working"""

import os

import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Check if API key is loaded
api_key = os.getenv("OPENROUTER_API_KEY")
print(f"🔑 API Key found: {'Yes' if api_key else 'No'}")
if api_key:
    print(f"🔑 API Key starts with: {api_key[:10]}...")

# Test OpenRouter account status
if api_key:
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        # Check account status
        response = requests.get(
            "https://openrouter.ai/api/v1/auth/key", headers=headers
        )
        if response.status_code == 200:
            account_info = response.json()
            print("✅ OpenRouter account status:")
            print(f"   - Credits remaining: ${account_info.get('credits', 'Unknown')}")
            print(f"   - Account status: {account_info.get('status', 'Unknown')}")
        else:
            print(f"❌ Failed to get account status: {response.status_code}")

    except Exception as e:
        print(f"❌ Account check failed: {e}")

# Test the API
try:
    client = OpenAI(
        base_url=os.getenv("OPENROUTER_API_BASE") or "https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    response = client.chat.completions.create(
        model=os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001"),
        messages=[{"role": "user", "content": "Hello, this is a test message."}],
        max_tokens=10,
    )

    print("✅ API test successful!")
    print(f"Response: {response.choices[0].message.content}")

except Exception as e:
    print(f"❌ API test failed: {e}")
    print("\n💡 If this fails, you can:")
    print("1. Check your OpenRouter account at: https://openrouter.ai/keys")
    print("2. Verify you have credits remaining")
    print("3. Or switch to Google Cloud AI (see below)")
