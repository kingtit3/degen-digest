#!/usr/bin/env python3
"""
Enhanced Viral Predictor for Ultimate Crypto Virality Detection
Advanced ML models with comprehensive feature engineering and real-time predictions
"""

import warnings
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

from sklearn.decomposition import PCA

# ML Libraries
from sklearn.ensemble import (
    GradientBoostingRegressor,
    RandomForestRegressor,
    VotingRegressor,
)
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.linear_model import Lasso, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler
from sklearn.svm import SVR

# Advanced ML
try:
    import lightgbm as lgb
    import xgboost as xgb

    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("XGBoost not available. Install with: pip install xgboost")

# Text Processing
import re

import emoji
import nltk

# Visualization
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob

from processor.scorer import extract_tickers
from utils.advanced_logging import get_logger

logger = get_logger(__name__)


class EnhancedViralPredictor:
    """Enhanced viral prediction with advanced ML models and feature engineering"""

    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.vectorizers = {}
        self.feature_selectors = {}
        self.is_trained = False
        self.feature_importance = {}
        self.model_performance = {}

        # Initialize NLTK components
        try:
            nltk.download("punkt", quiet=True)
            nltk.download("stopwords", quiet=True)
            nltk.download("wordnet", quiet=True)
            nltk.download("averaged_perceptron_tagger", quiet=True)
        except:
            logger.warning("NLTK components not available")

        self.stop_words = set(stopwords.words("english"))
        self.lemmatizer = WordNetLemmatizer()

        self._initialize_models()

    def _initialize_models(self):
        """Initialize all ML models"""

        # Base models
        self.models["rf"] = RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
        )

        self.models["gb"] = GradientBoostingRegressor(
            n_estimators=200, learning_rate=0.1, max_depth=8, random_state=42
        )

        self.models["ridge"] = Ridge(alpha=1.0)
        self.models["lasso"] = Lasso(alpha=0.1)
        self.models["svr"] = SVR(kernel="rbf", C=1.0, gamma="scale")
        self.models["mlp"] = MLPRegressor(
            hidden_layer_sizes=(100, 50), max_iter=500, random_state=42
        )

        # Advanced models (if available)
        if XGBOOST_AVAILABLE:
            self.models["xgb"] = xgb.XGBRegressor(
                n_estimators=200, learning_rate=0.1, max_depth=8, random_state=42
            )

            self.models["lgb"] = lgb.LGBMRegressor(
                n_estimators=200, learning_rate=0.1, max_depth=8, random_state=42
            )

        # Scalers
        self.scalers["standard"] = StandardScaler()
        self.scalers["minmax"] = MinMaxScaler()
        self.scalers["robust"] = RobustScaler()

        # Vectorizers
        self.vectorizers["tfidf"] = TfidfVectorizer(
            max_features=1000, stop_words="english", ngram_range=(1, 2)
        )

        self.vectorizers["count"] = CountVectorizer(
            max_features=500, stop_words="english", ngram_range=(1, 2)
        )

        # Feature selectors
        self.feature_selectors["kbest"] = SelectKBest(score_func=f_regression, k=50)
        self.feature_selectors["pca"] = PCA(n_components=20)

    def extract_advanced_features(self, item: dict) -> dict:
        """Extract comprehensive features for viral prediction"""

        text = (
            f"{item.get('text', '')} {item.get('title', '')} {item.get('summary', '')}"
        )

        # Basic text features
        features = self._extract_text_features(text)

        # Engagement features
        features.update(self._extract_engagement_features(item))

        # Author features
        features.update(self._extract_author_features(item))

        # Temporal features
        features.update(self._extract_temporal_features(item))

        # Content quality features
        features.update(self._extract_content_quality_features(item))

        # Market context features
        features.update(self._extract_market_context_features(item))

        # Network features
        features.update(self._extract_network_features(item))

        # Sentiment and emotion features
        features.update(self._extract_sentiment_features(text))

        # Topic and category features
        features.update(self._extract_topic_features(text))

        return features

    def _extract_text_features(self, text: str) -> dict:
        """Extract text-based features"""
        words = text.split()

        return {
            "text_length": len(text),
            "word_count": len(words),
            "avg_word_length": np.mean([len(w) for w in words]) if words else 0,
            "hashtag_count": len(re.findall(r"#\w+", text)),
            "mention_count": len(re.findall(r"@\w+", text)),
            "url_count": len(
                re.findall(
                    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
                    text,
                )
            ),
            "emoji_count": len(emoji.emoji_list(text)),
            "exclamation_count": text.count("!"),
            "question_count": text.count("?"),
            "uppercase_ratio": sum(1 for c in text if c.isupper()) / len(text)
            if text
            else 0,
            "digit_count": sum(1 for c in text if c.isdigit()),
            "punctuation_count": sum(1 for c in text if c in ".,;:!?"),
            "unique_words_ratio": len(set(words)) / len(words) if words else 0,
            "ticker_count": len(extract_tickers(text)),
        }

    def _extract_engagement_features(self, item: dict) -> dict:
        """Extract engagement-related features"""

        likes = item.get("likeCount", 0) or item.get("like_count", 0)
        retweets = item.get("retweetCount", 0) or item.get("retweet_count", 0)
        replies = item.get("replyCount", 0) or item.get("reply_count", 0)
        views = item.get("viewCount", 0) or item.get("view_count", 0)

        total_engagement = likes + retweets + replies

        return {
            "initial_likes": likes,
            "initial_retweets": retweets,
            "initial_replies": replies,
            "initial_views": views,
            "total_engagement": total_engagement,
            "engagement_ratio": total_engagement / max(views, 1),
            "retweet_ratio": retweets / max(likes, 1),
            "reply_ratio": replies / max(likes, 1),
            "engagement_velocity": item.get("engagement_velocity", 0),
            "viral_coefficient": item.get("viral_coefficient", 0),
            "influence_score": item.get("influence_score", 0),
        }

    def _extract_author_features(self, item: dict) -> dict:
        """Extract author-related features"""

        followers = item.get("userFollowersCount", 0) or item.get("author_followers", 0)
        following = item.get("userFollowingCount", 0) or item.get("author_following", 0)
        verified = item.get("userVerified", False) or item.get("author_verified", False)
        account_age = item.get("userAccountAgeDays", 0) or item.get(
            "author_account_age_days", 0
        )
        tweet_count = item.get("userTweetCount", 0) or item.get("author_tweet_count", 0)

        return {
            "author_followers": followers,
            "author_following": following,
            "author_verified": 1 if verified else 0,
            "author_account_age_days": account_age,
            "author_tweet_count": tweet_count,
            "author_follower_ratio": followers / max(following, 1),
            "author_engagement_rate": tweet_count / max(account_age, 1),
            "author_influence": np.log10(followers + 1) * (1 if verified else 0.5),
        }

    def _extract_temporal_features(self, item: dict) -> dict:
        """Extract temporal features"""

        published = item.get("published") or item.get("created_at")
        if isinstance(published, str):
            dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
        elif isinstance(published, datetime):
            dt = published
        else:
            dt = datetime.utcnow()

        return {
            "hour_of_day": dt.hour,
            "day_of_week": dt.weekday(),
            "is_weekend": 1 if dt.weekday() >= 5 else 0,
            "is_market_hours": 1 if 8 <= dt.hour <= 16 else 0,
            "is_peak_hours": 1 if 12 <= dt.hour <= 20 else 0,  # US peak hours
            "month": dt.month,
            "day_of_month": dt.day,
            "is_month_start": 1 if dt.day <= 3 else 0,
            "is_month_end": 1 if dt.day >= 28 else 0,
        }

    def _extract_content_quality_features(self, item: dict) -> dict:
        """Extract content quality features"""

        text = (
            f"{item.get('text', '')} {item.get('title', '')} {item.get('summary', '')}"
        )
        media_count = item.get("mediaCount", 0) or item.get("media_count", 0)
        is_reply = item.get("isReply", False) or item.get("is_reply", False)
        is_quote = item.get("isQuote", False) or item.get("is_quote", False)
        is_retweet = item.get("isRetweet", False) or item.get("is_retweet", False)
        thread_length = item.get("threadLength", 1) or item.get("thread_length", 1)

        return {
            "media_count": media_count,
            "is_reply": 1 if is_reply else 0,
            "is_quote": 1 if is_quote else 0,
            "is_retweet": 1 if is_retweet else 0,
            "thread_length": thread_length,
            "has_media": 1 if media_count > 0 else 0,
            "is_original": 1 if not (is_reply or is_quote or is_retweet) else 0,
            "content_complexity": len(set(text.split())) / len(text.split())
            if text.split()
            else 0,
        }

    def _extract_market_context_features(self, item: dict) -> dict:
        """Extract market context features"""

        # These would ideally come from external market data
        # For now, using basic heuristics

        text = (
            f"{item.get('text', '')} {item.get('title', '')} {item.get('summary', '')}"
        )
        text_lower = text.lower()

        return {
            "mentions_bitcoin": 1
            if any(word in text_lower for word in ["bitcoin", "btc", "$btc"])
            else 0,
            "mentions_ethereum": 1
            if any(word in text_lower for word in ["ethereum", "eth", "$eth"])
            else 0,
            "mentions_defi": 1
            if any(word in text_lower for word in ["defi", "yield", "apy"])
            else 0,
            "mentions_nft": 1
            if any(word in text_lower for word in ["nft", "opensea"])
            else 0,
            "mentions_meme": 1
            if any(word in text_lower for word in ["meme", "dog", "cat"])
            else 0,
            "mentions_airdrop": 1
            if any(word in text_lower for word in ["airdrop", "claim"])
            else 0,
            "mentions_scam": 1
            if any(word in text_lower for word in ["rug", "scam", "honeypot"])
            else 0,
            "mentions_pump": 1
            if any(word in text_lower for word in ["pump", "moon", "bull"])
            else 0,
        }

    def _extract_network_features(self, item: dict) -> dict:
        """Extract network-related features"""

        # These would require network analysis
        # For now, using basic metrics

        followers = item.get("userFollowersCount", 0) or item.get("author_followers", 0)
        following = item.get("userFollowingCount", 0) or item.get("author_following", 0)

        return {
            "network_size": followers + following,
            "network_density": following / max(followers, 1),
            "network_centrality": np.log10(followers + 1),
            "network_influence": followers / max(following, 1),
        }

    def _extract_sentiment_features(self, text: str) -> dict:
        """Extract sentiment and emotion features"""

        # Basic sentiment analysis
        blob = TextBlob(text)
        sentiment_polarity = blob.sentiment.polarity
        sentiment_subjectivity = blob.sentiment.subjectivity

        # Crypto-specific sentiment
        crypto_positive = [
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
            "lambo",
        ]
        crypto_negative = [
            "dump",
            "bear",
            "sell",
            "short",
            "rug",
            "scam",
            "dead",
            "💀",
            "📉",
            "rekt",
        ]

        words = text.lower().split()
        crypto_pos_count = sum(1 for word in words if word in crypto_positive)
        crypto_neg_count = sum(1 for word in words if word in crypto_negative)

        return {
            "sentiment_polarity": sentiment_polarity,
            "sentiment_subjectivity": sentiment_subjectivity,
            "crypto_sentiment": (crypto_pos_count - crypto_neg_count)
            / max(len(words), 1),
            "fomo_score": crypto_pos_count / max(len(words), 1),
            "fud_score": crypto_neg_count / max(len(words), 1),
            "sentiment_intensity": abs(sentiment_polarity),
        }

    def _extract_topic_features(self, text: str) -> dict:
        """Extract topic and category features"""

        text_lower = text.lower()

        topics = {
            "topic_bitcoin": 1
            if any(word in text_lower for word in ["bitcoin", "btc", "$btc"])
            else 0,
            "topic_ethereum": 1
            if any(word in text_lower for word in ["ethereum", "eth", "$eth"])
            else 0,
            "topic_defi": 1
            if any(word in text_lower for word in ["defi", "yield", "apy", "liquidity"])
            else 0,
            "topic_nft": 1
            if any(word in text_lower for word in ["nft", "opensea", "floor"])
            else 0,
            "topic_meme": 1
            if any(word in text_lower for word in ["meme", "dog", "cat", "pepe"])
            else 0,
            "topic_airdrop": 1
            if any(word in text_lower for word in ["airdrop", "claim", "free"])
            else 0,
            "topic_scam": 1
            if any(word in text_lower for word in ["rug", "scam", "honeypot"])
            else 0,
            "topic_pump": 1
            if any(word in text_lower for word in ["pump", "moon", "bull"])
            else 0,
            "topic_trading": 1
            if any(
                word in text_lower
                for word in ["trade", "chart", "technical", "analysis"]
            )
            else 0,
            "topic_news": 1
            if any(word in text_lower for word in ["news", "announcement", "update"])
            else 0,
        }

        return topics

    def prepare_training_data(self, items: list[dict]) -> tuple[np.ndarray, np.ndarray]:
        """Prepare training data with advanced features"""

        logger.info("Preparing training data with advanced features...")

        features_list = []
        targets = []

        for item in items:
            if not isinstance(item, dict):
                continue

            try:
                features = self.extract_advanced_features(item)
                features_list.append(features)

                # Target: engagement score or viral coefficient
                target = item.get("_engagement_score", 0) or item.get(
                    "viral_coefficient", 0
                )
                targets.append(target)

            except Exception as e:
                logger.error(f"Failed to process item: {e}")
                continue

        # Convert to DataFrame
        df = pd.DataFrame(features_list)

        # Handle missing values
        df = df.fillna(0)

        # Remove infinite values
        df = df.replace([np.inf, -np.inf], 0)

        logger.info(f"Prepared {len(df)} samples with {len(df.columns)} features")

        return df.values, np.array(targets)

    def train(self, items: list[dict], test_size: float = 0.2):
        """Train all models with advanced features"""

        logger.info("Training enhanced viral prediction models...")

        X, y = self.prepare_training_data(items)

        if len(X) < 100:
            logger.warning("Insufficient training data for reliable model")
            return

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        # Scale features
        X_train_scaled = self.scalers["standard"].fit_transform(X_train)
        X_test_scaled = self.scalers["standard"].transform(X_test)

        # Feature selection
        X_train_selected = self.feature_selectors["kbest"].fit_transform(
            X_train_scaled, y_train
        )
        X_test_selected = self.feature_selectors["kbest"].transform(X_test_scaled)

        # Train individual models
        for name, model in self.models.items():
            try:
                logger.info(f"Training {name} model...")
                model.fit(X_train_selected, y_train)

                # Predictions
                y_pred = model.predict(X_test_selected)

                # Metrics
                mse = mean_squared_error(y_test, y_pred)
                mae = mean_absolute_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)

                self.model_performance[name] = {
                    "mse": mse,
                    "mae": mae,
                    "r2": r2,
                    "rmse": np.sqrt(mse),
                }

                # Feature importance (for tree-based models)
                if hasattr(model, "feature_importances_"):
                    self.feature_importance[name] = model.feature_importances_

                logger.info(
                    f"{name} model - MSE: {mse:.4f}, MAE: {mae:.4f}, R²: {r2:.4f}"
                )

            except Exception as e:
                logger.error(f"Failed to train {name} model: {e}")
                continue

        # Create ensemble model
        try:
            self.models["ensemble"] = VotingRegressor(
                [
                    (name, model)
                    for name, model in self.models.items()
                    if name in self.model_performance
                ]
            )

            self.models["ensemble"].fit(X_train_selected, y_train)
            y_pred_ensemble = self.models["ensemble"].predict(X_test_selected)

            mse = mean_squared_error(y_test, y_pred_ensemble)
            mae = mean_absolute_error(y_test, y_pred_ensemble)
            r2 = r2_score(y_test, y_pred_ensemble)

            self.model_performance["ensemble"] = {
                "mse": mse,
                "mae": mae,
                "r2": r2,
                "rmse": np.sqrt(mse),
            }

            logger.info(
                f"Ensemble model - MSE: {mse:.4f}, MAE: {mae:.4f}, R²: {r2:.4f}"
            )

        except Exception as e:
            logger.error(f"Failed to create ensemble model: {e}")

        self.is_trained = True
        logger.info("Enhanced viral prediction models trained successfully")

    def predict_viral_score(self, item: dict, model_name: str = "ensemble") -> dict:
        """Predict viral score with confidence intervals"""

        if not self.is_trained:
            return {"score": 0.0, "confidence": 0.0, "model": "untrained"}

        try:
            features = self.extract_advanced_features(item)
            X = pd.DataFrame([features]).fillna(0).replace([np.inf, -np.inf], 0)

            # Scale and select features
            X_scaled = self.scalers["standard"].transform(X)
            X_selected = self.feature_selectors["kbest"].transform(X_scaled)

            # Get predictions from all models
            predictions = {}
            for name, model in self.models.items():
                if name in self.model_performance:
                    pred = model.predict(X_selected)[0]
                    predictions[name] = pred

            # Ensemble prediction
            if "ensemble" in predictions:
                score = predictions["ensemble"]
            else:
                score = np.mean(list(predictions.values()))

            # Calculate confidence based on model agreement
            if len(predictions) > 1:
                std_dev = np.std(list(predictions.values()))
                confidence = max(0, 1 - std_dev / abs(score)) if score != 0 else 0
            else:
                confidence = 0.8  # Default confidence for single model

            return {
                "score": float(score),
                "confidence": float(confidence),
                "model": model_name,
                "all_predictions": predictions,
                "feature_count": len(features),
            }

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {"score": 0.0, "confidence": 0.0, "model": "error"}

    def get_feature_importance(self, model_name: str = "rf") -> dict:
        """Get feature importance for a specific model"""

        if not self.is_trained or model_name not in self.feature_importance:
            return {}

        # Get feature names
        feature_names = [
            f"feature_{i}" for i in range(len(self.feature_importance[model_name]))
        ]

        # Create importance dict
        importance_dict = dict(zip(feature_names, self.feature_importance[model_name]))

        # Sort by importance
        sorted_importance = dict(
            sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
        )

        return sorted_importance

    def save_models(self, path: str = "models/enhanced_viral_predictor.joblib"):
        """Save all trained models and components"""

        if not self.is_trained:
            logger.warning("No trained models to save")
            return

        Path(path).parent.mkdir(parents=True, exist_ok=True)

        save_data = {
            "models": self.models,
            "scalers": self.scalers,
            "feature_selectors": self.feature_selectors,
            "model_performance": self.model_performance,
            "feature_importance": self.feature_importance,
            "is_trained": self.is_trained,
        }

        joblib.dump(save_data, path)
        logger.info(f"Enhanced models saved to {path}")

    def load_models(self, path: str = "models/enhanced_viral_predictor.joblib"):
        """Load trained models and components"""

        try:
            data = joblib.load(path)
            self.models = data["models"]
            self.scalers = data["scalers"]
            self.feature_selectors = data["feature_selectors"]
            self.model_performance = data["model_performance"]
            self.feature_importance = data["feature_importance"]
            self.is_trained = data["is_trained"]
            logger.info(f"Enhanced models loaded from {path}")
        except FileNotFoundError:
            logger.warning(f"No saved models found at {path}")
        except Exception as e:
            logger.error(f"Failed to load models: {e}")


# Global instance
enhanced_predictor = EnhancedViralPredictor()
