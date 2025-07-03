import datetime
import math
import re
from pathlib import Path
from typing import Any

import numpy as np
from joblib import load
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from processor import buzz as _buzz
from utils.advanced_logging import get_logger
from utils.logger import setup_logging

MODEL_PATH = Path("models/meme_lr.joblib")

_model: object | None = None
_analyzer = SentimentIntensityAnalyzer()
_virality_model = None

try:
    _virality_model = load(Path("models/virality_gb.joblib"))
except Exception:
    _virality_model = None

setup_logging()
logger = get_logger(__name__)


def extract_tickers(text: str) -> list[str]:
    """Extract cryptocurrency ticker symbols from text"""
    # Common crypto ticker patterns
    ticker_pattern = re.compile(r"\$[A-Z]{2,10}|[A-Z]{2,10}/USD|[A-Z]{2,10}/USDT")
    return ticker_pattern.findall(text.upper())


def get_sentiment_score(text: str) -> float:
    """Get sentiment score from text using VADER"""
    try:
        scores = _analyzer.polarity_scores(text)
        return scores["compound"]
    except Exception:
        return 0.0


# Ticker pattern for backward compatibility
ticker_pattern = re.compile(r"\$[A-Z]{2,10}|[A-Z]{2,10}/USD|[A-Z]{2,10}/USDT")


def _load_model():
    global _model
    if _model is None and MODEL_PATH.exists():
        try:
            _model = load(MODEL_PATH)
            logger.info("ml model loaded", path=str(MODEL_PATH))
        except Exception as exc:
            logger.warning("ml model load failed", exc_info=exc)


_load_model()


def _engagement_score(
    likes: int, retweets: int, replies: int, follower_count: int | None = None
) -> float:
    """Compute a 0-100 engagement score from raw metrics using a log scale.

    If ``follower_count`` is provided, engagement is normalised per-follower to
    avoid bias toward huge accounts.
    """
    weight_sum = likes + 2 * retweets + replies
    if follower_count and follower_count > 0:
        weight_sum = weight_sum / follower_count * 1000  # per-1 000 followers

    # Log scale to compress extreme values
    return min(math.log1p(weight_sum) * 25, 100)  # log1p(≈1500) ≈ 7.3 → 100


def degen_score(item: dict[str, Any]) -> int:
    """Return an approximate viral-hype score in the 0-100 range.

    Priority order:
    1. Probability from the optional ML meme classifier (if
       ``models/meme_lr.joblib`` is available).
    2. Engagement metrics (likes, retweets, replies) with log scaling.
    3. Fallback constant (20) when no signals are present.
    """

    text_content = item.get("full_text") or item.get("text") or ""

    # --- ML probability ---------------------------------------------------
    ml_score: float | None = None
    if _model and text_content:
        try:
            prob = _model.predict_proba([text_content])[0][1]
            ml_score = prob * 100  # 0-100 scale
        except Exception as exc:
            logger.debug("ml scorer failed", exc_info=exc)

    # --- Engagement score -------------------------------------------------
    likes = item.get("likeCount", 0)
    retweets = item.get("retweetCount", 0)
    replies = item.get("replyCount", 0)
    follower_count = item.get("userFollowersCount")

    engage_score = _engagement_score(likes, retweets, replies, follower_count)

    # Exponential time decay (half-life ≈12 h)
    created_at = item.get("created_at") or item.get("createdAt")
    if created_at:
        try:
            dt = datetime.datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            hours_ago = (datetime.datetime.utcnow() - dt).total_seconds() / 3600
            decay = math.exp(-hours_ago / 12)  # 50 % every 12 h
            engage_score *= max(decay, 0.2)  # keep at least 20 %
        except Exception:
            pass

    # Sentiment boost: strongly positive (>0.6) +5, strongly negative (<-0.6) -5
    if text_content:
        try:
            compound = _analyzer.polarity_scores(text_content)["compound"]
            if compound > 0.6:
                engage_score += 5
            elif compound < -0.6:
                engage_score -= 5
        except Exception:
            pass

    # Buzz acceleration bonus
    try:
        for sym in ticker_pattern.findall(text_content):
            if _buzz.get_accel(sym) > 2:
                engage_score += 10
                break
    except Exception:
        pass

    # Combine ML and engagement – weighted average preferring ML when present
    if ml_score is not None:
        base_score = 0.6 * ml_score + 0.4 * engage_score
    else:
        base_score = engage_score if engage_score > 0 else 20

    # virality model prediction
    if _virality_model:
        try:
            feat_vec = np.array(
                [
                    likes,
                    retweets,
                    replies,
                    len(text_content),
                    _analyzer.polarity_scores(text_content)["compound"],
                ]
            ).reshape(1, -1)
            pred = _virality_model.predict(feat_vec)[0]
            base_score = 0.5 * base_score + 0.5 * min(pred / 10, 100)  # normalise
        except Exception:
            pass

    score = int(min(base_score, 100))
    logger.debug("degen score", score=score)
    return score
