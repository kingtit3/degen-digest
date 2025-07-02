#!/usr/bin/env python3
"""
Enhanced Data Pipeline with Viral Prediction and Intelligent Analysis
This replaces the basic cloud function with advanced ML capabilities
"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List

import numpy as np
import requests

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from sqlmodel import Session, desc, select

from processor.enhanced_viral_predictor import EnhancedViralPredictor
from processor.scorer import extract_tickers, get_sentiment_score
from storage.db import RedditPost, Tweet, engine
from utils.advanced_logging import get_logger

logger = get_logger(__name__)


class EnhancedDataPipeline:
    """Enhanced data pipeline with viral prediction and intelligent analysis"""

    def __init__(self):
        self.viral_predictor = EnhancedViralPredictor()
        self.historical_data = []
        self.trends = {}
        self.viral_predictions = {}
        self.market_insights = {}

        # Load historical data for learning
        self._load_historical_data()

        # Train or load models
        self._initialize_models()

    def _load_historical_data(self):
        """Load historical data from database for learning"""
        logger.info("Loading historical data for ML training...")

        try:
            with Session(engine) as session:
                # Get recent tweets with engagement data
                tweets = session.exec(
                    select(Tweet)
                    .where(
                        Tweet.created_at
                        >= datetime.now(timezone.utc) - timedelta(days=30)
                    )
                    .order_by(desc(Tweet.created_at))
                ).all()

                for tweet in tweets:
                    self.historical_data.append(
                        {
                            "source": "twitter",
                            "text": tweet.full_text,
                            "user_screen_name": tweet.user_screen_name,
                            "user_followers_count": tweet.user_followers_count,
                            "user_verified": tweet.user_verified,
                            "like_count": tweet.like_count,
                            "retweet_count": tweet.retweet_count,
                            "reply_count": tweet.reply_count,
                            "created_at": tweet.created_at,
                            "engagement_score": (tweet.like_count or 0)
                            + (tweet.retweet_count or 0) * 2
                            + (tweet.reply_count or 0) * 3,
                        }
                    )

                # Get recent Reddit posts
                posts = session.exec(
                    select(RedditPost)
                    .where(
                        RedditPost.created_at
                        >= datetime.now(timezone.utc) - timedelta(days=30)
                    )
                    .order_by(desc(RedditPost.created_at))
                ).all()

                for post in posts:
                    self.historical_data.append(
                        {
                            "source": "reddit",
                            "title": post.title,
                            "author": post.author,
                            "subreddit": post.subreddit,
                            "score": post.score,
                            "num_comments": post.num_comments,
                            "created_at": post.created_at,
                            "engagement_score": post.score + post.num_comments * 2,
                        }
                    )

                logger.info(f"Loaded {len(self.historical_data)} historical items")

        except Exception as e:
            logger.error(f"Error loading historical data: {e}")

    def _initialize_models(self):
        """Initialize and train ML models"""
        logger.info("Initializing ML models...")

        try:
            # Check if we have enough data to train
            if len(self.historical_data) >= 100:
                logger.info("Training viral prediction models...")
                self.viral_predictor.train(self.historical_data)
                logger.info("Models trained successfully")
            else:
                logger.warning(
                    f"Insufficient historical data ({len(self.historical_data)} items). Need at least 100 items."
                )

        except Exception as e:
            logger.error(f"Error training models: {e}")

    def fetch_latest_data(self) -> list[dict]:
        """Fetch latest data from cloud function"""
        logger.info("Fetching latest data from cloud function...")

        try:
            url = "https://us-central1-lucky-union-463615-t3.cloudfunctions.net/degen-digest-refresh"
            response = requests.post(url, json={"generate_digest": False}, timeout=120)

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    # The cloud function doesn't return the actual data, so we need to fetch it differently
                    # For now, let's use the consolidated data file
                    consolidated_file = Path("output/consolidated_data.json")
                    if consolidated_file.exists():
                        with open(consolidated_file) as f:
                            raw_data = json.load(f)
                            # Convert nested structure to flat list
                            return self._flatten_consolidated_data(raw_data)
                    else:
                        logger.warning("No consolidated data file found")
                        return []
                else:
                    logger.error(f"Cloud function error: {data.get('message')}")
                    return []
            else:
                logger.error(f"HTTP error: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return []

    def _flatten_consolidated_data(self, raw_data: dict) -> list[dict]:
        """Convert nested consolidated data to flat list of items"""
        flattened_items = []

        # Process tweets
        if "tweets" in raw_data:
            for tweet in raw_data["tweets"]:
                item = {
                    "type": "tweet",
                    "source": "twitter",
                    "text": tweet.get("text", ""),
                    "id": tweet.get("id", ""),
                    "url": tweet.get("url", ""),
                    "user_screen_name": tweet.get("user", {}).get("screenName", ""),
                    "user_followers_count": tweet.get("user", {}).get(
                        "followersCount", 0
                    ),
                    "user_verified": tweet.get("user", {}).get("verified", False),
                    "like_count": tweet.get("likeCount", 0),
                    "retweet_count": tweet.get("retweetCount", 0),
                    "reply_count": tweet.get("replyCount", 0),
                    "quote_count": tweet.get("quoteCount", 0),
                    "view_count": tweet.get("viewCount", 0),
                    "created_at": tweet.get("createdAt", ""),
                    "engagement_score": (tweet.get("likeCount", 0) or 0)
                    + (tweet.get("retweetCount", 0) or 0) * 2
                    + (tweet.get("replyCount", 0) or 0) * 3,
                }
                flattened_items.append(item)

        # Process Reddit posts
        if "reddit_posts" in raw_data:
            for post in raw_data["reddit_posts"]:
                item = {
                    "type": "reddit_post",
                    "source": "reddit",
                    "title": post.get("title", ""),
                    "text": post.get("selftext", ""),
                    "id": post.get("id", ""),
                    "url": post.get("url", ""),
                    "author": post.get("author", ""),
                    "subreddit": post.get("subreddit", ""),
                    "score": post.get("score", 0),
                    "num_comments": post.get("num_comments", 0),
                    "created_at": post.get("created_utc", ""),
                    "engagement_score": (post.get("score", 0) or 0)
                    + (post.get("num_comments", 0) or 0) * 2,
                }
                flattened_items.append(item)

        # Process news articles
        if "news" in raw_data:
            for article in raw_data["news"]:
                item = {
                    "type": "news",
                    "source": "news",
                    "title": article.get("title", ""),
                    "text": article.get("description", ""),
                    "summary": article.get("content", ""),
                    "id": article.get("url", ""),
                    "url": article.get("url", ""),
                    "author": article.get("author", ""),
                    "published_at": article.get("publishedAt", ""),
                    "source_name": article.get("source", {}).get("name", ""),
                    "engagement_score": 0,  # News articles don't have engagement metrics
                }
                flattened_items.append(item)

        logger.info(f"Flattened {len(flattened_items)} items from consolidated data")
        return flattened_items

    def analyze_viral_potential(self, items: list[dict]) -> list[dict]:
        """Analyze viral potential of items using ML models"""
        logger.info("Analyzing viral potential...")

        enhanced_items = []

        for item in items:
            try:
                # Ensure item is a dictionary
                if not isinstance(item, dict):
                    logger.warning(f"Skipping non-dict item: {type(item)}")
                    continue

                # Extract advanced features
                features = self.viral_predictor.extract_advanced_features(item)

                # Predict viral score
                if self.viral_predictor.is_trained:
                    prediction = self.viral_predictor.predict_viral_score(item)
                    viral_score = prediction.get("viral_score", 0)
                    confidence = prediction.get("confidence", 0)
                else:
                    viral_score = 0
                    confidence = 0

                # Calculate trend indicators
                trend_indicators = self._calculate_trend_indicators(item)

                # Enhanced item with predictions
                enhanced_item = {
                    **item,
                    "viral_score": viral_score,
                    "viral_confidence": confidence,
                    "trend_indicators": trend_indicators,
                    "features": features,
                    "predicted_engagement": int(
                        viral_score * 1000
                    ),  # Scale to realistic numbers
                    "virality_probability": min(
                        viral_score / 10, 1.0
                    ),  # Convert to probability
                    "trending_score": self._calculate_trending_score(item, features),
                    "market_impact": self._assess_market_impact(item),
                    "content_quality": self._assess_content_quality(item),
                    "author_influence": self._assess_author_influence(item),
                    "timing_score": self._assess_timing_score(item),
                }

                enhanced_items.append(enhanced_item)

            except Exception as e:
                logger.warning(f"Error analyzing item: {e}")
                if isinstance(item, dict):
                    enhanced_items.append(item)

        return enhanced_items

    def _calculate_trend_indicators(self, item: dict) -> dict:
        """Calculate trend indicators for an item"""
        text = f"{item.get('text', '')} {item.get('title', '')}"

        return {
            "ticker_mentions": extract_tickers(text),
            "sentiment_trend": get_sentiment_score(text),
            "engagement_velocity": self._calculate_engagement_velocity(item),
            "topic_trend": self._identify_topic_trend(text),
            "market_sentiment": self._assess_market_sentiment(text),
        }

    def _calculate_engagement_velocity(self, item: dict) -> float:
        """Calculate engagement velocity (engagements per hour)"""
        created_at = item.get("created_at")
        if not created_at:
            return 0

        try:
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

            hours_since_creation = (
                datetime.now(timezone.utc) - created_at
            ).total_seconds() / 3600
            if hours_since_creation < 1:
                hours_since_creation = 1

            engagement = item.get("engagement_score", 0)
            return engagement / hours_since_creation

        except Exception:
            return 0

    def _identify_topic_trend(self, text: str) -> str:
        """Identify trending topics in text"""
        text_lower = text.lower()

        topics = {
            "defi": ["defi", "yield", "liquidity", "amm", "dex"],
            "nft": ["nft", "mint", "floor", "rarity"],
            "gaming": ["game", "play", "gaming", "metaverse"],
            "ai": ["ai", "artificial intelligence", "machine learning"],
            "meme": ["meme", "doge", "shib", "pepe"],
            "institutional": ["institutional", "etf", "adoption", "regulation"],
        }

        for topic, keywords in topics.items():
            if any(keyword in text_lower for keyword in keywords):
                return topic

        return "general"

    def _assess_market_sentiment(self, text: str) -> str:
        """Assess market sentiment from text"""
        text_lower = text.lower()

        bullish_words = ["bull", "moon", "pump", "buy", "long", "hodl", "diamond"]
        bearish_words = ["bear", "dump", "sell", "short", "crash", "rug"]

        bullish_count = sum(1 for word in bullish_words if word in text_lower)
        bearish_count = sum(1 for word in bearish_words if word in text_lower)

        if bullish_count > bearish_count:
            return "bullish"
        elif bearish_count > bullish_count:
            return "bearish"
        else:
            return "neutral"

    def _calculate_trending_score(self, item: dict, features: dict) -> float:
        """Calculate trending score based on multiple factors"""
        score = 0

        # Engagement velocity
        velocity = features.get("engagement_velocity", 0)
        score += min(velocity / 100, 10)  # Cap at 10 points

        # Author influence
        followers = item.get("user_followers_count", 0)
        score += min(followers / 100000, 5)  # Cap at 5 points

        # Content quality
        text_length = features.get("text_length", 0)
        score += min(text_length / 100, 3)  # Cap at 3 points

        # Sentiment
        sentiment = features.get("sentiment_score", 0)
        score += abs(sentiment) * 2  # Both positive and negative sentiment can trend

        return min(score, 20)  # Cap at 20

    def _assess_market_impact(self, item: dict) -> str:
        """Assess potential market impact"""
        text = f"{item.get('text', '')} {item.get('title', '')}"
        tickers = extract_tickers(text)

        if len(tickers) > 3:
            return "high"
        elif len(tickers) > 1:
            return "medium"
        else:
            return "low"

    def _assess_content_quality(self, item: dict) -> float:
        """Assess content quality score"""
        text = f"{item.get('text', '')} {item.get('title', '')}"

        score = 0

        # Length (not too short, not too long)
        if 50 <= len(text) <= 500:
            score += 2

        # Has hashtags but not too many
        hashtag_count = text.count("#")
        if 1 <= hashtag_count <= 5:
            score += 1

        # Has mentions
        if "@" in text:
            score += 1

        # Has URLs
        if "http" in text:
            score += 1

        # Has emojis (engagement factor)
        emoji_count = sum(1 for c in text if ord(c) > 127)
        if 1 <= emoji_count <= 3:
            score += 1

        return min(score, 6)

    def _assess_author_influence(self, item: dict) -> float:
        """Assess author influence score"""
        followers = item.get("user_followers_count", 0)
        verified = item.get("user_verified", False)

        score = 0

        # Follower count
        if followers > 1000000:
            score += 5
        elif followers > 100000:
            score += 3
        elif followers > 10000:
            score += 2
        elif followers > 1000:
            score += 1

        # Verification
        if verified:
            score += 2

        return min(score, 7)

    def _assess_timing_score(self, item: dict) -> float:
        """Assess timing score (when posted)"""
        created_at = item.get("created_at")
        if not created_at:
            return 0

        try:
            if isinstance(created_at, str):
                # Handle Twitter date format: "Mon Jun 30 03:50:16 +0000 2025"
                if " +0000 " in created_at:
                    # Parse Twitter format
                    from dateutil import parser

                    created_at = parser.parse(created_at)
                else:
                    # Try ISO format
                    created_at = datetime.fromisoformat(
                        created_at.replace("Z", "+00:00")
                    )

            hour = created_at.hour

            # Peak crypto trading hours (UTC)
            # 8-16 UTC covers US morning to Asia evening
            if 8 <= hour <= 16:
                return 3
            elif 6 <= hour <= 18:
                return 2
            else:
                return 1

        except Exception:
            return 1

    def generate_intelligent_digest(self, enhanced_items: list[dict]) -> str:
        """Generate intelligent digest with viral predictions and insights"""
        logger.info("Generating intelligent digest...")

        # Filter out non-dict items
        valid_items = [item for item in enhanced_items if isinstance(item, dict)]

        # Sort by viral score
        sorted_items = sorted(
            valid_items, key=lambda x: x.get("viral_score", 0), reverse=True
        )

        # Get top viral items
        top_viral = sorted_items[:10]

        # Group by source
        twitter_items = [
            item for item in valid_items if item.get("source") == "twitter"
        ]
        reddit_items = [item for item in valid_items if item.get("source") == "reddit"]

        # Calculate insights
        insights = self._calculate_market_insights(valid_items)

        digest = f"""# 🚀 Degen Digest - Intelligent Analysis
## 📊 Executive Summary - {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

### 🎯 Key Insights
- **Total Items Analyzed**: {len(enhanced_items)}
- **Viral Items Detected**: {len([x for x in enhanced_items if x.get('viral_score', 0) > 5])}
- **Market Sentiment**: {insights['overall_sentiment']}
- **Trending Topics**: {', '.join(insights['trending_topics'][:5])}
- **High Impact Items**: {len([x for x in enhanced_items if x.get('market_impact') == 'high'])}

### 📈 Viral Predictions
"""

        for i, item in enumerate(top_viral[:5], 1):
            viral_score = item.get("viral_score", 0)
            confidence = item.get("viral_confidence", 0)
            predicted_engagement = item.get("predicted_engagement", 0)

            text = (
                item.get("text", item.get("title", ""))[:80] + "..."
                if len(item.get("text", item.get("title", ""))) > 80
                else item.get("text", item.get("title", ""))
            )

            digest += f"""
#### {i}. 🚀 Viral Score: {viral_score:.1f} (Confidence: {confidence:.1%})
**Content**: {text}
**Predicted Engagement**: {predicted_engagement:,}
**Market Impact**: {item.get('market_impact', 'unknown').title()}
**Trending Score**: {item.get('trending_score', 0):.1f}
**Author Influence**: {item.get('author_influence', 0):.1f}
"""

        digest += f"""
### 🔥 Top Trending Items by Source

#### 🐦 Twitter ({len(twitter_items)} items)
"""

        for i, item in enumerate(
            sorted(twitter_items, key=lambda x: x.get("viral_score", 0), reverse=True)[
                :3
            ],
            1,
        ):
            text = (
                item.get("text", "")[:60] + "..."
                if len(item.get("text", "")) > 60
                else item.get("text", "")
            )
            digest += f"""
{i}. **Viral Score**: {item.get('viral_score', 0):.1f} | {text}
   - Author: @{item.get('user', {}).get('screen_name', 'unknown')}
   - Engagement: {item.get('engagement_score', 0):,}
   - Trend: {item.get('trend_indicators', {}).get('topic_trend', 'general')}
"""

        digest += f"""
#### 🔥 Reddit ({len(reddit_items)} items)
"""

        for i, item in enumerate(
            sorted(reddit_items, key=lambda x: x.get("viral_score", 0), reverse=True)[
                :3
            ],
            1,
        ):
            title = (
                item.get("title", "")[:60] + "..."
                if len(item.get("title", "")) > 60
                else item.get("title", "")
            )
            digest += f"""
{i}. **Viral Score**: {item.get('viral_score', 0):.1f} | {title}
   - Subreddit: r/{item.get('subreddit', 'unknown')}
   - Score: {item.get('score', 0):,}
   - Comments: {item.get('num_comments', 0):,}
"""

        digest += f"""
### 📊 Market Intelligence
- **Bullish Sentiment**: {insights['bullish_percentage']:.1%}
- **Bearish Sentiment**: {insights['bearish_percentage']:.1%}
- **Neutral Sentiment**: {insights['neutral_percentage']:.1%}
- **Average Viral Score**: {insights['avg_viral_score']:.1f}
- **High Quality Content**: {insights['high_quality_count']} items

### 🎯 Actionable Insights
"""

        for insight in insights["actionable_insights"]:
            digest += f"- {insight}\n"

        digest += f"""
---
*Generated by Enhanced Degen Digest AI* 🤖
*ML Models Trained on {len(self.historical_data)} Historical Items*
"""

        return digest

    def _calculate_market_insights(self, items: list[dict]) -> dict:
        """Calculate comprehensive market insights"""
        insights = {
            "overall_sentiment": "neutral",
            "trending_topics": [],
            "bullish_percentage": 0,
            "bearish_percentage": 0,
            "neutral_percentage": 0,
            "avg_viral_score": 0,
            "high_quality_count": 0,
            "actionable_insights": [],
        }

        if not items:
            return insights

        # Filter valid items
        valid_items = [item for item in items if isinstance(item, dict)]

        if not valid_items:
            return insights

        # Calculate sentiment distribution
        sentiments = []
        viral_scores = []
        topics = []
        quality_scores = []

        for item in valid_items:
            # Sentiment
            sentiment = item.get("trend_indicators", {}).get(
                "market_sentiment", "neutral"
            )
            sentiments.append(sentiment)

            # Viral scores
            viral_score = item.get("viral_score", 0)
            viral_scores.append(viral_score)

            # Topics
            topic = item.get("trend_indicators", {}).get("topic_trend", "general")
            topics.append(topic)

            # Quality
            quality = item.get("content_quality", 0)
            quality_scores.append(quality)

        # Calculate percentages
        total = len(sentiments)
        insights["bullish_percentage"] = sentiments.count("bullish") / total
        insights["bearish_percentage"] = sentiments.count("bearish") / total
        insights["neutral_percentage"] = sentiments.count("neutral") / total

        # Overall sentiment
        if insights["bullish_percentage"] > 0.4:
            insights["overall_sentiment"] = "bullish"
        elif insights["bearish_percentage"] > 0.4:
            insights["overall_sentiment"] = "bearish"
        else:
            insights["overall_sentiment"] = "neutral"

        # Trending topics
        topic_counts = {}
        for topic in topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

        insights["trending_topics"] = sorted(
            topic_counts.keys(), key=lambda x: topic_counts[x], reverse=True
        )

        # Average viral score
        insights["avg_viral_score"] = np.mean(viral_scores) if viral_scores else 0

        # High quality content
        insights["high_quality_count"] = sum(
            1 for score in quality_scores if score >= 4
        )

        # Actionable insights
        if insights["bullish_percentage"] > 0.6:
            insights["actionable_insights"].append(
                "Strong bullish sentiment detected - consider long positions"
            )
        elif insights["bearish_percentage"] > 0.6:
            insights["actionable_insights"].append(
                "Strong bearish sentiment detected - consider defensive positions"
            )

        if insights["avg_viral_score"] > 5:
            insights["actionable_insights"].append(
                "High viral potential detected - monitor for breakout opportunities"
            )

        if "defi" in insights["trending_topics"][:3]:
            insights["actionable_insights"].append(
                "DeFi trending - focus on DeFi tokens and protocols"
            )

        if "nft" in insights["trending_topics"][:3]:
            insights["actionable_insights"].append(
                "NFT market active - monitor NFT-related tokens"
            )

        return insights

    def run_full_analysis(self) -> dict:
        """Run complete enhanced analysis pipeline"""
        logger.info("Running enhanced data pipeline...")

        # Fetch latest data
        raw_data = self.fetch_latest_data()

        if not raw_data:
            logger.warning("No data fetched")
            return {"status": "error", "message": "No data available"}

        # Analyze viral potential
        enhanced_data = self.analyze_viral_potential(raw_data)

        # Filter valid items
        valid_items = [item for item in enhanced_data if isinstance(item, dict)]

        # Generate intelligent digest
        digest_content = self.generate_intelligent_digest(valid_items)

        # Save enhanced data
        output_dir = Path("output/enhanced_pipeline")
        output_dir.mkdir(exist_ok=True)

        # Save enhanced data
        enhanced_file = output_dir / "enhanced_data.json"
        with open(enhanced_file, "w") as f:
            json.dump(valid_items, f, indent=2, default=str)

        # Save viral predictions
        viral_file = output_dir / "viral_predictions.json"
        viral_predictions = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "predictions": [
                {
                    "id": item.get("id", item.get("url", "")),
                    "source": item.get("source"),
                    "viral_score": item.get("viral_score", 0),
                    "predicted_engagement": item.get("predicted_engagement", 0),
                    "confidence": item.get("viral_confidence", 0),
                    "market_impact": item.get("market_impact", "low"),
                    "trending_score": item.get("trending_score", 0),
                    "content": item.get("text", item.get("title", ""))[:100],
                }
                for item in sorted(
                    valid_items, key=lambda x: x.get("viral_score", 0), reverse=True
                )[:20]
            ],
        }
        with open(viral_file, "w") as f:
            json.dump(viral_predictions, f, indent=2)

        # Save digest
        digest_file = output_dir / "intelligent_digest.md"
        with open(digest_file, "w") as f:
            f.write(digest_content)

        # Save insights
        insights = self._calculate_market_insights(valid_items)
        insights_file = output_dir / "market_insights.json"
        with open(insights_file, "w") as f:
            json.dump(insights, f, indent=2)

        logger.info(f"Enhanced analysis completed. Processed {len(valid_items)} items.")

        return {
            "status": "success",
            "items_processed": len(valid_items),
            "viral_items": len([x for x in valid_items if x.get("viral_score", 0) > 5]),
            "avg_viral_score": insights["avg_viral_score"],
            "overall_sentiment": insights["overall_sentiment"],
            "digest_content": digest_content,
            "files_saved": [
                str(enhanced_file),
                str(viral_file),
                str(digest_file),
                str(insights_file),
            ],
        }


def main():
    """Main function to run enhanced pipeline"""
    pipeline = EnhancedDataPipeline()
    result = pipeline.run_full_analysis()

    print("🚀 Enhanced Data Pipeline Results:")
    print(f"Status: {result['status']}")
    print(f"Items Processed: {result.get('items_processed', 0)}")
    print(f"Viral Items: {result.get('viral_items', 0)}")
    print(f"Average Viral Score: {result.get('avg_viral_score', 0):.1f}")
    print(f"Overall Sentiment: {result.get('overall_sentiment', 'unknown')}")

    if result.get("digest_content"):
        print("\n📋 DIGEST PREVIEW:")
        print("=" * 50)
        lines = result["digest_content"].split("\n")[:30]
        for line in lines:
            print(line)
        if len(result["digest_content"].split("\n")) > 30:
            print("...")
        print("=" * 50)


if __name__ == "__main__":
    main()
