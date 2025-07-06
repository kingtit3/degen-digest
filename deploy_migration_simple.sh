#!/bin/bash

echo "🚀 Deploying Simple Migration Cloud Function"
echo "=========================================="

# Set variables
FUNCTION_NAME="migrate-to-sql-simple"
REGION="us-central1"
PROJECT_ID="lucky-union-463615-t3"

# Create a clean deployment directory
rm -rf migration_deploy_simple
mkdir -p migration_deploy_simple
cp cloud_function_migration/main.py migration_deploy_simple/
cp cloud_function_migration/requirements.txt migration_deploy_simple/

echo "Preparing function..."

# Deploy the function with better settings
gcloud functions deploy $FUNCTION_NAME \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source=migration_deploy_simple \
    --entry-point=migrate \
    --trigger-http \
    --allow-unauthenticated \
    --memory=1Gi \
    --timeout=900s \
    --min-instances=0 \
    --max-instances=1 \
    --set-env-vars="DB_HOST=34.9.71.174,DB_PORT=5432,DB_NAME=degen_digest,DB_USER=postgres,DB_PASSWORD=DegenDigest2024!,BUCKET_NAME=degen-digest-data,PROJECT_ID=$PROJECT_ID" \
    --project=$PROJECT_ID

if [ $? -eq 0 ]; then
    echo "✅ Simple migration function deployed successfully!"
    echo ""
    echo "🔧 To run the migration:"
    echo "gcloud functions call $FUNCTION_NAME --region=$REGION"
    echo ""
    echo "🔗 Function URL:"
    gcloud functions describe $FUNCTION_NAME --region=$REGION --format="value(serviceConfig.uri)"
else
    echo "❌ Deployment failed!"
    exit 1
fi
