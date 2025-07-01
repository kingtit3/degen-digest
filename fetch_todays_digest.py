#!/usr/bin/env python3
"""
Fetch today's digest from the cloud function and save it locally.
"""

import requests
import json
from pathlib import Path
from datetime import datetime
import sys

def fetch_todays_digest():
    """Fetch today's digest from the cloud function"""
    
    print("🚀 Fetching today's digest from cloud function...")
    
    # Cloud function URL
    url = "https://us-central1-lucky-union-463615-t3.cloudfunctions.net/degen-digest-refresh"
    
    # Request payload
    payload = {
        "generate_digest": True,
        "force_refresh": True
    }
    
    try:
        # Make request to cloud function
        response = requests.post(url, json=payload, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("status") == "success":
                print(f"✅ Success! Collected {data['metrics']['data_collected']} items")
                print(f"📊 Sources: {data['metrics']['sources']}")
                print(f"⏱️ Execution time: {data['metrics']['total_execution_time']:.2f}s")
                
                # Check if digest was generated
                if "digest_content" in data:
                    digest_content = data["digest_content"]
                    digest_date = data.get("digest_date", datetime.now().strftime('%Y-%m-%d'))
                    
                    # Save digest files locally
                    output_dir = Path("output")
                    output_dir.mkdir(exist_ok=True)
                    
                    # Save current digest
                    digest_path = output_dir / "digest.md"
                    with open(digest_path, 'w', encoding='utf-8') as f:
                        f.write(digest_content)
                    
                    # Save dated digest
                    dated_digest_path = output_dir / f"digest-{digest_date}.md"
                    with open(dated_digest_path, 'w', encoding='utf-8') as f:
                        f.write(digest_content)
                    
                    print(f"📄 Digest saved to: {digest_path}")
                    print(f"📄 Dated digest saved to: {dated_digest_path}")
                    
                    # Display first few lines of digest
                    print("\n" + "="*50)
                    print("📋 TODAY'S DIGEST PREVIEW:")
                    print("="*50)
                    lines = digest_content.split('\n')[:20]
                    for line in lines:
                        print(line)
                    if len(digest_content.split('\n')) > 20:
                        print("...")
                    print("="*50)
                    
                    return True
                else:
                    print("❌ No digest content in response")
                    return False
            else:
                print(f"❌ Cloud function returned error: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (function may still be running)")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = fetch_todays_digest()
    if success:
        print("\n🎉 Today's digest has been successfully fetched and saved!")
        print("You can now view it in the dashboard or open the files directly.")
    else:
        print("\n💥 Failed to fetch today's digest.")
        sys.exit(1) 