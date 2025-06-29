import json
import logging
from pathlib import Path
import re

from processor.scorer import degen_score
from processor.classifier import classify
from processor.summarizer import rewrite_content, rewrite_batch

from utils.logger import setup_logging
from enrich.token_price import get_prices_sync

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# initialize rich logging
setup_logging()

OUTPUT_DIR = Path("output")
DIGEST_MD = OUTPUT_DIR / "digest.md"
SEEN_IDS_FILE = OUTPUT_DIR / "seen_tweet_ids.json"

TEMPLATE_HEADER = "# 📰 Degen Digest – {date}\n\n"


def load_raw_sources():
    sources = {}
    for filename in ["twitter_raw.json", "reddit_raw.json", "telegram_raw.json"]:
        path = OUTPUT_DIR / filename
        if path.exists():
            sources[filename] = json.loads(path.read_text())
        else:
            sources[filename] = []
    return sources


def load_seen_ids():
    if SEEN_IDS_FILE.exists():
        try:
            return set(json.loads(SEEN_IDS_FILE.read_text()))
        except Exception:
            return set()
    return set()


def save_seen_ids(ids: set):
    SEEN_IDS_FILE.write_text(json.dumps(sorted(ids)))


def process_items(raw_items):
    processed = []
    seen_ids = load_seen_ids()

    # two-pass: first compute tag/score lists then batch LLM
    staging = []
    for item in raw_items:
        tag = classify(item)
        score = degen_score(item)
        staging.append((item, tag, score))

    # batch of 10
    for i in range(0, len(staging), 10):
        chunk = staging[i : i + 10]
        summaries = rewrite_batch([c[0] for c in chunk])
        for (orig, tag, score), summary in zip(chunk, summaries):
            tweet_id = orig.get("id") or orig.get("tweetId")
            processed.append({
                "tag": tag,
                "score": score,
                "headline": summary["headline"],
                "body": summary["body"],  # price placeholder fill later
                "link": orig.get("url") or orig.get("link"),
                "id": tweet_id,
                "text_raw": orig.get("full_text") or orig.get("text") or "",
            })

    # --- price enrichment ---
    ticker_pattern = re.compile(r"\$(\w{2,10})")
    tickers = set()
    for it in processed:
        tickers.update(ticker_pattern.findall(it["text_raw"]))

    price_map = get_prices_sync(list(tickers))

    for it in processed:
        symbols = ticker_pattern.findall(it["text_raw"])
        if symbols:
            infos = []
            for s in symbols:
                data = price_map.get(s.upper())
                if data and data["price"] is not None:
                    infos.append(f"${s.upper()} ${data['price']:.4g} ({data['change24h']:+.1f}% 24h)")
            if infos:
                it["body"] += "  \n" + " | ".join(infos)

    processed_items = processed
    processed_items.sort(key=lambda x: x["score"], reverse=True)

    return processed_items


def build_digest(processed_items):
    # Select top 10 by score but only one per tag where possible
    processed_items.sort(key=lambda x: x["score"], reverse=True)

    tag_order = [
        "🔥 Top CT Story",
        "💀 Rug of the Day",
        "🚀 Meme Launch",
        "🐳 Whale Move",
        "🧠 Alpha Thread",
        "💬 Quote of the Day",
    ]

    chosen = []
    used_tags = set()
    for item in processed_items:
        if item["tag"] not in used_tags:
            chosen.append(item)
            used_tags.add(item["tag"])
        if len(chosen) >= 10:
            break

    from datetime import date
    md = TEMPLATE_HEADER.format(date=date.today().isoformat())
    for item in chosen:
        md += f"{item['tag']}  \n**{item['headline']}**  \n{item['body']}  \n"
        if item["link"]:
            md += f"👉 [{item['link']}]({item['link']})\n\n"
        else:
            md += "\n"
    return md


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sources = load_raw_sources()
    all_raw = []
    for items in sources.values():
        all_raw.extend(items)
    logger.info("Processing %d items from raw sources", len(all_raw))
    processed = process_items(all_raw)
    digest_md = build_digest(processed)
    DIGEST_MD.write_text(digest_md)
    # update seen ids with ones used in digest
    new_ids = {item["id"] for item in processed if item.get("id")}
    if new_ids:
        existing = load_seen_ids()
        save_seen_ids(existing.union(new_ids))
    logger.info("Digest saved to %s", DIGEST_MD)

    # Post-processing outputs
    from datetime import date
    from utils.pdf import md_to_pdf
    from utils.notion import publish_page

    pdf_path = OUTPUT_DIR / f"digest-{date.today().isoformat()}.pdf"
    md_to_pdf(DIGEST_MD, pdf_path)

    publish_page(f"Degen Digest – {date.today().isoformat()}", DIGEST_MD)

    from storage.db import record_digest
    record_digest(date.today().isoformat(), DIGEST_MD, pdf_path)


if __name__ == "__main__":
    main() 