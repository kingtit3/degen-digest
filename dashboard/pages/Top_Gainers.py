import sys
from pathlib import Path
root = Path(__file__).resolve().parents[2]
if str(root) not in sys.path:
    sys.path.append(str(root))

import streamlit as st
import json
import humanize
from utils.advanced_logging import get_logger

logger = get_logger(__name__)

OUTPUT_DIR = Path("output")

st.set_page_config(page_title="Top Gainers", layout="wide")
st.title("📈 CoinGecko Top 24h Gainers")

cg_path = OUTPUT_DIR / "coingecko_raw.json"
if not cg_path.exists():
    st.info("No CoinGecko data yet. Run `python -m scrapers.coingecko_gainers`.")
    st.stop()

try:
    data = json.loads(cg_path.read_text())
except Exception as exc:
    st.error(f"Failed to read {cg_path}: {exc}")
    st.stop()

table = {
    "Symbol": [],
    "Name": [],
    "Price $": [],
    "% 24h": [],
    "Link": [],
}
for itm in data[:20]:
    title = itm["title"]  # e.g. "PEPE +42.3% in 24h"
    sym = title.split()[0]
    pct = title.split()[1]
    table["Symbol"].append(sym)
    table["Name"].append(itm["summary"].split()[0])
    price_part = itm["summary"].split("$")[-1].split()[0]
    table["Price $"] .append(price_part)
    table["% 24h"].append(pct.replace("+", ""))
    table["Link"].append(itm["link"])

st.table(table) 