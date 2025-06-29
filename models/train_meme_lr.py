"""Tiny script to train logistic regression meme classifier.
Run manually when you have labelled data CSV.
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from joblib import dump
from pathlib import Path

DATA_CSV = Path("models/meme_training_data.csv")  # required columns: text,label (1 meme,0 other)
MODEL_PATH = Path("models/meme_lr.joblib")


def train():
    df = pd.read_csv(DATA_CSV)
    X, y = df["text"], df["label"]
    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1,2))),
        ("clf", LogisticRegression(max_iter=1000)),
    ])
    pipe.fit(X, y)
    MODEL_PATH.parent.mkdir(exist_ok=True, parents=True)
    dump(pipe, MODEL_PATH)
    print("Model saved to", MODEL_PATH)


if __name__ == "__main__":
    train() 