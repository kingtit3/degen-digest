#!/usr/bin/env python3
"""
Enhanced Twitter Scraper for Ultimate Virality Prediction
Collects comprehensive data including engagement velocity, user influence, and content analysis
"""

import asyncio
import json
import os
import sys
import time
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.advanced_logging import get_logger

load_dotenv()

logger = get_logger(__name__)


@dataclass
class EnhancedTweet:
    """Enhanced tweet data structure with virality features"""

    tweet_id: str
    text: str
    author: str
    author_id: str
    created_at: datetime
    like_count: int
    retweet_count: int
    reply_count: int
    quote_count: int
    view_count: int
    bookmark_count: int

    # Enhanced features
    author_followers: int
    author_following: int
    author_verified: bool
    author_account_age_days: int
    author_tweet_count: int

    # Engagement velocity (calculated)
    engagement_velocity: float  # engagements per hour
    viral_coefficient: float  # (retweets + quotes) / followers
    influence_score: float  # weighted engagement score

    # Content analysis
    hashtag_count: int
    mention_count: int
    url_count: int
    media_count: int
    is_reply: bool
    is_quote: bool
    is_retweet: bool
    thread_length: int

    # Temporal features
    hour_of_day: int
    day_of_week: int
    is_weekend: bool
    market_hours: bool  # during crypto market hours

    # Additional metadata
    language: str
    sentiment_score: float
    topic_category: str
    ticker_mentions: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class EnhancedTwitterScraper:
    """Enhanced Twitter scraper with comprehensive data collection"""

    def __init__(self):
        self.apify_token = os.getenv("APIFY_API_TOKEN")
        self.twitter_bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        self.cache_file = Path("output/enhanced_twitter_cache.json")
        self.cache = self._load_cache()

        # Engagement tracking
        self.engagement_history = defaultdict(list)

        # Rate limiting
        self.request_count = 0
        self.last_request_time = time.time()
        self.rate_limit_delay = 1.0  # seconds between requests

    def _load_cache(self) -> dict:
        """Load cached data"""
        if self.cache_file.exists():
            try:
                return json.loads(self.cache_file.read_text())
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
        return {}

    def _save_cache(self):
        """Save cache to file"""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.cache_file.write_text(json.dumps(self.cache, indent=2, default=str))

    async def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
        self.request_count += 1

    def _calculate_engagement_velocity(self, tweet_data: dict) -> float:
        """Calculate engagement velocity (engagements per hour)"""
        created_at = datetime.fromisoformat(
            tweet_data.get("createdAt", "").replace("Z", "+00:00")
        )
        hours_since_creation = (datetime.utcnow() - created_at).total_seconds() / 3600

        if hours_since_creation < 1:
            hours_since_creation = 1  # minimum 1 hour to avoid division by zero

        total_engagements = (
            tweet_data.get("likeCount", 0)
            + tweet_data.get("retweetCount", 0) * 2
            + tweet_data.get("replyCount", 0) * 3
            + tweet_data.get("quoteCount", 0) * 2
        )

        return total_engagements / hours_since_creation

    def _calculate_viral_coefficient(self, tweet_data: dict) -> float:
        """Calculate viral coefficient"""
        followers = tweet_data.get("userFollowersCount", 1)
        if followers == 0:
            followers = 1

        viral_actions = tweet_data.get("retweetCount", 0) + tweet_data.get(
            "quoteCount", 0
        )
        return viral_actions / followers

    def _calculate_influence_score(self, tweet_data: dict) -> float:
        """Calculate weighted influence score"""
        # Weighted engagement score
        engagement_score = (
            tweet_data.get("likeCount", 0) * 1
            + tweet_data.get("retweetCount", 0) * 3
            + tweet_data.get("replyCount", 0) * 2
            + tweet_data.get("quoteCount", 0) * 3
            + tweet_data.get("viewCount", 0) * 0.1
        )

        # Author influence factor
        tweet_data.get("userFollowersCount", 0)
        author_verified = 1 if tweet_data.get("userVerified", False) else 0.5

        # Content quality factor
        text_length = len(tweet_data.get("text", ""))
        hashtag_count = len(
            [w for w in tweet_data.get("text", "").split() if w.startswith("#")]
        )
        url_count = len([w for w in tweet_data.get("text", "").split() if "http" in w])

        content_factor = min(
            1.0, (text_length / 280) * (1 + hashtag_count * 0.1) * (1 + url_count * 0.2)
        )

        return engagement_score * author_verified * content_factor

    def _extract_tickers(self, text: str) -> list[str]:
        """Extract crypto tickers from text"""
        import re

        # Common crypto ticker patterns
        ticker_patterns = [
            r"\$[A-Z]{2,10}",  # $BTC, $ETH, etc.
            r"\b[A-Z]{2,10}\s*/\s*[A-Z]{2,10}\b",  # BTC/USD, ETH/BTC
            r"\b[A-Z]{2,10}\s*to\s*[A-Z]{2,10}\b",  # BTC to USD
        ]

        tickers = []
        for pattern in ticker_patterns:
            matches = re.findall(pattern, text.upper())
            tickers.extend(matches)

        return list(set(tickers))

    def _analyze_content(self, text: str) -> dict[str, Any]:
        """Analyze tweet content for virality factors"""
        words = text.split()

        analysis = {
            "hashtag_count": len([w for w in words if w.startswith("#")]),
            "mention_count": len([w for w in words if w.startswith("@")]),
            "url_count": len([w for w in words if "http" in w]),
            "exclamation_count": text.count("!"),
            "question_count": text.count("?"),
            "uppercase_ratio": sum(1 for c in text if c.isupper()) / len(text)
            if text
            else 0,
            "emoji_count": len([c for c in text if ord(c) > 127]),
            "ticker_mentions": self._extract_tickers(text),
            "word_count": len(words),
            "character_count": len(text),
        }

        # Sentiment analysis (basic)
        positive_words = [
            "moon",
            "pump",
            "bull",
            "buy",
            "long",
            "hodl",
            "diamond",
            "rocket",
            "🚀",
            "💎",
        ]
        negative_words = [
            "dump",
            "bear",
            "sell",
            "short",
            "rug",
            "scam",
            "dead",
            "💀",
            "📉",
        ]

        positive_count = sum(1 for word in words if word.lower() in positive_words)
        negative_count = sum(1 for word in words if word.lower() in negative_words)

        analysis["sentiment_score"] = (positive_count - negative_count) / max(
            len(words), 1
        )

        return analysis

    def _is_market_hours(self, dt: datetime) -> bool:
        """Check if datetime is during crypto market hours (24/7 but with peak activity)"""
        # Crypto markets are 24/7, but peak activity is during US/Asia overlap
        hour = dt.hour
        # Peak hours: 8-16 UTC (US morning to Asia evening)
        return 8 <= hour <= 16

    async def scrape_enhanced_tweets(
        self,
        accounts: list[str],
        search_terms: list[str],
        max_tweets: int = 500,
        min_likes: int = 10,
        min_retweets: int = 5,
    ) -> list[EnhancedTweet]:
        """Scrape tweets with enhanced virality features"""

        logger.info(f"Starting enhanced Twitter scrape for {len(accounts)} accounts")

        # Use existing Apify scraper as base
        from scrapers.twitter_apify import run_tweet_scraper

        try:
            raw_tweets = run_tweet_scraper(
                accounts=accounts,
                search_terms=search_terms,
                max_tweets=max_tweets,
                min_likes=min_likes,
                min_retweets=min_retweets,
            )
        except Exception as e:
            logger.error(f"Failed to scrape tweets: {e}")
            return []

        enhanced_tweets = []

        for tweet_data in raw_tweets:
            try:
                # Parse creation time
                created_at = datetime.fromisoformat(
                    tweet_data.get("createdAt", "").replace("Z", "+00:00")
                )

                # Calculate enhanced features
                engagement_velocity = self._calculate_engagement_velocity(tweet_data)
                viral_coefficient = self._calculate_viral_coefficient(tweet_data)
                influence_score = self._calculate_influence_score(tweet_data)

                # Content analysis
                content_analysis = self._analyze_content(tweet_data.get("text", ""))

                # Create enhanced tweet object
                enhanced_tweet = EnhancedTweet(
                    tweet_id=tweet_data.get("id", ""),
                    text=tweet_data.get("text", ""),
                    author=tweet_data.get("userName", ""),
                    author_id=tweet_data.get("userId", ""),
                    created_at=created_at,
                    like_count=tweet_data.get("likeCount", 0),
                    retweet_count=tweet_data.get("retweetCount", 0),
                    reply_count=tweet_data.get("replyCount", 0),
                    quote_count=tweet_data.get("quoteCount", 0),
                    view_count=tweet_data.get("viewCount", 0),
                    bookmark_count=tweet_data.get("bookmarkCount", 0),
                    # Author features
                    author_followers=tweet_data.get("userFollowersCount", 0),
                    author_following=tweet_data.get("userFollowingCount", 0),
                    author_verified=tweet_data.get("userVerified", False),
                    author_account_age_days=tweet_data.get("userAccountAgeDays", 0),
                    author_tweet_count=tweet_data.get("userTweetCount", 0),
                    # Virality features
                    engagement_velocity=engagement_velocity,
                    viral_coefficient=viral_coefficient,
                    influence_score=influence_score,
                    # Content features
                    hashtag_count=content_analysis["hashtag_count"],
                    mention_count=content_analysis["mention_count"],
                    url_count=content_analysis["url_count"],
                    media_count=tweet_data.get("mediaCount", 0),
                    is_reply=tweet_data.get("isReply", False),
                    is_quote=tweet_data.get("isQuote", False),
                    is_retweet=tweet_data.get("isRetweet", False),
                    thread_length=tweet_data.get("threadLength", 1),
                    # Temporal features
                    hour_of_day=created_at.hour,
                    day_of_week=created_at.weekday(),
                    is_weekend=created_at.weekday() >= 5,
                    market_hours=self._is_market_hours(created_at),
                    # Additional features
                    language=tweet_data.get("language", "en"),
                    sentiment_score=content_analysis["sentiment_score"],
                    topic_category=self._categorize_topic(tweet_data.get("text", "")),
                    ticker_mentions=content_analysis["ticker_mentions"],
                )

                enhanced_tweets.append(enhanced_tweet)

            except Exception as e:
                logger.error(
                    f"Failed to process tweet {tweet_data.get('id', 'unknown')}: {e}"
                )
                continue

        logger.info(f"Enhanced {len(enhanced_tweets)} tweets with virality features")
        return enhanced_tweets

    def _categorize_topic(self, text: str) -> str:
        """Categorize tweet topic"""
        text_lower = text.lower()

        if any(word in text_lower for word in ["bitcoin", "btc", "$btc"]):
            return "bitcoin"
        elif any(word in text_lower for word in ["ethereum", "eth", "$eth"]):
            return "ethereum"
        elif any(word in text_lower for word in ["defi", "yield", "apy", "liquidity"]):
            return "defi"
        elif any(word in text_lower for word in ["nft", "opensea", "floor"]):
            return "nft"
        elif any(word in text_lower for word in ["meme", "dog", "cat", "pepe"]):
            return "meme"
        elif any(word in text_lower for word in ["airdrop", "claim", "free"]):
            return "airdrop"
        elif any(word in text_lower for word in ["rug", "scam", "honeypot"]):
            return "scam"
        elif any(word in text_lower for word in ["pump", "moon", "bull"]):
            return "pump"
        else:
            return "general"

    async def track_engagement_velocity(self, tweet_id: str, hours: int = 24):
        """Track engagement velocity over time for a specific tweet"""
        # This would require periodic polling of the same tweet
        # Implementation depends on API access and rate limits
        pass

    def save_enhanced_data(self, tweets: list[EnhancedTweet]):
        """Save enhanced tweet data"""
        output_file = Path("output/enhanced_twitter_data.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict format
        data = [tweet.to_dict() for tweet in tweets]

        # Add metadata
        metadata = {
            "scrape_time": datetime.utcnow().isoformat(),
            "total_tweets": len(tweets),
            "avg_engagement_velocity": sum(t.engagement_velocity for t in tweets)
            / len(tweets)
            if tweets
            else 0,
            "avg_viral_coefficient": sum(t.viral_coefficient for t in tweets)
            / len(tweets)
            if tweets
            else 0,
            "avg_influence_score": sum(t.influence_score for t in tweets) / len(tweets)
            if tweets
            else 0,
        }

        output_data = {"metadata": metadata, "tweets": data}

        output_file.write_text(json.dumps(output_data, indent=2, default=str))
        logger.info(f"Saved enhanced Twitter data to {output_file}")


async def main():
    """Main function for enhanced Twitter scraping"""
    from config.influencers import get_influencers
    from config.keywords import get_keywords

    scraper = EnhancedTwitterScraper()

    # Get configuration
    influencers = get_influencers()
    keywords = get_keywords()

    # Scrape enhanced tweets
    enhanced_tweets = await scraper.scrape_enhanced_tweets(
        accounts=influencers[:20],  # Limit for testing
        search_terms=keywords["twitter_search"],
        max_tweets=200,
        min_likes=10,
        min_retweets=5,
    )

    # Save enhanced data
    scraper.save_enhanced_data(enhanced_tweets)

    # Print summary
    if enhanced_tweets:
        avg_velocity = sum(t.engagement_velocity for t in enhanced_tweets) / len(
            enhanced_tweets
        )
        avg_viral_coef = sum(t.viral_coefficient for t in enhanced_tweets) / len(
            enhanced_tweets
        )
        avg_influence = sum(t.influence_score for t in enhanced_tweets) / len(
            enhanced_tweets
        )

        logger.info("Enhanced Twitter scrape completed:")
        logger.info(f"  - Total tweets: {len(enhanced_tweets)}")
        logger.info(f"  - Avg engagement velocity: {avg_velocity:.2f}")
        logger.info(f"  - Avg viral coefficient: {avg_viral_coef:.4f}")
        logger.info(f"  - Avg influence score: {avg_influence:.2f}")


if __name__ == "__main__":
    asyncio.run(main())
