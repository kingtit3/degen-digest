#!/usr/bin/env python3
"""
Enhanced Viral Content Consolidator
Processes all data sources and identifies the most viral content for short-form video creation
"""
import heapq
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List

# Add current directory to path
sys.path.append(".")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ViralContentConsolidator:
    """Consolidates data from all sources and identifies viral content opportunities"""

    def __init__(self):
        self.bucket_name = "degen-digest-data"
        self.project_id = "lucky-union-463615-t3"
        self.viral_keywords = self._load_viral_keywords()
        self.content_scores = {}

    def _load_viral_keywords(self) -> dict[str, list[str]]:
        """Load viral keywords by category"""
        return {
            "memecoin": [
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
                "wojak",
                "chad",
                "based",
                "degen",
                "mooning",
                "pumping",
                "fomo",
                "fud",
                "hodl",
                "diamond hands",
                "wen",
                "ser",
                "ngmi",
                "wagmi",
                "gm",
                "gn",
                "gm fam",
                "gm ser",
                "gm king",
                "gm queen",
            ],
            "launchpad": [
                "launchpad",
                "ido",
                "initial dex offering",
                "token launch",
                "presale",
                "fair launch",
                "stealth launch",
                "pinksale",
                "dxsale",
                "bounce",
                "polkastarter",
                "daomaker",
                "trustpad",
                "seedify",
                "gamefi",
                "new token",
                "ico",
                "initial coin offering",
                "whitelist",
                "kyc",
            ],
            "airdrop": [
                "airdrop",
                "free tokens",
                "claim",
                "eligibility",
                "snapshot",
                "whitelist",
                "retroactive",
                "community airdrop",
                "token distribution",
                "free crypto",
                "claim now",
                "don't miss out",
            ],
            "farming": [
                "yield farming",
                "farming",
                "liquidity mining",
                "staking",
                "apy",
                "apr",
                "rewards",
                "harvest",
                "compound",
                "auto compound",
                "vault",
                "strategy",
                "defi farming",
                "liquidity provider",
                "lp",
                "amm",
                "dex farming",
                "impermanent loss",
                "yield optimizer",
            ],
            "solana": [
                "solana",
                "sol",
                "phantom",
                "solflare",
                "raydium",
                "orca",
                "serum",
                "jupiter",
                "pyth",
                "bonk",
                "dogwifhat",
                "samoyedcoin",
                "marinade",
                "jito",
                "tensor",
                "magic eden",
                "saga",
                "firedancer",
                "solana mobile",
                "solana pay",
                "spl",
                "spl token",
            ],
            "urgency": [
                "now",
                "today",
                "live",
                "breaking",
                "urgent",
                "don't miss",
                "last chance",
                "limited time",
                "expires",
                "deadline",
                "hurry",
                "quick",
                "fast",
                "immediate",
                "instant",
                "right now",
            ],
            "viral": [
                "viral",
                "trending",
                "hot",
                "fire",
                "lit",
                "savage",
                "epic",
                "legendary",
                "insane",
                "crazy",
                "wild",
                "amazing",
                "incredible",
                "unbelievable",
                "mind blowing",
                "game changer",
            ],
        }

    def load_data_from_gcs(self) -> dict[str, Any]:
        """Load all data from Google Cloud Storage"""
        try:
            from google.cloud import storage

            client = storage.Client(project=self.project_id)
            bucket = client.bucket(self.bucket_name)

            data_sources = {
                "twitter": "data/twitter_latest.json",
                "reddit": "data/reddit_latest.json",
                "news": "data/news_latest.json",
                "coingecko": "data/coingecko_latest.json",
                "dexscreener": "data/dexscreener_latest.json",
                "dexpaprika": "data/dexpaprika_latest.json",
            }

            all_data = {}

            for source, path in data_sources.items():
                try:
                    blob = bucket.blob(path)
                    if blob.exists():
                        content = blob.download_as_text()
                        data = json.loads(content)
                        all_data[source] = data
                        logger.info(
                            f"✅ Loaded {source}: {self._count_items(data)} items"
                        )
                    else:
                        logger.warning(f"⚠️ No data found for {source}")
                        all_data[source] = {
                            "items": [],
                            "metadata": {"status": "no_data"},
                        }
                except Exception as e:
                    logger.error(f"❌ Error loading {source}: {e}")
                    all_data[source] = {
                        "items": [],
                        "metadata": {"status": "error", "error": str(e)},
                    }

            return all_data

        except Exception as e:
            logger.error(f"❌ Error loading data from GCS: {e}")
            return {}

    def _count_items(self, data: dict[str, Any]) -> int:
        """Count items in data structure"""
        if "posts" in data:
            return len(data["posts"])
        elif "articles" in data:
            return len(data["articles"])
        elif "coins" in data:
            return len(data["coins"])
        elif "tokens" in data:
            return len(data["tokens"])
        elif "tweets" in data:
            return len(data["tweets"])
        else:
            return 0

    def calculate_viral_score(self, item: dict[str, Any], source: str) -> float:
        """Calculate viral score for an item"""
        score = 0.0
        text = ""

        # Extract text content based on source
        if source == "twitter":
            text = item.get("text", "") + " " + item.get("user", {}).get("name", "")
        elif source == "reddit":
            text = item.get("title", "") + " " + item.get("description", "")
        elif source == "news":
            text = item.get("title", "") + " " + item.get("description", "")
        elif source == "coingecko":
            text = item.get("name", "") + " " + str(item.get("symbol", ""))
        elif source == "dexscreener":
            text = item.get("name", "") + " " + str(item.get("symbol", ""))
        elif source == "dexpaprika":
            text = item.get("name", "") + " " + str(item.get("symbol", ""))

        text_lower = text.lower()

        # Base score from viral keywords
        for category, keywords in self.viral_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    if category == "memecoin":
                        score += 10.0
                    elif category == "launchpad":
                        score += 8.0
                    elif category == "airdrop":
                        score += 7.0
                    elif category == "farming":
                        score += 6.0
                    elif category == "solana":
                        score += 5.0
                    elif category == "urgency":
                        score += 4.0
                    elif category == "viral":
                        score += 3.0

        # Source-specific scoring
        if source == "twitter":
            # Twitter engagement metrics
            retweets = item.get("retweet_count", 0)
            likes = item.get("like_count", 0)
            replies = item.get("reply_count", 0)
            score += (retweets * 0.1) + (likes * 0.05) + (replies * 0.15)

            # User influence
            followers = item.get("user", {}).get("followers_count", 0)
            if followers > 100000:
                score += 5.0
            elif followers > 10000:
                score += 3.0
            elif followers > 1000:
                score += 1.0

        elif source == "reddit":
            # Reddit engagement
            upvotes = item.get("engagement", {}).get("upvotes", 0)
            comments = item.get("engagement", {}).get("comments", 0)
            score += (upvotes * 0.01) + (comments * 0.1)

            # Viral potential from metadata
            viral_potential = item.get("viral_potential", {})
            if viral_potential.get("sentiment") == "positive":
                score += 2.0
            if viral_potential.get("urgency") == "high":
                score += 3.0

        elif source == "news":
            # News source credibility
            source_name = item.get("source", "").lower()
            credible_sources = [
                "cointelegraph",
                "coindesk",
                "decrypt",
                "theblock",
                "cryptonews",
            ]
            if any(src in source_name for src in credible_sources):
                score += 2.0

            # Viral potential from metadata
            viral_potential = item.get("viral_potential", {})
            if viral_potential.get("sentiment") == "positive":
                score += 2.0
            if viral_potential.get("urgency") == "high":
                score += 3.0

        elif source == "coingecko":
            # Price momentum
            price_24h = item.get("price_change_percentage_24h", 0)
            if price_24h > 50:
                score += 10.0
            elif price_24h > 20:
                score += 5.0
            elif price_24h > 10:
                score += 2.0

            # Market cap ranking
            market_cap_rank = item.get("market_cap_rank")
            if market_cap_rank and market_cap_rank <= 100:
                score += 3.0
            elif market_cap_rank and market_cap_rank <= 500:
                score += 1.0

            # Trending score
            trending_score = item.get("viral_potential", {}).get("trending_score", 0)
            score += trending_score * 0.1

        elif source in ["dexscreener", "dexpaprika"]:
            # DEX-specific metrics
            price_change = item.get("price_change_24h", 0)
            if price_change > 50:
                score += 8.0
            elif price_change > 20:
                score += 4.0

            # Liquidity
            liquidity = item.get("liquidity", {}).get("usd", 0)
            if liquidity > 100000:
                score += 2.0

        # Time decay (newer content gets higher score)
        try:
            if "published" in item:
                published = datetime.fromisoformat(
                    item["published"].replace("Z", "+00:00")
                )
                hours_old = (
                    datetime.now(published.tzinfo) - published
                ).total_seconds() / 3600
                if hours_old < 1:
                    score += 5.0
                elif hours_old < 6:
                    score += 3.0
                elif hours_old < 24:
                    score += 1.0
        except:
            pass

        return score

    def identify_viral_content(self, all_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Identify the most viral content across all sources"""
        viral_items = []

        for source, data in all_data.items():
            items = []

            # Extract items based on source structure
            if source == "twitter":
                items = data.get("tweets", [])
            elif source == "reddit":
                items = data.get("posts", [])
            elif source == "news":
                items = data.get("articles", [])
            elif source == "coingecko":
                items = data.get("coins", [])
            elif source in ["dexscreener", "dexpaprika"]:
                items = data.get("tokens", [])

            # Calculate viral scores for each item
            for item in items:
                viral_score = self.calculate_viral_score(item, source)
                if viral_score > 5.0:  # Only include items with decent viral potential
                    viral_item = {
                        "source": source,
                        "item": item,
                        "viral_score": viral_score,
                        "category": self._categorize_item(item, source),
                        "processed_at": datetime.now().isoformat(),
                    }
                    viral_items.append(viral_item)

        # Sort by viral score (highest first)
        viral_items.sort(key=lambda x: x["viral_score"], reverse=True)

        return viral_items

    def _categorize_item(self, item: dict[str, Any], source: str) -> str:
        """Categorize item based on content"""
        text = ""

        if source == "twitter":
            text = item.get("text", "")
        elif source == "reddit":
            text = item.get("title", "") + " " + item.get("description", "")
        elif source == "news":
            text = item.get("title", "") + " " + item.get("description", "")
        elif source in ["coingecko", "dexscreener", "dexpaprika"]:
            text = item.get("name", "") + " " + str(item.get("symbol", ""))

        text_lower = text.lower()

        # Check categories in order of priority
        if any(keyword in text_lower for keyword in self.viral_keywords["memecoin"]):
            return "memecoin"
        elif any(keyword in text_lower for keyword in self.viral_keywords["launchpad"]):
            return "launchpad"
        elif any(keyword in text_lower for keyword in self.viral_keywords["airdrop"]):
            return "airdrop"
        elif any(keyword in text_lower for keyword in self.viral_keywords["farming"]):
            return "farming"
        elif any(keyword in text_lower for keyword in self.viral_keywords["solana"]):
            return "solana"
        else:
            return "general"

    def generate_viral_report(
        self, viral_items: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Generate comprehensive viral content report"""
        report = {
            "summary": {
                "total_viral_items": len(viral_items),
                "generated_at": datetime.now().isoformat(),
                "top_sources": {},
                "top_categories": {},
                "viral_score_ranges": {
                    "explosive": 0,  # 50+
                    "high": 0,  # 20-49
                    "medium": 0,  # 10-19
                    "low": 0,  # 5-9
                },
            },
            "top_viral_content": viral_items[:20],  # Top 20 items
            "category_breakdown": {},
            "source_breakdown": {},
            "recommendations": [],
        }

        # Analyze viral items
        for item in viral_items:
            source = item["source"]
            category = item["category"]
            score = item["viral_score"]

            # Update source breakdown
            if source not in report["source_breakdown"]:
                report["source_breakdown"][source] = {
                    "count": 0,
                    "avg_score": 0,
                    "total_score": 0,
                }
            report["source_breakdown"][source]["count"] += 1
            report["source_breakdown"][source]["total_score"] += score

            # Update category breakdown
            if category not in report["category_breakdown"]:
                report["category_breakdown"][category] = {
                    "count": 0,
                    "avg_score": 0,
                    "total_score": 0,
                }
            report["category_breakdown"][category]["count"] += 1
            report["category_breakdown"][category]["total_score"] += score

            # Update score ranges
            if score >= 50:
                report["summary"]["viral_score_ranges"]["explosive"] += 1
            elif score >= 20:
                report["summary"]["viral_score_ranges"]["high"] += 1
            elif score >= 10:
                report["summary"]["viral_score_ranges"]["medium"] += 1
            else:
                report["summary"]["viral_score_ranges"]["low"] += 1

        # Calculate averages
        for source_data in report["source_breakdown"].values():
            source_data["avg_score"] = source_data["total_score"] / source_data["count"]

        for category_data in report["category_breakdown"].values():
            category_data["avg_score"] = (
                category_data["total_score"] / category_data["count"]
            )

        # Generate recommendations
        report["recommendations"] = self._generate_recommendations(viral_items)

        return report

    def _generate_recommendations(self, viral_items: list[dict[str, Any]]) -> list[str]:
        """Generate content recommendations for short-form videos"""
        recommendations = []

        # Analyze top items for patterns
        top_items = viral_items[:10]

        # Count categories in top items
        category_counts = {}
        for item in top_items:
            category = item["category"]
            category_counts[category] = category_counts.get(category, 0) + 1

        # Generate recommendations based on patterns
        if category_counts.get("memecoin", 0) >= 3:
            recommendations.append(
                "🔥 Multiple memecoin opportunities detected - focus on trending memecoins for maximum engagement"
            )

        if category_counts.get("launchpad", 0) >= 2:
            recommendations.append(
                "🚀 Launchpad season is active - cover new token launches and presales"
            )

        if category_counts.get("airdrop", 0) >= 2:
            recommendations.append(
                "🎁 Airdrop opportunities detected - create content about free token claims"
            )

        if category_counts.get("solana", 0) >= 3:
            recommendations.append(
                "⚡ Solana ecosystem is hot - focus on Solana-based projects and tokens"
            )

        # Check for explosive viral content
        explosive_count = sum(1 for item in top_items if item["viral_score"] >= 50)
        if explosive_count >= 2:
            recommendations.append(
                "💥 Explosive viral content detected - prioritize these items for immediate content creation"
            )

        # Check for urgency patterns
        urgent_items = [
            item
            for item in top_items
            if "now" in str(item["item"]).lower()
            or "today" in str(item["item"]).lower()
        ]
        if len(urgent_items) >= 3:
            recommendations.append(
                "⏰ High urgency content detected - create time-sensitive videos for maximum impact"
            )

        return recommendations

    def save_viral_report(self, report: dict[str, Any]) -> bool:
        """Save viral report to GCS"""
        try:
            from google.cloud import storage

            client = storage.Client(project=self.project_id)
            bucket = client.bucket(self.bucket_name)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Save timestamped report
            timestamped_path = f"viral_reports/viral_content_{timestamp}.json"
            blob = bucket.blob(timestamped_path)
            blob.upload_from_string(
                json.dumps(report, indent=2, ensure_ascii=False),
                content_type="application/json",
            )

            # Save latest report
            latest_path = "viral_reports/viral_content_latest.json"
            blob = bucket.blob(latest_path)
            blob.upload_from_string(
                json.dumps(report, indent=2, ensure_ascii=False),
                content_type="application/json",
            )

            logger.info(f"✅ Saved viral report: {timestamped_path} and {latest_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to save viral report: {e}")
            return False

    def run_consolidation(self) -> dict[str, Any]:
        """Run the complete viral content consolidation process"""
        logger.info("🚀 Starting Enhanced Viral Content Consolidation...")

        # Load data from all sources
        all_data = self.load_data_from_gcs()
        if not all_data:
            logger.error("❌ No data loaded from GCS")
            return {"status": "error", "message": "No data available"}

        # Identify viral content
        viral_items = self.identify_viral_content(all_data)
        logger.info(f"✅ Identified {len(viral_items)} viral items")

        # Generate report
        report = self.generate_viral_report(viral_items)
        logger.info(
            f"✅ Generated viral report with {len(report['top_viral_content'])} top items"
        )

        # Save report
        if self.save_viral_report(report):
            logger.info("✅ Viral report saved successfully")
        else:
            logger.error("❌ Failed to save viral report")

        return report


def main():
    """Main function"""
    consolidator = ViralContentConsolidator()
    report = consolidator.run_consolidation()

    # Print summary
    if report.get("status") != "error":
        summary = report["summary"]
        print("\n🎯 VIRAL CONTENT SUMMARY")
        print(f"Total viral items: {summary['total_viral_items']}")
        print(f"Explosive content: {summary['viral_score_ranges']['explosive']}")
        print(f"High viral content: {summary['viral_score_ranges']['high']}")
        print(f"Medium viral content: {summary['viral_score_ranges']['medium']}")

        print("\n📊 TOP CATEGORIES:")
        for category, data in report["category_breakdown"].items():
            print(
                f"  {category}: {data['count']} items (avg score: {data['avg_score']:.1f})"
            )

        print("\n💡 RECOMMENDATIONS:")
        for rec in report["recommendations"]:
            print(f"  • {rec}")

        print("\n🔥 TOP 5 VIRAL ITEMS:")
        for i, item in enumerate(report["top_viral_content"][:5], 1):
            source = item["source"]
            category = item["category"]
            score = item["viral_score"]
            content = item["item"]

            if source == "twitter":
                text = content.get("text", "")[:100] + "..."
            elif source == "reddit":
                text = content.get("title", "")[:100] + "..."
            elif source == "news":
                text = content.get("title", "")[:100] + "..."
            else:
                text = str(content.get("name", ""))[:100] + "..."

            print(f"  {i}. [{source.upper()}] [{category}] (Score: {score:.1f})")
            print(f"     {text}")
            print()


if __name__ == "__main__":
    main()
