import os
import logging
import json
from pathlib import Path
from typing import List

from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from dotenv import load_dotenv
from utils.logger import setup_logging

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
SESSION_NAME = os.getenv("TELEGRAM_SESSION", "degen_digest")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
setup_logging()

# Public channels/groups to monitor
TARGET_CHANNELS = [
    "@SolanaMemeCalls",
    "@CryptoAlpha",
]


async def collect_messages(channel_usernames: List[str], limit: int = 100):
    if API_ID == 0 or API_HASH is None:
        raise ValueError("TELEGRAM_API_ID/HASH not set")

    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()

    try:
        all_messages = []
        for ch in channel_usernames:
            logger.info("Fetching messages for %s", ch)
            async for message in client.iter_messages(ch, limit=limit):
                if message.text:
                    all_messages.append({
                        "channel": ch,
                        "date": str(message.date),
                        "text": message.text,
                        "id": message.id,
                    })
        return all_messages
    finally:
        await client.disconnect()


def main():
    import asyncio
    messages = asyncio.run(collect_messages(TARGET_CHANNELS, limit=200))
    out_path = Path("output/telegram_raw.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(messages, indent=2))
    logger.info("Saved %d Telegram messages", len(messages))


if __name__ == "__main__":
    main() 