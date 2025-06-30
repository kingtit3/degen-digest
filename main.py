"""Entry point that orchestrates scraping outputs → digest.

Adds a `run_id` (UUID) bound to the structured‐logging context so every log
event coming from this process can be correlated end-to-end.
"""

import json
import logging
import uuid
import os

from pathlib import Path
import re
from typing import List, Dict

from processor.scorer import degen_score
from processor.classifier import classify
from processor.summarizer import rewrite_content, rewrite_batch
from enrich.token_price import get_prices_sync
from processor.viral_predictor import predictor
from processor.content_clustering import clusterer

from utils.logger import setup_logging
from utils.advanced_logging import get_logger

setup_logging()

# ---------------------------------------------------------------------------
# Correlate this run via UUID (when structlog is available).  Import guarded so
# the script still runs in environments that lack structlog.
# ---------------------------------------------------------------------------

run_id = str(uuid.uuid4())

try:
    import structlog.contextvars as ctx  # type: ignore

    ctx.bind_contextvars(run_id=run_id)
except (ModuleNotFoundError, AttributeError):
    # Structlog missing or older version – skip context binding.
    pass

logger = get_logger(__name__)

from utils.advanced_logging import _STRUCTLOG_AVAILABLE  # type: ignore

if _STRUCTLOG_AVAILABLE:
    logger.info("digest run start", run_id=run_id)
else:
    logger.info(f"digest run start run_id={run_id}")

OUTPUT_DIR = Path("output")
DIGEST_MD = OUTPUT_DIR / "digest.md"
SEEN_IDS_FILE = OUTPUT_DIR / "seen_tweet_ids.json"

# New human-friendly template
TEMPLATE_HEADER = """# 🚀 Degen Digest - Crypto Market Intelligence

**Date:** {date} | **Edition:** Daily Market Report

---

## 📋 Executive Summary

{executive_summary}

---

## 🎯 Key Takeaways

{key_takeaways}

---

## 📊 Market Overview

{market_overview}

---

"""

def load_raw_sources():
    sources = {}
    for filename in ["twitter_raw.json", "reddit_raw.json", "telegram_raw.json", "newsapi_raw.json", "coingecko_raw.json"]:
        path = OUTPUT_DIR / filename
        if path.exists():
            data = json.loads(path.read_text())
            prefix = filename.split("_", 1)[0]
            for d in data:
                if isinstance(d, dict):
                    d["_source"] = prefix
            sources[filename] = data
        else:
            sources[filename] = []
    return sources


def load_seen_ids():
    if SEEN_IDS_FILE.exists():
        try:
            return set(json.loads(SEEN_IDS_FILE.read_text()))
        except Exception:
            return set()
    return set()


def save_seen_ids(ids: set):
    SEEN_IDS_FILE.write_text(json.dumps(sorted(ids)))


def process_items(items: List[Dict]) -> List[Dict]:
    """Process and score items with enhanced ML features"""
    processed = []
    
    for item in items:
        if not isinstance(item, dict):
            continue
            
        # Apply existing scoring
        item["_engagement_score"] = degen_score(item)
        
        # Add viral prediction
        item["_predicted_viral_score"] = predictor.predict_viral_score(item)
        
        processed.append(item)
    
    # Sort by engagement score
    processed.sort(key=lambda x: x.get("_engagement_score", 0), reverse=True)
    
    # Run content clustering on top items
    if len(processed) > 10:
        top_items = processed[:100]  # Cluster top 100 items
        try:
            clusters = clusterer.cluster_content(top_items)
            topics = clusterer.extract_topics(top_items)
            logger.info(f"Content clustering complete: {len(clusters)} clusters, {len(topics)} topics")
        except Exception as e:
            logger.warning(f"Content clustering failed: {e}")
    
    return processed


def create_executive_summary(chosen_items: List[Dict]) -> str:
    """Create a human-friendly executive summary"""
    try:
        from processor.summarizer import client as _llm_client

        # Create a structured summary prompt
        stories = []
        for i, item in enumerate(chosen_items[:5], 1):  # Top 5 stories
            headline = item.get('headline', 'Unknown story')
            stories.append(f"{i}. {headline}")
        
        prompt = f"""
        Create a professional, concise executive summary (150-200 words) for a crypto market intelligence report.
        
        Focus on:
        - Main market trends and themes
        - Key developments and their potential impact
        - Notable price movements or market shifts
        - Emerging opportunities or risks
        
        Use clear, professional language that a financial analyst would understand.
        Avoid jargon and make it accessible to both crypto veterans and newcomers.
        
        Top stories to summarize:
        {chr(10).join(stories)}
        
        Format the summary with clear paragraphs and bullet points where appropriate.
        """
        
        _resp = _llm_client.chat.completions.create(
            model=os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300,
        )
        return _resp.choices[0].message.content.strip()
    except Exception as exc:
        logger.warning("Executive summary generation failed: %s", exc)
        return "Market analysis unavailable due to technical issues."


def create_key_takeaways(chosen_items: List[Dict]) -> str:
    """Create key takeaways from the top stories"""
    takeaways = []
    
    # Extract key themes and insights
    themes = {}
    for item in chosen_items[:8]:  # Top 8 items
        tag = item.get('tag', 'General')
        if tag not in themes:
            themes[tag] = []
        themes[tag].append(item.get('headline', ''))
    
    # Create structured takeaways
    for theme, headlines in themes.items():
        if headlines:
            takeaways.append(f"**{theme}:** {headlines[0]}")
    
    # Add market sentiment
    sentiment = "bullish" if len([i for i in chosen_items if "bull" in i.get('headline', '').lower()]) > len([i for i in chosen_items if "bear" in i.get('headline', '').lower()]) else "bearish"
    takeaways.append(f"**Market Sentiment:** Overall {sentiment} with mixed signals")
    
    return "\n".join(takeaways)


def create_market_overview(processed_items: List[Dict]) -> str:
    """Create a comprehensive market overview section"""
    total_stories = len(processed_items)
    top_engagement = max([item.get("_engagement_score", 0) for item in processed_items]) if processed_items else 0
    avg_engagement = sum([item.get("_engagement_score", 0) for item in processed_items]) / len(processed_items) if processed_items else 0
    
    # Get source breakdown
    sources = {}
    for item in processed_items:
        source = item.get('_source', 'unknown')
        sources[source] = sources.get(source, 0) + 1
    
    source_breakdown = ", ".join([f"{source}: {count}" for source, count in sources.items()])
    
    return f"""
### 📈 Data Insights
- **Total Stories Analyzed:** {total_stories:,}
- **Top Engagement Score:** {top_engagement:.1f}
- **Average Engagement:** {avg_engagement:.1f}
- **Data Sources:** {source_breakdown}

### 🎯 Market Themes
Based on our analysis of today's top crypto content, the market is showing:
- **High Activity Areas:** {', '.join([item.get('tag', 'General') for item in processed_items[:3]])}
- **Trending Topics:** {', '.join([item.get('headline', '')[:30] for item in processed_items[:2]])}
- **Engagement Patterns:** {f"Peak engagement around {processed_items[0].get('tag', 'General') if processed_items else 'N/A'}"}
"""


def build_digest(processed_items):
    # Select top 12 by score but only one per tag where possible
    processed_items.sort(key=lambda x: x["_engagement_score"], reverse=True)

    tag_order = [
        "🔥 Top CT Story",
        "💀 Rug of the Day", 
        "🚀 Meme Launch",
        "🐳 Whale Move",
        "🧠 Alpha Thread",
        "💬 Quote of the Day",
    ]

    chosen = []
    used_tags = set()
    for item in processed_items:
        if item["tag"] not in used_tags:
            chosen.append(item)
            used_tags.add(item["tag"])
        if len(chosen) >= 12:  # Increased from 10 to 12
            break

    from datetime import date

    # Create executive summary
    executive_summary = create_executive_summary(chosen)
    
    # Create key takeaways
    key_takeaways = create_key_takeaways(chosen)
    
    # Create market overview
    market_overview = create_market_overview(processed_items)

    # Build the main digest content
    md = TEMPLATE_HEADER.format(
        date=date.today().strftime("%B %d, %Y"),
        executive_summary=executive_summary,
        key_takeaways=key_takeaways,
        market_overview=market_overview
    )

    # Top Stories section with improved organization
    md += "## 🔥 Top Stories of the Day\n\n"
    
    # Group stories by category for better organization
    story_categories = {
        "🔥 Market Movers": [],
        "🚀 New Launches": [],
        "🐳 Whale Activity": [],
        "🧠 Alpha & Insights": [],
        "💬 Community Highlights": []
    }
    
    for item in chosen:
        tag = item.get('tag', 'General')
        if 'Top CT Story' in tag or 'Rug' in tag:
            story_categories["🔥 Market Movers"].append(item)
        elif 'Meme Launch' in tag:
            story_categories["🚀 New Launches"].append(item)
        elif 'Whale Move' in tag:
            story_categories["🐳 Whale Activity"].append(item)
        elif 'Alpha Thread' in tag:
            story_categories["🧠 Alpha & Insights"].append(item)
        else:
            story_categories["💬 Community Highlights"].append(item)
    
    # Display stories by category
    for category, stories in story_categories.items():
        if stories:
            md += f"### {category}\n\n"
            for idx, item in enumerate(stories, 1):
                md += f"**{idx}. {item['headline']}**\n\n"
                md += f"{item['body']}\n\n"
                
                # Add engagement metrics in a clean format
                engagement_info = []
                if item.get('likeCount'):
                    engagement_info.append(f"❤️ {item['likeCount']:,}")
                if item.get('retweetCount'):
                    engagement_info.append(f"🔄 {item['retweetCount']:,}")
                if item.get('replyCount'):
                    engagement_info.append(f"💬 {item['replyCount']:,}")
                if item.get('viewCount'):
                    engagement_info.append(f"👁️ {item['viewCount']:,}")
                if item.get('_engagement_score'):
                    engagement_info.append(f"📊 Score: {item['_engagement_score']:.1f}")
                
                if engagement_info:
                    md += f"*Metrics: {' | '.join(engagement_info)}*\n\n"
                
                md += "---\n\n"
    
    # Add market analysis section
    md += "## 📊 Market Analysis\n\n"
    
    # Price movements (if available)
    try:
        prices = get_prices_sync()
        if prices:
            md += "### 💰 Key Price Movements\n\n"
            for symbol, data in list(prices.items())[:5]:  # Top 5
                change_24h = data.get('price_change_percentage_24h', 0)
                emoji = "🟢" if change_24h > 0 else "🔴" if change_24h < 0 else "⚪"
                md += f"{emoji} **{symbol.upper()}:** ${data.get('current_price', 0):,.2f} ({change_24h:+.2f}%)\n\n"
    except Exception as e:
        logger.warning(f"Price data unavailable: {e}")
        md += "*Price data temporarily unavailable*\n\n"
    
    # Add insights section
    md += "### 💡 Market Insights\n\n"
    md += "Based on today's analysis:\n\n"
    
    insights = []
    if len([i for i in chosen if 'bull' in i.get('headline', '').lower()]) > len([i for i in chosen if 'bear' in i.get('headline', '').lower())]):
        insights.append("• Market sentiment appears bullish with positive momentum")
    else:
        insights.append("• Market sentiment shows caution with mixed signals")
    
    if any('whale' in i.get('headline', '').lower() for i in chosen):
        insights.append("• Significant whale activity detected, indicating institutional interest")
    
    if any('launch' in i.get('headline', '').lower() for i in chosen):
        insights.append("• New project launches and token releases creating market opportunities")
    
    if not insights:
        insights.append("• Market showing normal volatility with standard trading patterns")
    
    md += "\n".join(insights) + "\n\n"
    
    # Add footer
    md += "---\n\n"
    md += "## 📋 Report Information\n\n"
    md += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
    md += "**Data Sources:** Twitter, Reddit, Telegram, NewsAPI, CoinGecko\n\n"
    md += "**Analysis Method:** AI-powered content analysis with engagement scoring\n\n"
    md += "---\n\n"
    md += "*This report is generated automatically and should not be considered as financial advice. Always do your own research.*\n\n"
    md += "🚀 **Degen Digest** - Your daily crypto intelligence companion"

    return md


def main():
    """Main orchestration function."""
    logger.info("Starting digest generation")

    # Load raw data
    sources = load_raw_sources()
    all_items = []
    for source_name, items in sources.items():
        all_items.extend(items)

    logger.info(f"Processing {len(all_items)} items from raw sources")

    # Load seen IDs for deduplication
    seen_ids = load_seen_ids()

    # Filter out already processed items
    new_items = []
    for item in all_items:
        item_id = item.get("id") or item.get("tweetId") or item.get("_id")
        if item_id and str(item_id) not in seen_ids:
            new_items.append(item)

    logger.info(f"Found {len(new_items)} new items to process")

    if not new_items:
        logger.info("No new items to process")
        return

    # Process items
    processed_items = process_items(new_items)

    # Classify and rewrite content
    for item in processed_items:
        # Classify
        item["tag"] = classify(item)
        
        # Rewrite content
        rewritten = rewrite_content(item)
        item["headline"] = rewritten["headline"]
        item["body"] = rewritten["body"]

    # Build digest
    digest_content = build_digest(processed_items)

    # Save digest
    DIGEST_MD.write_text(digest_content)
    logger.info(f"Digest saved to {DIGEST_MD}")

    # Update seen IDs
    new_seen_ids = set()
    for item in processed_items:
        item_id = item.get("id") or item.get("tweetId") or item.get("_id")
        if item_id:
            new_seen_ids.add(str(item_id))
    
    seen_ids.update(new_seen_ids)
    save_seen_ids(seen_ids)

    # Generate PDF
    try:
        from utils.pdf import generate_pdf
        pdf_path = generate_pdf(digest_content, f"digest-{date.today().isoformat()}")
        logger.info(f"PDF generated: {pdf_path}")
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")

    logger.info("Digest generation complete")


if __name__ == "__main__":
    main() 