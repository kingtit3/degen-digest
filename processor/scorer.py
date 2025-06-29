from typing import Dict, Any
import random
import logging
from utils.logger import setup_logging
from pathlib import Path
from typing import Optional

from joblib import load

MODEL_PATH = Path("models/meme_lr.joblib")

_model: Optional[object] = None


def _load_model():
    global _model
    if _model is None and MODEL_PATH.exists():
        try:
            _model = load(MODEL_PATH)
            logger.info("ML scorer model loaded")
        except Exception as exc:
            logger.warning("Failed to load ML model: %s", exc)

_load_model()


def degen_score(item: Dict[str, Any]) -> int:
    """Return a 0-100 score estimating hype.

    Current implementation is heuristic placeholder.
    """
    # If ML model available and we have text, use its probability
    if _model and item.get("full_text") or item.get("text"):
        try:
            prob = _model.predict_proba([item.get("full_text") or item.get("text")])[0][1]
            base = prob * 100
        except Exception as exc:
            logger.debug("ML scorer failed: %s", exc)
            base = 0
    else:
        likes = item.get("likeCount", 0)
        retweets = item.get("retweetCount", 0)
        replies = item.get("replyCount", 0)

        engagement = likes * 1 + retweets * 2 + replies * 0.5
        # Log scale
        import math
        base = min(engagement / 1000 * 20, 60)  # cap at 60

    # Randomness for meme potential
    meme_factor = random.randint(0, 40)
    return int(min(base + meme_factor, 100)) 