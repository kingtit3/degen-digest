#!/bin/bash

# Setup script for Playwright Twitter Crawler
echo "🚀 Setting up Playwright Twitter Crawler..."
echo "=========================================="

# Install Playwright Python package
echo "📦 Installing Playwright Python package..."
pip install playwright

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# Verify installation
echo "✅ Verifying installation..."
python -c "from playwright.async_api import async_playwright; print('Playwright installed successfully!')"

echo ""
echo "🎉 Playwright setup complete!"
echo ""
echo "📋 Usage:"
echo "   Test crawler: python test_playwright_crawler.py"
echo "   Single crawl: python scripts/playwright_pipeline.py --mode single"
echo "   Continuous:   python scripts/playwright_pipeline.py --mode continuous --interval 10"
echo ""
echo "⚠️  Note: Make sure to respect Twitter's terms of service and rate limits!"
