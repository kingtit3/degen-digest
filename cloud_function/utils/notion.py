"""Notion integration helper."""

from pathlib import Path

from notion_client import Client

from utils.advanced_logging import get_logger
from utils.env import get

logger = get_logger(__name__)


def publish_page(title: str, markdown_path: Path):
    """Publish markdown file as page in a Notion database.

    Requires NOTION_TOKEN and NOTION_DATABASE_ID environment variables.
    """
    token = get("NOTION_TOKEN")
    db_id = get("NOTION_DATABASE_ID")
    if not token or not db_id:
        logger.info("notion skipped - env unset")
        return

    client = Client(auth=token)
    md_content = markdown_path.read_text()

    try:
        client.pages.create(
            parent={"database_id": db_id},
            properties={
                "Name": {"title": [{"text": {"content": title}}]},
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": md_content}}]
                    },
                }
            ],
        )
        logger.info("notion page created")
    except Exception as exc:
        logger.error("notion publish failed", exc_info=exc)
