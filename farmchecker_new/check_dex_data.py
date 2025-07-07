#!/usr/bin/env python3
"""
Check DEX data structure to understand why migration found no pairs
"""

import json
import os
from google.cloud import storage

def get_gcs_client():
    """Create GCS client"""
    try:
        client = storage.Client()
        bucket = client.bucket('degen-digest-data')
        return client, bucket
    except Exception as e:
        print(f"❌ Failed to create GCS client: {e}")
        return None, None

def check_dex_data():
    """Check DEX data structure"""
    print("🔍 Checking DEX data structure...")
    
    client, bucket = get_gcs_client()
    if not bucket:
        return
    
    # Check DexScreener data
    print("\n📊 DexScreener Data:")
    blobs = list(bucket.list_blobs(prefix='dexscreener_data/'))
    print(f"Found {len(blobs)} DexScreener files")
    
    if blobs:
        blob = blobs[0]
        try:
            content = blob.download_as_text()
            data = json.loads(content)
            print(f"Sample file: {blob.name}")
            print(f"Type: {type(data)}")
            if isinstance(data, dict):
                print(f"Keys: {list(data.keys())}")
                if 'token_pairs' in data:
                    print(f"Token pairs type: {type(data['token_pairs'])}")
                    print(f"Token pairs length: {len(data['token_pairs']) if isinstance(data['token_pairs'], (list, dict)) else 'N/A'}")
                    if isinstance(data['token_pairs'], list) and data['token_pairs']:
                        print(f"First token pair: {data['token_pairs'][0]}")
                        print(f"First token pair type: {type(data['token_pairs'][0])}")
                if 'pair_by_id' in data:
                    print(f"Pair by ID type: {type(data['pair_by_id'])}")
                    print(f"Pair by ID length: {len(data['pair_by_id']) if isinstance(data['pair_by_id'], dict) else 'N/A'}")
                    if isinstance(data['pair_by_id'], dict) and data['pair_by_id']:
                        first_key = list(data['pair_by_id'].keys())[0]
                        print(f"First pair by ID: {data['pair_by_id'][first_key]}")
                        print(f"First pair by ID type: {type(data['pair_by_id'][first_key])}")
                if 'search_pairs' in data:
                    print(f"Search pairs type: {type(data['search_pairs'])}")
                    print(f"Search pairs length: {len(data['search_pairs']) if isinstance(data['search_pairs'], list) else 'N/A'}")
                    if isinstance(data['search_pairs'], list) and data['search_pairs']:
                        print(f"First search pair: {data['search_pairs'][0]}")
                        print(f"First search pair type: {type(data['search_pairs'][0])}")
            elif isinstance(data, list):
                print(f"List length: {len(data)}")
                if data:
                    print(f"Sample item: {list(data[0].keys())}")
        except Exception as e:
            print(f"Error reading file: {e}")
    
    # Check DexPaprika data
    print("\n📊 DexPaprika Data:")
    blobs = list(bucket.list_blobs(prefix='dexpaprika_data/'))
    print(f"Found {len(blobs)} DexPaprika files")
    
    if blobs:
        blob = blobs[0]
        try:
            content = blob.download_as_text()
            data = json.loads(content)
            print(f"Sample file: {blob.name}")
            print(f"Type: {type(data)}")
            if isinstance(data, dict):
                print(f"Keys: {list(data.keys())}")
                if 'token_data' in data:
                    print(f"Token data type: {type(data['token_data'])}")
                    print(f"Token data length: {len(data['token_data']) if isinstance(data['token_data'], (list, dict)) else 'N/A'}")
                    if isinstance(data['token_data'], dict) and data['token_data']:
                        first_key = list(data['token_data'].keys())[0]
                        print(f"First token data: {data['token_data'][first_key]}")
                        print(f"First token data type: {type(data['token_data'][first_key])}")
                    elif isinstance(data['token_data'], list) and data['token_data']:
                        print(f"First token data: {data['token_data'][0]}")
                        print(f"First token data type: {type(data['token_data'][0])}")
            elif isinstance(data, list):
                print(f"List length: {len(data)}")
                if data:
                    print(f"Sample item: {list(data[0].keys())}")
        except Exception as e:
            print(f"Error reading file: {e}")

if __name__ == "__main__":
    check_dex_data() 