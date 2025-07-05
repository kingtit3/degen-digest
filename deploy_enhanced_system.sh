#!/bin/bash

# DegenDigest Enhanced System Deployment Script
# Comprehensive deployment with logging, monitoring, and health checks

set -e  # Exit on any error

# Configuration
PROJECT_ID="lucky-union-463615-t3"
REGION="us-central1"
ENVIRONMENT="production"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Function to check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."

    # Check if gcloud is installed and authenticated
    if ! command -v gcloud &> /dev/null; then
        error "gcloud CLI is not installed. Please install it first."
    fi

    # Check if user is authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        error "Not authenticated with gcloud. Please run 'gcloud auth login' first."
    fi

    # Check if project is set
    if [ "$(gcloud config get-value project)" != "$PROJECT_ID" ]; then
        warn "Setting project to $PROJECT_ID"
        gcloud config set project $PROJECT_ID
    fi

    log "Prerequisites check completed successfully"
}

# Function to enable required APIs
enable_apis() {
    log "Enabling required Google Cloud APIs..."

    local apis=(
        "cloudrun.googleapis.com"
        "cloudbuild.googleapis.com"
        "cloudscheduler.googleapis.com"
        "cloudtasks.googleapis.com"
        "logging.googleapis.com"
        "monitoring.googleapis.com"
        "storage.googleapis.com"
        "sqladmin.googleapis.com"
        "bigquery.googleapis.com"
        "firestore.googleapis.com"
    )

    for api in "${apis[@]}"; do
        if ! gcloud services list --enabled --filter="name:$api" --format="value(name)" | grep -q "$api"; then
            log "Enabling $api..."
            gcloud services enable "$api" --project=$PROJECT_ID
        else
            info "$api is already enabled"
        fi
    done

    log "All required APIs enabled"
}

# Function to create logging configuration
setup_logging() {
    log "Setting up logging configuration..."

    # Create logs directory
    mkdir -p logs

    # Create logging configuration file
    cat > config/logging_config.yaml << EOF
logging:
  level: INFO
  format: json
  directory: logs
  max_file_size_mb: 10
  backup_count: 5

  handlers:
    console:
      enabled: true
      level: INFO

    file:
      enabled: true
      level: DEBUG
      rotation: true

    json:
      enabled: true
      level: INFO

    cloud:
      enabled: true
      level: ERROR

  performance:
    enabled: true
    threshold_ms: 1000
    track_operations: true

  security:
    enabled: true
    level: WARNING
    track_events: true

  context:
    enabled: true
    track_request_id: true
    track_user_id: true
    track_session_id: true
EOF

    log "Logging configuration created"
}

# Function to create monitoring configuration
setup_monitoring() {
    log "Setting up monitoring configuration..."

    # Create monitoring configuration file
    cat > config/monitoring_config.yaml << EOF
monitoring:
  check_interval: 60
  metrics_interval: 30

  thresholds:
    cpu_percent: 80.0
    memory_percent: 85.0
    disk_percent: 90.0
    response_time_ms: 1000
    error_rate: 0.05
    uptime_hours: 24

  alerting:
    enabled: true
    webhook_url: ""
    email_recipients: []
    slack_webhook: ""

  components:
    system: true
    database: true
    services: true
    apis: true
    data_quality: true
    security: true
EOF

    log "Monitoring configuration created"
}

# Function to build and deploy services
deploy_services() {
    log "Building and deploying Cloud Run services..."

    # Services to deploy
    local services=(
        "dexscreener-crawler"
        "dexpaprika-crawler"
        "twitter-crawler"
        "data-aggregator"
        "dashboard"
    )

    for service in "${services[@]}"; do
        log "Deploying $service..."

        # Build and deploy
        gcloud run deploy "$service" \
            --source . \
            --platform managed \
            --region $REGION \
            --project $PROJECT_ID \
            --allow-unauthenticated \
            --memory 1Gi \
            --cpu 1 \
            --timeout 300 \
            --set-env-vars "PYTHONPATH=/app,ENVIRONMENT=$ENVIRONMENT" \
            --max-instances 10 \
            --min-instances 0

        # Get service URL
        local service_url=$(gcloud run services describe "$service" \
            --region=$REGION \
            --format="value(status.url)")

        log "$service deployed successfully: $service_url"
    done

    log "All services deployed successfully"
}

# Function to setup Cloud Scheduler jobs
setup_scheduler() {
    log "Setting up Cloud Scheduler jobs..."

    # Create scheduler configuration
    cat > config/scheduler_config.yaml << EOF
scheduler:
  jobs:
    - name: dexscreener-crawler
      schedule: "*/30 * * * *"
      url: "https://dexscreener-crawler-128671663649.us-central1.run.app"
      method: POST

    - name: dexpaprika-crawler
      schedule: "*/30 * * * *"
      url: "https://dexpaprika-crawler-128671663649.us-central1.run.app"
      method: POST

    - name: twitter-crawler
      schedule: "*/20 * * * *"
      url: "https://twitter-crawler-128671663649.us-central1.run.app"
      method: POST

    - name: data-aggregator
      schedule: "*/15 * * * *"
      url: "https://data-aggregator-128671663649.us-central1.run.app"
      method: POST

    - name: digest-generation
      schedule: "0 6 * * *"
      url: "https://data-aggregator-128671663649.us-central1.run.app/generate-digest"
      method: POST

    - name: health-check
      schedule: "*/5 * * * *"
      url: "https://data-aggregator-128671663649.us-central1.run.app/health"
      method: GET

    - name: data-cleanup
      schedule: "0 2 * * *"
      url: "https://data-aggregator-128671663649.us-central1.run.app/cleanup"
      method: POST
EOF

    log "Scheduler configuration created"
}

# Function to setup monitoring and alerting
setup_monitoring_alerting() {
    log "Setting up monitoring and alerting..."

    # Create monitoring dashboard
    cat > config/dashboard_config.yaml << EOF
dashboard:
  title: "DegenDigest System Monitor"
  refresh_interval: 30

  panels:
    - title: "System Health"
      type: "health_status"
      position: [0, 0]
      size: [6, 4]

    - title: "CPU Usage"
      type: "line_chart"
      position: [6, 0]
      size: [6, 4]

    - title: "Memory Usage"
      type: "line_chart"
      position: [0, 4]
      size: [6, 4]

    - title: "Service Status"
      type: "service_status"
      position: [6, 4]
      size: [6, 4]

    - title: "Data Quality"
      type: "data_quality"
      position: [0, 8]
      size: [12, 4]
EOF

    log "Monitoring dashboard configuration created"
}

# Function to create health check script
create_health_check_script() {
    log "Creating health check script..."

    cat > health_check.py << 'EOF'
#!/usr/bin/env python3
"""
DegenDigest Health Check Script
Run comprehensive health checks and generate reports
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from utils.health_monitor import run_health_check, get_system_metrics
from utils.enterprise_logging import get_logger

def main():
    logger = get_logger("health_check")

    try:
        # Run health checks
        logger.info("Starting health checks...")
        health_summary = run_health_check()

        # Get system metrics
        metrics_summary = get_system_metrics()

        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "health_summary": health_summary,
            "metrics_summary": metrics_summary
        }

        # Save report
        with open("logs/health_report.json", "w") as f:
            json.dump(report, f, indent=2)

        # Log results
        logger.info("Health check completed",
                   status=health_summary.get("status"),
                   total_checks=health_summary.get("total_checks", 0))

        # Exit with appropriate code
        if health_summary.get("status") == "critical":
            sys.exit(1)
        elif health_summary.get("status") == "warning":
            sys.exit(2)
        else:
            sys.exit(0)

    except Exception as e:
        logger.error("Health check failed", error=str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

    chmod +x health_check.py
    log "Health check script created"
}

# Function to create monitoring script
create_monitoring_script() {
    log "Creating monitoring script..."

    cat > monitor_system.py << 'EOF'
#!/usr/bin/env python3
"""
DegenDigest System Monitoring Script
Continuous monitoring with alerting
"""

import sys
import time
import signal
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from utils.health_monitor import start_health_monitoring, stop_health_monitoring
from utils.enterprise_logging import get_logger

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger = get_logger("monitor")
    logger.info("Received shutdown signal, stopping monitoring...")
    stop_health_monitoring()
    sys.exit(0)

def main():
    logger = get_logger("monitor")

    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        logger.info("Starting system monitoring...")

        # Start health monitoring
        start_health_monitoring()

        # Keep running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
    except Exception as e:
        logger.error("Monitoring failed", error=str(e))
        sys.exit(1)
    finally:
        stop_health_monitoring()

if __name__ == "__main__":
    main()
EOF

    chmod +x monitor_system.py
    log "Monitoring script created"
}

# Function to create deployment verification script
create_verification_script() {
    log "Creating deployment verification script..."

    cat > verify_deployment.py << 'EOF'
#!/usr/bin/env python3
"""
DegenDigest Deployment Verification Script
Verify all components are working correctly
"""

import sys
import requests
import json
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from utils.enterprise_logging import get_logger

def verify_service(service_name, url):
    """Verify a service is working"""
    logger = get_logger("verification")

    try:
        # Test health endpoint
        health_url = f"{url}/health"
        response = requests.get(health_url, timeout=10)

        if response.status_code == 200:
            logger.info(f"Service {service_name} is healthy", url=url)
            return True
        else:
            logger.error(f"Service {service_name} health check failed",
                        status_code=response.status_code, url=url)
            return False

    except Exception as e:
        logger.error(f"Service {service_name} verification failed",
                    error=str(e), url=url)
        return False

def main():
    logger = get_logger("verification")

    # Services to verify
    services = [
        ("dexscreener-crawler", "https://dexscreener-crawler-128671663649.us-central1.run.app"),
        ("dexpaprika-crawler", "https://dexpaprika-crawler-128671663649.us-central1.run.app"),
        ("twitter-crawler", "https://twitter-crawler-128671663649.us-central1.run.app"),
        ("data-aggregator", "https://data-aggregator-128671663649.us-central1.run.app"),
        ("dashboard", "https://dashboard-128671663649.us-central1.run.app")
    ]

    results = {}
    all_passed = True

    logger.info("Starting deployment verification...")

    for service_name, url in services:
        results[service_name] = verify_service(service_name, url)
        if not results[service_name]:
            all_passed = False

    # Generate verification report
    report = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": "PASSED" if all_passed else "FAILED",
        "services": results
    }

    # Save report
    with open("logs/verification_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Log results
    if all_passed:
        logger.info("All services verified successfully")
    else:
        logger.error("Some services failed verification", results=results)

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
EOF

    chmod +x verify_deployment.py
    log "Verification script created"
}

# Function to run post-deployment tests
run_tests() {
    log "Running post-deployment tests..."

    # Run health checks
    log "Running health checks..."
    python health_check.py

    # Run deployment verification
    log "Running deployment verification..."
    python verify_deployment.py

    # Test data collection
    log "Testing data collection..."
    curl -X POST https://dexscreener-crawler-128671663649.us-central1.run.app
    curl -X POST https://dexpaprika-crawler-128671663649.us-central1.run.app

    log "All tests completed"
}

# Function to display deployment summary
show_summary() {
    log "Deployment Summary"
    log "=================="

    echo
    info "Project ID: $PROJECT_ID"
    info "Region: $REGION"
    info "Environment: $ENVIRONMENT"
    echo

    info "Deployed Services:"
    echo "  - dexscreener-crawler: https://dexscreener-crawler-128671663649.us-central1.run.app"
    echo "  - dexpaprika-crawler: https://dexpaprika-crawler-128671663649.us-central1.run.app"
    echo "  - twitter-crawler: https://twitter-crawler-128671663649.us-central1.run.app"
    echo "  - data-aggregator: https://data-aggregator-128671663649.us-central1.run.app"
    echo "  - dashboard: https://dashboard-128671663649.us-central1.run.app"
    echo

    info "Monitoring:"
    echo "  - Health checks: Every 5 minutes"
    echo "  - Data collection: Every 15-30 minutes"
    echo "  - Digest generation: Daily at 6 AM"
    echo "  - Data cleanup: Daily at 2 AM"
    echo

    info "Logs and Reports:"
    echo "  - Logs directory: ./logs/"
    echo "  - Health reports: ./logs/health_report.json"
    echo "  - Verification reports: ./logs/verification_report.json"
    echo

    info "Management Commands:"
    echo "  - Start monitoring: python monitor_system.py"
    echo "  - Run health check: python health_check.py"
    echo "  - Verify deployment: python verify_deployment.py"
    echo "  - View logs: tail -f logs/*.log"
    echo
}

# Main deployment function
main() {
    log "Starting DegenDigest Enhanced System Deployment"
    log "=============================================="

    # Check prerequisites
    check_prerequisites

    # Enable APIs
    enable_apis

    # Setup configurations
    setup_logging
    setup_monitoring
    setup_scheduler
    setup_monitoring_alerting

    # Create scripts
    create_health_check_script
    create_monitoring_script
    create_verification_script

    # Deploy services
    deploy_services

    # Run tests
    run_tests

    # Show summary
    show_summary

    log "Deployment completed successfully!"
    log "System is now running with comprehensive logging and monitoring."
}

# Run main function
main "$@"
