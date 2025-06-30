from typing import Dict
import logging
from utils.logger import setup_logging
from utils.advanced_logging import get_logger

setup_logging()
logger = get_logger(__name__)

TAGS = [
    "🔥 Top CT Story",
    "💀 Rug of the Day",
    "🚀 Meme Launch",
    "🐳 Whale Move",
    "🧠 Alpha Thread",
    "💬 Quote of the Day",
]


def classify(item: Dict) -> str:
    text = (item.get("full_text") or item.get("text") or "").lower()
    if any(w in text for w in ["rug", "scam"]):
        return "💀 Rug of the Day"
    if any(w in text for w in ["whale", "bought", "sold"]):
        return "🐳 Whale Move"
    if any(w in text for w in ["launch", "new coin", "$", "token"]):
        return "🚀 Meme Launch"
    if any(w in text for w in ["thread", "🧵"]):
        return "🧠 Alpha Thread"
    if any(w in text for w in ["quote", "\""]):
        return "💬 Quote of the Day"
    tag = "🔥 Top CT Story"
    logger.debug("classifier default", text=text[:80])
    return tag 