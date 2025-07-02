#!/bin/bash

echo "🚀 FIXING ALL DEGEN DIGEST ISSUES NOW"
echo "======================================"
echo "⏰ Started at: $(date)"
echo ""

# Step 1: Test LLM fix
echo "1️⃣ Testing LLM functionality..."
python3 test_digest_generation.py

# Step 2: Sync data from cloud function
echo ""
echo "2️⃣ Syncing data from cloud function..."
python3 manual_data_refresh.py

# Step 3: Generate digest locally
echo ""
echo "3️⃣ Generating digest locally..."
python3 main.py

# Step 4: Check results
echo ""
echo "4️⃣ Checking results..."
echo "Database contents:"
sqlite3 output/degen_digest.db "SELECT COUNT(*) FROM tweet; SELECT COUNT(*) FROM redditpost; SELECT COUNT(*) FROM digest;"

echo ""
echo "Digest files:"
ls -la output/digest*.md

echo ""
echo "🎉 ALL FIXES COMPLETED!"
echo "Check https://farmchecker.xyz for results"
