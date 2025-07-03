#!/usr/bin/env python3
"""
Run Intelligent Analysis - Get Viral Predictions and Actionable Insights
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def main():
    """Run the enhanced analysis pipeline"""
    print("🚀 Starting Intelligent Analysis...")
    print("=" * 60)

    try:
        # Import and run the enhanced pipeline
        from enhanced_data_pipeline import EnhancedDataPipeline

        print("📊 Loading historical data for ML training...")
        pipeline = EnhancedDataPipeline()

        print("🔍 Running enhanced analysis...")
        result = pipeline.run_full_analysis()

        if result["status"] == "success":
            print("\n✅ ANALYSIS COMPLETED SUCCESSFULLY!")
            print("=" * 60)

            print(f"📈 Items Processed: {result['items_processed']}")
            print(f"🚀 Viral Items Detected: {result['viral_items']}")
            print(f"📊 Average Viral Score: {result['avg_viral_score']:.1f}")
            print(f"📈 Overall Sentiment: {result['overall_sentiment']}")

            print("\n📁 Files Generated:")
            for file_path in result["files_saved"]:
                print(f"   ✅ {file_path}")

            print("\n📋 INTELLIGENT DIGEST PREVIEW:")
            print("=" * 60)

            # Show digest preview
            digest_lines = result["digest_content"].split("\n")
            for i, line in enumerate(digest_lines[:40]):
                print(line)

            if len(digest_lines) > 40:
                print("...")
                print(
                    "(Full digest saved to output/enhanced_pipeline/intelligent_digest.md)"
                )

            print("=" * 60)
            print("🎯 NEXT STEPS:")
            print("1. Check output/enhanced_pipeline/ for detailed analysis")
            print("2. Review viral_predictions.json for top viral items")
            print("3. Read intelligent_digest.md for actionable insights")
            print("4. Use market_insights.json for trading decisions")

        else:
            print(f"❌ Analysis failed: {result.get('message', 'Unknown error')}")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required packages are installed:")
        print("pip install scikit-learn pandas numpy plotly nltk textblob")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
