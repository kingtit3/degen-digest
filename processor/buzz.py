from __future__ import annotations
import re, json, time
from pathlib import Path
from collections import Counter
from typing import Dict
from utils.advanced_logging import get_logger

logger = get_logger(__name__)

SNAP_DIR = Path("output/buzz")
SNAP_DIR.mkdir(parents=True, exist_ok=True)

ticker_re = re.compile(r"\$(\w{2,10})")
hashtag_re = re.compile(r"#(\w{2,20})")


def _extract_terms(text: str):
    return ticker_re.findall(text) + hashtag_re.findall(text)


def make_snapshot(items: list[dict]):
    """Write a snapshot ``buzz_YYYYMMDD_HH.json`` with term counts."""
    counter: Counter[str] = Counter()
    for it in items:
        txt = (it.get("full_text") or it.get("text") or it.get("summary") or "").lower()
        counter.update(t.lower() for t in _extract_terms(txt))
    ts = time.gmtime()
    fname = SNAP_DIR / time.strftime("buzz_%Y%m%d_%H.json", ts)
    with fname.open("w") as f:
        json.dump(counter, f)
    logger.info("buzz snapshot saved", path=str(fname), unique=len(counter))

# ---------------------------------------------------------------------------
# Acceleration helper
# ---------------------------------------------------------------------------
_recent_cache: Dict[str, float] | None = None
_prev_cache: Dict[str, float] | None = None


def _load_two_latest():
    files = sorted(SNAP_DIR.glob("buzz_*.json"))[-2:]
    if len(files) < 2:
        return {}, {}
    with files[-1].open() as f1, files[-2].open() as f2:
        recent = json.load(f1)
        prev = json.load(f2)
    return recent, prev


def get_accel(term: str) -> float:
    global _recent_cache, _prev_cache
    if _recent_cache is None:
        _recent_cache, _prev_cache = _load_two_latest()
    recent = _recent_cache.get(term.lower(), 0)
    prev = _prev_cache.get(term.lower(), 0)
    avg_prev_hour = prev / 1 if prev else 0.1  # avoid div/0
    return recent / avg_prev_hour if avg_prev_hour else 1.0 