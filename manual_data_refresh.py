#!/usr/bin/env python3
"""
Manual data refresh script to trigger cloud function and save data locally.
"""

import json
from datetime import datetime
from pathlib import Path

import requests


def main():
    print("🔄 Manual Data Refresh")
    print("=" * 30)

    # Cloud function URL
    url = "https://us-central1-lucky-union-463615-t3.cloudfunctions.net/refresh_data"

    # Request payload
    payload = {"generate_digest": True, "force_refresh": True}

    try:
        print("📡 Calling cloud function...")
        response = requests.post(url, json=payload, timeout=300)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('status', 'unknown')}")

            # Save the full response
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)

            response_file = output_dir / "cloud_function_response.json"
            with open(response_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)

            print(f"💾 Response saved to: {response_file}")

            # Extract and save digest if available
            if "digest_content" in data:
                digest_content = data["digest_content"]
                digest_date = data.get(
                    "digest_date", datetime.now().strftime("%Y-%m-%d")
                )

                # Save current digest
                digest_path = output_dir / "digest.md"
                with open(digest_path, "w", encoding="utf-8") as f:
                    f.write(digest_content)

                # Save dated digest
                dated_digest_path = output_dir / f"digest-{digest_date}.md"
                with open(dated_digest_path, "w", encoding="utf-8") as f:
                    f.write(digest_content)

                print(f"📄 Digest saved to: {digest_path}")
                print(f"📄 Dated digest saved to: {dated_digest_path}")

            # Extract and save processed data if available
            if "processed_data" in data:
                processed_data = data["processed_data"]

                # Save consolidated data
                consolidated_path = output_dir / "consolidated_data.json"
                with open(consolidated_path, "w", encoding="utf-8") as f:
                    json.dump(processed_data, f, indent=2, default=str)

                print(f"📊 Processed data saved to: {consolidated_path}")

                # Separate by source
                sources = {"twitter": [], "reddit": [], "news": []}
                for item in processed_data:
                    source = item.get("source", "unknown")
                    if source in sources:
                        sources[source].append(item)

                # Save individual source files
                for source, data_list in sources.items():
                    if data_list:
                        source_path = output_dir / f"{source}_raw.json"
                        with open(source_path, "w", encoding="utf-8") as f:
                            json.dump(data_list, f, indent=2, default=str)
                        print(f"   📄 Saved {len(data_list)} {source} items")

            # Show metrics
            metrics = data.get("metrics", {})
            print("\n📈 Metrics:")
            print(f"   • Data collected: {metrics.get('data_collected', 0)}")
            print(f"   • Data processed: {metrics.get('data_processed', 0)}")
            print(f"   • Execution time: {metrics.get('total_execution_time', 0):.2f}s")
            print(f"   • Sources: {metrics.get('sources', {})}")

        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
