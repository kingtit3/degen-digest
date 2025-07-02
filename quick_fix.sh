#!/bin/bash

echo "🚀 Quick Fix for Degen Digest Issues"
echo "===================================="

# Step 1: Test LLM fix
echo "1. Testing LLM functionality..."
python3 test_digest_generation.py 2>/dev/null || echo "LLM test failed, continuing..."

# Step 2: Sync data from cloud function
echo "2. Syncing data from cloud function..."
python3 manual_data_refresh.py 2>/dev/null || echo "Manual refresh failed, trying curl..."

# Step 3: Try curl if Python fails
echo "3. Trying cloud function via curl..."
curl -X POST https://us-central1-lucky-union-463615-t3.cloudfunctions.net/refresh_data \
  -H "Content-Type: application/json" \
  -d '{"generate_digest": true, "force_refresh": true}' \
  --max-time 60 2>/dev/null || echo "Cloud function call failed"

# Step 4: Generate digest locally
echo "4. Generating digest locally..."
python3 main.py 2>/dev/null || echo "Main script failed"

# Step 5: Check results
echo "5. Checking results..."
echo "Database contents:"
sqlite3 output/degen_digest.db "SELECT COUNT(*) FROM tweet; SELECT COUNT(*) FROM redditpost; SELECT COUNT(*) FROM digest;" 2>/dev/null || echo "Database check failed"

echo "Digest files:"
ls -la output/digest*.md 2>/dev/null || echo "No digest files found"

echo "🎉 Quick fix completed!"
echo "Check https://farmchecker.xyz for results"
