import json
import logging
import os
import subprocess
import sys
import time
import traceback
from datetime import UTC, datetime, timezone
from pathlib import Path

import functions_framework
import requests

# Set up comprehensive logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_environment():
    """Set up the cloud function environment with necessary dependencies"""
    logger.info("Setting up cloud function environment...")

    # Install required packages
    packages = [
        "requests==2.31.0",
        "beautifulsoup4==4.12.2",
        "feedparser==6.0.10",
        "vaderSentiment==3.3.2",
        "pandas==2.0.3",
        "numpy==1.24.3",
        "python-dotenv==1.0.0",
        "schedule==1.2.0",
        "humanize==4.7.0",
    ]

    for package in packages:
        try:
            logger.info(f"Installing {package}...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                logger.warning(f"Failed to install {package}: {result.stderr}")
            else:
                logger.info(f"Successfully installed {package}")
        except Exception as e:
            logger.warning(f"Error installing {package}: {e}")


def collect_twitter_data():
    """Collect Twitter data using Apify API"""
    logger.info("Collecting Twitter data...")

    # Apify API configuration
    apify_token = os.environ.get("APIFY_API_TOKEN")
    if not apify_token:
        logger.error("APIFY_API_TOKEN not found in environment variables")
        return None

    try:
        # Search for crypto-related tweets
        search_terms = [
            "crypto",
            "bitcoin",
            "ethereum",
            "altcoin",
            "defi",
            "nft",
            "moon",
            "pump",
            "dump",
            "hodl",
            "fomo",
        ]

        twitter_data = []

        for term in search_terms[:3]:  # Limit to 3 terms to avoid rate limits
            logger.info(f"Searching for tweets with term: {term}")

            # Use Apify Twitter scraper (same as local scraper)
            url = f"https://api.apify.com/v2/acts/kaitoeasyapi~twitter-x-data-tweet-scraper-pay-per-result-cheapest/runs?token={apify_token}"

            payload = {
                "mode": "SCRAPE",
                "searchTerms": [term],
                "tweetsDesired": 50,
                "tweetFilters": {
                    "minLikes": 10,
                    "minRetweets": 5,
                    "includeRetweets": False,
                    "includeReplies": False,
                },
                "includeMetrics": True,
                "addUserInfo": True,
            }

            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                run_data = response.json()
                run_id = run_data["data"]["id"]

                # Wait for completion and get results
                time.sleep(10)
                results_url = f"https://api.apify.com/v2/acts/kaitoeasyapi~twitter-x-data-tweet-scraper-pay-per-result-cheapest/runs/{run_id}/dataset/items?token={apify_token}"
                results_response = requests.get(results_url, timeout=30)

                if results_response.status_code == 200:
                    tweets = results_response.json()
                    twitter_data.extend(tweets)
                    logger.info(f"Collected {len(tweets)} tweets for term '{term}'")
                else:
                    logger.warning(
                        f"Failed to get results for term '{term}': {results_response.status_code}"
                    )
            else:
                logger.warning(
                    f"Failed to start scraper for term '{term}': {response.status_code}"
                )

        return twitter_data

    except Exception as e:
        logger.error(f"Error collecting Twitter data: {e}")
        return None


def collect_reddit_data():
    """Collect Reddit data using RSS feeds"""
    logger.info("Collecting Reddit data...")

    try:
        import feedparser

        subreddits = [
            "cryptocurrency",
            "bitcoin",
            "ethereum",
            "altcoin",
            "defi",
            "nft",
            "cryptomarkets",
            "satoshistreetbets",
        ]

        reddit_data = []

        for subreddit in subreddits[:4]:  # Limit to 4 subreddits
            logger.info(f"Collecting from r/{subreddit}")

            try:
                feed_url = f"https://www.reddit.com/r/{subreddit}/hot/.rss"
                feed = feedparser.parse(feed_url)

                for entry in feed.entries[:10]:  # Top 10 posts
                    post_data = {
                        "source": "reddit",
                        "subreddit": subreddit,
                        "title": entry.title,
                        "url": entry.link,
                        "author": entry.author
                        if hasattr(entry, "author")
                        else "unknown",
                        "score": 0,  # RSS doesn't provide scores
                        "created_utc": datetime.now(UTC).isoformat(),
                        "num_comments": 0,  # RSS doesn't provide comment counts
                        "selftext": entry.summary if hasattr(entry, "summary") else "",
                    }
                    reddit_data.append(post_data)

                logger.info(f"Collected {len(feed.entries)} posts from r/{subreddit}")

            except Exception as e:
                logger.warning(f"Error collecting from r/{subreddit}: {e}")
                continue

        return reddit_data

    except Exception as e:
        logger.error(f"Error collecting Reddit data: {e}")
        return None


def collect_news_data():
    """Collect news data using NewsAPI"""
    logger.info("Collecting news data...")

    newsapi_key = os.environ.get("NEWSAPI_KEY")
    if not newsapi_key:
        logger.warning("NEWSAPI_KEY not found, skipping news collection")
        return None

    try:
        keywords = ["cryptocurrency", "bitcoin", "ethereum", "blockchain", "defi"]
        news_data = []

        for keyword in keywords[:2]:  # Limit to 2 keywords
            logger.info(f"Searching news for: {keyword}")

            url = "https://newsapi.org/v2/everything"
            params = {
                "q": keyword,
                "apiKey": newsapi_key,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 20,
            }

            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                articles = response.json().get("articles", [])

                for article in articles:
                    news_item = {
                        "source": "news",
                        "title": article.get("title", ""),
                        "url": article.get("url", ""),
                        "description": article.get("description", ""),
                        "published_at": article.get("publishedAt", ""),
                        "source_name": article.get("source", {}).get("name", ""),
                        "content": article.get("content", ""),
                    }
                    news_data.append(news_item)

                logger.info(f"Collected {len(articles)} news articles for '{keyword}'")
            else:
                logger.warning(
                    f"NewsAPI request failed for '{keyword}': {response.status_code}"
                )

        return news_data

    except Exception as e:
        logger.error(f"Error collecting news data: {e}")
        return None


def analyze_sentiment(text):
    """Analyze sentiment of text using VADER"""
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

        analyzer = SentimentIntensityAnalyzer()
        scores = analyzer.polarity_scores(text)
        return scores
    except Exception as e:
        logger.warning(f"Sentiment analysis failed: {e}")
        return {"compound": 0, "pos": 0, "neg": 0, "neu": 0}


def process_data(all_data):
    """Process and analyze collected data"""
    logger.info("Processing collected data...")

    processed_data = []

    for item in all_data:
        try:
            # Extract text for sentiment analysis
            text = ""
            if item.get("source") == "twitter":
                text = item.get("full_text", item.get("text", ""))
            elif item.get("source") == "reddit":
                text = item.get("title", "") + " " + item.get("selftext", "")
            elif item.get("source") == "news":
                text = item.get("title", "") + " " + item.get("description", "")

            # Analyze sentiment
            sentiment = analyze_sentiment(text)

            # Calculate engagement score
            engagement_score = 0
            if item.get("source") == "twitter":
                engagement_score = (
                    item.get("retweet_count", 0)
                    + item.get("favorite_count", 0) * 2
                    + item.get("reply_count", 0) * 3
                )
            elif item.get("source") == "reddit":
                engagement_score = (
                    item.get("score", 0) + item.get("num_comments", 0) * 2
                )

            # Add processed data
            processed_item = {
                **item,
                "sentiment": sentiment,
                "engagement_score": engagement_score,
                "processed_at": datetime.now(UTC).isoformat(),
            }

            processed_data.append(processed_item)

        except Exception as e:
            logger.warning(f"Error processing item: {e}")
            continue

    return processed_data


def generate_digest(processed_data):
    """Generate a human-friendly digest from processed data"""
    logger.info("Generating digest...")

    try:
        # Sort by engagement score
        sorted_data = sorted(
            processed_data, key=lambda x: x.get("engagement_score", 0), reverse=True
        )

        # Get top items
        top_twitter = [item for item in sorted_data if item.get("source") == "twitter"][
            :5
        ]
        top_reddit = [item for item in sorted_data if item.get("source") == "reddit"][
            :5
        ]
        top_news = [item for item in sorted_data if item.get("source") == "news"][:5]

        # Generate digest content
        digest_content = f"""# 🚀 Degen Digest - {datetime.now().strftime('%Y-%m-%d')}

## 📊 Executive Summary
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}
Total items analyzed: {len(processed_data)}
Sources: Twitter ({len([x for x in processed_data if x.get('source') == 'twitter'])}), Reddit ({len([x for x in processed_data if x.get('source') == 'reddit'])}), News ({len([x for x in processed_data if x.get('source') == 'news'])}))

## 🐦 Top Twitter Moments
"""

        for i, tweet in enumerate(top_twitter, 1):
            text = (
                tweet.get("full_text", tweet.get("text", ""))[:100] + "..."
                if len(tweet.get("full_text", tweet.get("text", ""))) > 100
                else tweet.get("full_text", tweet.get("text", ""))
            )
            engagement = tweet.get("engagement_score", 0)
            sentiment = tweet.get("sentiment", {}).get("compound", 0)
            sentiment_emoji = (
                "🚀" if sentiment > 0.1 else "📉" if sentiment < -0.1 else "➡️"
            )

            digest_content += f"""
### {i}. {sentiment_emoji} {text}
- **Engagement:** {engagement:,} interactions
- **Sentiment:** {sentiment:.2f}
- **Author:** @{tweet.get('user', {}).get('screen_name', 'unknown')}
- **Link:** {tweet.get('url', 'N/A')}
"""

        digest_content += """
## 🔥 Hot Reddit Posts
"""

        for i, post in enumerate(top_reddit, 1):
            title = (
                post.get("title", "")[:80] + "..."
                if len(post.get("title", "")) > 80
                else post.get("title", "")
            )
            engagement = post.get("engagement_score", 0)
            sentiment = post.get("sentiment", {}).get("compound", 0)
            sentiment_emoji = (
                "🚀" if sentiment > 0.1 else "📉" if sentiment < -0.1 else "➡️"
            )

            digest_content += f"""
### {i}. {sentiment_emoji} {title}
- **Engagement:** {engagement:,} points
- **Sentiment:** {sentiment:.2f}
- **Subreddit:** r/{post.get('subreddit', 'unknown')}
- **Link:** {post.get('url', 'N/A')}
"""

        digest_content += """
## 📰 Breaking News
"""

        for i, news in enumerate(top_news, 1):
            title = (
                news.get("title", "")[:80] + "..."
                if len(news.get("title", "")) > 80
                else news.get("title", "")
            )
            sentiment = news.get("sentiment", {}).get("compound", 0)
            sentiment_emoji = (
                "🚀" if sentiment > 0.1 else "📉" if sentiment < -0.1 else "➡️"
            )

            digest_content += f"""
### {i}. {sentiment_emoji} {title}
- **Source:** {news.get('source_name', 'unknown')}
- **Sentiment:** {sentiment:.2f}
- **Published:** {news.get('published_at', 'N/A')}
- **Link:** {news.get('url', 'N/A')}
"""

        digest_content += f"""
## 📈 Market Sentiment Overview
- **Overall Sentiment:** {sum([x.get('sentiment', {}).get('compound', 0) for x in processed_data]) / len(processed_data):.2f}
- **Total Engagement:** {sum([x.get('engagement_score', 0) for x in processed_data]):,}
- **Data Quality:** {len([x for x in processed_data if x.get('sentiment')])}/{len(processed_data)} items analyzed

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
*Generated by Degen Digest Cloud Function* 🤖
"""

        return digest_content

    except Exception as e:
        logger.error(f"Error generating digest: {e}")
        return f"Error generating digest: {str(e)}"


def save_data(processed_data, digest_content):
    """Save data to database and generate digest files"""
    logger.info("Saving data to database and generating digest files...")

    try:
        # Create output directory
        output_dir = Path("/tmp/output")  # Use /tmp for cloud function
        output_dir.mkdir(exist_ok=True)

        # Save processed data as JSON for syncing back to local system
        data_json_path = output_dir / "consolidated_data.json"
        with open(data_json_path, "w", encoding="utf-8") as f:
            json.dump(processed_data, f, indent=2, default=str)

        # Save digest files
        if digest_content:
            # Save markdown digest
            digest_md_path = output_dir / "digest.md"
            with open(digest_md_path, "w", encoding="utf-8") as f:
                f.write(digest_content)

            # Save dated digest
            date_str = datetime.now().strftime("%Y-%m-%d")
            dated_digest_path = output_dir / f"digest-{date_str}.md"
            with open(dated_digest_path, "w", encoding="utf-8") as f:
                f.write(digest_content)

            logger.info(f"Saved digest files to {output_dir}")

        return str(output_dir)

    except Exception as e:
        logger.error(f"Error saving data: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None


@functions_framework.http
def refresh_data(request):
    """
    Main cloud function entry point for data collection and digest generation.

    This function is completely self-contained and doesn't rely on external files.
    """

    start_time = time.time()
    execution_id = os.environ.get("K_REVISION", "unknown")

    logger.info(f"Cloud function started - Execution ID: {execution_id}")

    try:
        # Parse request data
        request_data = {}
        if request.method == "POST":
            try:
                request_data = request.get_json() or {}
            except Exception as e:
                logger.warning(f"Failed to parse request JSON: {e}")

        # Extract parameters
        force_refresh = request_data.get("force_refresh", False)
        should_generate_digest = request_data.get("generate_digest", True)

        logger.info(
            f"Parameters - Force refresh: {force_refresh}, Generate digest: {should_generate_digest}"
        )

        # Step 1: Setup environment
        setup_environment()

        # Step 2: Collect data from multiple sources
        all_data = []

        # Collect Twitter data using built-in method
        logger.info("Starting Twitter data collection...")
        twitter_data = collect_twitter_data()
        if twitter_data:
            all_data.extend(twitter_data)
            logger.info(f"Collected {len(twitter_data)} Twitter items")
        else:
            logger.warning("No Twitter data collected")

        # Collect Reddit data using built-in method
        logger.info("Starting Reddit data collection...")
        reddit_data = collect_reddit_data()
        if reddit_data:
            all_data.extend(reddit_data)
            logger.info(f"Collected {len(reddit_data)} Reddit items")
        else:
            logger.warning("No Reddit data collected")

        # Collect news data using built-in method
        logger.info("Starting news data collection...")
        news_data = collect_news_data()
        if news_data:
            all_data.extend(news_data)
            logger.info(f"Collected {len(news_data)} news items")
        else:
            logger.warning("No news data collected")

        if not all_data:
            logger.warning("No data collected from any source")
            return {
                "status": "warning",
                "message": "No data collected from any source",
                "timestamp": datetime.now(UTC).isoformat(),
            }, 200

        # Step 3: Process and analyze data
        processed_data = process_data(all_data)
        logger.info(f"Processed {len(processed_data)} items")

        # Step 4: Generate digest
        digest_content = None
        if should_generate_digest:
            digest_content = generate_digest(processed_data)
            logger.info("Digest generated successfully")

        # Step 5: Save data
        save_data(processed_data, digest_content)

        # Step 6: Prepare response
        total_time = time.time() - start_time

        response_data = {
            "status": "success",
            "message": "Data collection and processing completed successfully",
            "execution_id": execution_id,
            "metrics": {
                "total_execution_time": total_time,
                "data_collected": len(all_data),
                "data_processed": len(processed_data),
                "sources": {
                    "twitter": len(
                        [x for x in all_data if x.get("source") == "twitter"]
                    ),
                    "reddit": len([x for x in all_data if x.get("source") == "reddit"]),
                    "news": len([x for x in all_data if x.get("source") == "news"]),
                },
                "digest_generated": should_generate_digest
                and digest_content is not None,
            },
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # Include digest content in response if generated
        if digest_content:
            response_data["digest_content"] = digest_content
            response_data["digest_date"] = datetime.now().strftime("%Y-%m-%d")

        # Include processed data for syncing back to local system
        response_data["processed_data"] = processed_data

        logger.info(
            f"Cloud function completed successfully - Total time: {total_time:.2f}s"
        )

        return response_data

    except Exception as e:
        error_time = time.time() - start_time
        error_msg = f"Unexpected error in cloud function: {str(e)}"

        logger.error(
            f"Cloud function error - Execution ID: {execution_id}, Error: {str(e)}"
        )
        logger.error(f"Traceback: {traceback.format_exc()}")

        return {
            "status": "error",
            "message": error_msg,
            "execution_id": execution_id,
            "execution_time": error_time,
            "timestamp": datetime.now(UTC).isoformat(),
        }, 500


@functions_framework.http
def health_check(request):
    """Health check endpoint"""
    try:
        logger.info("Health check requested")

        health_status = {
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat(),
            "environment": "cloud_function",
            "version": "2.0.0",
            "features": [
                "twitter_data_collection",
                "reddit_data_collection",
                "news_data_collection",
                "sentiment_analysis",
                "digest_generation",
            ],
        }

        return health_status

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(UTC).isoformat(),
        }, 500
