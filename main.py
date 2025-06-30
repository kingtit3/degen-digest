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

TEMPLATE_HEADER = "# 📰 Degen Digest – {date}\n\n"


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


def build_digest(processed_items):
    # Select top 10 by score but only one per tag where possible
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
        if len(chosen) >= 10:
            break

    from datetime import date

    # --- build TL;DR synopsis via LLM -----------------------------------
    try:
        from processor.summarizer import client as _llm_client  # reuse configured OpenAI/OpenRouter client

        prompt = (
            "Write a professional, concise (150-200 words) crypto market summary covering these headlines. "
            "Use clear, professional language that a financial analyst would understand. "
            "Focus on market trends, key developments, and their potential impact: \n"
            + "\n".join([h['headline'] for h in chosen])
        )
        _resp = _llm_client.chat.completions.create(
            model=os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200,
        )
        synopsis = _resp.choices[0].message.content.strip()
    except Exception as exc:
        logger.warning("Synopsis generation failed: %s", exc)
        synopsis = "*(Market summary unavailable)*"

    md = TEMPLATE_HEADER.format(date=date.today().isoformat())
    md += f"## 📋 Executive Summary\n\n{synopsis}\n\n---\n\n"

    # Market Overview Section
    md += "## 📊 Market Overview\n\n"
    md += "**Date:** " + date.today().strftime("%B %d, %Y") + "\n\n"
    md += "**Key Metrics:**\n"
    md += "- Total Stories Analyzed: " + str(len(processed_items)) + "\n"
    md += "- Top Engagement Score: " + str(max([item.get("_engagement_score", 0) for item in processed_items])) + "\n"
    md += "- Average Engagement: " + str(round(sum([item.get("_engagement_score", 0) for item in processed_items]) / len(processed_items), 2)) + "\n\n"
    md += "---\n\n"

    # Headlines section with full context
    md += "## 🔥 Top Stories of the Day\n\n"
    for idx, item in enumerate(chosen, 1):
        md += f"### {idx}. {item['tag']}\n\n"
        md += f"**Headline:** {item['headline']}\n\n"
        md += f"**Full Story:** {item['body']}\n\n"
        
        # Add engagement metrics if available
        engagement_info = []
        if item.get('likeCount'):
            engagement_info.append(f"Likes: {item['likeCount']:,}")
        if item.get('retweetCount'):
            engagement_info.append(f"Retweets: {item['retweetCount']:,}")
        if item.get('replyCount'):
            engagement_info.append(f"Replies: {item['replyCount']:,}")
        if item.get('viewCount'):
            engagement_info.append(f"Views: {item['viewCount']:,}")
        if item.get('_engagement_score'):
            engagement_info.append(f"Engagement Score: {item['_engagement_score']:.1f}")
        if item.get('_predicted_viral_score'):
            engagement_info.append(f"Viral Prediction: {item['_predicted_viral_score']:.1f}")
        
        if engagement_info:
            md += f"**Metrics:** {', '.join(engagement_info)}\n\n"
        
        # Add source information
        source = item.get('_source', 'Unknown')
        if source == 'twitter':
            source = 'Twitter'
        elif source == 'reddit':
            source = 'Reddit'
        elif source == 'telegram':
            source = 'Telegram'
        elif source == 'newsapi':
            source = 'News API'
        elif source == 'coingecko':
            source = 'CoinGecko'
        
        md += f"**Source:** {source}\n\n"
        
        if item['link']:
            md += f"**Link:** [{item['link']}]({item['link']})\n\n"
        
        md += "---\n\n"

    # Market Analysis Section
    md += "## 📈 Market Analysis\n\n"
    
    # Sentiment breakdown
    positive_count = sum(1 for item in processed_items if item.get('_sentiment_score', 0) > 0.1)
    negative_count = sum(1 for item in processed_items if item.get('_sentiment_score', 0) < -0.1)
    neutral_count = len(processed_items) - positive_count - negative_count
    
    md += f"**Sentiment Distribution:**\n"
    md += f"- Positive: {positive_count} stories ({positive_count/len(processed_items)*100:.1f}%)\n"
    md += f"- Neutral: {neutral_count} stories ({neutral_count/len(processed_items)*100:.1f}%)\n"
    md += f"- Negative: {negative_count} stories ({negative_count/len(processed_items)*100:.1f}%)\n\n"
    
    # Source breakdown
    source_counts = {}
    for item in processed_items:
        source = item.get('_source', 'unknown')
        source_counts[source] = source_counts.get(source, 0) + 1
    
    md += "**Content Sources:**\n"
    for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
        source_name = source.title()
        md += f"- {source_name}: {count} stories\n"
    md += "\n"

    # Sources appendix (page break then list all links)
    md += "\n\\newpage\n\n## 🌐 All Sources & References\n\n"
    md += "**Note:** All links are provided for reference and verification purposes.\n\n"
    
    # Group sources by type
    twitter_links = []
    reddit_links = []
    telegram_links = []
    news_links = []
    other_links = []
    
    for it in processed_items:
        if it['link']:
            if 'twitter.com' in it['link'] or 'x.com' in it['link']:
                twitter_links.append(it['link'])
            elif 'reddit.com' in it['link']:
                reddit_links.append(it['link'])
            elif 't.me' in it['link']:
                telegram_links.append(it['link'])
            elif any(domain in it['link'] for domain in ['cointelegraph.com', 'coindesk.com', 'decrypt.co', 'theblock.co']):
                news_links.append(it['link'])
            else:
                other_links.append(it['link'])
    
    if twitter_links:
        md += "**Twitter Sources:**\n"
        for link in twitter_links:
            md += f"- {link}\n"
        md += "\n"
    
    if reddit_links:
        md += "**Reddit Sources:**\n"
        for link in reddit_links:
            md += f"- {link}\n"
        md += "\n"
    
    if telegram_links:
        md += "**Telegram Sources:**\n"
        for link in telegram_links:
            md += f"- {link}\n"
        md += "\n"
    
    if news_links:
        md += "**News Sources:**\n"
        for link in news_links:
            md += f"- {link}\n"
        md += "\n"
    
    if other_links:
        md += "**Other Sources:**\n"
        for link in other_links:
            md += f"- {link}\n"
        md += "\n"
    
    # Footer
    md += "\n---\n\n"
    md += "**Disclaimer:** This digest is for informational purposes only. It does not constitute financial advice. "
    md += "Always conduct your own research before making investment decisions.\n\n"
    md += f"*Generated on {date.today().strftime('%B %d, %Y at %H:%M UTC')}*\n"
    
    return md


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sources = load_raw_sources()
    all_raw = []
    for items in sources.values():
        all_raw.extend(items)
    logger.info("Processing %d items from raw sources", len(all_raw))
    processed = process_items(all_raw)
    digest_md = build_digest(processed)
    DIGEST_MD.write_text(digest_md)
    # update seen ids with ones used in digest
    new_ids = {str(item["id"]) for item in processed if item.get("id")}
    if new_ids:
        existing = load_seen_ids()
        save_seen_ids(existing.union(new_ids))
    logger.info("Digest saved to %s", DIGEST_MD)

    # Post-processing outputs
    from datetime import date
    from utils.pdf import md_to_pdf
    from utils.notion import publish_page

    pdf_path = OUTPUT_DIR / f"digest-{date.today().isoformat()}.pdf"
    md_to_pdf(DIGEST_MD, pdf_path)

    publish_page(f"Degen Digest – {date.today().isoformat()}", DIGEST_MD)

    from storage.db import record_digest
    record_digest(date.today().isoformat(), DIGEST_MD, pdf_path)

    # buzz snapshot
    from processor import buzz as _buzz
    _buzz.make_snapshot(all_raw)


if __name__ == "__main__":
    main() 