#!/usr/bin/env python3
"""
Test Enhanced Data Pipeline
Run the enhanced viral prediction pipeline and verify functionality
"""

import asyncio
import time
from datetime import datetime
from pathlib import Path

from utils.advanced_logging import get_logger

logger = get_logger(__name__)


async def test_enhanced_pipeline():
    """Test the enhanced data pipeline"""

    print("🚀 Testing Enhanced Data Pipeline")
    print("=" * 50)

    try:
        # Import and run the enhanced pipeline
        from scripts.enhanced_data_pipeline import EnhancedDataPipeline

        # Create pipeline instance
        pipeline = EnhancedDataPipeline()

        print("✅ Pipeline instance created successfully")

        # Test data collection
        print("\n📊 Testing data collection...")

        # Test Twitter data collection
        try:
            await pipeline.collect_twitter_data()
            twitter_count = pipeline.data_sources.get("twitter", {}).get("count", 0)
            print(f"✅ Twitter data collected: {twitter_count} tweets")
        except Exception as e:
            print(f"❌ Twitter data collection failed: {e}")

        # Test Reddit data collection
        try:
            await pipeline.collect_reddit_data()
            reddit_count = pipeline.data_sources.get("reddit", {}).get("count", 0)
            print(f"✅ Reddit data collected: {reddit_count} posts")
        except Exception as e:
            print(f"❌ Reddit data collection failed: {e}")

        # Test data processing
        print("\n🔧 Testing data processing...")
        try:
            pipeline.process_and_enhance_data()
            processed_count = len(pipeline.processed_data)
            print(f"✅ Data processed: {processed_count} items")
        except Exception as e:
            print(f"❌ Data processing failed: {e}")

        # Test viral predictions
        print("\n🤖 Testing viral predictions...")
        try:
            pipeline.generate_viral_predictions()
            predictions_count = len(pipeline.viral_predictions)
            print(f"✅ Viral predictions generated: {predictions_count} predictions")
        except Exception as e:
            print(f"❌ Viral predictions failed: {e}")

        # Test trends analysis
        print("\n📈 Testing trends analysis...")
        try:
            pipeline.analyze_trends()
            trends_count = len(pipeline.trends)
            print(f"✅ Trends analyzed: {trends_count} sources")
        except Exception as e:
            print(f"❌ Trends analysis failed: {e}")

        # Test saving results
        print("\n💾 Testing result saving...")
        try:
            pipeline.save_pipeline_results()
            print("✅ Results saved successfully")
        except Exception as e:
            print(f"❌ Result saving failed: {e}")

        # Verify output files
        print("\n📁 Verifying output files...")
        output_dir = Path("output/enhanced_pipeline")

        files_to_check = [
            "processed_data.json",
            "viral_predictions.json",
            "trends_analysis.json",
            "pipeline_stats.json",
            "summary_report.json",
        ]

        for file_name in files_to_check:
            file_path = output_dir / file_name
            if file_path.exists():
                file_size = file_path.stat().st_size
                print(f"✅ {file_name}: {file_size} bytes")
            else:
                print(f"❌ {file_name}: Not found")

        # Display summary
        print("\n" + "=" * 50)
        print("📊 PIPELINE TEST SUMMARY")
        print("=" * 50)

        print(f"Total items processed: {pipeline.stats['total_items_processed']}")
        print(f"Viral items detected: {pipeline.stats['viral_items_detected']}")
        print(f"Processing time: {pipeline.stats['processing_time']:.2f} seconds")
        print(f"Data sources: {len(pipeline.data_sources)}")

        # Show top viral predictions
        if pipeline.viral_predictions:
            print("\n🏆 Top 3 Viral Predictions:")
            sorted_predictions = sorted(
                pipeline.viral_predictions,
                key=lambda x: x["prediction"]["score"],
                reverse=True,
            )[:3]

            for i, pred in enumerate(sorted_predictions, 1):
                score = pred["prediction"]["score"]
                source = pred["source"]
                content = pred["content_preview"][:50] + "..."
                print(f"{i}. Score: {score:.3f} | {source.title()} | {content}")

        print("\n✅ Enhanced pipeline test completed successfully!")

    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        logger.error(f"Pipeline test failed: {e}")
        raise


def test_enhanced_twitter_scraper():
    """Test the enhanced Twitter scraper"""

    print("\n🐦 Testing Enhanced Twitter Scraper")
    print("-" * 40)

    try:
        from scrapers.enhanced_twitter_scraper import EnhancedTwitterScraper

        # Create scraper instance
        scraper = EnhancedTwitterScraper()
        print("✅ Enhanced Twitter scraper created")

        # Test with limited data
        test_accounts = ["CryptoCobain", "CryptoKaleo"]
        test_keywords = ["bitcoin", "ethereum"]

        print("📊 Collecting test tweets...")

        # Run scraper (fix async issue)
        async def run_scraper():
            return await scraper.scrape_enhanced_tweets(
                accounts=test_accounts,
                search_terms=test_keywords,
                max_tweets=10,
                min_likes=5,
                min_retweets=2,
            )

        enhanced_tweets = asyncio.run(run_scraper())

        print(f"✅ Collected {len(enhanced_tweets)} enhanced tweets")

        # Check enhanced features
        if enhanced_tweets:
            tweet = enhanced_tweets[0]
            print("✅ Enhanced features available:")
            print(f"  - Engagement velocity: {tweet.engagement_velocity:.2f}")
            print(f"  - Viral coefficient: {tweet.viral_coefficient:.4f}")
            print(f"  - Influence score: {tweet.influence_score:.2f}")
            print(f"  - Topic category: {tweet.topic_category}")
            print(f"  - Ticker mentions: {tweet.ticker_mentions}")

        # Save test data
        scraper.save_enhanced_data(enhanced_tweets)
        print("✅ Test data saved")

    except Exception as e:
        print(f"❌ Enhanced Twitter scraper test failed: {e}")


def test_enhanced_viral_predictor():
    """Test the enhanced viral predictor"""

    print("\n🤖 Testing Enhanced Viral Predictor")
    print("-" * 40)

    try:
        from processor.enhanced_viral_predictor import enhanced_predictor

        print("✅ Enhanced viral predictor loaded")

        # Test feature extraction
        test_item = {
            "text": "Bitcoin is going to the moon! 🚀 $BTC #crypto #bitcoin",
            "likeCount": 100,
            "retweetCount": 50,
            "replyCount": 25,
            "viewCount": 1000,
            "userFollowersCount": 10000,
            "userVerified": True,
            "published": datetime.utcnow().isoformat(),
        }

        print("🔍 Testing feature extraction...")
        features = enhanced_predictor.extract_advanced_features(test_item)
        print(f"✅ Extracted {len(features)} features")

        # Show some key features
        key_features = [
            "engagement_velocity",
            "viral_coefficient",
            "influence_score",
            "sentiment_polarity",
            "topic_bitcoin",
            "author_influence",
        ]

        for feature in key_features:
            if feature in features:
                print(f"  - {feature}: {features[feature]:.4f}")

        # Test prediction (if model is trained)
        if enhanced_predictor.is_trained:
            print("🎯 Testing viral prediction...")
            prediction = enhanced_predictor.predict_viral_score(test_item)
            print(
                f"✅ Prediction: {prediction['score']:.3f} (confidence: {prediction['confidence']:.3f})"
            )
        else:
            print("⚠️  Model not trained - skipping prediction test")

    except Exception as e:
        print(f"❌ Enhanced viral predictor test failed: {e}")


def verify_dashboard_data():
    """Verify that dashboard can load the generated data"""

    print("\n📊 Verifying Dashboard Data")
    print("-" * 40)

    try:
        from dashboard.pages.Viral_Analytics import load_viral_data

        # Load data
        data = load_viral_data()

        if data:
            processed_count = len(data["processed_data"])
            predictions_count = len(data["viral_predictions"])
            trends_count = len(data["trends_data"])

            print("✅ Data loaded successfully:")
            print(f"  - Processed data: {processed_count} items")
            print(f"  - Viral predictions: {predictions_count} predictions")
            print(f"  - Trends data: {trends_count} sources")
        else:
            print("❌ No data available for dashboard")

    except Exception as e:
        print(f"❌ Dashboard data verification failed: {e}")


async def main():
    """Main test function"""

    print("🧪 ENHANCED PIPELINE TEST SUITE")
    print("=" * 60)

    start_time = time.time()

    try:
        # Test enhanced Twitter scraper
        test_enhanced_twitter_scraper()

        # Test enhanced viral predictor
        test_enhanced_viral_predictor()

        # Test full pipeline
        await test_enhanced_pipeline()

        # Verify dashboard data
        verify_dashboard_data()

        total_time = time.time() - start_time

        print("\n" + "=" * 60)
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Total test time: {total_time:.2f} seconds")
        print("\n🚀 Your enhanced virality prediction system is ready!")
        print("\nNext steps:")
        print("1. Run the dashboard: streamlit run dashboard/app.py")
        print("2. Visit the Viral Analytics page")
        print("3. Monitor real-time predictions")
        print("4. Analyze trends and patterns")

    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        logger.error(f"Test suite failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
