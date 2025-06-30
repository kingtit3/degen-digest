import sys
from pathlib import Path
import json, re
from collections import Counter
import streamlit as st
from utils.advanced_logging import get_logger

root = Path(__file__).resolve().parents[2]
if str(root) not in sys.path:
    sys.path.append(str(root))

logger = get_logger(__name__)

SNAP_DIR = Path("output/buzz")
files = sorted(SNAP_DIR.glob("buzz_*.json"))[-2:]

st.set_page_config(page_title="Buzz Heatmap", layout="wide")
st.title("⚡️ Ticker / Hashtag Acceleration")

if len(files) < 2:
    st.info("Need at least two buzz snapshots. Build digest twice.")
    st.stop()

with files[-1].open() as f1, files[-2].open() as f2:
    recent = json.load(f1);
    prev = json.load(f2)

rows = []
for term, cnt in recent.items():
    prev_avg = prev.get(term, 0)/1  # prev hr
    accel = cnt / (prev_avg or 0.1)
    rows.append((term, cnt, accel))

rows.sort(key=lambda x: x[2], reverse=True)
rows = rows[:20]

st.subheader("Top accelerating terms (last hour vs prev)")

import pandas as pd
st.table(pd.DataFrame({
    "Term": [r[0] for r in rows],
    "Count (1h)": [r[1] for r in rows],
    "Accel x": [f"{r[2]:.1f}" for r in rows],
})) 