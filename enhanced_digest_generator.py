#!/usr/bin/env python3
"""
Enhanced Digest Generator
Integrates with the new enhanced viral content system for better analysis
"""

import json
import logging
import os
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

# Google Cloud Storage imports
try:
    from google.cloud import storage

    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedDigestGenerator:
    def __init__(
        self,
        project_id: str = "lucky-union-463615-t3",
        bucket_name: str = "degen-digest-data",
    ):
        self.project_id = project_id
        self.bucket_name = bucket_name
        self.gcs_client = None
        self.gcs_bucket = None

        # Initialize GCS if available
        if GCS_AVAILABLE:
            try:
                self.gcs_client = storage.Client(project=project_id)
                self.gcs_bucket = self.gcs_client.bucket(bucket_name)
                logger.info(f"GCS initialized: {bucket_name}")
            except Exception as e:
                logger.error(f"Failed to initialize GCS: {e}")

        # Output directory
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

        # Database path
        self.db_path = self.output_dir / "degen_digest.db"

    def load_enhanced_data(self) -> dict[str, Any]:
        """Load data from enhanced viral content system"""
        data = {"reddit": [], "news": [], "coingecko": [], "twitter": []}

        # Load from GCS first (enhanced system)
        if self.gcs_bucket:
            try:
                # Load enhanced Reddit data
                reddit_blob = self.gcs_bucket.blob("data/reddit_latest.json")
                if reddit_blob.exists():
                    reddit_data = json.loads(reddit_blob.download_as_text())
                    data["reddit"] = reddit_data.get("posts", [])
                    logger.info(
                        f"Loaded {len(data['reddit'])} enhanced Reddit posts from GCS"
                    )

                # Load enhanced News data
                news_blob = self.gcs_bucket.blob("data/news_latest.json")
                if news_blob.exists():
                    news_data = json.loads(news_blob.download_as_text())
                    data["news"] = news_data.get("articles", [])
                    logger.info(
                        f"Loaded {len(data['news'])} enhanced News articles from GCS"
                    )

                # Load enhanced CoinGecko data
                coingecko_blob = self.gcs_bucket.blob("data/coingecko_latest.json")
                if coingecko_blob.exists():
                    coingecko_data = json.loads(coingecko_blob.download_as_text())
                    data["coingecko"] = coingecko_data.get("coins", [])
                    logger.info(
                        f"Loaded {len(data['coingecko'])} enhanced CoinGecko coins from GCS"
                    )

            except Exception as e:
                logger.error(f"Error loading from GCS: {e}")

        # Fallback to local files
        if not data["reddit"] and (self.output_dir / "reddit_raw.json").exists():
            with open(self.output_dir / "reddit_raw.json") as f:
                data["reddit"] = json.load(f)
                logger.info(
                    f"Loaded {len(data['reddit'])} Reddit posts from local file"
                )

        if not data["news"] and (self.output_dir / "newsapi_raw.json").exists():
            with open(self.output_dir / "newsapi_raw.json") as f:
                data["news"] = json.load(f)
                logger.info(f"Loaded {len(data['news'])} News articles from local file")

        if not data["coingecko"] and (self.output_dir / "coingecko_raw.json").exists():
            with open(self.output_dir / "coingecko_raw.json") as f:
                data["coingecko"] = json.load(f)
                logger.info(
                    f"Loaded {len(data['coingecko'])} CoinGecko coins from local file"
                )

        # Load Twitter data
        if (self.output_dir / "twitter_latest.json").exists():
            with open(self.output_dir / "twitter_latest.json") as f:
                twitter_data = json.load(f)
                data["twitter"] = twitter_data.get("tweets", [])
                logger.info(
                    f"Loaded {len(data['twitter'])} Twitter tweets from local file"
                )

        return data

    def analyze_viral_potential(self, item: dict[str, Any]) -> dict[str, Any]:
        """Analyze viral potential of content item"""
        viral_score = 0
        viral_factors = []

        # Check for viral keywords
        viral_keywords = [
            "moon",
            "pump",
            "100x",
            "1000x",
            "gem",
            "next gem",
            "pepe",
            "doge",
            "shib",
            "floki",
            "chad",
            "based",
            "degen",
            "mooning",
            "pumping",
            "fomo",
            "fud",
            "hodl",
            "launchpad",
            "ido",
            "airdrop",
            "presale",
            "fair launch",
            "stealth launch",
            "yield farming",
            "farming",
            "staking",
            "apy",
            "apr",
            "rewards",
            "solana",
            "sol",
            "phantom",
            "bonk",
            "dogwifhat",
            "jupiter",
            "pyth",
            "now",
            "today",
            "live",
            "breaking",
            "urgent",
            "don't miss",
            "last chance",
            "viral",
            "trending",
            "hot",
            "fire",
            "lit",
            "savage",
            "epic",
            "legendary",
        ]

        text = ""
        if "title" in item:
            text += item["title"] + " "
        if "description" in item:
            text += item["description"] + " "
        if "text" in item:
            text += item["text"] + " "

        text_lower = text.lower()

        # Count viral keywords
        keyword_count = sum(1 for keyword in viral_keywords if keyword in text_lower)
        if keyword_count > 0:
            viral_score += keyword_count * 0.1
            viral_factors.append(f"{keyword_count} viral keywords")

        # Check for urgency indicators
        urgency_words = [
            "now",
            "today",
            "live",
            "breaking",
            "urgent",
            "don't miss",
            "last chance",
        ]
        urgency_count = sum(1 for word in urgency_words if word in text_lower)
        if urgency_count > 0:
            viral_score += urgency_count * 0.2
            viral_factors.append(f"{urgency_count} urgency indicators")

        # Check for sentiment
        if "sentiment" in item:
            sentiment = item["sentiment"]
            if sentiment == "positive":
                viral_score += 0.3
                viral_factors.append("positive sentiment")
            elif sentiment == "negative":
                viral_score -= 0.1

        # Check for engagement (if available)
        if "engagement" in item and isinstance(item["engagement"], dict):
            engagement = item["engagement"]
            if "upvotes" in engagement and engagement["upvotes"] > 100:
                viral_score += 0.2
                viral_factors.append("high engagement")

        # Check for price movement (for coins)
        if "price_change_percentage_24h" in item:
            change = item["price_change_percentage_24h"]
            if change > 20:
                viral_score += 0.4
                viral_factors.append("strong price movement")
            elif change > 10:
                viral_score += 0.2
                viral_factors.append("moderate price movement")

        return {
            "viral_score": min(viral_score, 1.0),  # Cap at 1.0
            "viral_factors": viral_factors,
            "viral_level": "high"
            if viral_score > 0.5
            else "medium"
            if viral_score > 0.2
            else "low",
        }

    def categorize_content(self, item: dict[str, Any]) -> str:
        """Categorize content based on keywords and source"""
        text = ""
        if "title" in item:
            text += item["title"] + " "
        if "description" in item:
            text += item["description"] + " "
        if "text" in item:
            text += item["text"] + " "

        text_lower = text.lower()

        # Memecoin category
        memecoin_keywords = [
            "pepe",
            "doge",
            "shib",
            "floki",
            "wojak",
            "bonk",
            "dogwifhat",
            "moon",
            "pump",
            "gem",
        ]
        if any(keyword in text_lower for keyword in memecoin_keywords):
            return "memecoin"

        # DeFi category
        defi_keywords = [
            "defi",
            "yield farming",
            "farming",
            "staking",
            "apy",
            "apr",
            "liquidity",
            "amm",
            "dex",
        ]
        if any(keyword in text_lower for keyword in defi_keywords):
            return "defi"

        # NFT category
        nft_keywords = [
            "nft",
            "non-fungible",
            "opensea",
            "magic eden",
            "tensor",
            "jupiter",
        ]
        if any(keyword in text_lower for keyword in nft_keywords):
            return "nft"

        # Solana category
        solana_keywords = [
            "solana",
            "sol",
            "phantom",
            "solflare",
            "raydium",
            "orca",
            "serum",
            "jupiter",
            "pyth",
        ]
        if any(keyword in text_lower for keyword in solana_keywords):
            return "solana"

        # Launchpad category
        launchpad_keywords = [
            "launchpad",
            "ido",
            "presale",
            "fair launch",
            "stealth launch",
            "whitelist",
        ]
        if any(keyword in text_lower for keyword in launchpad_keywords):
            return "launchpad"

        # Airdrop category
        airdrop_keywords = [
            "airdrop",
            "claim",
            "eligibility",
            "snapshot",
            "free tokens",
        ]
        if any(keyword in text_lower for keyword in airdrop_keywords):
            return "airdrop"

        # Bitcoin/Ethereum category
        bitcoin_keywords = ["bitcoin", "btc", "ethereum", "eth", "crypto", "blockchain"]
        if any(keyword in text_lower for keyword in bitcoin_keywords):
            return "bitcoin_ethereum"

        return "general"

    def generate_enhanced_digest(self) -> dict[str, Any]:
        """Generate enhanced digest with viral content analysis"""
        logger.info("🔄 Generating enhanced digest...")

        # Load data
        data = self.load_enhanced_data()

        # Process and analyze all items
        all_items = []

        # Process Reddit posts
        for post in data["reddit"]:
            viral_analysis = self.analyze_viral_potential(post)
            category = self.categorize_content(post)

            processed_post = {
                "id": post.get("id", f"reddit_{len(all_items)}"),
                "title": post.get("title", ""),
                "description": post.get("description", ""),
                "link": post.get("link", ""),
                "source": "reddit",
                "subreddit": post.get("subreddit", ""),
                "category": category,
                "viral_analysis": viral_analysis,
                "published": post.get("published", datetime.now(UTC).isoformat()),
                "engagement": post.get("engagement", {}),
                "sentiment": post.get("sentiment", "neutral"),
            }
            all_items.append(processed_post)

        # Process News articles
        for article in data["news"]:
            viral_analysis = self.analyze_viral_potential(article)
            category = self.categorize_content(article)

            processed_article = {
                "id": article.get("id", f"news_{len(all_items)}"),
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "link": article.get("url", ""),
                "source": "news",
                "source_name": article.get("source", ""),
                "category": category,
                "viral_analysis": viral_analysis,
                "published": article.get("publishedAt", datetime.now(UTC).isoformat()),
                "sentiment": article.get("sentiment", "neutral"),
            }
            all_items.append(processed_article)

        # Process CoinGecko coins
        for coin in data["coingecko"]:
            viral_analysis = self.analyze_viral_potential(coin)
            category = self.categorize_content(coin)

            processed_coin = {
                "id": coin.get("id", f"coingecko_{len(all_items)}"),
                "name": coin.get("name", ""),
                "symbol": coin.get("symbol", ""),
                "price": coin.get("current_price", 0),
                "market_cap": coin.get("market_cap", 0),
                "price_change_24h": coin.get("price_change_percentage_24h", 0),
                "source": "coingecko",
                "category": category,
                "viral_analysis": viral_analysis,
                "published": coin.get("published", datetime.now(UTC).isoformat()),
            }
            all_items.append(processed_coin)

        # Process Twitter tweets
        for tweet in data["twitter"]:
            viral_analysis = self.analyze_viral_potential(tweet)
            category = self.categorize_content(tweet)

            processed_tweet = {
                "id": tweet.get("id", f"twitter_{len(all_items)}"),
                "text": tweet.get("text", ""),
                "user": tweet.get("username", ""),
                "source": "twitter",
                "category": category,
                "viral_analysis": viral_analysis,
                "published": tweet.get("created_at", datetime.now(UTC).isoformat()),
                "engagement": tweet.get(
                    "engagement", {"likes": 0, "retweets": 0, "replies": 0}
                ),
            }
            all_items.append(processed_tweet)

        # Sort by viral score
        all_items.sort(key=lambda x: x["viral_analysis"]["viral_score"], reverse=True)

        # Generate digest content
        digest_content = self.create_digest_content(all_items)

        # Save digest
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        digest_data = {
            "metadata": {
                "generated_at": datetime.now(UTC).isoformat(),
                "total_items": len(all_items),
                "sources": list({item["source"] for item in all_items}),
                "categories": list({item["category"] for item in all_items}),
                "viral_content_count": len(
                    [
                        item
                        for item in all_items
                        if item["viral_analysis"]["viral_level"] == "high"
                    ]
                ),
                "enhanced_analysis": True,
            },
            "content": digest_content,
            "items": all_items[:100],  # Top 100 items
        }

        # Save to file
        digest_file = self.output_dir / f"enhanced_digest_{timestamp}.json"
        with open(digest_file, "w") as f:
            json.dump(digest_data, f, indent=2, ensure_ascii=False)

        # Save latest
        latest_file = self.output_dir / "enhanced_digest_latest.json"
        with open(latest_file, "w") as f:
            json.dump(digest_data, f, indent=2, ensure_ascii=False)

        # Generate markdown version
        markdown_content = self.generate_markdown_digest(digest_data)
        markdown_file = (
            self.output_dir
            / f"enhanced_digest_{datetime.now().strftime('%Y-%m-%d')}.md"
        )
        with open(markdown_file, "w") as f:
            f.write(markdown_content)

        # Upload to GCS if available
        if self.gcs_bucket:
            try:
                # Upload JSON
                blob = self.gcs_bucket.blob(f"data/enhanced_digest_{timestamp}.json")
                blob.upload_from_string(
                    json.dumps(digest_data, indent=2, ensure_ascii=False)
                )

                # Upload latest
                latest_blob = self.gcs_bucket.blob("data/enhanced_digest_latest.json")
                latest_blob.upload_from_string(
                    json.dumps(digest_data, indent=2, ensure_ascii=False)
                )

                # Upload markdown
                md_blob = self.gcs_bucket.blob(
                    f"data/enhanced_digest_{datetime.now().strftime('%Y-%m-%d')}.md"
                )
                md_blob.upload_from_string(markdown_content)

                logger.info("✅ Enhanced digest uploaded to GCS")
            except Exception as e:
                logger.error(f"Failed to upload to GCS: {e}")

        logger.info(f"✅ Enhanced digest generated: {len(all_items)} items analyzed")
        return digest_data

    def create_digest_content(self, items: list[dict[str, Any]]) -> dict[str, Any]:
        """Create structured digest content"""
        # Group by category
        categories = {}
        for item in items:
            category = item["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(item)

        # Get top viral items
        top_viral = [
            item for item in items if item["viral_analysis"]["viral_level"] == "high"
        ][:10]

        # Get top items by source
        by_source = {}
        for item in items:
            source = item["source"]
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(item)

        return {
            "top_viral": top_viral,
            "by_category": categories,
            "by_source": by_source,
            "summary": {
                "total_items": len(items),
                "viral_items": len(top_viral),
                "categories": list(categories.keys()),
                "sources": list(by_source.keys()),
            },
        }

    def generate_markdown_digest(self, digest_data: dict[str, Any]) -> str:
        """Generate markdown version of digest"""
        metadata = digest_data["metadata"]
        content = digest_data["content"]

        markdown = f"""# 🚀 Enhanced Degen Digest - {datetime.now().strftime('%Y-%m-%d')}

## 📊 Executive Summary
Generated on: {metadata['generated_at']}
Total items analyzed: {metadata['total_items']}
Viral content items: {metadata['viral_content_count']}
Sources: {', '.join(metadata['sources'])}
Categories: {', '.join(metadata['categories'])}

## 🔥 Top Viral Content

"""

        # Add top viral items
        for i, item in enumerate(content["top_viral"][:10], 1):
            viral_score = item["viral_analysis"]["viral_score"]
            viral_factors = ", ".join(item["viral_analysis"]["viral_factors"])

            if item["source"] == "reddit":
                markdown += f"""### {i}. 🚀 {item['title'][:100]}...
- **Viral Score:** {viral_score:.2f}
- **Viral Factors:** {viral_factors}
- **Subreddit:** r/{item['subreddit']}
- **Category:** {item['category']}
- **Link:** {item['link']}

"""
            elif item["source"] == "news":
                markdown += f"""### {i}. 📰 {item['title'][:100]}...
- **Viral Score:** {viral_score:.2f}
- **Viral Factors:** {viral_factors}
- **Source:** {item['source_name']}
- **Category:** {item['category']}
- **Link:** {item['link']}

"""
            elif item["source"] == "coingecko":
                markdown += f"""### {i}. 💰 {item['name']} ({item['symbol']})
- **Viral Score:** {viral_score:.2f}
- **Viral Factors:** {viral_factors}
- **Price:** ${item['price']}
- **24h Change:** {item['price_change_24h']:.2f}%
- **Category:** {item['category']}

"""
            elif item["source"] == "twitter":
                markdown += f"""### {i}. 🐦 {item['text'][:100]}...
- **Viral Score:** {viral_score:.2f}
- **Viral Factors:** {viral_factors}
- **User:** @{item['user']}
- **Category:** {item['category']}

"""

        # Add category breakdown
        markdown += "\n## 📈 Category Breakdown\n\n"
        for category, items in content["by_category"].items():
            if items:
                markdown += f"### {category.title()}: {len(items)} items\n"
                for item in items[:3]:  # Top 3 per category
                    if "title" in item:
                        markdown += f"- {item['title'][:80]}...\n"
                    elif "name" in item:
                        markdown += f"- {item['name']} ({item['symbol']})\n"
                    elif "text" in item:
                        markdown += f"- {item['text'][:80]}...\n"
                markdown += "\n"

        markdown += """
---
*Generated by Enhanced Degen Digest System* 🤖
*Viral Content Analysis Powered by AI* 🧠
"""

        return markdown


def main():
    """Main function"""
    print("🚀 Enhanced Digest Generator")
    print("=" * 50)

    generator = EnhancedDigestGenerator()
    digest_data = generator.generate_enhanced_digest()

    print("✅ Enhanced digest generated successfully!")
    print(f"📊 Total items analyzed: {digest_data['metadata']['total_items']}")
    print(f"🔥 Viral content items: {digest_data['metadata']['viral_content_count']}")
    print("📄 Files saved to output/ directory")
    print("☁️ Data uploaded to Google Cloud Storage")

    return 0


if __name__ == "__main__":
    main()
