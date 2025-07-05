import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import logging
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors.rpcerrorlist import ChannelPrivateError, UsernameInvalidError

from utils.advanced_logging import get_logger
from utils.logger import setup_logging

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
SESSION_NAME = os.getenv("TELEGRAM_SESSION", "degen_digest")

logger = get_logger(__name__)
logging.basicConfig(level=logging.INFO)
setup_logging()

# Public channels/groups to monitor
TARGET_CHANNELS = [
    "@SolanaMemeCalls",
    "@CryptoAlpha",
    "@binancekillers",
    "@cryptoclubpump",
    "@RavenProSupport",
    "@AltSignals",
    "@jamescpt",
    "@degeninvestor",
    "@ryder_reilly",
    "@iqcash_admin",
    "@gqsoul",
    "@Arpiner7",
    "@mikevazovskyi",
    "@robertus78",
    "@Fesions",
    "@BitcoinSmarts",
]


async def collect_messages(channel_usernames: list[str], limit: int = 100):
    """Collect recent Telegram messages from public channels (async)."""
    if API_ID == 0 or API_HASH is None:
        raise ValueError("TELEGRAM_API_ID/HASH not set")

    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()

    try:
        all_messages = []
        for ch in channel_usernames:
            logger.info("tg fetch", channel=ch)
            try:
                async for message in client.iter_messages(ch, limit=limit):
                    if message.text:
                        all_messages.append(
                            {
                                "channel": ch,
                                "date": str(message.date),
                                "text": message.text,
                                "id": message.id,
                            }
                        )
            except (UsernameInvalidError, ChannelPrivateError) as exc:
                logger.warning("telegram channel skipped", channel=ch, exc_info=exc)
                continue
        return all_messages
    finally:
        await client.disconnect()


def main():
    import asyncio

    messages = asyncio.run(collect_messages(TARGET_CHANNELS, limit=200))
    out_path = Path("output/telegram_raw.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(messages, indent=2))
    logger.info("telegram messages saved", count=len(messages))


if __name__ == "__main__":
    main()
