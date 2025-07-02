#!/usr/bin/env python3
"""
Content classifier for crypto content with enhanced Solana detection
"""

from typing import Any

from utils.advanced_logging import get_logger

logger = get_logger(__name__)


def classify(item: dict[str, Any]) -> str:
    """Classify content with enhanced Solana detection"""

    # Extract text content
    text = ""
    if item.get("text"):
        text += " " + item["text"]
    if item.get("full_text"):
        text += " " + item["full_text"]
    if item.get("title"):
        text += " " + item["title"]
    if item.get("headline"):
        text += " " + item["headline"]
    if item.get("body"):
        text += " " + item["body"]

    text = text.lower()

    # Enhanced Solana detection (high priority)
    solana_keywords = [
        "solana",
        "sol",
        "$sol",
        "saga",
        "phantom",
        "solflare",
        "raydium",
        "orca",
        "jupiter",
        "serum",
        "mango",
        "saber",
        "spl",
        "spl token",
        "metaplex",
        "candy machine",
        "magic eden",
        "opensea solana",
        "solana nft",
        "solana defi",
        "solana dex",
        "solana airdrop",
        "bonk",
        "$bonk",
        "dogwifhat",
        "wif",
        "$wif",
        "bome",
        "$bome",
        "popcat",
        "$popcat",
        "book of meme",
        "jup",
        "$jup",
        "ray",
        "$ray",
        "orca",
        "$orca",
        "mngo",
        "$mngo",
        "srm",
        "$srm",
        "sbr",
        "$sbr",
        "solana ecosystem",
        "solana season",
        "solana summer",
    ]

    # Check for Solana content first (high priority)
    solana_count = sum(1 for keyword in solana_keywords if keyword in text)
    if solana_count > 0:
        # Determine Solana subcategory
        if any(
            word in text
            for word in [
                "bonk",
                "$bonk",
                "dogwifhat",
                "wif",
                "$wif",
                "bome",
                "$bome",
                "popcat",
                "$popcat",
                "book of meme",
            ]
        ):
            return "🔥 Solana Meme Token"
        elif any(
            word in text
            for word in ["airdrop", "claim", "free", "drop", "eligible", "whitelist"]
        ):
            return "🚀 Solana Airdrop"
        elif any(
            word in text
            for word in [
                "launch",
                "launched",
                "new",
                "presale",
                "ico",
                "ido",
                "fair launch",
                "stealth",
            ]
        ):
            return "🚀 Solana Token Launch"
        elif any(
            word in text
            for word in ["rug", "scam", "honeypot", "fake", "ponzi", "pyramid"]
        ):
            return "💀 Solana Rug"
        elif any(
            word in text
            for word in [
                "phantom",
                "solflare",
                "raydium",
                "orca",
                "jupiter",
                "serum",
                "mango",
                "saber",
                "metaplex",
                "magic eden",
            ]
        ):
            return "🔧 Solana Ecosystem"
        elif any(
            word in text
            for word in [
                "nft",
                "opensea",
                "floor",
                "mint",
                "collection",
                "art",
                "gaming",
            ]
        ):
            return "🎨 Solana NFT"
        elif any(
            word in text
            for word in [
                "defi",
                "yield",
                "apy",
                "liquidity",
                "swap",
                "amm",
                "dex",
                "lending",
            ]
        ):
            return "🏦 Solana DeFi"
        elif any(
            word in text
            for word in ["pump", "moon", "bull", "rocket", "🚀", "mooning", "pumping"]
        ):
            return "📈 Solana Pump"
        elif any(
            word in text
            for word in ["dump", "bear", "sell", "short", "dead", "💀", "📉"]
        ):
            return "📉 Solana Dump"
        else:
            return "🌞 Solana General"

    # General crypto classification (maintain market pulse)
    if any(
        word in text for word in ["rug", "scam", "honeypot", "fake", "ponzi", "pyramid"]
    ):
        return "💀 Rug of the Day"

    if any(
        word in text
        for word in ["airdrop", "claim", "free", "drop", "eligible", "whitelist"]
    ):
        return "🪂 Airdrop Alert"

    if any(
        word in text
        for word in [
            "launch",
            "launched",
            "new",
            "presale",
            "ico",
            "ido",
            "fair launch",
            "stealth",
        ]
    ):
        return "🚀 Meme Launch"

    if any(
        word in text
        for word in ["whale", "whales", "big money", "large transfer", "whale alert"]
    ):
        return "🐳 Whale Move"

    if any(
        word in text
        for word in ["alpha", "insider", "tip", "secret", "exclusive", "leak"]
    ):
        return "🧠 Alpha Thread"

    if any(word in text for word in ["bitcoin", "btc", "$btc", "satoshi", "halving"]):
        return "₿ Bitcoin News"

    if any(word in text for word in ["ethereum", "eth", "$eth", "vitalik", "merge"]):
        return "🔷 Ethereum Update"

    if any(
        word in text
        for word in [
            "defi",
            "yield",
            "apy",
            "liquidity",
            "swap",
            "amm",
            "dex",
            "lending",
        ]
    ):
        return "🏦 DeFi Protocol"

    if any(
        word in text
        for word in ["nft", "opensea", "floor", "mint", "collection", "art", "gaming"]
    ):
        return "🎨 NFT Collection"

    if any(
        word in text for word in ["meme", "dog", "cat", "pepe", "shib", "doge", "wojak"]
    ):
        return "🐕 Meme Coin"

    if any(
        word in text
        for word in ["pump", "moon", "bull", "rocket", "🚀", "mooning", "pumping"]
    ):
        return "📈 Pump Alert"

    if any(
        word in text for word in ["dump", "bear", "sell", "short", "dead", "💀", "📉"]
    ):
        return "📉 Dump Alert"

    if any(
        word in text
        for word in [
            "trading",
            "chart",
            "technical",
            "analysis",
            "ta",
            "support",
            "resistance",
        ]
    ):
        return "📊 Trading Analysis"

    if any(
        word in text
        for word in [
            "news",
            "announcement",
            "update",
            "release",
            "partnership",
            "adoption",
        ]
    ):
        return "📰 Crypto News"

    # Default classification
    return "💬 General Crypto"


def get_solana_score(item: dict[str, Any]) -> float:
    """Calculate Solana relevance score (0-1)"""

    # Extract text content
    text = ""
    if item.get("text"):
        text += " " + item["text"]
    if item.get("full_text"):
        text += " " + item["full_text"]
    if item.get("title"):
        text += " " + item["title"]
    if item.get("headline"):
        text += " " + item["headline"]
    if item.get("body"):
        text += " " + item["body"]

    text = text.lower()

    # Solana keywords with weights
    solana_keywords = {
        # High weight keywords
        "solana": 1.0,
        "sol": 0.9,
        "$sol": 0.9,
        "bonk": 0.8,
        "$bonk": 0.8,
        "dogwifhat": 0.8,
        "wif": 0.8,
        "$wif": 0.8,
        "bome": 0.8,
        "$bome": 0.8,
        "book of meme": 0.8,
        "popcat": 0.8,
        "$popcat": 0.8,
        # Medium weight keywords
        "phantom": 0.7,
        "raydium": 0.7,
        "orca": 0.7,
        "jupiter": 0.7,
        "serum": 0.7,
        "mango": 0.7,
        "saber": 0.7,
        "metaplex": 0.7,
        "magic eden": 0.7,
        "spl": 0.7,
        "spl token": 0.7,
        # Lower weight keywords
        "saga": 0.6,
        "solflare": 0.6,
        "candy machine": 0.6,
        "opensea solana": 0.6,
        "solana nft": 0.6,
        "solana defi": 0.6,
        "solana dex": 0.6,
        "solana airdrop": 0.6,
        "solana ecosystem": 0.6,
        "solana season": 0.6,
        "solana summer": 0.6,
    }

    # Calculate score
    total_score = 0
    max_possible_score = 0

    for keyword, weight in solana_keywords.items():
        if keyword in text:
            total_score += weight
        max_possible_score += weight

    if max_possible_score == 0:
        return 0.0

    return min(1.0, total_score / max_possible_score)


def is_solana_priority(item: dict[str, Any]) -> bool:
    """Check if item should be prioritized for Solana focus"""
    solana_score = get_solana_score(item)
    return solana_score > 0.3  # Threshold for Solana priority
