"""Lightweight token price fetcher using Coingecko public API.

Given a list of ticker symbols (e.g. ["PEPE", "BONK"]) it returns a mapping
symbol -> {price, change24h}. Uses /search to map symbol to id.
"""

from __future__ import annotations

import httpx
import asyncio
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

COINGECKO_BASE = "https://api.coingecko.com/api/v3"
_headers = {"Accept": "application/json"}


async def _symbol_to_id(client: httpx.AsyncClient, symbol: str) -> str | None:
    try:
        r = await client.get(f"{COINGECKO_BASE}/search", params={"query": symbol}, headers=_headers)
        r.raise_for_status()
        data = r.json()
        for coin in data.get("coins", []):
            if coin.get("symbol", "").lower() == symbol.lower():
                return coin["id"]
    except Exception as exc:
        logger.debug("symbol search failed %s: %s", symbol, exc)
    return None


async def _fetch_prices(ids: List[str]) -> Dict[str, Dict]:
    if not ids:
        return {}
    try:
        params = {
            "ids": ",".join(ids),
            "vs_currencies": "usd",
            "include_24hr_change": "true",
        }
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{COINGECKO_BASE}/simple/price", params=params, headers=_headers, timeout=20)
            r.raise_for_status()
            return r.json()
    except Exception as exc:
        logger.warning("price fetch failed: %s", exc)
        return {}


async def get_prices(symbols: List[str]) -> Dict[str, Dict]:
    """Return mapping symbol -> {price, change24h}. Missing symbols omitted."""
    async with httpx.AsyncClient(timeout=20) as client:
        tasks = {symbol: asyncio.create_task(_symbol_to_id(client, symbol)) for symbol in symbols}
        id_map: Dict[str, str] = {}
        for sym, t in tasks.items():
            cid = await t
            if cid:
                id_map[sym] = cid
        price_data = await _fetch_prices(list(id_map.values()))
        result = {}
        for sym, cid in id_map.items():
            pdata = price_data.get(cid)
            if pdata:
                result[sym.upper()] = {
                    "price": pdata.get("usd"),
                    "change24h": pdata.get("usd_24h_change"),
                }
        return result


def get_prices_sync(symbols: List[str]):
    return asyncio.run(get_prices(symbols)) 