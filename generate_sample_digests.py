#!/usr/bin/env python3
"""Generate sample digests for testing the archive functionality"""

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

## 🎬 **Daily Degen Digest Script Template**

Here's a daily script generation template for Daily Degen Digest — designed to give you a fast, repeatable way to plug in new data each day and generate short-form video scripts that hit hard and stay on brand:

⸻

🧠 **Daily Degen Digest Script Template**

⏱ **Target Length:** ~60–90 seconds
📆 **Use:** Reusable daily for your crypto Solana video content

⸻

🎬 **Prompt Template (for AI or manual scripting):**

**Prompt:**
Write a 60–90 second script for a short-form video episode of "Daily Degen Digest", a fast-paced Solana-focused series.

The tone should be casual, sharp, and crypto-native — filled with memes, slang, and sarcasm, like a Twitter degen giving the daily rundown.

Include the following sections:

⸻

**1. Cold Open / Hook (1–2 lines):**
Grab attention fast with something wild, funny, or stats-based.

**2. Top 3 Memecoin Movers (3–4 sentences):**
For each coin, give the name, % change, market cap, and vibe.
Optional: Mention a tweet, community reaction, or rug warning.
Example format:

*"$PEEPORUG did a 45x from 3k to 140k before dumping harder than SBF's PR team. Classic."*

**3. Launch Radar (1–2 new tokens):**
Mention new launches from Pump.fun or LetsBonk.fun.
Call out launch speed, wallet count, or any signs of going viral.

**4. Solana Ecosystem Update (1 highlight):**
Cover any dev news, dapp/tool releases, partnerships, or weird events.
Keep it snappy — you're talking to degens, not VCs.

**5. Outro Call-to-Action:**
Sign off in-character with a strong closer.

*"That's your hit of hopium for today — like, follow, and stay wrecked."*

⸻

✅ **Example Inputs**
- **Top movers:**
  - $RIBBIT: +230%, 9k mcap
  - $FUDGOD: +120%, rugged at 20k
  - $JANKDOG: +80%, still climbing
- **New launches:** $LICKCOIN, $420WAGMI
- **Ecosystem news:** Phantom adds multi-wallet drag feature

⸻

*Let me know if you want a version that pulls real data from your Cabal ECA Alerts bot or Twitter scrapers — I can auto-fill this daily.*

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
    print(
        "🌐 Start your dashboard to view the Digest Archive: streamlit run dashboard/app.py"
    )


if __name__ == "__main__":
    main()
