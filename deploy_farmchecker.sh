#!/bin/bash

# FarmChecker.xyz Deployment Script
# Deploys the complete automated data pipeline

set -e

echo "🚀 Deploying to FarmChecker.xyz..."
echo "=================================="

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

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    print_error "Please run this script from the DegenDigest root directory"
    exit 1
fi

print_status "Starting FarmChecker.xyz deployment..."

# 1. Install/Update Dependencies
print_status "Installing dependencies..."
pip install -r requirements.txt
pip install python-dateutil scikit-learn pandas numpy plotly nltk textblob xgboost lightgbm

# 2. Create necessary directories
print_status "Creating output directories..."
mkdir -p output/enhanced_pipeline
mkdir -p logs
mkdir -p models

# 3. Initialize database
print_status "Initializing database..."
python recreate_db.py

# 4. Test all scrapers
print_status "Testing scrapers..."
python scrapers/reddit_rss.py
python scrapers/newsapi_headlines.py
python scrapers/coingecko_gainers.py

# 5. Test data processing
print_status "Testing data processing..."
python run_deduplication.py
python fetch_todays_digest.py
python run_intelligent_analysis.py

# 6. Test dashboard
print_status "Testing dashboard..."
python dashboard/app.py &
DASHBOARD_PID=$!
sleep 5
kill $DASHBOARD_PID 2>/dev/null || true

# 7. Create systemd service for automated pipeline
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/farmchecker-pipeline.service > /dev/null <<EOF
[Unit]
Description=FarmChecker.xyz Automated Data Pipeline
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(which python) scripts/automated_data_pipeline.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 8. Create systemd service for dashboard
print_status "Creating dashboard service..."
sudo tee /etc/systemd/system/farmchecker-dashboard.service > /dev/null <<EOF
[Unit]
Description=FarmChecker.xyz Dashboard
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(which python) dashboard/app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 9. Enable and start services
print_status "Enabling services..."
sudo systemctl daemon-reload
sudo systemctl enable farmchecker-pipeline.service
sudo systemctl enable farmchecker-dashboard.service

# 10. Create cron job for backup
print_status "Setting up backup cron job..."
(crontab -l 2>/dev/null; echo "0 2 * * * cd $(pwd) && python scripts/cloud_storage_sync.py") | crontab -

# 11. Create health check script
print_status "Creating health check script..."
cat > check_farmchecker_health.sh <<'EOF'
#!/bin/bash

# FarmChecker.xyz Health Check Script

echo "🏥 FarmChecker.xyz Health Check"
echo "================================"

# Check if services are running
echo "📊 Checking services..."
if systemctl is-active --quiet farmchecker-pipeline.service; then
    echo "✅ Pipeline service is running"
else
    echo "❌ Pipeline service is not running"
fi

if systemctl is-active --quiet farmchecker-dashboard.service; then
    echo "✅ Dashboard service is running"
else
    echo "❌ Dashboard service is not running"
fi

# Check data files
echo "📁 Checking data files..."
if [ -f "output/consolidated_data.json" ]; then
    SIZE=$(wc -c < output/consolidated_data.json)
    echo "✅ Consolidated data: ${SIZE} bytes"
else
    echo "❌ Consolidated data file missing"
fi

if [ -f "output/enhanced_pipeline/intelligent_digest.md" ]; then
    echo "✅ Intelligent digest exists"
else
    echo "❌ Intelligent digest missing"
fi

# Check database
echo "🗄️ Checking database..."
if [ -f "output/degen_digest.db" ]; then
    echo "✅ Database exists"
    # Count recent items
    RECENT_TWEETS=$(sqlite3 output/degen_digest.db "SELECT COUNT(*) FROM tweets WHERE created_at >= datetime('now', '-1 hour');" 2>/dev/null || echo "0")
    RECENT_REDDIT=$(sqlite3 output/degen_digest.db "SELECT COUNT(*) FROM reddit_posts WHERE created_at >= datetime('now', '-1 hour');" 2>/dev/null || echo "0")
    echo "📊 Recent items: ${RECENT_TWEETS} tweets, ${RECENT_REDDIT} reddit posts"
else
    echo "❌ Database missing"
fi

# Check logs
echo "📋 Recent log entries..."
tail -5 logs/degen_digest.log 2>/dev/null || echo "No log file found"

echo "================================"
EOF

chmod +x check_farmchecker_health.sh

# 12. Create monitoring script
print_status "Creating monitoring script..."
cat > monitor_farmchecker.sh <<'EOF'
#!/bin/bash

# FarmChecker.xyz Monitoring Script

while true; do
    clear
    echo "🔍 FarmChecker.xyz Live Monitor"
    echo "================================"
    echo "Last updated: $(date)"
    echo ""
    
    # Check services
    echo "📊 Services:"
    if systemctl is-active --quiet farmchecker-pipeline.service; then
        echo "✅ Pipeline: RUNNING"
    else
        echo "❌ Pipeline: STOPPED"
    fi
    
    if systemctl is-active --quiet farmchecker-dashboard.service; then
        echo "✅ Dashboard: RUNNING"
    else
        echo "❌ Dashboard: STOPPED"
    fi
    
    echo ""
    
    # Check data
    echo "📁 Data Status:"
    if [ -f "output/consolidated_data.json" ]; then
        SIZE=$(wc -c < output/consolidated_data.json)
        MOD_TIME=$(stat -c %y output/consolidated_data.json)
        echo "✅ Data file: ${SIZE} bytes (modified: ${MOD_TIME})"
    else
        echo "❌ Data file: MISSING"
    fi
    
    echo ""
    
    # Show recent activity
    echo "📋 Recent Activity:"
    tail -3 logs/degen_digest.log 2>/dev/null || echo "No recent activity"
    
    echo ""
    echo "Press Ctrl+C to exit"
    sleep 10
done
EOF

chmod +x monitor_farmchecker.sh

# 13. Start services
print_status "Starting services..."
sudo systemctl start farmchecker-pipeline.service
sudo systemctl start farmchecker-dashboard.service

# 14. Final status check
print_status "Performing final status check..."
sleep 5

if systemctl is-active --quiet farmchecker-pipeline.service; then
    print_success "Pipeline service started successfully"
else
    print_error "Pipeline service failed to start"
fi

if systemctl is-active --quiet farmchecker-dashboard.service; then
    print_success "Dashboard service started successfully"
else
    print_error "Dashboard service failed to start"
fi

# 15. Display final information
echo ""
echo "🎉 FarmChecker.xyz Deployment Complete!"
echo "========================================"
echo ""
echo "📋 Services:"
echo "   • Pipeline: systemctl status farmchecker-pipeline.service"
echo "   • Dashboard: systemctl status farmchecker-dashboard.service"
echo ""
echo "🔧 Management Commands:"
echo "   • Start pipeline: sudo systemctl start farmchecker-pipeline.service"
echo "   • Stop pipeline: sudo systemctl stop farmchecker-pipeline.service"
echo "   • View logs: sudo journalctl -u farmchecker-pipeline.service -f"
echo "   • Health check: ./check_farmchecker_health.sh"
echo "   • Live monitor: ./monitor_farmchecker.sh"
echo ""
echo "📊 Data Collection Schedule:"
echo "   • Twitter: Every 3 hours"
echo "   • Reddit/News/Coingecko: Every 30 minutes"
echo "   • Data processing: After each scrape run"
echo ""
echo "🌐 Dashboard should be available at: http://localhost:8501"
echo ""

print_success "Deployment completed successfully!" 