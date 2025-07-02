#!/bin/bash

echo "🔄 Triggering Cloud Function for Fresh Data"
echo "=========================================="

# Trigger the cloud function
curl -X POST https://us-central1-lucky-union-463615-t3.cloudfunctions.net/refresh_data \
  -H "Content-Type: application/json" \
  -d '{"generate_digest": true, "force_refresh": true}' \
  --max-time 300

echo ""
echo "✅ Cloud function triggered!"
echo "Check the response above for status"
