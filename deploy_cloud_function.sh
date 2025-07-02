#!/bin/bash

# Deploy updated cloud function
echo "🚀 Deploying updated cloud function..."

# Set project and region
PROJECT_ID="lucky-union-463615-t3"
REGION="us-central1"

# Deploy the function
cd cloud_function

echo "📦 Deploying cloud function..."
gcloud functions deploy refresh_data \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --memory 2GB \
  --timeout 540s \
  --source . \
  --project $PROJECT_ID \
  --region $REGION

if [ $? -eq 0 ]; then
    echo "✅ Cloud function deployed successfully!"
    echo "🌐 Function URL: https://${REGION}-${PROJECT_ID}.cloudfunctions.net/refresh_data"
else
    echo "❌ Cloud function deployment failed!"
    exit 1
fi

cd ..

echo "🎉 Deployment complete!"
echo "💡 You can now run: python manual_data_refresh.py"
