import subprocess, sys, pathlib, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

commands = [
    [sys.executable, "-m", "scrapers.twitter_apify"],
    [sys.executable, "-m", "scrapers.telegram_telethon"],
    [sys.executable, "-m", "scrapers.reddit_rss"],
    [sys.executable, "-m", "scrapers.newsapi_headlines"],
    [sys.executable, "-m", "scrapers.coingecko_gainers"],
    [sys.executable, "main.py"],  # rebuild digest
]

for cmd in commands:
    print("Running", cmd)
    ret = subprocess.call(cmd, cwd=str(ROOT))
    if ret != 0:
        print("Command failed", cmd, ret)
        sys.exit(ret)
    time.sleep(1)
print("All tasks completed successfully") 