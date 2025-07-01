#!/bin/bash

# Enhanced System Production Deployment Script
# Deploys the complete enhanced viral prediction system

set -e

echo "🚀 Deploying Enhanced Viral Prediction System"
echo "=============================================="

# Configuration
PROJECT_ID="degen-digest-123456"
REGION="us-central1"
SERVICE_NAME="degen-digest-enhanced"
CLOUD_FUNCTION_NAME="degen-digest-function-enhanced"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI is not installed. Please install it first."
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install it first."
        exit 1
    fi
    
    print_success "All dependencies are installed"
}

# Authenticate with Google Cloud
authenticate_gcloud() {
    print_status "Authenticating with Google Cloud..."
    
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_warning "No active gcloud authentication found. Please run: gcloud auth login"
        gcloud auth login
    fi
    
    gcloud config set project $PROJECT_ID
    gcloud config set run/region $REGION
    
    print_success "Google Cloud authentication completed"
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    pip install -r requirements.txt
    
    # Install additional dependencies for enhanced system
    pip install nest-asyncio schedule
    
    print_success "Dependencies installed"
}

# Run comprehensive tests
run_tests() {
    print_status "Running comprehensive tests..."
    
    python test_all_enhancements.py
    
    if [ $? -eq 0 ]; then
        print_success "All tests passed"
    else
        print_error "Tests failed. Please fix issues before deployment."
        exit 1
    fi
}

# Build and push Docker image
build_docker_image() {
    print_status "Building Docker image..."
    
    # Build with no cache to ensure latest changes
    docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME:latest --no-cache .
    
    print_success "Docker image built"
    
    print_status "Pushing Docker image to Google Container Registry..."
    
    docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:latest
    
    print_success "Docker image pushed"
}

# Deploy to Cloud Run
deploy_cloud_run() {
    print_status "Deploying to Cloud Run..."
    
    gcloud run deploy $SERVICE_NAME \
        --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --memory 2Gi \
        --cpu 2 \
        --timeout 3600 \
        --concurrency 80 \
        --max-instances 10 \
        --set-env-vars "ENVIRONMENT=production" \
        --set-env-vars "ENABLE_ENHANCED_FEATURES=true"
    
    print_success "Cloud Run service deployed"
}

# Deploy Cloud Function
deploy_cloud_function() {
    print_status "Deploying Cloud Function..."
    
    cd cloud_function
    
    gcloud functions deploy $CLOUD_FUNCTION_NAME \
        --runtime python39 \
        --trigger-http \
        --allow-unauthenticated \
        --memory 512MB \
        --timeout 540s \
        --set-env-vars "ENVIRONMENT=production" \
        --set-env-vars "ENABLE_ENHANCED_FEATURES=true"
    
    cd ..
    
    print_success "Cloud Function deployed"
}

# Set up monitoring and logging
setup_monitoring() {
    print_status "Setting up monitoring and logging..."
    
    # Enable required APIs
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable run.googleapis.com
    gcloud services enable cloudfunctions.googleapis.com
    gcloud services enable logging.googleapis.com
    gcloud services enable monitoring.googleapis.com
    
    print_success "Monitoring and logging configured"
}

# Verify deployment
verify_deployment() {
    print_status "Verifying deployment..."
    
    # Get Cloud Run service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
    
    print_status "Cloud Run service URL: $SERVICE_URL"
    
    # Test the service
    print_status "Testing service..."
    
    # Wait a moment for service to be ready
    sleep 30
    
    # Test basic connectivity
    if curl -f -s "$SERVICE_URL" > /dev/null; then
        print_success "Service is responding"
    else
        print_warning "Service may not be fully ready yet"
    fi
    
    # Get Cloud Function URL
    FUNCTION_URL=$(gcloud functions describe $CLOUD_FUNCTION_NAME --format="value(httpsTrigger.url)")
    
    print_status "Cloud Function URL: $FUNCTION_URL"
    
    print_success "Deployment verification completed"
}

# Create deployment summary
create_deployment_summary() {
    print_status "Creating deployment summary..."
    
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
    FUNCTION_URL=$(gcloud functions describe $CLOUD_FUNCTION_NAME --format="value(httpsTrigger.url)")
    
    cat > DEPLOYMENT_SUMMARY.md << EOF
# Enhanced System Deployment Summary

## Deployment Information
- **Date**: $(date)
- **Project ID**: $PROJECT_ID
- **Region**: $REGION

## Services Deployed

### Cloud Run Service
- **Service Name**: $SERVICE_NAME
- **URL**: $SERVICE_URL
- **Memory**: 2Gi
- **CPU**: 2
- **Max Instances**: 10

### Cloud Function
- **Function Name**: $CLOUD_FUNCTION_NAME
- **URL**: $FUNCTION_URL
- **Memory**: 512MB
- **Timeout**: 540s

## Enhanced Features Enabled
- ✅ Multi-platform data collection (Twitter, Reddit, Telegram, News, Market, Discord)
- ✅ Advanced viral prediction with ensemble ML models
- ✅ Real-time data processing pipeline
- ✅ Automated model retraining
- ✅ Data quality monitoring
- ✅ Enhanced analytics dashboard

## Next Steps
1. Access the dashboard at: $SERVICE_URL
2. Monitor logs: \`gcloud logs tail --service=$SERVICE_NAME\`
3. Check function logs: \`gcloud functions logs read $CLOUD_FUNCTION_NAME\`
4. Run enhanced pipeline: \`python scripts/enhanced_data_pipeline.py\`

## Monitoring
- View service metrics in Google Cloud Console
- Check application logs for any issues
- Monitor data quality reports in the dashboard

## Support
For issues or questions, check the logs and documentation.
EOF
    
    print_success "Deployment summary created: DEPLOYMENT_SUMMARY.md"
}

# Main deployment function
main() {
    echo "Starting enhanced system deployment..."
    echo
    
    check_dependencies
    authenticate_gcloud
    install_dependencies
    run_tests
    setup_monitoring
    build_docker_image
    deploy_cloud_run
    deploy_cloud_function
    verify_deployment
    create_deployment_summary
    
    echo
    echo "🎉 Enhanced System Deployment Complete!"
    echo "======================================"
    echo
    echo "Services deployed:"
    echo "- Cloud Run: $SERVICE_NAME"
    echo "- Cloud Function: $CLOUD_FUNCTION_NAME"
    echo
    echo "Next steps:"
    echo "1. Access your dashboard"
    echo "2. Monitor the enhanced pipeline"
    echo "3. Check data quality reports"
    echo "4. Review viral predictions"
    echo
    echo "For detailed information, see: DEPLOYMENT_SUMMARY.md"
}

# Run main function
main "$@" 