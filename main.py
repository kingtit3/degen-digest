"""Entry point that orchestrates scraping outputs → digest.

Adds a `run_id` (UUID) bound to the structured‐logging context so every log
event coming from this process can be correlated end-to-end.
"""

import json
import logging
import uuid
import os
from datetime import datetime

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
TEMPLATE_HEADER = """# 🚀 Degen Digest - Your Daily Crypto Intelligence

**Date:** {date} | **What's Hot in Crypto Today**

---

## 🎯 **TL;DR - What You Need to Know**

{executive_summary}

---

## 🔥 **Today's Hottest Stories**

{key_takeaways}

---

## 📊 **Market Pulse**

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
    """Create a human-friendly, conversational executive summary"""
    try:
        from processor.summarizer import client as _llm_client

        # Create a conversational summary prompt
        stories = []
        for i, item in enumerate(chosen_items[:5], 1):  # Top 5 stories
            headline = item.get('headline', 'Unknown story')
            stories.append(f"{i}. {headline}")
        
        prompt = f"""
        Create a conversational, engaging summary (150-200 words) for crypto enthusiasts and content creators.
        
        Write this as if you're talking to a friend about what's happening in crypto today. Make it:
        - Conversational and easy to understand
        - Actionable (what should people pay attention to?)
        - Engaging and interesting to read
        - Perfect for creating content around
        
        Focus on:
        - What's the biggest story everyone's talking about?
        - What opportunities or risks should people know about?
        - What's the overall mood in the crypto space?
        - Any trends that content creators should focus on?
        
        Use natural language, avoid jargon, and make it sound like a knowledgeable friend explaining what's up.
        
        Top stories to summarize:
        {chr(10).join(stories)}
        
        Start with something engaging like "Here's what's shaking up the crypto world today..." and make it flow naturally.
        """
        
        _resp = _llm_client.chat.completions.create(
            model=os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=350,
        )
        return _resp.choices[0].message.content.strip()
    except Exception as exc:
        logger.warning("Executive summary generation failed: %s", exc)
        return "Here's what's shaking up the crypto world today - we've got some interesting developments brewing, but technical issues are preventing us from getting the full picture right now."


def create_key_takeaways(chosen_items: List[Dict]) -> str:
    """Create content-creation focused key takeaways"""
    if not chosen_items:
        return "No major stories to highlight today."
    
    # Extract key themes and create content-friendly takeaways
    themes = {}
    for item in chosen_items[:8]:  # Top 8 items
        tag = item.get('tag', 'General')
        headline = item.get('headline', '')
        
        # Simplify tags for better content creation
        if 'Top CT Story' in tag:
            simplified_tag = "🔥 Viral Story"
        elif 'Rug' in tag:
            simplified_tag = "💀 Rug Alert"
        elif 'Meme Launch' in tag:
            simplified_tag = "🚀 New Launch"
        elif 'Whale Move' in tag:
            simplified_tag = "🐳 Whale Activity"
        elif 'Alpha Thread' in tag:
            simplified_tag = "🧠 Alpha Leak"
        elif 'Quote' in tag:
            simplified_tag = "💬 Hot Take"
        else:
            simplified_tag = "📰 General"
            
        if simplified_tag not in themes:
            themes[simplified_tag] = []
        themes[simplified_tag].append(headline)
    
    # Create content-friendly takeaways
    takeaways = []
    
    # Find the most viral story
    if themes.get("🔥 Viral Story"):
        viral_story = themes["🔥 Viral Story"][0]
        takeaways.append(f"**🔥 The Viral Story:** {viral_story}")
    
    # Find the biggest risk/opportunity
    if themes.get("💀 Rug Alert"):
        rug_story = themes["💀 Rug Alert"][0]
        takeaways.append(f"**⚠️ Risk Alert:** {rug_story}")
    
    # Find new opportunities
    if themes.get("🚀 New Launch"):
        launch_story = themes["🚀 New Launch"][0]
        takeaways.append(f"**🚀 Opportunity:** {launch_story}")
    
    # Find whale activity
    if themes.get("🐳 Whale Activity"):
        whale_story = themes["🐳 Whale Activity"][0]
        takeaways.append(f"**🐳 Big Money Move:** {whale_story}")
    
    # Find alpha/insights
    if themes.get("🧠 Alpha Leak"):
        alpha_story = themes["🧠 Alpha Leak"][0]
        takeaways.append(f"**🧠 Alpha Insight:** {alpha_story}")
    
    # Find community sentiment
    if themes.get("💬 Hot Take"):
        hot_take = themes["💬 Hot Take"][0]
        takeaways.append(f"**💬 Community Buzz:** {hot_take}")
    
    # Add market mood
    bullish_count = len([i for i in chosen_items if any(word in i.get('headline', '').lower() for word in ['bull', 'moon', 'pump', 'green', 'up'])])
    bearish_count = len([i for i in chosen_items if any(word in i.get('headline', '').lower() for word in ['bear', 'dump', 'red', 'down', 'crash'])])
    
    if bullish_count > bearish_count:
        mood = "optimistic and bullish"
    elif bearish_count > bullish_count:
        mood = "cautious and bearish"
    else:
        mood = "mixed and uncertain"
    
    takeaways.append(f"**📊 Overall Mood:** The crypto community is feeling {mood} today")
    
    # Add content creation tips
    takeaways.append(f"**🎯 Content Ideas:** Focus on {themes.get('🔥 Viral Story', ['general crypto news'])[0][:50]}... for maximum engagement")
    
    return "\n\n".join(takeaways)


def create_market_overview(processed_items: List[Dict]) -> str:
    """Create a conversational market overview for content creators"""
    if not processed_items:
        return "Not enough data to analyze today's market activity."
    
    total_stories = len(processed_items)
    top_engagement = max([item.get("_engagement_score", 0) for item in processed_items]) if processed_items else 0
    avg_engagement = sum([item.get("_engagement_score", 0) for item in processed_items]) / len(processed_items) if processed_items else 0
    
    # Get source breakdown
    sources = {}
    for item in processed_items:
        source = item.get('_source', 'unknown')
        sources[source] = sources.get(source, 0) + 1
    
    # Find trending topics
    trending_topics = []
    for item in processed_items[:5]:
        headline = item.get('headline', '')
        if headline and len(headline) > 10:
            trending_topics.append(headline[:40] + "..." if len(headline) > 40 else headline)
    
    # Determine market activity level
    if total_stories > 1000:
        activity_level = "🔥 Super Active"
    elif total_stories > 500:
        activity_level = "📈 Very Active"
    elif total_stories > 200:
        activity_level = "📊 Moderately Active"
    else:
        activity_level = "😴 Quiet"
    
    # Find the most engaging content type
    content_types = {}
    for item in processed_items[:20]:
        tag = item.get('tag', 'General')
        score = item.get('_engagement_score', 0)
        if tag not in content_types:
            content_types[tag] = {'count': 0, 'total_score': 0}
        content_types[tag]['count'] += 1
        content_types[tag]['total_score'] += score
    
    best_content_type = "general crypto news"
    best_avg_score = 0
    for tag, data in content_types.items():
        avg_score = data['total_score'] / data['count']
        if avg_score > best_avg_score:
            best_avg_score = avg_score
            best_content_type = tag
    
    return f"""
### 📊 **What We're Seeing Today**

**Market Activity:** {activity_level} - We analyzed {total_stories:,} stories from across the crypto space

**Engagement Levels:** 
- Highest scoring story: {top_engagement:.1f}/100
- Average engagement: {avg_engagement:.1f}/100

**Where the Action Is:** Most engagement is coming from {best_content_type.lower()} content

**Trending Topics:** {', '.join(trending_topics[:3]) if trending_topics else 'General market discussion'}

### 🎯 **Content Creator Insights**

**Best Performing Content:** {best_content_type} is getting the most love today

**Engagement Sweet Spot:** Stories scoring above {avg_engagement + 10:.1f} are performing well

**Source Breakdown:** {', '.join([f'{source} ({count})' for source, count in list(sources.items())[:3]])}

**Pro Tip:** Focus on {best_content_type.lower()} content for maximum reach today
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

    # Stories section with conversational tone
    md += "## 📰 **Deep Dive: Today's Top Stories**\n\n"
    
    # Group stories by category for better organization
    story_categories = {
        "🔥 **The Big Stories** (Everyone's Talking About)": [],
        "🚀 **New Opportunities** (Projects & Launches)": [],
        "🐳 **Big Money Moves** (Whale Activity)": [],
        "🧠 **Alpha & Insights** (Inside Scoop)": [],
        "💬 **Community Vibes** (What People Are Saying)": []
    }
    
    for item in chosen:
        tag = item.get('tag', 'General')
        if 'Top CT Story' in tag or 'Rug' in tag:
            story_categories["🔥 **The Big Stories** (Everyone's Talking About)"].append(item)
        elif 'Meme Launch' in tag:
            story_categories["🚀 **New Opportunities** (Projects & Launches)"].append(item)
        elif 'Whale Move' in tag:
            story_categories["🐳 **Big Money Moves** (Whale Activity)"].append(item)
        elif 'Alpha Thread' in tag:
            story_categories["🧠 **Alpha & Insights** (Inside Scoop)"].append(item)
        else:
            story_categories["💬 **Community Vibes** (What People Are Saying)"].append(item)
    
    # Display stories by category with conversational tone
    for category, stories in story_categories.items():
        if stories:
            md += f"### {category}\n\n"
            for idx, item in enumerate(stories, 1):
                # Make headlines more conversational
                headline = item['headline']
                if headline.startswith('**') and headline.endswith('**'):
                    headline = headline[2:-2]  # Remove markdown bold
                
                md += f"**{idx}. {headline}**\n\n"
                
                # Make the body more conversational
                body = item['body']
                if body:
                    # Add conversational transitions
                    if not body.startswith(('Here', 'This', 'The', 'A', 'An')):
                        body = f"Here's what's happening: {body}"
                    md += f"{body}\n\n"
                
                # Add engagement metrics in a friendly way
                engagement_info = []
                if item.get('likeCount'):
                    engagement_info.append(f"❤️ {item['likeCount']:,} likes")
                if item.get('retweetCount'):
                    engagement_info.append(f"🔄 {item['retweetCount']:,} shares")
                if item.get('replyCount'):
                    engagement_info.append(f"💬 {item['replyCount']:,} comments")
                if item.get('viewCount'):
                    engagement_info.append(f"👁️ {item['viewCount']:,} views")
                if item.get('_engagement_score'):
                    score = item['_engagement_score']
                    if score > 80:
                        engagement_info.append(f"🔥 Viral ({score:.1f}/100)")
                    elif score > 60:
                        engagement_info.append(f"📈 Hot ({score:.1f}/100)")
                    else:
                        engagement_info.append(f"📊 Score: {score:.1f}/100")
                
                if engagement_info:
                    md += f"*Engagement: {' | '.join(engagement_info)}*\n\n"
                
                md += "---\n\n"
    
    # Add actionable insights section
    md += "## 💡 **What This Means for You**\n\n"
    
    # Generate actionable insights
    insights = []
    
    # Price movements (if available)
    try:
        prices = get_prices_sync()
        if prices:
            md += "### 💰 **Key Price Movements**\n\n"
            for symbol, data in list(prices.items())[:5]:  # Top 5
                change_24h = data.get('price_change_percentage_24h', 0)
                emoji = "🟢" if change_24h > 0 else "🔴" if change_24h < 0 else "⚪"
                md += f"{emoji} **{symbol.upper()}:** ${data.get('current_price', 0):,.2f} ({change_24h:+.2f}%)\n\n"
    except Exception as e:
        logger.warning(f"Price data unavailable: {e}")
    
    # Add content creation insights
    md += "### 🎯 **Content Creation Opportunities**\n\n"
    
    # Find the most viral story for content ideas
    viral_story = None
    for item in chosen:
        if item.get('_engagement_score', 0) > 80:
            viral_story = item
            break
    
    if viral_story:
        md += f"**🔥 Viral Topic:** {viral_story.get('headline', '')}\n\n"
        md += f"**Content Ideas:**\n"
        md += f"• Create a deep dive video on this topic\n"
        md += f"• Make a reaction video to the community response\n"
        md += f"• Write a thread explaining the implications\n"
        md += f"• Host a Twitter Space discussion\n\n"
    
    # Add market sentiment insights
    bullish_count = len([i for i in chosen if any(word in i.get('headline', '').lower() for word in ['bull', 'moon', 'pump', 'green', 'up'])])
    bearish_count = len([i for i in chosen if any(word in i.get('headline', '').lower() for word in ['bear', 'dump', 'red', 'down', 'crash'])])
    
    if bullish_count > bearish_count:
        md += "**📈 Market Sentiment:** Bullish vibes today - focus on opportunities and positive developments\n\n"
    elif bearish_count > bullish_count:
        md += "**📉 Market Sentiment:** Cautious mood - focus on risk management and defensive strategies\n\n"
    else:
        md += "**📊 Market Sentiment:** Mixed signals - balanced approach recommended\n\n"
    
    # Add footer with more conversational tone
    md += "---\n\n"
    md += "## 📋 **About This Report**\n\n"
    md += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
    md += "**Data Sources:** Twitter, Reddit, Telegram, NewsAPI, CoinGecko\n\n"
    md += "**Analysis Method:** AI-powered content analysis with engagement scoring\n\n"
    md += "---\n\n"
    md += "*This report is generated automatically and should not be considered as financial advice. Always do your own research and never invest more than you can afford to lose.*\n\n"
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

    # Automatically rename digest with today's date
    try:
        from rename_digest import rename_digest
        rename_digest()
        logger.info("Digest automatically renamed with date")
    except Exception as e:
        logger.warning(f"Auto-rename failed: {e}")

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