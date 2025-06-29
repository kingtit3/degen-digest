from typing import Dict, Any
import random
import logging
from utils.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def degen_score(item: Dict[str, Any]) -> int:
    """Return a 0-100 score estimating hype.

    Current implementation is heuristic placeholder.
    """
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