#!/bin/bash

# FarmChecker.xyz Cloud Deployment Script
# Deploys the updated dashboard to Google Cloud Run with domain mapping

set -e

echo "🚀 Deploying FarmChecker.xyz to Google Cloud..."
echo "================================================"

# Configuration
PROJECT_ID="lucky-union-463615-t3"
REGION="us-central1"
SERVICE_NAME="farmchecker-dashboard"
DOMAIN="farmchecker.xyz"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

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

# Check dependencies
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

# Enable required APIs
enable_apis() {
    print_status "Enabling required APIs..."

    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable run.googleapis.com
    gcloud services enable domains.googleapis.com
    gcloud services enable dns.googleapis.com

    print_success "APIs enabled"
}

# Build and push Docker image
build_and_push_image() {
    print_status "Building Docker image for farmchecker.xyz..."

    # Build with no cache to ensure latest changes
    docker build --platform=linux/amd64 -f Dockerfile.dashboard -t $IMAGE_NAME:latest --no-cache .

    print_success "Docker image built"

    print_status "Pushing Docker image to Google Container Registry..."

    docker push $IMAGE_NAME:latest

    print_success "Docker image pushed"
}

# Deploy to Cloud Run
deploy_to_cloud_run() {
    print_status "Deploying to Cloud Run..."

    gcloud run deploy $SERVICE_NAME \
        --image $IMAGE_NAME:latest \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --memory 4Gi \
        --cpu 2 \
        --timeout 3600 \
        --concurrency 80 \
        --max-instances 10 \
        --port 8501 \
        --set-env-vars "ENVIRONMENT=production" \
        --set-env-vars "DOMAIN=$DOMAIN" \
        --set-env-vars "ENABLE_CLOUD_CRAWLER=true"

    print_success "Cloud Run service deployed"
}

# Map custom domain
map_custom_domain() {
    print_status "Mapping custom domain: $DOMAIN"

    # Check if domain mapping already exists
    if gcloud alpha run domain-mappings list --region=$REGION --filter="metadata.name=$DOMAIN" --format="value(metadata.name)" | grep -q "$DOMAIN"; then
        print_warning "Domain mapping already exists, updating..."
        gcloud alpha run domain-mappings update $DOMAIN \
            --service $SERVICE_NAME \
            --region $REGION
    else
        print_status "Creating new domain mapping..."
        gcloud alpha run domain-mappings create $DOMAIN \
            --service $SERVICE_NAME \
            --region $REGION
    fi

    print_success "Domain mapping configured"
}

# Verify SSL certificate
verify_ssl() {
    print_status "Verifying SSL certificate..."

    # Wait for SSL certificate to be provisioned
    print_status "Waiting for SSL certificate to be provisioned (this may take a few minutes)..."

    for i in {1..30}; do
        if curl -f -s "https://$DOMAIN" > /dev/null 2>&1; then
            print_success "SSL certificate is active and domain is accessible"
            break
        else
            print_status "Waiting for SSL certificate... (attempt $i/30)"
            sleep 30
        fi
    done

    if [ $i -eq 30 ]; then
        print_warning "SSL certificate may still be provisioning. Please check manually in a few minutes."
    fi
}

# Test the deployment
test_deployment() {
    print_status "Testing deployment..."

    # Test Cloud Run service directly
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

    print_status "Testing Cloud Run service: $SERVICE_URL"

    if curl -f -s "$SERVICE_URL" > /dev/null; then
        print_success "Cloud Run service is responding"
    else
        print_warning "Cloud Run service may not be fully ready yet"
    fi

    # Test custom domain
    print_status "Testing custom domain: https://$DOMAIN"

    if curl -f -s "https://$DOMAIN" > /dev/null; then
        print_success "Custom domain is accessible"
    else
        print_warning "Custom domain may not be ready yet. Please check in a few minutes."
    fi
}

# Create deployment summary
create_deployment_summary() {
    print_status "Creating deployment summary..."

    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

    cat > FARMCHECKER_DEPLOYMENT_SUMMARY.md << EOF
# FarmChecker.xyz Deployment Summary

## Deployment Information
- **Project ID:** $PROJECT_ID
- **Region:** $REGION
- **Service Name:** $SERVICE_NAME
- **Custom Domain:** $DOMAIN
- **Deployment Date:** $(date)

## URLs
- **Cloud Run Service:** $SERVICE_URL
- **Custom Domain:** https://$DOMAIN

## Features Deployed
- ✅ Updated dashboard with simplified crawler controls
- ✅ Cloud Run integration for Solana crawler
- ✅ HTTP-based crawler control (Start/Stop)
- ✅ Automatic 18-hour schedule in cloud
- ✅ No login/settings UI required
- ✅ Real-time status monitoring

## Crawler Integration
- **Cloud Crawler URL:** https://solana-crawler-128671663649.us-central1.run.app
- **Status Endpoint:** /status
- **Start Endpoint:** /start
- **Stop Endpoint:** /stop

## Management Commands
\`\`\`bash
# View service status
gcloud run services describe $SERVICE_NAME --region=$REGION

# View logs
gcloud logs read --service=$SERVICE_NAME --limit=50

# Update deployment
./deploy_farmchecker_cloud.sh

# Check domain mapping
gcloud alpha run domain-mappings list --region=$REGION
\`\`\`

## Health Check
Visit https://$DOMAIN to verify the dashboard is working correctly.

EOF

    print_success "Deployment summary created: FARMCHECKER_DEPLOYMENT_SUMMARY.md"
}

# Main deployment process
main() {
    echo "🚀 Starting FarmChecker.xyz deployment..."
    echo "================================================"

    check_dependencies
    authenticate_gcloud
    enable_apis
    build_and_push_image
    deploy_to_cloud_run
    map_custom_domain
    verify_ssl
    test_deployment
    create_deployment_summary

    echo ""
    echo "🎉 FarmChecker.xyz Deployment Complete!"
    echo "========================================"
    echo ""
    echo "🌐 Your dashboard is now live at: https://$DOMAIN"
    echo ""
    echo "📊 Crawler Status:"
    echo "   • Cloud crawler is running at: https://solana-crawler-128671663649.us-central1.run.app"
    echo "   • 18-hour automatic schedule enabled"
    echo "   • Use dashboard to start/stop manually"
    echo ""
    echo "🔧 Management:"
    echo "   • View logs: gcloud logs read --service=$SERVICE_NAME --limit=50"
    echo "   • Update deployment: ./deploy_farmchecker_cloud.sh"
    echo "   • Health check: curl -f https://$DOMAIN"
    echo ""

    print_success "FarmChecker.xyz is now live! 🚀"
}

# Run main function
main "$@"
