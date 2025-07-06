#!/usr/bin/env python3
"""
Check the actual structure of crypto data
"""
import json

from google.cloud import storage

# Configuration
GCS_BUCKET = "degen-digest-data"
PROJECT_ID = "lucky-union-463615-t3"


def check_crypto_structure():
    """Check the structure of crypto data"""
    try:
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(GCS_BUCKET)

        # Get crypto data
        crypto_blob = bucket.blob("consolidated/crypto_consolidated.json")
        data = json.loads(crypto_blob.download_as_text())

        print("=== CRYPTO DATA STRUCTURE ===")
        print(f"Top-level keys: {list(data.keys())}")

        if "metadata" in data:
            print(f"\nMetadata: {data['metadata']}")

        if "gainers" in data:
            gainers = data["gainers"]
            print(f"\nGainers count: {len(gainers)}")
            if gainers:
                print(f"Sample gainer: {gainers[0]}")
                print(f"Gainer keys: {list(gainers[0].keys())}")

        # Check other crypto files
        print("\n=== OTHER CRYPTO FILES ===")
        blobs = list(bucket.list_blobs(prefix="consolidated/"))
        for blob in blobs:
            if "crypto" in blob.name or "coingecko" in blob.name or "dex" in blob.name:
                print(f"\nFile: {blob.name}")
                try:
                    file_data = json.loads(blob.download_as_text())
                    print(f"  Keys: {list(file_data.keys())}")
                    if "data" in file_data:
                        print(f"  Data count: {len(file_data['data'])}")
                except Exception as e:
                    print(f"  Error reading: {e}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    check_crypto_structure()
