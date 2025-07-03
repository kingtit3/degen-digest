"""LLM response cache.

Stores prompt hash and response JSON in SQLite to avoid double-charging.
"""

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path("output/llm_cache.sqlite")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

_conn: sqlite3.Connection | None = None


def _get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(DB_PATH)
        _conn.execute(
            """CREATE TABLE IF NOT EXISTS cache (
                hash TEXT PRIMARY KEY,
                response TEXT
            )"""
        )
    return _conn


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def get(prompt: str) -> dict[str, Any] | None:
    h = _hash(prompt)
    cur = _get_conn().execute("SELECT response FROM cache WHERE hash=?", (h,))
    row = cur.fetchone()
    if row:
        return json.loads(row[0])
    return None


def set(prompt: str, response: dict[str, Any]):
    h = _hash(prompt)
    _get_conn().execute(
        "INSERT OR REPLACE INTO cache(hash, response) VALUES (?, ?)",
        (h, json.dumps(response)),
    )
    _get_conn().commit()
