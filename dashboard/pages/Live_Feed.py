import sys
from pathlib import Path
root_path = Path(__file__).resolve().parents[2]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

import streamlit as st
import json
from datetime import datetime
from utils.advanced_logging import get_logger

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

logger = get_logger(__name__)

OUTPUT_DIR = Path("output")

st.set_page_config(page_title="Live Feed", layout="wide")

st.title("🔄 Live Raw Feed (auto-refresh 60 s)")

# Auto-refresh every 60 seconds
if st_autorefresh:
    st_autorefresh(interval=60_000, key="feed-refresh")
else:
    st.warning("Install streamlit-autorefresh for auto-refresh or refresh manually.")

items: list[dict] = []
for fname in ["twitter_raw.json", "reddit_raw.json", "telegram_raw.json", "coingecko_raw.json"]:
    path = OUTPUT_DIR / fname
    if path.exists():
        try:
            data = json.loads(path.read_text())
            for d in data:
                d["_src"] = fname.split("_", 1)[0]
            items.extend(data)
        except Exception as exc:
            logger.warning("failed reading %s: %s", fname, exc)

# sort by date/timestamp if available
items.sort(key=lambda x: x.get("createdAt") or x.get("date") or x.get("published") or "", reverse=True)

show = items[:30]

for it in show:
    src = it.get("_src")
    ts = it.get("createdAt") or it.get("date") or it.get("published")
    ts_fmt = ts[:19] if ts else ""
    text = it.get("full_text") or it.get("text") or it.get("title")
    with st.expander(f"[{src}] {ts_fmt} – {text[:80]}"):
        st.write(text)
        link = it.get("url") or it.get("link")
        if link:
            st.markdown(f"[Open link]({link})") 