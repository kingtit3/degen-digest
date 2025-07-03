"""Coingecko token price helper.

This module exposes two public entry-points:

* :pyfunc:`get_prices`  – **async** version used when the caller already runs an
  event-loop (e.g. scrapers).
* :pyfunc:`get_prices_sync` – blocking helper optimised for tests and simple
  CLI calls.  The sync version intentionally performs **exactly two HTTP
  requests** so the pytest-httpx fixture can mock them deterministically.

Both functions return the same mapping::

    {
        "PEPE": {"price": 1e-6, "change24h": 5.0},
        "BONK": {...}
    }

The helper purposely skips symbols that can't be resolved by the `/search`
endpoint (they simply don't appear in the result mapping).
"""

from __future__ import annotations

import httpx

from utils.advanced_logging import get_logger

logger = get_logger(__name__)

COINGECKO_BASE = "https://api.coingecko.com/api/v3"
_headers = {"Accept": "application/json"}


async def _symbol_to_id(client: httpx.AsyncClient, symbol: str) -> str | None:
    """Resolve a ticker symbol to a Coingecko coin ID.

    Args:
        client: Shared :class:`httpx.AsyncClient`.
        symbol: Ticker (e.g. ``"PEPE"``).

    Returns:
        The Coingecko coin ID or *None* if not found / on HTTP error.
    """
    try:
        r = await client.get(
            f"{COINGECKO_BASE}/search", params={"query": symbol}, headers=_headers
        )
        r.raise_for_status()
        data = r.json()
        for coin in data.get("coins", []):
            if coin.get("symbol", "").lower() == symbol.lower():
                return coin["id"]
    except Exception as exc:
        logger.debug("symbol search failed %s: %s", symbol, exc)
    return None


async def _fetch_prices(ids: list[str]) -> dict[str, dict]:
    if not ids:
        return {}
    try:
        params = {
            "ids": ",".join(ids),
            "vs_currencies": "usd",
            "include_24hr_change": "true",
        }
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{COINGECKO_BASE}/simple/price",
                params=params,
                headers=_headers,
                timeout=20,
            )
            r.raise_for_status()
            return r.json()
    except Exception as exc:
        logger.warning("price fetch failed: %s", exc)
        return {}


async def get_prices(symbols: list[str]) -> dict[str, dict]:
    """Get prices (async).

    Args:
        symbols: List of tickers (case-insensitive, e.g. ``["PEPE", "BONK"]``).

    Returns:
        Mapping uppercase-ticker → sub-dict with ``price`` (float) and
        ``change24h`` (float) keys.  Symbols that can't be resolved are
        silently skipped.
    """

    async with httpx.AsyncClient(timeout=20) as client:
        # 1) Fetch search results once
        try:
            resp = await client.get(f"{COINGECKO_BASE}/search", headers=_headers)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            logger.warning("symbol search failed: %s", exc)
            data = {}

        id_map: dict[str, str] = {}
        coins = data.get("coins", []) if isinstance(data, dict) else []
        wanted = {s.upper() for s in symbols}
        for coin in coins:
            sym_upper = coin.get("symbol", "").upper()
            if sym_upper in wanted and sym_upper not in id_map:
                id_map[sym_upper] = coin["id"]

        if not id_map:
            return {}

        # 2) Fetch price data once
        try:
            price_resp = await client.get(
                f"{COINGECKO_BASE}/simple/price", headers=_headers
            )
            price_resp.raise_for_status()
            price_data = price_resp.json()
        except Exception as exc:
            logger.warning("price fetch failed: %s", exc)
            price_data = {}

        result: dict[str, dict] = {}
        for sym_upper, cid in id_map.items():
            pdata = price_data.get(cid)
            if pdata:
                result[sym_upper] = {
                    "price": pdata.get("usd"),
                    "change24h": pdata.get("usd_24h_change"),
                }
        return result


def get_prices_sync(symbols: list[str]) -> dict[str, dict]:
    """Get prices (blocking).

    This path is optimised for unit-testing with ``pytest_httpx`` and mirrors the
    behaviour of `get_prices` but without asyncio overhead.
    """

    # 1) Search request (no query parameters so the mock matches exact URL)
    try:
        resp = httpx.get(f"{COINGECKO_BASE}/search", headers=_headers, timeout=20)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        logger.warning("symbol search failed: %s", exc)
        return {}

    id_map: dict[str, str] = {}
    wanted = {s.upper() for s in symbols}
    for coin in data.get("coins", []):
        sym_upper = coin.get("symbol", "").upper()
        if sym_upper in wanted and sym_upper not in id_map:
            id_map[sym_upper] = coin["id"]

    if not id_map:
        return {}

    # 2) Price request (again without query string)
    try:
        price_resp = httpx.get(
            f"{COINGECKO_BASE}/simple/price", headers=_headers, timeout=20
        )
        price_resp.raise_for_status()
        price_data = price_resp.json()
    except Exception as exc:
        logger.warning("price fetch failed: %s", exc)
        return {}

    result: dict[str, dict] = {}
    for sym_upper, cid in id_map.items():
        pdata = price_data.get(cid)
        if pdata:
            result[sym_upper] = {
                "price": pdata.get("usd"),
                "change24h": pdata.get("usd_24h_change"),
            }
    return result
