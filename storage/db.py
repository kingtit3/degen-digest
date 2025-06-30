"""SQLite storage using SQLModel.

Provides Tweet, RedditPost, Digest models and helper insert/query functions.
"""

from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta

from sqlmodel import SQLModel, create_engine, Field, Session, select
from utils.advanced_logging import get_logger

logger = get_logger(__name__)

DB_PATH = Path("output/degen_digest.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)


class Tweet(SQLModel, table=True):
    id: str = Field(primary_key=True)
    text: str
    full_text: Optional[str] = None
    author: Optional[str] = None
    author_username: Optional[str] = None
    tweet_id: Optional[str] = None
    created_at: Optional[str] = None
    published: Optional[datetime] = None
    like_count: Optional[int] = 0
    retweet_count: Optional[int] = 0
    reply_count: Optional[int] = 0
    view_count: Optional[int] = 0
    quote_count: Optional[int] = 0
    bookmark_count: Optional[int] = 0
    user_followers_count: Optional[int] = 0
    user_verified: Optional[bool] = False
    engagement_score: Optional[float] = 0.0
    scraped_at: datetime = Field(default_factory=datetime.utcnow)


class RedditPost(SQLModel, table=True):
    id: str = Field(primary_key=True)
    title: str
    link: str
    subreddit: Optional[str] = None
    created_at: Optional[str] = None
    scraped_at: datetime = Field(default_factory=datetime.utcnow)


class Digest(SQLModel, table=True):
    date: str = Field(primary_key=True)
    markdown_path: str
    pdf_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Track monthly LLM token usage
class LLMUsage(SQLModel, table=True):
    month: str = Field(primary_key=True)  # YYYY-MM
    tokens: int = 0
    cost_usd: float = 0.0


# Additional snapshots of engagement captured after initial scrape
class TweetMetrics(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tweet_id: str = Field(index=True)
    captured_at: datetime = Field(default_factory=datetime.utcnow)
    like_count: int = 0
    retweet_count: int = 0
    reply_count: int = 0
    quote_count: int | None = None
    bookmark_count: int | None = None


# create tables
SQLModel.metadata.create_all(engine)


# Helper API -----------------------------------------------------

def add_tweets(tweets: List[dict]):
    if not tweets:
        return
    objs: list[Tweet] = []
    for t in tweets:
        tid = t.get("id") or t.get("tweetId")
        if not tid:
            continue
        objs.append(
            Tweet(
                id=str(tid),
                text=t.get("full_text") or t.get("text", ""),
                full_text=t.get("full_text") or t.get("text", ""),
                author=t.get("userScreenName"),
                author_username=t.get("userScreenName"),
                tweet_id=str(tid),
                created_at=t.get("createdAt"),
                published=datetime.fromisoformat(t.get("createdAt").replace('Z', '+00:00')) if t.get("createdAt") else None,
                like_count=t.get("likeCount"),
                retweet_count=t.get("retweetCount"),
                reply_count=t.get("replyCount"),
                view_count=t.get("viewCount"),
                quote_count=t.get("quoteCount"),
                bookmark_count=t.get("bookmarkCount"),
                user_followers_count=t.get("userFollowersCount"),
                user_verified=t.get("userVerified", False),
            )
        )
    with Session(engine) as session:
        for obj in objs:
            if session.get(Tweet, obj.id):
                continue
            session.add(obj)
        session.commit()
    if objs:
        logger.info("tweets stored", count=len(objs))


def add_reddit_posts(posts: List[dict]):
    if not posts:
        return
    objs = []
    for p in posts:
        pid = p.get("link")
        if not pid:
            continue
        objs.append(
            RedditPost(
                id=pid,
                title=p.get("title", ""),
                link=pid,
                subreddit=p.get("subreddit"),
                created_at=p.get("published"),
            )
        )
    with Session(engine) as session:
        for obj in objs:
            if session.get(RedditPost, obj.id):
                continue
            session.add(obj)
        session.commit()
    if objs:
        logger.info("reddit posts stored", count=len(objs))


def record_digest(date_str: str, md_path: Path, pdf_path: Optional[Path] = None):
    with Session(engine) as session:
        if session.get(Digest, date_str):
            logger.info("Digest for %s already recorded", date_str)
            return
        session.add(
            Digest(
                date=date_str,
                markdown_path=str(md_path),
                pdf_path=str(pdf_path) if pdf_path else None,
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

def add_llm_tokens(tokens: int, cost: float):
    month = datetime.utcnow().strftime("%Y-%m")
    with Session(engine) as session:
        usage = session.get(LLMUsage, month)
        if usage is None:
            usage = LLMUsage(month=month, tokens=tokens, cost_usd=cost)
            session.add(usage)
        else:
            usage.tokens += tokens
            usage.cost_usd += cost
        session.commit()
    logger.debug("LLM tokens added", month=month, tokens=tokens, cost=cost)


def get_month_usage(month: str):
    with Session(engine) as session:
        return session.get(LLMUsage, month)


# ---------------------------------------------------------------------------
# Helpers for metrics refresh
# ---------------------------------------------------------------------------

def recent_tweet_ids(hours: int = 2) -> list[str]:
    """Return tweet IDs scraped within the last *hours*."""
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    with Session(engine) as sess:
        rows = sess.exec(select(Tweet.id).where(Tweet.scraped_at >= cutoff)).all()
    return [r for r in rows]


def add_tweet_metrics(metrics: list[dict]):
    """Insert TweetMetrics rows, skipping duplicates."""
    if not metrics:
        return
    with Session(engine) as sess:
        for m in metrics:
            sess.add(TweetMetrics(**m))
        sess.commit()