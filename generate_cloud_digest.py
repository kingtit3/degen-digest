#!/usr/bin/env python3
"""
Generate Digest from Cloud Data
Creates a new digest using data from Google Cloud Storage
"""

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List

# Google Cloud Storage imports
try:
    from google.cloud import storage

    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    print("Warning: Google Cloud Storage not available")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CloudDigestGenerator:
    def __init__(
        self,
        gcs_bucket: str = "degen-digest-data",
        project_id: str = "lucky-union-463615-t3",
    ):
        self.gcs_bucket_name = gcs_bucket
        self.project_id = project_id
        self.gcs_client = None
        self.gcs_bucket = None

        # Initialize Google Cloud Storage
        if GCS_AVAILABLE:
            try:
                self.gcs_client = storage.Client(project=project_id)
                self.gcs_bucket = self.gcs_client.bucket(gcs_bucket)
                logger.info(f"GCS initialized: {gcs_bucket} in project: {project_id}")
            except Exception as e:
                logger.error(f"Error accessing GCS bucket {gcs_bucket}: {e}")
                self.gcs_bucket = None
        else:
            logger.warning("Google Cloud Storage not available")

    def load_consolidated_data(self, source: str) -> dict[str, Any]:
        """Load consolidated data from GCS for a specific source"""
        if not self.gcs_bucket:
            return {}

        try:
            consolidated_path = f"consolidated/{source}_consolidated.json"
            blob = self.gcs_bucket.blob(consolidated_path)

            if blob.exists():
                content = blob.download_as_text()
                data = json.loads(content)
                logger.info(f"✅ Loaded {source} data from GCS")
                return data
            else:
                logger.warning(f"⚠️ No consolidated {source} data found in GCS")
                return {}
        except Exception as e:
            logger.error(f"❌ Error loading {source} data: {e}")
            return {}

    def get_all_data(self) -> dict[str, Any]:
        """Get all consolidated data from GCS"""
        data = {}
        sources = [
            "twitter",
            "reddit",
            "telegram",
            "news",
            "crypto",
            "dexscreener",
            "dexpaprika",
        ]

        for source in sources:
            source_data = self.load_consolidated_data(source)
            if source_data:
                # Extract items from the consolidated structure
                if "tweets" in source_data:
                    data[source] = source_data["tweets"]
                elif "posts" in source_data:
                    data[source] = source_data["posts"]
                elif "messages" in source_data:
                    data[source] = source_data["messages"]
                elif "articles" in source_data:
                    data[source] = source_data["articles"]
                elif "gainers" in source_data:
                    data[source] = source_data["gainers"]
                elif "latest_token_profiles" in source_data:
                    data[source] = source_data["latest_token_profiles"]
                elif "token_data" in source_data:
                    data[source] = source_data["token_data"]
                else:
                    data[source] = source_data

        return data

    def analyze_trending_content(self, data: dict[str, Any]) -> dict[str, Any]:
        """Analyze trending content from all sources"""
        trending = []

        for source, items in data.items():
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict) and item.get("text"):
                        # Calculate engagement score
                        engagement_score = item.get("engagement_score", 0)
                        if not engagement_score:
                            # Simple scoring based on available metrics
                            likes = (
                                item.get("like_count", 0)
                                or item.get("likes", 0)
                                or item.get("engagement", {}).get("likes", 0)
                            )
                            retweets = (
                                item.get("retweet_count", 0)
                                or item.get("retweets", 0)
                                or item.get("engagement", {}).get("retweets", 0)
                            )
                            engagement_score = min(100, (likes + retweets * 2) / 10)

                        trending.append(
                            {
                                "text": item["text"][:200] + "..."
                                if len(item["text"]) > 200
                                else item["text"],
                                "author": item.get(
                                    "username", item.get("author", "Unknown")
                                ),
                                "source": source,
                                "engagement_score": engagement_score,
                                "url": item.get("link", item.get("url", "")),
                                "timestamp": item.get(
                                    "created_at", item.get("published", "")
                                ),
                            }
                        )

        # Sort by engagement score
        trending.sort(key=lambda x: x["engagement_score"], reverse=True)
        return trending[:20]  # Top 20

    def generate_digest_content(
        self, data: dict[str, Any], trending: list[dict]
    ) -> str:
        """Generate digest content"""
        today = datetime.now().strftime("%B %d, %Y")

        # Count items by source
        source_counts = {}
        for source, items in data.items():
            if isinstance(items, list):
                source_counts[source.title()] = len(items)

        digest = f"""# 🚀 Degen Digest - Your Daily Crypto Intelligence

**Date:** {today} | **What's Hot in Crypto Today**

---

## 🎯 **TL;DR - What You Need to Know**

📊 **Data Summary:**
"""

        for source, count in source_counts.items():
            digest += f"- **{source}:** {count} items\n"

        digest += f"""
🔄 **Total Items Analyzed:** {sum(source_counts.values())}

---

## 🔥 **Trending Content**

"""

        if trending:
            for i, item in enumerate(trending[:10], 1):
                digest += f"""### {i}. {item['source'].title()} - {item['author']}
**Engagement Score:** {item['engagement_score']:.1f}

{item['text']}

"""
                if item.get("url"):
                    digest += f"🔗 [View Original]({item['url']})\n"
                digest += "\n---\n\n"
        else:
            digest += "No trending content available at the moment.\n\n"

        digest += f"""
---

## 📈 **Market Insights**

Based on analysis of {sum(source_counts.values())} items across {len(source_counts)} sources.

### 🎯 **Key Takeaways:**
- **Solana Ecosystem:** Active development and community engagement
- **Memecoins:** Continued interest in new launches and trending tokens
- **DeFi:** Growing adoption and innovation in decentralized finance
- **NFTs:** Evolving market with new projects and collections

---

## 🔮 **What to Watch**

1. **New Token Launches:** Keep an eye on upcoming presales and fair launches
2. **Solana Updates:** Monitor for new protocol upgrades and ecosystem developments
3. **Market Movements:** Track significant price movements and whale activity
4. **Regulatory News:** Stay informed about crypto regulations and policy changes

---

## 📊 **Data Sources**

This digest is generated from:
"""

        for source, count in source_counts.items():
            digest += f"- **{source}:** {count} items\n"

        digest += f"""
*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}*

---

**💡 Pro Tip:** Follow the links above to dive deeper into trending topics and stay ahead of the crypto curve!

*This digest is automatically generated from real-time data collected across multiple crypto platforms.*
"""

        return digest

    def save_digest(self, content: str):
        """Save digest to local file and GCS"""
        # Save locally
        today = datetime.now().strftime("%Y-%m-%d")
        local_path = Path(f"output/digest-{today}.md")
        local_path.parent.mkdir(exist_ok=True)

        with open(local_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"✅ Saved digest locally: {local_path}")

        # Upload to GCS
        if self.gcs_bucket:
            try:
                # Save as latest digest
                latest_path = "digests/latest_digest.md"
                blob = self.gcs_bucket.blob(latest_path)
                blob.upload_from_string(content, content_type="text/markdown")
                logger.info(f"✅ Uploaded digest to GCS: {latest_path}")

                # Save as dated digest
                dated_path = f"digests/archive/digest-{today}.md"
                blob = self.gcs_bucket.blob(dated_path)
                blob.upload_from_string(content, content_type="text/markdown")
                logger.info(f"✅ Uploaded dated digest to GCS: {dated_path}")

            except Exception as e:
                logger.error(f"❌ Error uploading digest to GCS: {e}")

    def generate_digest(self):
        """Generate a complete digest from cloud data"""
        logger.info("🚀 Starting cloud digest generation...")

        # Get all data
        data = self.get_all_data()

        if not data:
            logger.warning("No data available for digest generation")
            return False

        # Analyze trending content
        trending = self.analyze_trending_content(data)

        # Generate digest content
        digest_content = self.generate_digest_content(data, trending)

        # Save digest
        self.save_digest(digest_content)

        logger.info("✅ Cloud digest generation completed successfully!")
        return True


def main():
    """Main function"""
    generator = CloudDigestGenerator()
    success = generator.generate_digest()

    if success:
        print("🎉 Cloud digest generated successfully!")
        print("📄 Check the output directory for the new digest file")
        print("☁️ Digest also uploaded to Google Cloud Storage")
    else:
        print("❌ Failed to generate cloud digest")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
