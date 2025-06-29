# Degen Digest

A daily one-page digest distilling the spiciest 🍿 alpha, memes, and whale moves from Crypto Twitter, Reddit, and Telegram.

## Features

* Scrapes 50+ top CT influencer accounts and viral keyword searches via Apify
* Monitors high-signal subreddits via RSS and public Telegram alpha channels via Telethon
* Scores each post with a custom **Degen Score** (0-100) factoring engagement & meme potential
* Auto-rewrites content using CT slang, emojis, memes (<50 words)
* Classifies into six categories: 🔥 Top CT Story, 💀 Rug of the Day, 🚀 Meme Launch, 🐳 Whale Move, 🧠 Alpha Thread, 💬 Quote of the Day
* Exports a Markdown digest that can be converted to HTML/PDF or published to Notion
* Designed to run daily via cron at 10:00 AM EST
* Rich logging to console **and** rotating file `logs/degen_digest.log`

## Quickstart

```bash
# 1. Install deps
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure secrets
cp .env.example .env
# edit .env and fill in keys for Apify, Telegram, OpenAI

# 3. Run scrapers (takes a few minutes)
python scrapers/twitter_apify.py
python scrapers/reddit_rss.py
# optional – telegram once creds ready
python scrapers/telegram_telethon.py

# 4. Build digest
python main.py
cat output/digest.md
```

Logs live-tail: `tail -f logs/degen_digest.log`

Full architecture docs in `docs/ARCHITECTURE.md`.

## Scheduling
Add the following cron entry (adjust path to venv):

```cron
0 10 * * * cd /path/to/DegenDigest && source .venv/bin/activate && python scrapers/twitter_apify.py && python scrapers/reddit_rss.py && python scrapers/telegram_telethon.py && python main.py >> logs/cron.log 2>&1
```

## Extending
* Add/remove influencers in `config/influencers.json`
* Tune keyword filters in `config/keywords.json`
* Improve score logic in `processor/scorer.py`
* Replace OpenAI with another LLM by editing `processor/summarizer.py`

### Security / Secrets

Use `direnv` to keep secrets out of commits:

```bash
echo 'layout python' > .envrc
echo 'export APIFY_API_TOKEN=...' >> .envrc   # etc.
direnv allow
```

# or Docker
docker build -t degen-digest .
docker run --env-file .env -v $(pwd)/output:/app/output degen-digest 