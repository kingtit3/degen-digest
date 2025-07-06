# 🎯 Enhanced Viral Content System Guide

## Overview

Your DegenDigest system has been enhanced to focus specifically on **viral content collection** for short-form video creation. This system now captures and analyzes data from all sources with a laser focus on:

- 🔥 **Memecoins & Viral Tokens**
- 🚀 **Launchpads & IDOs**
- 🎁 **Airdrops & Free Tokens**
- 🌾 **Farming & Yield Opportunities**
- ⚡ **Solana Ecosystem**
- 📈 **Price Momentum & Trending**

## 🚀 Quick Deployment

### 1. Set Environment Variables

```bash
export NEWSAPI_KEY="your_newsapi_key_here"
export PROJECT_ID="lucky-union-463615-t3"
export BUCKET_NAME="degen-digest-data"
```

### 2. Deploy the Enhanced System

```bash
# Make script executable
chmod +x deploy_enhanced_viral_system.sh

# Run deployment
./deploy_enhanced_viral_system.sh
```

### 3. Verify Deployment

```bash
# Check system health
python monitor_viral_system.py

# Run viral content consolidation
python scripts/enhanced_viral_consolidator.py
```

## 📊 Enhanced Data Sources

### 🔴 Enhanced Reddit Crawler

**Focus:** Memecoin communities, launchpads, airdrops, farming

- **Subreddits:** 20+ targeted subreddits
- **Categories:** memecoin, launchpad, airdrop, farming, solana, trading, general
- **Schedule:** Every 30 minutes (6 AM - 12 AM)
- **Expected Data:** 300+ posts per day

**Key Subreddits:**

- `CryptoMoonShots` - Memecoin opportunities
- `launchpad`, `IDO`, `presale` - Launchpad content
- `airdrop`, `CryptoAirdrops` - Airdrop opportunities
- `defi`, `yieldfarming` - Farming opportunities
- `Solana`, `SolanaNFTs`, `SolanaDeFi` - Solana ecosystem

### 📰 Enhanced News Crawler

**Focus:** Breaking crypto news, announcements, partnerships

- **Queries:** 20+ targeted search queries
- **Categories:** memecoin, launchpad, airdrop, farming, solana, general
- **Schedule:** Every 45 minutes (6 AM - 12 AM)
- **Expected Data:** 200+ articles per day

**Key Search Queries:**

- Memecoin trends: `memecoin OR pepe OR doge OR bonk OR dogwifhat`
- Launchpads: `launchpad OR ido OR presale OR fair launch`
- Airdrops: `airdrop OR free tokens OR claim OR eligibility`
- Farming: `yield farming OR liquidity mining OR staking`
- Solana: `solana OR sol OR phantom OR raydium OR jupiter`

### 📈 Enhanced CoinGecko Crawler

**Focus:** Trending coins, price momentum, new launches

- **Endpoints:** 8 comprehensive endpoints
- **Categories:** trending, memecoin, farming, gaming, exchange, solana, launchpad, gainers
- **Schedule:** Every 20 minutes (6 AM - 12 AM)
- **Expected Data:** 400+ coins per day

**Key Endpoints:**

- `/search/trending` - Most viral coins
- `/coins/markets?category=meme-token` - Memecoins
- `/coins/markets?category=decentralized-finance-defi` - Farming opportunities
- `/coins/markets?order=created_desc` - New launches
- Solana ecosystem specific coins

### 🔍 DexScreener & DexPaprika Crawlers

**Focus:** DEX trending tokens, Solana ecosystem

- **Schedule:** Every 15 minutes (6 AM - 12 AM)
- **Expected Data:** 150+ tokens per day

## 🎯 Viral Content Analysis

### Viral Scoring System

Each piece of content is scored based on:

1. **Keyword Detection** (Base Score)

   - Memecoin keywords: +10 points
   - Launchpad keywords: +8 points
   - Airdrop keywords: +7 points
   - Farming keywords: +6 points
   - Solana keywords: +5 points
   - Urgency keywords: +4 points
   - Viral keywords: +3 points

2. **Source-Specific Scoring**

   - **Twitter:** Engagement metrics, user influence
   - **Reddit:** Upvotes, comments, viral potential
   - **News:** Source credibility, viral potential
   - **CoinGecko:** Price momentum, market cap ranking
   - **DEX:** Price changes, liquidity

3. **Time Decay**
   - < 1 hour: +5 points
   - < 6 hours: +3 points
   - < 24 hours: +1 point

### Viral Score Ranges

- **Explosive:** 50+ points (immediate content creation)
- **High:** 20-49 points (high priority)
- **Medium:** 10-19 points (good potential)
- **Low:** 5-9 points (monitor)

## 📋 Viral Content Categories

### 🔥 Memecoin Content

- Trending memecoins (Pepe, Doge, Bonk, etc.)
- Viral token launches
- Community sentiment and engagement
- Price pumps and mooning content

### 🚀 Launchpad Content

- New token launches and IDOs
- Presale opportunities
- Fair launches and stealth launches
- Whitelist and KYC requirements

### 🎁 Airdrop Content

- Free token distributions
- Eligibility requirements
- Snapshot dates
- Claim deadlines

### 🌾 Farming Content

- Yield farming opportunities
- Liquidity mining rewards
- Staking APY/APR
- Auto-compound strategies

### ⚡ Solana Content

- Solana ecosystem updates
- New Solana projects
- Phantom wallet features
- Solana DeFi opportunities

## 🛠️ System Components

### 1. Enhanced Cloud Tasks

- `cloud_tasks_reddit.py` - Enhanced Reddit crawler
- `cloud_tasks_news.py` - Enhanced News crawler
- `cloud_tasks_coingecko.py` - Enhanced CoinGecko crawler
- `cloud_tasks_dexscreener.py` - DexScreener crawler
- `cloud_tasks_dexpaprika.py` - DexPaprika crawler

### 2. Viral Content Consolidator

- `scripts/enhanced_viral_consolidator.py` - Main consolidation script
- Processes all data sources
- Calculates viral scores
- Generates actionable recommendations

### 3. System Monitor

- `monitor_viral_system.py` - Health monitoring
- Tracks all components
- Provides real-time insights

### 4. Deployment Script

- `deploy_enhanced_viral_system.sh` - Complete deployment
- Sets up Cloud Functions
- Configures Cloud Scheduler
- Tests all components

## 📈 Expected Daily Data Collection

| Source          | Items/Day | Focus Areas                      |
| --------------- | --------- | -------------------------------- |
| **Reddit**      | 300+      | Memecoins, Launchpads, Airdrops  |
| **News**        | 200+      | Breaking news, Announcements     |
| **CoinGecko**   | 400+      | Trending coins, Price momentum   |
| **DexScreener** | 100+      | DEX trending tokens              |
| **DexPaprika**  | 50+       | Solana ecosystem                 |
| **Twitter**     | 200+      | Real-time viral content          |
| **Total**       | **1250+** | **Comprehensive viral coverage** |

## 🎯 Content Creation Recommendations

### High-Priority Content (Score 50+)

- **Immediate action required**
- Create short-form videos within 1-2 hours
- Focus on urgency and FOMO
- Use trending hashtags and viral language

### Medium-Priority Content (Score 20-49)

- **Create within 4-6 hours**
- Focus on educational value
- Include analysis and context
- Build community engagement

### Monitoring Content (Score 10-19)

- **Track for 24 hours**
- Look for momentum building
- Prepare content templates
- Monitor for score increases

## 🔧 Monitoring & Maintenance

### Daily Monitoring

```bash
# Check system health
python monitor_viral_system.py

# Run viral consolidation
python scripts/enhanced_viral_consolidator.py

# Check GCS for latest data
gsutil ls gs://degen-digest-data/data/
gsutil ls gs://degen-digest-data/viral_reports/
```

### Weekly Maintenance

- Review viral content performance
- Adjust keyword lists based on trends
- Update subreddit and query lists
- Monitor system costs and performance

### Monthly Optimization

- Analyze viral content patterns
- Update scoring algorithms
- Add new data sources
- Optimize scheduling

## 📊 Data Storage Structure

```
gs://degen-digest-data/
├── data/
│   ├── twitter_latest.json
│   ├── reddit_latest.json
│   ├── news_latest.json
│   ├── coingecko_latest.json
│   ├── dexscreener_latest.json
│   └── dexpaprika_latest.json
├── viral_reports/
│   ├── viral_content_latest.json
│   └── viral_content_YYYYMMDD_HHMMSS.json
└── backups/
    └── [timestamped backups]
```

## 🚨 Troubleshooting

### Common Issues

1. **Cloud Functions Not Responding**

   ```bash
   # Check function status
   gcloud functions describe enhanced-reddit-crawler --region=us-central1

   # View logs
   gcloud functions logs read enhanced-reddit-crawler --region=us-central1
   ```

2. **Scheduler Jobs Failing**

   ```bash
   # Check job status
   gcloud scheduler jobs describe reddit-viral-crawler --location=us-central1

   # View job history
   gcloud scheduler jobs list --location=us-central1
   ```

3. **Data Not Updating**

   ```bash
   # Check GCS files
   gsutil ls -l gs://degen-digest-data/data/

   # Check file timestamps
   gsutil ls -la gs://degen-digest-data/data/reddit_latest.json
   ```

### Performance Optimization

1. **Increase Memory/Timeout**

   ```bash
   gcloud functions deploy enhanced-reddit-crawler \
     --memory 1024MB \
     --timeout 540s
   ```

2. **Adjust Scheduling**
   ```bash
   # More frequent updates during peak hours
   gcloud scheduler jobs update reddit-viral-crawler \
     --schedule="*/15 6-23 * * *"
   ```

## 🎉 Success Metrics

### Viral Content Success Indicators

- **Explosive content (50+ score):** 10+ items per day
- **High viral content (20-49 score):** 50+ items per day
- **Total viral items:** 100+ items per day
- **Category coverage:** All 6 categories represented

### System Health Targets

- **Overall health:** >90%
- **Data freshness:** <2 hours old
- **Function uptime:** >99%
- **Scheduler reliability:** >99%

## 🔮 Future Enhancements

### Planned Features

1. **AI-powered content analysis**
2. **Automated video script generation**
3. **Social media trend prediction**
4. **Cross-platform viral tracking**
5. **Real-time alert system**

### Integration Opportunities

1. **TikTok API integration**
2. **YouTube Shorts optimization**
3. **Instagram Reels tracking**
4. **Discord bot integration**
5. **Telegram channel monitoring**

---

## 🚀 Ready to Deploy?

Your enhanced viral content system is designed to capture **every viral opportunity** in the crypto space. With 1250+ data points per day and intelligent viral scoring, you'll never miss the next big trend.

**Deploy now and start creating viral short-form content!** 🎯
