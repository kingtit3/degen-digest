#!/usr/bin/env python3
"""Generate sample digests for testing the archive functionality"""

import os
from datetime import datetime, timedelta
from pathlib import Path

def create_sample_digest(date, title, content):
    """Create a sample digest file"""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    filename = f"digest-{date.strftime('%Y-%m-%d')}.md"
    filepath = output_dir / filename
    
    digest_content = f"""# 🚀 Degen Digest - Crypto Market Intelligence

**Date:** {date.strftime('%B %d, %Y')} | **Edition:** Daily Market Report

---

## 📋 Executive Summary

{title}

{content}

---

## 🎯 Key Takeaways

**💀 Rug of the Day:** Sample rug alert for {date.strftime('%Y-%m-%d')}
**🚀 Meme Launch:** Sample meme launch
**🔥 Top CT Story:** Sample crypto Twitter story
**💬 Quote of the Day:** Sample quote
**🐳 Whale Move:** Sample whale activity
**🧠 Alpha Thread:** Sample alpha thread
**Market Sentiment:** Sample sentiment

---

## 📊 Market Overview

### 📈 Data Insights
- **Total Stories Analyzed:** 1,000
- **Top Engagement Score:** 95.0
- **Average Engagement:** 25.2
- **Data Sources:** twitter: 950, telegram: 50

### 🎯 Market Themes
Based on our analysis of today's top crypto content, the market is showing:
- **High Activity Areas:** Sample activity areas
- **Trending Topics:** Sample trending topics
- **Engagement Patterns:** Sample engagement patterns

---

## 🔥 Top Stories of the Day

### 🔥 Market Movers

**1. Sample Market Mover Story**

Sample content for market mover story.

*Metrics: ❤️ 300 | 🔄 15 | 💬 5 | 👁️ 5,000 | 📊 Score: 95.0*

---

## 📊 Market Analysis

### 💡 Market Insights

Based on today's analysis:

• Sample market insight for {date.strftime('%Y-%m-%d')}

---

## 📋 Report Information

**Generated:** {date.strftime('%Y-%m-%d %H:%M:%S')} UTC

**Data Sources:** Twitter, Reddit, Telegram, NewsAPI, CoinGecko

**Analysis Method:** AI-powered content analysis with engagement scoring

---

*This report is generated automatically and should not be considered as financial advice. Always do your own research.*

🚀 **Degen Digest** - Your daily crypto intelligence companion
"""
    
    filepath.write_text(digest_content)
    print(f"✅ Created sample digest: {filename}")

def main():
    """Generate sample digests for the last 7 days"""
    print("🚀 Generating sample digests...")
    
    # Create sample digests for the last 7 days
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        title = f"Sample Executive Summary for {date.strftime('%B %d, %Y')}"
        content = f"This is a sample executive summary for {date.strftime('%B %d, %Y')}. It contains sample market analysis and insights for testing the digest archive functionality."
        
        create_sample_digest(date, title, content)
    
    print("🎉 Sample digests generated successfully!")
    print("📁 Check the 'output' directory for the generated files.")
    print("🌐 Start your dashboard to view the Digest Archive: streamlit run dashboard/app.py")

if __name__ == "__main__":
    main() 