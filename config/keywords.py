#!/usr/bin/env python3
"""
Keywords configuration for enhanced viral prediction
"""

def get_keywords():
    """Get keywords for different platforms"""
    return {
        "twitter_search": [
            "rug", "airdrop", "new coin", "launched", "celebrity token", "bonk", "pump", "0 tax",
            "moon", "bull", "bear", "dump", "scam", "honeypot", "free", "claim", "drop",
            "bitcoin", "ethereum", "btc", "eth", "defi", "nft", "meme", "altcoin", "crypto",
            "trading", "chart", "technical", "analysis", "news", "announcement", "update"
        ],
        "reddit": [
            "rug", "airdrop", "scam", "launch", "meme coin", "celebrity", "pump", "dump",
            "bitcoin", "ethereum", "defi", "nft", "trading", "analysis", "news", "moon"
        ],
        "telegram": [
            "rug", "airdrop", "token", "launch", "whale", "pump", "dump", "scam", "free",
            "bitcoin", "ethereum", "defi", "nft", "meme", "altcoin", "crypto"
        ],
        "news": [
            "cryptocurrency", "bitcoin", "ethereum", "blockchain", "defi", "nft", "crypto",
            "regulation", "adoption", "institutional", "investment", "trading", "market"
        ],
        "market": [
            "bitcoin", "ethereum", "defi", "nft", "meme", "altcoin", "stablecoin", "exchange"
        ]
    }

def get_viral_keywords():
    """Get keywords that indicate potential virality"""
    return {
        "high_viral": [
            "moon", "pump", "bull", "rocket", "🚀", "💎", "diamond", "hodl", "lambo",
            "airdrop", "free", "claim", "drop", "launch", "new", "announcement"
        ],
        "medium_viral": [
            "bitcoin", "ethereum", "btc", "eth", "defi", "nft", "crypto", "trading",
            "analysis", "chart", "technical", "news", "update"
        ],
        "low_viral": [
            "bear", "dump", "sell", "short", "dead", "💀", "📉", "rekt", "scam", "rug"
        ],
        "trending_topics": [
            "bitcoin etf", "ethereum merge", "defi summer", "nft boom", "meme season",
            "altcoin season", "bull run", "bear market", "crypto winter"
        ]
    }

def get_sentiment_keywords():
    """Get keywords for sentiment analysis"""
    return {
        "positive": [
            "moon", "pump", "bull", "buy", "long", "hodl", "diamond", "rocket", "🚀", "💎",
            "lambo", "mooning", "pumping", "bullish", "bullrun", "moonboy", "diamond hands"
        ],
        "negative": [
            "dump", "bear", "sell", "short", "rug", "scam", "honeypot", "dead", "💀", "📉",
            "rekt", "dumpster", "bearish", "bear market", "paper hands", "fud"
        ],
        "fomo": [
            "moon", "pump", "rocket", "🚀", "mooning", "pumping", "fomo", "fear of missing out",
            "last chance", "don't miss", "going to moon", "next bitcoin"
        ],
        "fud": [
            "scam", "rug", "honeypot", "dead", "💀", "dump", "bear", "sell", "fud",
            "fear uncertainty doubt", "ponzi", "bubble", "crash"
        ]
    }

def get_topic_keywords():
    """Get keywords for topic categorization"""
    return {
        "bitcoin": ["bitcoin", "btc", "$btc", "satoshi", "halving", "bitcoin etf"],
        "ethereum": ["ethereum", "eth", "$eth", "vitalik", "merge", "ethereum 2.0"],
        "defi": ["defi", "yield", "apy", "liquidity", "swap", "amm", "dex", "lending"],
        "nft": ["nft", "opensea", "floor", "mint", "collection", "art", "gaming"],
        "meme": ["meme", "dog", "cat", "pepe", "shib", "doge", "bonk", "wojak"],
        "airdrop": ["airdrop", "claim", "free", "drop", "eligible", "whitelist"],
        "scam": ["rug", "scam", "honeypot", "fake", "ponzi", "pyramid"],
        "pump": ["pump", "moon", "bull", "rocket", "🚀", "mooning", "pumping"],
        "trading": ["trade", "chart", "technical", "analysis", "ta", "support", "resistance"],
        "news": ["news", "announcement", "update", "release", "partnership", "adoption"]
    } 