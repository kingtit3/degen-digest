#!/usr/bin/env python3
"""Create a simple test digest file"""

from pathlib import Path
from datetime import datetime

def create_test_digest():
    """Create a test digest file"""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Create a test digest for today
    today = datetime.now()
    filename = f"digest-{today.strftime('%Y-%m-%d')}.md"
    filepath = output_dir / filename
    
    test_content = f"""# 🚀 Degen Digest - Crypto Market Intelligence

**Date:** {today.strftime('%B %d, %Y')} | **Edition:** Daily Market Report

---

## 📋 Executive Summary

This is a test digest for {today.strftime('%B %d, %Y')}. The digest archive functionality is working correctly!

---

## 🎯 Key Takeaways

**💀 Rug of the Day:** Test rug alert
**🚀 Meme Launch:** Test meme launch
**🔥 Top CT Story:** Test crypto Twitter story
**💬 Quote of the Day:** Test quote
**🐳 Whale Move:** Test whale activity
**🧠 Alpha Thread:** Test alpha thread
**Market Sentiment:** Test sentiment

---

## 📊 Market Overview

### 📈 Data Insights
- **Total Stories Analyzed:** 1,000
- **Top Engagement Score:** 95.0
- **Average Engagement:** 25.2
- **Data Sources:** twitter: 950, telegram: 50

---

## 📋 Report Information

**Generated:** {today.strftime('%Y-%m-%d %H:%M:%S')} UTC

**Data Sources:** Twitter, Reddit, Telegram, NewsAPI, CoinGecko

**Analysis Method:** AI-powered content analysis with engagement scoring

---

*This report is generated automatically and should not be considered as financial advice. Always do your own research.*

🚀 **Degen Digest** - Your daily crypto intelligence companion
"""
    
    filepath.write_text(test_content)
    print(f"✅ Created test digest: {filename}")
    print(f"📁 File location: {filepath.absolute()}")

if __name__ == "__main__":
    create_test_digest() 