from datetime import timedelta
from pathlib import Path

import numpy as np
from joblib import dump
from sklearn.ensemble import GradientBoostingRegressor
from sqlmodel import Session, select
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from storage.db import Tweet, TweetMetrics, engine
from utils.advanced_logging import get_logger

logger = get_logger(__name__)

MODEL_PATH = Path("models/virality_gb.joblib")
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

analyzer = SentimentIntensityAnalyzer()


def build_dataset():
    X, y = [], []
    with Session(engine) as sess:
        tweets = sess.exec(select(Tweet)).all()
        metrics_map = {}
        rows = sess.exec(select(TweetMetrics)).all()
        for m in rows:
            metrics_map.setdefault(m.tweet_id, []).append(m)

        for tw in tweets:
            mids = metrics_map.get(tw.id)
            if not mids:
                continue
            # pick first snapshot >30m & <120m after scrape
            first = None
            for m in sorted(mids, key=lambda x: x.captured_at):
                delta = m.captured_at - tw.scraped_at
                if timedelta(minutes=30) <= delta <= timedelta(hours=2):
                    first = m
                    break
            if not first:
                continue
            # features
            text = tw.text.lower()
            feat = [
                tw.like_count or 0,
                tw.retweet_count or 0,
                tw.reply_count or 0,
                (first.like_count - (tw.like_count or 0))
                or 0,  # growth likes (target alt?)
                len(text),
                text.count("🚀") + text.count("moon"),
                analyzer.polarity_scores(text)["compound"],
            ]
            growth = first.like_count - (tw.like_count or 0)
            if growth < 0:
                continue
            X.append(feat)
            y.append(growth)
    return np.array(X), np.array(y)


def main():
    X, y = build_dataset()
    if len(X) < 100:
        logger.info("not enough data to train", samples=len(X))
        return
    model = GradientBoostingRegressor(random_state=0)
    model.fit(X, y)
    dump(model, MODEL_PATH)
    logger.info("virality model trained", samples=len(X), path=str(MODEL_PATH))


if __name__ == "__main__":
    main()
