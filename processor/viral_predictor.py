import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import re
import emoji

from utils.advanced_logging import get_logger
from processor.scorer import extract_tickers, get_sentiment_score

logger = get_logger(__name__)

class ViralPredictor:
    def __init__(self):
        self.models = {
            'rf': RandomForestRegressor(n_estimators=100, random_state=42),
            'gb': GradientBoostingRegressor(n_estimators=100, random_state=42)
        }
        self.scaler = StandardScaler()
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.is_trained = False
        
    def extract_features(self, item: Dict) -> Dict:
        """Extract comprehensive features for viral prediction"""
        text = f"{item.get('text', '')} {item.get('title', '')} {item.get('summary', '')}"
        
        # Text features
        features = {
            'text_length': len(text),
            'word_count': len(text.split()),
            'hashtag_count': len(re.findall(r'#\w+', text)),
            'mention_count': len(re.findall(r'@\w+', text)),
            'url_count': len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)),
            'emoji_count': len(emoji.emoji_list(text)),
            'exclamation_count': text.count('!'),
            'question_count': text.count('?'),
            'uppercase_ratio': sum(1 for c in text if c.isupper()) / len(text) if text else 0,
            'ticker_count': len(extract_tickers(text)),
            'sentiment_score': get_sentiment_score(text),
        }
        
        # Engagement features (if available)
        features.update({
            'initial_likes': item.get('likeCount', 0),
            'initial_retweets': item.get('retweetCount', 0),
            'initial_replies': item.get('replyCount', 0),
            'initial_views': item.get('viewCount', 0),
            'author_followers': item.get('userFollowersCount', 0),
            'author_verified': 1 if item.get('userVerified', False) else 0,
        })
        
        # Time features
        published = item.get('published')
        if published:
            dt = datetime.fromisoformat(published.replace('Z', '+00:00'))
            features.update({
                'hour_of_day': dt.hour,
                'day_of_week': dt.weekday(),
                'is_weekend': 1 if dt.weekday() >= 5 else 0,
            })
        
        # Source features
        features.update({
            'is_twitter': 1 if 'twitter' in item.get('_source', '').lower() else 0,
            'is_reddit': 1 if 'reddit' in item.get('_source', '').lower() else 0,
            'is_telegram': 1 if 'telegram' in item.get('_source', '').lower() else 0,
        })
        
        return features
    
    def prepare_training_data(self, items: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data with features and targets"""
        features_list = []
        targets = []
        
        for item in items:
            if not isinstance(item, dict):
                continue
                
            features = self.extract_features(item)
            features_list.append(features)
            
            # Target: engagement score after 24 hours (or current if recent)
            target = item.get('_engagement_score', 0)
            targets.append(target)
        
        # Convert to DataFrame for easier processing
        df = pd.DataFrame(features_list)
        
        # Handle missing values
        df = df.fillna(0)
        
        return df.values, np.array(targets)
    
    def train(self, items: List[Dict]):
        """Train the viral prediction models"""
        logger.info("Training viral prediction models...")
        
        X, y = self.prepare_training_data(items)
        
        if len(X) < 100:
            logger.warning("Insufficient training data for reliable model")
            return
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train models
        for name, model in self.models.items():
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            logger.info(f"{name} model - MSE: {mse:.4f}, R²: {r2:.4f}")
        
        self.is_trained = True
        logger.info("Viral prediction models trained successfully")
    
    def predict_viral_score(self, item: Dict) -> float:
        """Predict viral score for a single item"""
        if not self.is_trained:
            return 0.0
        
        features = self.extract_features(item)
        X = pd.DataFrame([features]).fillna(0).values
        X_scaled = self.scaler.transform(X)
        
        # Ensemble prediction (average of all models)
        predictions = []
        for model in self.models.values():
            pred = model.predict(X_scaled)[0]
            predictions.append(pred)
        
        return np.mean(predictions)
    
    def save_models(self, path: str = "models/viral_predictor.joblib"):
        """Save trained models"""
        if self.is_trained:
            joblib.dump({
                'models': self.models,
                'scaler': self.scaler,
                'is_trained': self.is_trained
            }, path)
            logger.info(f"Models saved to {path}")
    
    def load_models(self, path: str = "models/viral_predictor.joblib"):
        """Load trained models"""
        try:
            data = joblib.load(path)
            self.models = data['models']
            self.scaler = data['scaler']
            self.is_trained = data['is_trained']
            logger.info(f"Models loaded from {path}")
        except FileNotFoundError:
            logger.warning(f"No saved models found at {path}")

# Global instance
predictor = ViralPredictor() 