#!/usr/bin/env python3
"""
Sync data from cloud function back to local system and save to database.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests


def sync_cloud_data():
    """Fetch data from cloud function and save to local system"""

    print("🔄 Syncing data from cloud function...")

    # Cloud function URL
    url = "https://us-central1-lucky-union-463615-t3.cloudfunctions.net/refresh_data"

    # Request payload
    payload = {"generate_digest": True, "force_refresh": True}

    try:
        # Make request to cloud function
        response = requests.post(url, json=payload, timeout=300)  # 5 minute timeout

        if response.status_code == 200:
            data = response.json()

            if data.get("status") == "success":
                print(
                    f"✅ Success! Collected {data['metrics']['data_collected']} items"
                )
                print(f"📊 Sources: {data['metrics']['sources']}")
                print(
                    f"⏱️ Execution time: {data['metrics']['total_execution_time']:.2f}s"
                )

                # Save processed data to local files
                if "processed_data" in data:
                    save_processed_data(data["processed_data"])

                # Save digest if generated
                if "digest_content" in data:
                    save_digest(data["digest_content"], data.get("digest_date"))

                # Save to database
                save_to_database(data.get("processed_data", []))

                return True
            else:
                print(
                    f"❌ Cloud function returned error: {data.get('message', 'Unknown error')}"
                )
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error syncing data: {e}")
        return False


def save_processed_data(processed_data):
    """Save processed data to local JSON files"""
    print("💾 Saving processed data...")

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # Save consolidated data
    consolidated_path = output_dir / "consolidated_data.json"
    with open(consolidated_path, "w", encoding="utf-8") as f:
        json.dump(processed_data, f, indent=2, default=str)

    # Separate by source
    sources = {"twitter": [], "reddit": [], "news": []}

    for item in processed_data:
        source = item.get("source", "unknown")
        if source in sources:
            sources[source].append(item)

    # Save individual source files
    for source, data in sources.items():
        if data:
            source_path = output_dir / f"{source}_raw.json"
            with open(source_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
            print(f"   📄 Saved {len(data)} {source} items")

    print(f"✅ Processed data saved to {consolidated_path}")


def save_digest(digest_content, digest_date=None):
    """Save digest content to local files"""
    print("📄 Saving digest...")

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # Save current digest
    digest_path = output_dir / "digest.md"
    with open(digest_path, "w", encoding="utf-8") as f:
        f.write(digest_content)

    # Save dated digest
    if digest_date:
        dated_digest_path = output_dir / f"digest-{digest_date}.md"
        with open(dated_digest_path, "w", encoding="utf-8") as f:
            f.write(digest_content)
        print(f"   📄 Saved dated digest: {dated_digest_path}")

    print(f"✅ Digest saved to {digest_path}")


def save_to_database(processed_data):
    """Save data to local SQLite database"""
    print("🗄️ Saving to database...")

    try:
        # Import database models
        from sqlmodel import Session

        from storage.db import RedditPost, Tweet, engine

        with Session(engine) as session:
            tweets_added = 0
            reddit_added = 0

            for item in processed_data:
                if item.get("source") == "twitter":
                    # Check if tweet already exists
                    existing = session.exec(
                        f"SELECT id FROM tweet WHERE tweet_id = '{item.get('id_str', str(item.get('id', '')))}'"
                    ).first()

                    if not existing:
                        tweet = Tweet(
                            tweet_id=item.get("id_str", str(item.get("id", ""))),
                            full_text=item.get("full_text", item.get("text", "")),
                            user_screen_name=item.get("user", {}).get(
                                "screen_name", "unknown"
                            ),
                            user_followers_count=item.get("user", {}).get(
                                "followers_count", 0
                            ),
                            user_verified=item.get("user", {}).get("verified", False),
                            like_count=item.get("favorite_count", 0),
                            retweet_count=item.get("retweet_count", 0),
                            reply_count=item.get("reply_count", 0),
                            created_at=datetime.fromisoformat(
                                item.get("created_at", datetime.now().isoformat())
                            ),
                            scraped_at=datetime.now(timezone.utc),
                        )
                        session.add(tweet)
                        tweets_added += 1

                elif item.get("source") == "reddit":
                    # Check if post already exists
                    existing = session.exec(
                        f"SELECT id FROM redditpost WHERE post_id = '{item.get('url', '')}'"
                    ).first()

                    if not existing:
                        post = RedditPost(
                            post_id=item.get("url", ""),
                            title=item.get("title", ""),
                            author=item.get("author", "unknown"),
                            subreddit=item.get("subreddit", ""),
                            score=item.get("score", 0),
                            num_comments=item.get("num_comments", 0),
                            created_at=datetime.fromisoformat(
                                item.get("created_utc", datetime.now().isoformat())
                            ),
                            link=item.get("url", ""),
                            scraped_at=datetime.now(timezone.utc),
                        )
                        session.add(post)
                        reddit_added += 1

            session.commit()
            print(f"   📊 Added {tweets_added} tweets, {reddit_added} reddit posts")

    except Exception as e:
        print(f"❌ Error saving to database: {e}")
        import traceback

        traceback.print_exc()


def main():
    """Main function"""
    print("🚀 Degen Digest Cloud Data Sync")
    print("=" * 50)
    print(f"⏰ Started at: {datetime.now()}")

    success = sync_cloud_data()

    if success:
        print("\n🎉 Data sync completed successfully!")
        print("📊 Check the dashboard at https://farmchecker.xyz for updated data")
    else:
        print("\n❌ Data sync failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
