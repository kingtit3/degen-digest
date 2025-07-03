import re
from collections import Counter

import numpy as np
from sklearn.cluster import DBSCAN, KMeans
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from processor.scorer import extract_tickers
from utils.advanced_logging import get_logger

logger = get_logger(__name__)


class ContentClusterer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=2000,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
        )
        self.cluster_model = None
        self.topic_model = None
        self.clusters = {}
        self.topics = {}

    def preprocess_text(self, items: list[dict]) -> list[str]:
        """Preprocess text for clustering"""
        texts = []
        for item in items:
            if not isinstance(item, dict):
                continue

            # Combine all text fields
            text = f"{item.get('text', '')} {item.get('title', '')} {item.get('summary', '')}"

            # Clean text
            text = re.sub(r"http\S+", "", text)  # Remove URLs
            text = re.sub(r"@\w+", "", text)  # Remove mentions
            text = re.sub(r"#\w+", "", text)  # Remove hashtags
            text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
            text = text.lower().strip()

            if len(text) > 10:  # Only include substantial text
                texts.append(text)
            else:
                texts.append("")

        return texts

    def cluster_content(self, items: list[dict], method: str = "dbscan") -> dict:
        """Cluster content into similar groups"""
        logger.info(f"Clustering {len(items)} items using {method}")

        texts = self.preprocess_text(items)

        if not texts or all(not text for text in texts):
            logger.warning("No valid text for clustering")
            return {}

        # Vectorize text
        try:
            tfidf_matrix = self.vectorizer.fit_transform(texts)
        except ValueError as e:
            logger.error(f"Vectorization failed: {e}")
            return {}

        # Perform clustering
        if method == "dbscan":
            self.cluster_model = DBSCAN(eps=0.3, min_samples=3)
        elif method == "kmeans":
            n_clusters = min(10, len(items) // 5)  # Dynamic cluster count
            self.cluster_model = KMeans(n_clusters=n_clusters, random_state=42)

        cluster_labels = self.cluster_model.fit_predict(tfidf_matrix)

        # Group items by cluster
        clusters = {}
        for i, label in enumerate(cluster_labels):
            if label == -1:  # Noise points in DBSCAN
                continue

            if label not in clusters:
                clusters[label] = []
            clusters[label].append(items[i])

        # Calculate cluster statistics
        cluster_stats = {}
        for label, cluster_items in clusters.items():
            if len(cluster_items) < 2:
                continue

            # Extract common terms
            " ".join(
                [
                    f"{item.get('text', '')} {item.get('title', '')} {item.get('summary', '')}"
                    for item in cluster_items
                ]
            )

            # Find common tickers
            tickers = []
            for item in cluster_items:
                tickers.extend(
                    extract_tickers(f"{item.get('text', '')} {item.get('title', '')}")
                )

            # Calculate engagement stats
            engagement_scores = [
                item.get("_engagement_score", 0) for item in cluster_items
            ]

            cluster_stats[label] = {
                "size": len(cluster_items),
                "avg_engagement": np.mean(engagement_scores),
                "max_engagement": max(engagement_scores),
                "common_tickers": Counter(tickers).most_common(5),
                "sources": Counter(
                    [item.get("_source", "unknown") for item in cluster_items]
                ),
                "items": cluster_items,
            }

        self.clusters = cluster_stats
        logger.info(f"Created {len(cluster_stats)} clusters")
        return cluster_stats

    def extract_topics(self, items: list[dict], n_topics: int = 8) -> dict:
        """Extract latent topics from content"""
        logger.info(f"Extracting {n_topics} topics from {len(items)} items")

        texts = self.preprocess_text(items)

        if not texts or all(not text for text in texts):
            logger.warning("No valid text for topic modeling")
            return {}

        # Vectorize text
        try:
            tfidf_matrix = self.vectorizer.fit_transform(texts)
        except ValueError as e:
            logger.error(f"Vectorization failed: {e}")
            return {}

        # Topic modeling with NMF
        self.topic_model = NMF(n_components=n_topics, random_state=42)
        topic_matrix = self.topic_model.fit_transform(tfidf_matrix)

        # Get feature names (words)
        feature_names = self.vectorizer.get_feature_names_out()

        # Extract top words for each topic
        topics = {}
        for topic_idx, topic in enumerate(self.topic_model.components_):
            top_words_idx = topic.argsort()[-10:][::-1]  # Top 10 words
            top_words = [feature_names[i] for i in top_words_idx]
            topics[topic_idx] = {"words": top_words, "strength": topic.max()}

        # Assign topics to items
        item_topics = {}
        for i, item in enumerate(items):
            if i < len(topic_matrix):
                topic_scores = topic_matrix[i]
                dominant_topic = topic_scores.argmax()
                item_topics[i] = {
                    "topic_id": dominant_topic,
                    "topic_score": topic_scores[dominant_topic],
                    "all_scores": topic_scores.tolist(),
                }

        self.topics = topics
        logger.info(f"Extracted {len(topics)} topics")
        return topics

    def find_similar_content(
        self, target_item: dict, items: list[dict], top_k: int = 5
    ) -> list[tuple[dict, float]]:
        """Find content similar to a target item"""
        if not isinstance(target_item, dict):
            return []

        # Prepare target text
        target_text = f"{target_item.get('text', '')} {target_item.get('title', '')} {target_item.get('summary', '')}"
        target_text = re.sub(r"http\S+", "", target_text)
        target_text = re.sub(r"@\w+", "", target_text)
        target_text = re.sub(r"#\w+", "", target_text)
        target_text = re.sub(r"[^\w\s]", "", target_text)
        target_text = target_text.lower().strip()

        # Prepare all texts
        all_texts = [target_text]
        valid_items = []

        for item in items:
            if not isinstance(item, dict):
                continue
            text = f"{item.get('text', '')} {item.get('title', '')} {item.get('summary', '')}"
            text = re.sub(r"http\S+", "", text)
            text = re.sub(r"@\w+", "", text)
            text = re.sub(r"#\w+", "", text)
            text = re.sub(r"[^\w\s]", "", text)
            text = text.lower().strip()

            if len(text) > 10:
                all_texts.append(text)
                valid_items.append(item)

        if len(all_texts) < 2:
            return []

        # Vectorize
        try:
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
        except ValueError:
            return []

        # Calculate similarities
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])

        # Get top similar items
        similar_indices = similarities[0].argsort()[-top_k:][::-1]
        similar_items = []

        for idx in similar_indices:
            if idx < len(valid_items):
                similarity = similarities[0][idx]
                similar_items.append((valid_items[idx], similarity))

        return similar_items

    def get_cluster_summary(self) -> list[dict]:
        """Get summary of all clusters"""
        summaries = []

        for cluster_id, stats in self.clusters.items():
            summary = {
                "cluster_id": cluster_id,
                "size": stats["size"],
                "avg_engagement": round(stats["avg_engagement"], 2),
                "max_engagement": round(stats["max_engagement"], 2),
                "top_tickers": [ticker for ticker, count in stats["common_tickers"]],
                "top_sources": [
                    source for source, count in stats["sources"].most_common(3)
                ],
                "sample_titles": [
                    item.get("title", item.get("text", ""))[:100]
                    for item in stats["items"][:3]
                ],
            }
            summaries.append(summary)

        return sorted(summaries, key=lambda x: x["avg_engagement"], reverse=True)


# Global instance
clusterer = ContentClusterer()
