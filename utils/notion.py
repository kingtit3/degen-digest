"""Notion integration helper."""

from notion_client import Client
import logging
from pathlib import Path
from utils.env import get

logger = logging.getLogger(__name__)


def publish_page(title: str, markdown_path: Path):
    """Publish markdown file as page in a Notion database.

    Requires NOTION_TOKEN and NOTION_DATABASE_ID environment variables.
    """
    token = get("NOTION_TOKEN")
    db_id = get("NOTION_DATABASE_ID")
    if not token or not db_id:
        logger.info("Notion env vars not set; skipping publish")
        return

    client = Client(auth=token)
    md_content = markdown_path.read_text()

    try:
        client.pages.create(
            parent={"database_id": db_id},
            properties={
                "Name": {"title": [{"text": {"content": title}}]},
            },
            children=[{
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": md_content}}]
                }
            }]
        )
        logger.info("Notion page created successfully")
    except Exception as exc:
        logger.error("Failed to publish to Notion: %s", exc) 