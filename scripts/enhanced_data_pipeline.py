#!/usr/bin/env python3
"""
Enhanced Data Pipeline for Ultimate Virality Prediction
Comprehensive data collection, processing, and analysis pipeline
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path

import nest_asyncio
import numpy as np

# Apply nest_asyncio for better async handling
nest_asyncio.apply()

from processor.enhanced_viral_predictor import enhanced_predictor
from scrapers.enhanced_twitter_scraper import EnhancedTwitterScraper
from utils.advanced_logging import get_logger

logger = get_logger(__name__)


class EnhancedDataPipeline:
    """Comprehensive data pipeline for virality prediction"""

    def __init__(self):
        self.twitter_scraper = EnhancedTwitterScraper()
        self.data_sources = {}
        self.processed_data = []
        self.viral_predictions = []

        # Pipeline configuration
        self.config = {
            "max_tweets_per_source": 200,  # Reduced for faster processing
            "min_engagement_threshold": 5,  # Lowered threshold
            "update_frequency_minutes": 30,
            "enable_real_time": True,
            "save_intermediate": True,
            "use_existing_data": True,  # Use existing data files
        }

        # Performance tracking
        self.stats = {
            "total_items_processed": 0,
            "viral_items_detected": 0,
            "processing_time": 0,
            "last_update": None,
        }

    async def run_full_pipeline(self):
        """Run the complete enhanced data pipeline"""

        start_time = time.time()
        logger.info("Starting enhanced data pipeline...")

        try:
            # Step 1: Collect data from all sources
            await self.collect_all_data()

            # Step 2: Process and enhance data
            self.process_and_enhance_data()

            # Step 3: Generate viral predictions
            self.generate_viral_predictions()

            # Step 4: Analyze trends and patterns
            self.analyze_trends()

            # Step 5: Save results
            self.save_pipeline_results()

            # Step 6: Update statistics
            self.update_statistics(start_time)

            logger.info("Enhanced data pipeline completed successfully")

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise

    async def collect_all_data(self):
        """Collect data from all sources"""

        logger.info("Collecting data from all sources...")

        # First, try to use existing data files
        if self.config["use_existing_data"]:
            await self.load_existing_data()

        # Then collect fresh data from sources that work
        await self.collect_twitter_data()
        await self.collect_reddit_data()
        await self.collect_telegram_data()
        await self.collect_news_data()
        await self.collect_market_data()

        # Only add Discord if we don't have enough data
        if sum(len(data.get("data", [])) for data in self.data_sources.values()) < 100:
            await self.collect_discord_data()

        logger.info(
            f"Data collection completed. Total sources: {len(self.data_sources)}"
        )

    async def load_existing_data(self):
        """Load existing data from files"""

        logger.info("Loading existing data files...")

        # Load Twitter data
        twitter_file = Path("output/twitter_raw.json")
        if twitter_file.exists():
            try:
                with open(twitter_file) as f:
                    twitter_data = json.load(f)

                # Convert to enhanced format
                enhanced_twitter = self.enhance_twitter_data(
                    twitter_data[:100]
                )  # Limit to 100 items

                self.data_sources["twitter"] = {
                    "data": enhanced_twitter,
                    "count": len(enhanced_twitter),
                    "timestamp": datetime.utcnow().isoformat(),
                    "source": "existing_file",
                }

                logger.info(
                    f"Loaded {len(enhanced_twitter)} Twitter items from existing file"
                )

            except Exception as e:
                logger.error(f"Failed to load Twitter data: {e}")

        # Load Reddit data
        reddit_file = Path("output/reddit_raw.json")
        if reddit_file.exists():
            try:
                with open(reddit_file) as f:
                    reddit_data = json.load(f)

                # Convert to enhanced format
                enhanced_reddit = self.enhance_reddit_data(
                    reddit_data[:50]
                )  # Limit to 50 items

                self.data_sources["reddit"] = {
                    "data": enhanced_reddit,
                    "count": len(enhanced_reddit),
                    "timestamp": datetime.utcnow().isoformat(),
                    "source": "existing_file",
                }

                logger.info(
                    f"Loaded {len(enhanced_reddit)} Reddit items from existing file"
                )

            except Exception as e:
                logger.error(f"Failed to load Reddit data: {e}")

        # Load Telegram data
        telegram_file = Path("output/telegram_raw.json")
        if telegram_file.exists():
            try:
                with open(telegram_file) as f:
                    telegram_data = json.load(f)

                # Convert to enhanced format
                enhanced_telegram = self.enhance_telegram_data(
                    telegram_data[:50]
                )  # Limit to 50 items

                self.data_sources["telegram"] = {
                    "data": enhanced_telegram,
                    "count": len(enhanced_telegram),
                    "timestamp": datetime.utcnow().isoformat(),
                    "source": "existing_file",
                }

                logger.info(
                    f"Loaded {len(enhanced_telegram)} Telegram items from existing file"
                )

            except Exception as e:
                logger.error(f"Failed to load Telegram data: {e}")

    def enhance_twitter_data(self, twitter_data: list[dict]) -> list[dict]:
        """Enhance Twitter data with virality features"""

        enhanced_data = []

        for tweet in twitter_data:
            try:
                # Extract basic metrics
                likes = tweet.get("likeCount", 0)
                retweets = tweet.get("retweetCount", 0)
                replies = tweet.get("replyCount", 0)
                quotes = tweet.get("quoteCount", 0)

                # Calculate engagement velocity (simplified)
                engagement_velocity = (
                    likes + retweets * 2 + replies * 3 + quotes * 2
                ) / 10

                # Calculate viral coefficient
                followers = tweet.get("user", {}).get("followersCount", 1000)
                viral_coefficient = (retweets + quotes) / max(followers, 1)

                # Calculate influence score
                influence_score = engagement_velocity * np.log10(followers + 1)

                # Enhanced tweet
                enhanced_tweet = {
                    "id": tweet.get("id", f"twitter_{len(enhanced_data)}"),
                    "text": tweet.get("text", ""),
                    "author": tweet.get("user", {}).get("username", "unknown"),
                    "timestamp": tweet.get("date", datetime.utcnow().isoformat()),
                    "likes": likes,
                    "retweets": retweets,
                    "replies": replies,
                    "quotes": quotes,
                    "followers": followers,
                    "engagement_velocity": engagement_velocity,
                    "viral_coefficient": viral_coefficient,
                    "influence_score": influence_score,
                    "source": "twitter",
                    "enhanced_at": datetime.utcnow().isoformat(),
                }

                enhanced_data.append(enhanced_tweet)

            except Exception as e:
                logger.error(f"Failed to enhance Twitter tweet: {e}")
                continue

        return enhanced_data

    async def collect_twitter_data(self):
        """Collect enhanced Twitter data"""

        # Skip if we already have Twitter data
        if "twitter" in self.data_sources:
            logger.info("Twitter data already loaded from existing file")
            return

        logger.info("Collecting enhanced Twitter data...")

        try:
            # Load configuration
            from config.influencers import get_influencers
            from config.keywords import get_keywords

            influencers = get_influencers()
            keywords = get_keywords()

            # Collect enhanced tweets
            enhanced_tweets = await self.twitter_scraper.scrape_enhanced_tweets(
                accounts=influencers[:20],  # Reduced for faster processing
                search_terms=keywords["twitter_search"][:10],  # Reduced keywords
                max_tweets=self.config["max_tweets_per_source"],
                min_likes=self.config["min_engagement_threshold"],
                min_retweets=2,  # Lowered threshold
            )

            # Save enhanced data
            self.twitter_scraper.save_enhanced_data(enhanced_tweets)

            # Store in pipeline
            self.data_sources["twitter"] = {
                "data": enhanced_tweets,
                "count": len(enhanced_tweets),
                "timestamp": datetime.utcnow().isoformat(),
            }

            logger.info(f"Collected {len(enhanced_tweets)} enhanced tweets")

        except Exception as e:
            logger.error(f"Twitter data collection failed: {e}")
            self.data_sources["twitter"] = {"data": [], "count": 0, "error": str(e)}

    async def collect_reddit_data(self):
        """Collect enhanced Reddit data"""

        # Skip if we already have Reddit data
        if "reddit" in self.data_sources:
            logger.info("Reddit data already loaded from existing file")
            return

        logger.info("Collecting Reddit data...")

        try:
            # Use existing Reddit scraper with improved async handling
            from scrapers.reddit_rss import main as reddit_scraper

            # Run Reddit scraper in a separate event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                reddit_data = reddit_scraper()
            finally:
                loop.close()

            # Enhance Reddit data with virality features
            enhanced_reddit = self.enhance_reddit_data(reddit_data)

            self.data_sources["reddit"] = {
                "data": enhanced_reddit,
                "count": len(enhanced_reddit),
                "timestamp": datetime.utcnow().isoformat(),
            }

            logger.info(f"Collected {len(enhanced_reddit)} Reddit posts")

        except Exception as e:
            logger.error(f"Reddit data collection failed: {e}")
            self.data_sources["reddit"] = {"data": [], "count": 0, "error": str(e)}

    def enhance_reddit_data(self, reddit_data: list[dict]) -> list[dict]:
        """Enhance Reddit data with virality features"""

        enhanced_data = []

        for post in reddit_data:
            try:
                # Calculate engagement velocity
                created_at = datetime.fromisoformat(
                    post.get("published", "").replace("Z", "+00:00")
                )
                hours_since_creation = (
                    datetime.utcnow() - created_at
                ).total_seconds() / 3600

                score = post.get("score", 0)
                comments = post.get("numComments", 0)

                engagement_velocity = (score + comments * 2) / max(
                    hours_since_creation, 1
                )

                # Calculate viral coefficient
                viral_coefficient = comments / max(score, 1)

                # Enhanced features
                enhanced_post = {
                    "id": post.get("id", f"reddit_{len(enhanced_data)}"),
                    "text": post.get("title", "") + " " + post.get("summary", ""),
                    "title": post.get("title", ""),
                    "author": post.get("author", "unknown"),
                    "timestamp": post.get("published", datetime.utcnow().isoformat()),
                    "score": score,
                    "comments": comments,
                    "engagement_velocity": engagement_velocity,
                    "viral_coefficient": viral_coefficient,
                    "influence_score": score * np.log10(comments + 1),
                    "source": "reddit",
                    "enhanced_at": datetime.utcnow().isoformat(),
                }

                enhanced_data.append(enhanced_post)

            except Exception as e:
                logger.error(f"Failed to enhance Reddit post: {e}")
                continue

        return enhanced_data

    async def collect_telegram_data(self):
        """Collect Telegram data"""

        # Skip if we already have Telegram data
        if "telegram" in self.data_sources:
            logger.info("Telegram data already loaded from existing file")
            return

        logger.info("Collecting Telegram data...")

        try:
            # Use existing Telegram scraper
            from scrapers.telegram_telethon import main as telegram_scraper

            # Run Telegram scraper
            telegram_data = telegram_scraper()

            # Enhance Telegram data
            enhanced_telegram = self.enhance_telegram_data(telegram_data)

            self.data_sources["telegram"] = {
                "data": enhanced_telegram,
                "count": len(enhanced_telegram),
                "timestamp": datetime.utcnow().isoformat(),
            }

            logger.info(f"Collected {len(enhanced_telegram)} Telegram messages")

        except Exception as e:
            logger.error(f"Telegram data collection failed: {e}")
            self.data_sources["telegram"] = {"data": [], "count": 0, "error": str(e)}

    def enhance_telegram_data(self, telegram_data: list[dict]) -> list[dict]:
        """Enhance Telegram data with virality features"""

        enhanced_data = []

        for message in telegram_data:
            try:
                # Basic enhancement for Telegram
                enhanced_message = {
                    "id": message.get("id", f"telegram_{len(enhanced_data)}"),
                    "text": message.get("text", ""),
                    "author": message.get("sender", "unknown"),
                    "timestamp": message.get("date", datetime.utcnow().isoformat()),
                    "engagement_velocity": 0,  # Telegram doesn't have public engagement metrics
                    "viral_coefficient": 0,
                    "influence_score": 0,
                    "source": "telegram",
                    "enhanced_at": datetime.utcnow().isoformat(),
                }

                enhanced_data.append(enhanced_message)

            except Exception as e:
                logger.error(f"Failed to enhance Telegram message: {e}")
                continue

        return enhanced_data

    async def collect_news_data(self):
        """Collect news data"""

        logger.info("Collecting news data...")

        try:
            # Use existing NewsAPI scraper
            from scrapers.newsapi_headlines import main as news_scraper

            # Run news scraper
            news_data = news_scraper()

            # Enhance news data
            enhanced_news = self.enhance_news_data(news_data)

            self.data_sources["news"] = {
                "data": enhanced_news,
                "count": len(enhanced_news),
                "timestamp": datetime.utcnow().isoformat(),
            }

            logger.info(f"Collected {len(enhanced_news)} news articles")

        except Exception as e:
            logger.error(f"News data collection failed: {e}")
            self.data_sources["news"] = {"data": [], "count": 0, "error": str(e)}

    def enhance_news_data(self, news_data: list[dict]) -> list[dict]:
        """Enhance news data with virality features"""

        enhanced_data = []

        for article in news_data:
            try:
                # News articles don't have engagement metrics, but we can analyze content
                enhanced_article = {
                    "id": article.get("id", f"news_{len(enhanced_data)}"),
                    "text": article.get("title", "")
                    + " "
                    + article.get("description", ""),
                    "title": article.get("title", ""),
                    "author": article.get("author", "unknown"),
                    "timestamp": article.get(
                        "publishedAt", datetime.utcnow().isoformat()
                    ),
                    "engagement_velocity": 0,
                    "viral_coefficient": 0,
                    "influence_score": 0,
                    "source": "news",
                    "enhanced_at": datetime.utcnow().isoformat(),
                }

                enhanced_data.append(enhanced_article)

            except Exception as e:
                logger.error(f"Failed to enhance news article: {e}")
                continue

        return enhanced_data

    async def collect_market_data(self):
        """Collect market data"""

        logger.info("Collecting market data...")

        try:
            # Use existing CoinGecko scraper
            from scrapers.coingecko_gainers import main as market_scraper

            # Run market scraper
            market_data = market_scraper()

            # Enhance market data
            enhanced_market = self.enhance_market_data(market_data)

            self.data_sources["market"] = {
                "data": enhanced_market,
                "count": len(enhanced_market),
                "timestamp": datetime.utcnow().isoformat(),
            }

            logger.info(f"Collected {len(enhanced_market)} market data points")

        except Exception as e:
            logger.error(f"Market data collection failed: {e}")
            self.data_sources["market"] = {"data": [], "count": 0, "error": str(e)}

    def enhance_market_data(self, market_data: list[dict]) -> list[dict]:
        """Enhance market data with virality features"""

        enhanced_data = []

        for coin in market_data:
            try:
                # Calculate market-based virality indicators
                price_change = coin.get("price_change_percentage_24h", 0)
                volume_change = coin.get("volume_change_percentage_24h", 0)

                # Market virality score based on price and volume changes
                market_virality = abs(price_change) * 0.7 + abs(volume_change) * 0.3

                enhanced_coin = {
                    "id": coin.get("id", f"market_{len(enhanced_data)}"),
                    "text": f"{coin.get('name', 'Unknown')} price change: {price_change:.2f}%",
                    "name": coin.get("name", "Unknown"),
                    "symbol": coin.get("symbol", "UNKNOWN"),
                    "price_change": price_change,
                    "volume_change": volume_change,
                    "engagement_velocity": market_virality,
                    "viral_coefficient": market_virality / 100,  # Normalize
                    "influence_score": market_virality,
                    "source": "market",
                    "enhanced_at": datetime.utcnow().isoformat(),
                }

                enhanced_data.append(enhanced_coin)

            except Exception as e:
                logger.error(f"Failed to enhance market data: {e}")
                continue

        return enhanced_data

    async def collect_discord_data(self):
        """Collect Discord data (new source)"""

        logger.info("Collecting Discord data...")

        try:
            # Use new Discord scraper
            from scrapers.discord_scraper import DiscordScraper

            async with DiscordScraper() as scraper:
                discord_data = await scraper.scrape_discord_channels(
                    max_messages=20
                )  # Reduced for speed
                enhanced_discord = scraper.enhance_discord_data(discord_data)

            self.data_sources["discord"] = {
                "data": enhanced_discord,
                "count": len(enhanced_discord),
                "timestamp": datetime.utcnow().isoformat(),
            }

            logger.info(f"Collected {len(enhanced_discord)} Discord messages")

        except Exception as e:
            logger.error(f"Discord data collection failed: {e}")
            self.data_sources["discord"] = {"data": [], "count": 0, "error": str(e)}

    def process_and_enhance_data(self):
        """Process and enhance all collected data"""

        logger.info("Processing and enhancing data...")

        all_data = []

        # Combine all data sources
        for _source_name, source_data in self.data_sources.items():
            if "data" in source_data and source_data["data"]:
                all_data.extend(source_data["data"])

        # Apply additional processing
        processed_data = []

        for item in all_data:
            try:
                # Add processing timestamp
                item["processed_at"] = datetime.utcnow().isoformat()

                # Add data quality score
                item["data_quality_score"] = self.calculate_data_quality(item)

                # Add content categorization
                item["content_category"] = self.categorize_content(item)

                processed_data.append(item)

            except Exception as e:
                logger.error(f"Failed to process item: {e}")
                continue

        self.processed_data = processed_data
        logger.info(f"Processed {len(processed_data)} items")

    def calculate_data_quality(self, item: dict) -> float:
        """Calculate data quality score"""

        score = 0.0

        # Check for required fields
        required_fields = ["text", "timestamp", "source"]
        for field in required_fields:
            if item.get(field):
                score += 0.2

        # Check for engagement metrics
        if item.get("engagement_velocity", 0) > 0:
            score += 0.2

        if item.get("viral_coefficient", 0) > 0:
            score += 0.2

        # Check for temporal data
        if item.get("timestamp") or item.get("published"):
            score += 0.2

        # Check for source information
        if item.get("source"):
            score += 0.2

        return min(score, 1.0)

    def categorize_content(self, item: dict) -> str:
        """Categorize content based on text and metadata"""

        text = (
            f"{item.get('text', '')} {item.get('title', '')} {item.get('summary', '')}"
        )
        text_lower = text.lower()

        # Define categories and keywords
        categories = {
            "bitcoin": ["bitcoin", "btc", "$btc"],
            "ethereum": ["ethereum", "eth", "$eth"],
            "defi": ["defi", "yield", "apy", "liquidity", "swap"],
            "nft": ["nft", "opensea", "floor", "mint"],
            "meme": ["meme", "dog", "cat", "pepe"],
            "airdrop": ["airdrop", "claim", "free"],
            "scam": ["rug", "scam", "honeypot"],
            "pump": ["pump", "moon", "bull"],
            "trading": ["trade", "chart", "technical", "analysis"],
            "news": ["news", "announcement", "update"],
        }

        # Find matching category
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category

        return "general"

    def generate_viral_predictions(self):
        """Generate viral predictions for all processed data"""

        logger.info("Generating viral predictions...")

        # Check if model is trained
        if not enhanced_predictor.is_trained:
            logger.warning("Viral prediction model not trained. Training now...")
            self.train_viral_model()

        predictions = []

        for item in self.processed_data:
            try:
                # Generate prediction
                prediction = enhanced_predictor.predict_viral_score(item)

                # Add prediction to item
                item["viral_prediction"] = prediction

                # Add to predictions list
                predictions.append(
                    {
                        "item_id": item.get("id", "unknown"),
                        "source": item.get("source", "unknown"),
                        "prediction": prediction,
                        "content_preview": item.get("text", "")[:100] + "..."
                        if item.get("text")
                        else "",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

            except Exception as e:
                logger.error(f"Failed to predict virality for item: {e}")
                continue

        self.viral_predictions = predictions
        logger.info(f"Generated {len(predictions)} viral predictions")

    def train_viral_model(self):
        """Train the viral prediction model"""

        logger.info("Training viral prediction model...")

        # Use processed data for training
        if len(self.processed_data) < 20:  # Lowered threshold
            logger.warning("Insufficient data for training. Need at least 20 items.")
            return

        # Add engagement scores for training
        for item in self.processed_data:
            item["_engagement_score"] = item.get("engagement_velocity", 0)

        # Train the model
        enhanced_predictor.train(self.processed_data)

        logger.info("Viral prediction model trained successfully")

    def analyze_trends(self):
        """Analyze trends and patterns in the data"""

        logger.info("Analyzing trends and patterns...")

        # Group by source
        source_analysis = {}
        for item in self.processed_data:
            source = item.get("source", "unknown")
            if source not in source_analysis:
                source_analysis[source] = []
            source_analysis[source].append(item)

        # Analyze each source
        trends = {}
        for source, items in source_analysis.items():
            if items:
                trends[source] = {
                    "total_items": len(items),
                    "avg_engagement_velocity": np.mean(
                        [i.get("engagement_velocity", 0) for i in items]
                    ),
                    "avg_viral_coefficient": np.mean(
                        [i.get("viral_coefficient", 0) for i in items]
                    ),
                    "top_categories": self.get_top_categories(items),
                    "viral_items": len(
                        [
                            i
                            for i in items
                            if i.get("viral_prediction", {}).get("score", 0) > 0.5
                        ]
                    ),
                }

        self.trends = trends
        logger.info(f"Analyzed trends for {len(trends)} sources")

    def get_top_categories(self, items: list[dict], top_n: int = 5) -> list[dict]:
        """Get top categories from items"""

        category_counts = {}
        for item in items:
            category = item.get("content_category", "unknown")
            category_counts[category] = category_counts.get(category, 0) + 1

        # Sort by count
        sorted_categories = sorted(
            category_counts.items(), key=lambda x: x[1], reverse=True
        )

        return [
            {"category": cat, "count": count}
            for cat, count in sorted_categories[:top_n]
        ]

    def save_pipeline_results(self):
        """Save all pipeline results"""

        logger.info("Saving pipeline results...")

        # Create output directory
        output_dir = Path("output/enhanced_pipeline")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save processed data
        processed_file = output_dir / "processed_data.json"
        with open(processed_file, "w") as f:
            json.dump(self.processed_data, f, indent=2, default=str)

        # Save viral predictions
        predictions_file = output_dir / "viral_predictions.json"
        with open(predictions_file, "w") as f:
            json.dump(self.viral_predictions, f, indent=2, default=str)

        # Save trends analysis
        trends_file = output_dir / "trends_analysis.json"
        with open(trends_file, "w") as f:
            json.dump(self.trends, f, indent=2, default=str)

        # Save pipeline statistics
        stats_file = output_dir / "pipeline_stats.json"
        with open(stats_file, "w") as f:
            json.dump(self.stats, f, indent=2, default=str)

        # Save summary report
        self.generate_summary_report(output_dir)

        logger.info(f"Pipeline results saved to {output_dir}")

    def generate_summary_report(self, output_dir: Path):
        """Generate a summary report"""

        report = {
            "pipeline_run": {
                "timestamp": datetime.utcnow().isoformat(),
                "total_items_processed": self.stats["total_items_processed"],
                "viral_items_detected": self.stats["viral_items_detected"],
                "processing_time": self.stats["processing_time"],
                "data_sources": len(self.data_sources),
            },
            "data_sources_summary": {
                source: {
                    "count": data.get("count", 0),
                    "timestamp": data.get("timestamp", "unknown"),
                    "error": data.get("error", None),
                }
                for source, data in self.data_sources.items()
            },
            "viral_predictions_summary": {
                "total_predictions": len(self.viral_predictions),
                "high_viral_score": len(
                    [
                        p
                        for p in self.viral_predictions
                        if p["prediction"]["score"] > 0.7
                    ]
                ),
                "medium_viral_score": len(
                    [
                        p
                        for p in self.viral_predictions
                        if 0.3 < p["prediction"]["score"] <= 0.7
                    ]
                ),
                "low_viral_score": len(
                    [
                        p
                        for p in self.viral_predictions
                        if p["prediction"]["score"] <= 0.3
                    ]
                ),
            },
            "trends_summary": self.trends,
        }

        report_file = output_dir / "summary_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

    def update_statistics(self, start_time: float):
        """Update pipeline statistics"""

        self.stats["total_items_processed"] = len(self.processed_data)
        self.stats["viral_items_detected"] = len(
            [p for p in self.viral_predictions if p["prediction"]["score"] > 0.5]
        )
        self.stats["processing_time"] = time.time() - start_time
        self.stats["last_update"] = datetime.utcnow().isoformat()


async def main():
    """Main function to run the enhanced data pipeline"""

    pipeline = EnhancedDataPipeline()

    try:
        await pipeline.run_full_pipeline()

        # Print summary
        print("\n" + "=" * 50)
        print("ENHANCED DATA PIPELINE SUMMARY")
        print("=" * 50)
        print(f"Total items processed: {pipeline.stats['total_items_processed']}")
        print(f"Viral items detected: {pipeline.stats['viral_items_detected']}")
        print(f"Processing time: {pipeline.stats['processing_time']:.2f} seconds")
        print(f"Data sources: {len(pipeline.data_sources)}")
        print(f"Viral predictions: {len(pipeline.viral_predictions)}")

        # Print top viral items
        if pipeline.viral_predictions:
            print("\nTop Viral Items:")
            sorted_predictions = sorted(
                pipeline.viral_predictions,
                key=lambda x: x["prediction"]["score"],
                reverse=True,
            )[:5]

            for i, pred in enumerate(sorted_predictions, 1):
                print(
                    f"{i}. Score: {pred['prediction']['score']:.3f} | "
                    f"Source: {pred['source']} | "
                    f"Content: {pred['content_preview']}"
                )

        print("\nPipeline completed successfully!")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
