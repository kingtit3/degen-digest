# Degen Digest – Architectural Overview

This document drills into the core components of the project, the data flow, and operational details.

---

## High-Level Workflow

```
┌────────────┐   ┌────────┐   ┌──────────────┐   ┌───────────┐   ┌──────────────┐
│  Scheduler │──▶│Scrapers│──▶│Raw JSON files│──▶│Processor  │──▶│Digest Markdown│
└────────────┘   └────────┘   └──────────────┘   └───────────┘   └──────────────┘
```

1. **Scheduler** – cron (10 AM EST) or manual shell.
2. **Scrapers** – Twitter (Apify), Reddit (RSS), Telegram (Telethon). Each saves a raw json payload under `output/`.
3. **Processor** – Combines all raw items, classifies, scores, rewrites via LLM, and dedups against `seen_tweet_ids.json`.
4. **Digest** – A single Markdown file (`output/digest.md`) suitable for conversion to HTML / PDF / Notion.

---

## Code Map

| Path | Responsibility |
|------|----------------|
| `scrapers/twitter_apify.py` | Calls your Apify actor / task. Polls, downloads dataset to `output/twitter_raw.json`. |
| `scrapers/reddit_rss.py` | Parses RSS feeds with keyword filter. |
| `scrapers/telegram_telethon.py` | Pulls latest messages from target Telegram channels (optional). |
| `processor/scorer.py` | Heuristic **Degen Score** (0–100). |
| `processor/classifier.py` | Maps text to one of six digest tags. |
| `processor/summarizer.py` | LLM rewrite via OpenRouter. |
| `main.py` | Orchestration, deduplication, digest assembly. |
| `utils/logger.py` | Rich logging (console + rotating file). |

---

## Logging

* Console and `logs/degen_digest.log`. Rotates at 5 MB×5 files.
* Each module imports `setup_logging()` once – hierarchical loggers cascade.
* HTTP events from `httpx` (used by OpenRouter) are bubbled to INFO level for traceability.

---

## Environment (.env)

```
APIFY_API_TOKEN=xxx
OPENROUTER_API_KEY=xxx
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
OPENROUTER_MODEL=google/gemini-2.0-flash-001
TELEGRAM_API_ID=
TELEGRAM_API_HASH=
```

---

## Deduplication Strategy

* During `process_items()`, every tweet's `id` / `tweetId` is checked against `output/seen_tweet_ids.json`.
* After building the digest, the IDs included are appended to the file.
* Subsequent runs ignore already-digested tweets – ensures fresh content each day.

---

## Extending

* **Models** – set `OPENROUTER_MODEL` or override in `processor/summarizer.py`.
* **New Sources** – drop another scraper script that outputs JSON to `output/`. If each item includes `text`/`summary`, it will auto-ingest.
* **Analytics / Publish** – hook `main.py` to push Markdown to Notion API or convert to PDF with `pandoc`.

---

© Degen Digest 2025 