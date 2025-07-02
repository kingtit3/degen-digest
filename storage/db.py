"""SQLite storage using SQLModel.

Provides Tweet, RedditPost, Digest models and helper insert/query functions.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from dateutil import parser as dateparser
from sqlmodel import Field, Session, SQLModel, create_engine, select

from utils.advanced_logging import get_logger

logger = get_logger(__name__)

DB_PATH = Path("output/degen_digest.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)


class Tweet(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tweet_id: str = Field(unique=True, index=True)
    full_text: str
    user_screen_name: str
    user_followers_count: int
    user_verified: bool
    like_count: int
    retweet_count: int
    reply_count: int
    view_count: int | None = Field(default=None)
    quote_count: int | None = Field(default=None)
    bookmark_count: int | None = Field(default=None)
    created_at: datetime | None = Field(default=None)
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RedditPost(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    post_id: str | None = Field(default=None, unique=True, index=True)
    title: str
    author: str | None = Field(default=None)
    subreddit: str | None = Field(default=None)
    score: int | None = Field(default=None)
    num_comments: int | None = Field(default=None)
    created_at: datetime | None = Field(default=None)
    link: str
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Digest(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    digest_id: str = Field(unique=True, index=True)
    content: str
    summary: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    file_path: str | None = None


# Track monthly LLM token usage
class LLMUsage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    month: str = Field(index=True)
    model: str
    tokens_used: int
    cost_usd: float
    captured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Additional snapshots of engagement captured after initial scrape
class TweetMetrics(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tweet_id: str = Field(index=True)
    captured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    like_count: int = 0
    retweet_count: int = 0
    reply_count: int = 0
    quote_count: int | None = None
    bookmark_count: int | None = None


# create tables
SQLModel.metadata.create_all(engine)


# Helper API -----------------------------------------------------


def _parse_tweet_date(date_str: str) -> datetime | None:
    """Parse tweet date from various formats"""
    if not date_str:
        return None

    try:
        # Try ISO format first
        if "T" in date_str and ("Z" in date_str or "+" in date_str):
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))

        # Try parsing with dateutil
        try:
            import dateutil.parser

            return dateutil.parser.parse(date_str)
        except ImportError:
            # Fallback to manual parsing for common Twitter format
            import re

            # Parse format like "Tue Jul 01 23:13:29 +0000 2025"
            pattern = r"(\w{3})\s+(\w{3})\s+(\d{1,2})\s+(\d{2}):(\d{2}):(\d{2})\s+([+-]\d{4})\s+(\d{4})"
            match = re.match(pattern, date_str)
            if match:
                (
                    day_name,
                    month_name,
                    day,
                    hour,
                    minute,
                    second,
                    tz_offset,
                    year,
                ) = match.groups()
                # Convert to datetime (simplified - assumes UTC)
                from datetime import datetime, timezone

                return datetime(
                    int(year),
                    {
                        "Jan": 1,
                        "Feb": 2,
                        "Mar": 3,
                        "Apr": 4,
                        "May": 5,
                        "Jun": 6,
                        "Jul": 7,
                        "Aug": 8,
                        "Sep": 9,
                        "Oct": 10,
                        "Nov": 11,
                        "Dec": 12,
                    }[month_name],
                    int(day),
                    int(hour),
                    int(minute),
                    int(second),
                    tzinfo=timezone.utc,
                )
            return None

    except Exception as e:
        logger.warning(f"Failed to parse tweet date '{date_str}': {e}")
        return None


def add_tweets(tweets: list[dict]):
    if not tweets:
        return
    objs: list[Tweet] = []
    for t in tweets:
        tid = t.get("id") or t.get("tweetId")
        if not tid:
            continue
        objs.append(
            Tweet(
                tweet_id=str(tid),
                full_text=t.get("full_text") or t.get("text", ""),
                user_screen_name=t.get("userScreenName", ""),
                user_followers_count=t.get("userFollowersCount", 0),
                user_verified=t.get("userVerified", False),
                like_count=t.get("likeCount", 0),
                retweet_count=t.get("retweetCount", 0),
                reply_count=t.get("replyCount", 0),
                view_count=t.get("viewCount"),
                quote_count=t.get("quoteCount"),
                bookmark_count=t.get("bookmarkCount"),
                created_at=_parse_tweet_date(t.get("createdAt"))
                if t.get("createdAt")
                else None,
            )
        )
    with Session(engine) as session:
        for obj in objs:
            # Check if tweet already exists by tweet_id
            existing = session.exec(
                select(Tweet).where(Tweet.tweet_id == obj.tweet_id)
            ).first()
            if existing:
                continue
            session.add(obj)
        session.commit()
    if objs:
        logger.info("tweets stored", count=len(objs))


def add_reddit_posts(posts: list[dict]):
    if not posts:
        return
    objs = []
    for p in posts:
        pid = p.get("link")
        if not pid:
            continue
        created_at = p.get("published")
        if isinstance(created_at, str):
            try:
                created_at = dateparser.parse(created_at)
            except Exception:
                created_at = None
        objs.append(
            RedditPost(
                post_id=pid,  # Use post_id instead of id for the URL
                title=p.get("title", ""),
                link=pid,
                subreddit=p.get("subreddit"),
                created_at=created_at,
            )
        )
    with Session(engine) as session:
        for obj in objs:
            # Check if post already exists by post_id
            existing = session.exec(
                select(RedditPost).where(RedditPost.post_id == obj.post_id)
            ).first()
            if existing:
                continue
            session.add(obj)
        session.commit()
    if objs:
        logger.info("reddit posts stored", count=len(objs))


def record_digest(date_str: str, md_path: Path, pdf_path: Path | None = None):
    with Session(engine) as session:
        # Check if digest already exists by digest_id
        existing = session.exec(
            select(Digest).where(Digest.digest_id == date_str)
        ).first()
        if existing:
            logger.info("Digest for %s already recorded", date_str)
            return
        session.add(
            Digest(
                digest_id=date_str,
                content="",  # Will be filled by the digest generation
                summary="",  # Will be filled by the digest generation
                file_path=str(md_path),
            )
        )
        session.commit()
    logger.info("digest recorded", date=date_str)


def stats():
    with Session(engine) as session:
        tw = session.exec(select(Tweet).count()).one()
        rd = session.exec(select(RedditPost).count()).one()
        dg = session.exec(select(Digest).count()).one()
    print(f"Tweets: {tw}\nReddit posts: {rd}\nDigests: {dg}")


# LLM usage helpers ---------------------------------------------------


def add_llm_tokens(tokens: int, cost: float, model: str = "default"):
    month = datetime.now(timezone.utc).strftime("%Y-%m")
    with Session(engine) as session:
        # Check if usage record exists for this month and model
        existing = session.exec(
            select(LLMUsage).where(LLMUsage.month == month, LLMUsage.model == model)
        ).first()
        if existing is None:
            usage = LLMUsage(
                month=month, model=model, tokens_used=tokens, cost_usd=cost
            )
            session.add(usage)
        else:
            existing.tokens_used += tokens
            existing.cost_usd += cost
        session.commit()
    logger.debug("LLM tokens added", month=month, model=model, tokens=tokens, cost=cost)


def get_month_usage(month: str, model: str = "default"):
    with Session(engine) as session:
        return session.exec(
            select(LLMUsage).where(LLMUsage.month == month, LLMUsage.model == model)
        ).first()


# ---------------------------------------------------------------------------
# Helpers for metrics refresh
# ---------------------------------------------------------------------------


def recent_tweet_ids(hours: int = 2) -> list[str]:
    """Return tweet IDs scraped within the last *hours*."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    with Session(engine) as sess:
        rows = sess.exec(select(Tweet.tweet_id).where(Tweet.scraped_at >= cutoff)).all()
    return [r for r in rows]


def add_tweet_metrics(metrics: list[dict]):
    """Insert TweetMetrics rows, skipping duplicates."""
    if not metrics:
        return
    with Session(engine) as sess:
        for m in metrics:
            sess.add(TweetMetrics(**m))
        sess.commit()
