#!/bin/bash

# Degen Digest - Fix All Issues Script
# This script fixes all identified issues in the system

set -e

echo "🚀 Degen Digest - Fix All Issues"
echo "================================="
echo "⏰ Started at: $(date)"
echo ""

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

# Step 1: Check Python environment
print_status "Checking Python environment..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    print_success "Using python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    print_success "Using python"
else
    print_error "Python not found. Please install Python 3.7+"
    exit 1
fi

# Step 2: Check if we're in the right directory
if [ ! -f "main.py" ]; then
    print_error "Please run this script from the DegenDigest root directory"
    exit 1
fi

print_success "Running from correct directory"

# Step 3: Install dependencies
print_status "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    $PYTHON_CMD -m pip install -r requirements.txt
    print_success "Dependencies installed"
else
    print_warning "requirements.txt not found, skipping dependency installation"
fi

# Step 4: Test LLM functionality
print_status "Testing LLM functionality..."
if [ -f "test_digest_generation.py" ]; then
    if $PYTHON_CMD test_digest_generation.py; then
        print_success "LLM functionality test passed"
    else
        print_warning "LLM functionality test failed, but continuing..."
    fi
else
    print_warning "test_digest_generation.py not found, skipping LLM test"
fi

# Step 5: Trigger cloud function for fresh data
print_status "Triggering cloud function for fresh data..."
CLOUD_FUNCTION_URL="https://us-central1-lucky-union-463615-t3.cloudfunctions.net/refresh_data"

if command -v curl &> /dev/null; then
    print_status "Calling cloud function..."
    RESPONSE=$(curl -s -X POST "$CLOUD_FUNCTION_URL" \
        -H "Content-Type: application/json" \
        -d '{"generate_digest": true, "force_refresh": true}' \
        --max-time 300)

    if [ $? -eq 0 ]; then
        print_success "Cloud function called successfully"
        echo "Response: $RESPONSE" | head -c 200
        echo "..."
    else
        print_warning "Cloud function call failed, trying manual data refresh..."
    fi
else
    print_warning "curl not found, skipping cloud function call"
fi

# Step 6: Try manual data refresh
print_status "Attempting manual data refresh..."
if [ -f "manual_data_refresh.py" ]; then
    if $PYTHON_CMD manual_data_refresh.py; then
        print_success "Manual data refresh completed"
    else
        print_warning "Manual data refresh failed, trying local scrapers..."
    fi
else
    print_warning "manual_data_refresh.py not found"
fi

# Step 7: Run local scrapers
print_status "Running local scrapers..."
SCRAPERS=("scrapers/reddit_rss.py" "scrapers/newsapi_headlines.py" "scrapers/coingecko_gainers.py")

for scraper in "${SCRAPERS[@]}"; do
    if [ -f "$scraper" ]; then
        print_status "Running $scraper..."
        if $PYTHON_CMD "$scraper"; then
            print_success "$scraper completed"
        else
            print_warning "$scraper failed"
        fi
    else
        print_warning "$scraper not found"
    fi
done

# Step 8: Generate digest
print_status "Generating digest..."
if [ -f "main.py" ]; then
    if $PYTHON_CMD main.py; then
        print_success "Digest generation completed"
    else
        print_warning "Digest generation failed, trying alternative method..."
        if [ -f "generate_digest.py" ]; then
            $PYTHON_CMD generate_digest.py
        fi
    fi
else
    print_error "main.py not found"
fi

# Step 9: Run data processing
print_status "Running data processing..."
if [ -f "run_deduplication.py" ]; then
    if $PYTHON_CMD run_deduplication.py; then
        print_success "Data deduplication completed"
    else
        print_warning "Data deduplication failed"
    fi
fi

if [ -f "run_enhanced_system.py" ]; then
    if $PYTHON_CMD run_enhanced_system.py; then
        print_success "Enhanced system processing completed"
    else
        print_warning "Enhanced system processing failed"
    fi
fi

# Step 10: Check results
print_status "Checking results..."

# Check database
if [ -f "output/degen_digest.db" ]; then
    if command -v sqlite3 &> /dev/null; then
        TWEET_COUNT=$(sqlite3 output/degen_digest.db "SELECT COUNT(*) FROM tweet;" 2>/dev/null || echo "0")
        REDDIT_COUNT=$(sqlite3 output/degen_digest.db "SELECT COUNT(*) FROM redditpost;" 2>/dev/null || echo "0")
        DIGEST_COUNT=$(sqlite3 output/degen_digest.db "SELECT COUNT(*) FROM digest;" 2>/dev/null || echo "0")

        print_status "Database contents:"
        echo "  - Tweets: $TWEET_COUNT"
        echo "  - Reddit posts: $REDDIT_COUNT"
        echo "  - Digests: $DIGEST_COUNT"
    else
        print_warning "sqlite3 not found, cannot check database"
    fi
else
    print_warning "Database not found"
fi

# Check digest files
DIGEST_FILES=$(ls output/digest*.md 2>/dev/null | wc -l)
if [ "$DIGEST_FILES" -gt 0 ]; then
    print_success "Found $DIGEST_FILES digest files"
    ls -la output/digest*.md
else
    print_warning "No digest files found"
fi

# Check raw data files
RAW_FILES=$(ls output/*_raw.json 2>/dev/null | wc -l)
if [ "$RAW_FILES" -gt 0 ]; then
    print_success "Found $RAW_FILES raw data files"
    ls -la output/*_raw.json
else
    print_warning "No raw data files found"
fi

# Step 11: Final status
echo ""
echo "🎉 Fix All Issues Script Completed!"
echo "==================================="
echo "⏰ Finished at: $(date)"
echo ""
echo "📊 Next Steps:"
echo "1. Check the dashboard at https://farmchecker.xyz"
echo "2. Verify data is showing in all pages"
echo "3. Download the latest digest"
echo ""
echo "🔍 If issues persist:"
echo "1. Check logs in logs/degen_digest.log"
echo "2. Verify environment variables are set"
echo "3. Check network connectivity"
echo "4. Run individual scripts manually"
echo ""
echo "📋 Manual verification commands:"
echo "  sqlite3 output/degen_digest.db \"SELECT COUNT(*) FROM tweet;\""
echo "  ls -la output/digest*.md"
echo "  curl -s https://farmchecker.xyz | head -20"
