#!/bin/bash

# Deploy Cloud Function with full codebase
echo "🚀 Deploying Cloud Function with full codebase..."

# Set project
PROJECT_ID="lucky-union-463615-t3"
REGION="us-central1"
FUNCTION_NAME="farmchecker-data-refresh"

# Create a temporary directory for deployment
TEMP_DIR=$(mktemp -d)
echo "📁 Created temp directory: $TEMP_DIR"

# Copy the entire codebase to temp directory
echo "📋 Copying codebase..."
cp -r . "$TEMP_DIR/"
cd "$TEMP_DIR"

# Remove unnecessary files for cloud function
echo "🧹 Cleaning up unnecessary files..."
rm -rf .git
rm -rf logs/*
rm -rf output/*
rm -rf __pycache__
rm -rf */__pycache__
rm -rf .streamlit
rm -rf degen_digest.session

# Create a .gcloudignore file
echo "📝 Creating .gcloudignore..."
cat > .gcloudignore << EOF
.git
.gitignore
logs/
output/
__pycache__/
*.session
.streamlit/
*.log
*.db
*.sqlite
*.pdf
*.md
EOF

# Deploy the cloud function
echo "🚀 Deploying cloud function..."
gcloud functions deploy "$FUNCTION_NAME" \
    --gen2 \
    --runtime=python311 \
    --region="$REGION" \
    --source=. \
    --entry-point=refresh_data \
    --trigger-http \
    --allow-unauthenticated \
    --memory=4GB \
    --timeout=540s \
    --set-env-vars="LOG_EXECUTION_ID=true"

# Clean up
echo "🧹 Cleaning up..."
cd ..
rm -rf "$TEMP_DIR"

echo "✅ Cloud function deployment completed!"
echo "🌐 Function URL: https://$REGION-$PROJECT_ID.cloudfunctions.net/$FUNCTION_NAME" 