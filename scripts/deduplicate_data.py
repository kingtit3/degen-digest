#!/usr/bin/env python3
"""
Data Deduplication Script for Degen Digest
Removes duplicate data from all sources and creates clean datasets.
"""

import json
import hashlib
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Set
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataDeduplicator:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.deduplicated_dir = self.output_dir / "deduplicated"
        self.deduplicated_dir.mkdir(exist_ok=True)
        
    def generate_content_hash(self, item: Dict[str, Any]) -> str:
        """Generate a hash for content-based deduplication"""
        # Create a normalized text representation
        text = ""
        
        # For tweets
        if item.get('source') == 'twitter' or 'full_text' in item:
            text = item.get('full_text', item.get('text', ''))
            text += str(item.get('userScreenName', ''))
            text += str(item.get('createdAt', ''))
        
        # For Reddit posts
        elif item.get('source') == 'reddit' or 'title' in item:
            text = item.get('title', '')
            text += str(item.get('author', ''))
            text += str(item.get('published', ''))
        
        # For Telegram messages
        elif item.get('source') == 'telegram' or 'message' in item:
            text = item.get('message', '')
            text += str(item.get('sender', ''))
            text += str(item.get('date', ''))
        
        # For news articles
        elif item.get('source') == 'news' or 'title' in item:
            text = item.get('title', '')
            text += str(item.get('author', ''))
            text += str(item.get('publishedAt', ''))
        
        # Normalize text
        text = text.lower().strip()
        
        # Generate hash
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def deduplicate_twitter_data(self) -> Dict[str, Any]:
        """Deduplicate Twitter data"""
        logger.info("Deduplicating Twitter data...")
        
        twitter_file = self.output_dir / "twitter_raw.json"
        if not twitter_file.exists():
            logger.warning("Twitter data file not found")
            return {"tweets": [], "duplicates_removed": 0}
        
        try:
            with open(twitter_file, 'r') as f:
                tweets = json.load(f)
            
            original_count = len(tweets)
            seen_hashes = set()
            unique_tweets = []
            duplicates = []
            
            for tweet in tweets:
                content_hash = self.generate_content_hash(tweet)
                
                if content_hash not in seen_hashes:
                    seen_hashes.add(content_hash)
                    unique_tweets.append(tweet)
                else:
                    duplicates.append(tweet)
            
            # Save deduplicated data
            deduplicated_file = self.deduplicated_dir / "twitter_deduplicated.json"
            with open(deduplicated_file, 'w') as f:
                json.dump(unique_tweets, f, indent=2, default=str)
            
            duplicates_removed = original_count - len(unique_tweets)
            logger.info(f"Twitter: {duplicates_removed} duplicates removed ({original_count} -> {len(unique_tweets)})")
            
            return {
                "tweets": unique_tweets,
                "duplicates_removed": duplicates_removed,
                "original_count": original_count,
                "final_count": len(unique_tweets)
            }
            
        except Exception as e:
            logger.error(f"Error deduplicating Twitter data: {e}")
            return {"tweets": [], "duplicates_removed": 0}
    
    def deduplicate_reddit_data(self) -> Dict[str, Any]:
        """Deduplicate Reddit data"""
        logger.info("Deduplicating Reddit data...")
        
        reddit_file = self.output_dir / "reddit_raw.json"
        if not reddit_file.exists():
            logger.warning("Reddit data file not found")
            return {"reddit_posts": [], "duplicates_removed": 0}
        
        try:
            with open(reddit_file, 'r') as f:
                posts = json.load(f)
            
            original_count = len(posts)
            seen_hashes = set()
            unique_posts = []
            duplicates = []
            
            for post in posts:
                content_hash = self.generate_content_hash(post)
                
                if content_hash not in seen_hashes:
                    seen_hashes.add(content_hash)
                    unique_posts.append(post)
                else:
                    duplicates.append(post)
            
            # Save deduplicated data
            deduplicated_file = self.deduplicated_dir / "reddit_deduplicated.json"
            with open(deduplicated_file, 'w') as f:
                json.dump(unique_posts, f, indent=2, default=str)
            
            duplicates_removed = original_count - len(unique_posts)
            logger.info(f"Reddit: {duplicates_removed} duplicates removed ({original_count} -> {len(unique_posts)})")
            
            return {
                "reddit_posts": unique_posts,
                "duplicates_removed": duplicates_removed,
                "original_count": original_count,
                "final_count": len(unique_posts)
            }
            
        except Exception as e:
            logger.error(f"Error deduplicating Reddit data: {e}")
            return {"reddit_posts": [], "duplicates_removed": 0}
    
    def deduplicate_telegram_data(self) -> Dict[str, Any]:
        """Deduplicate Telegram data"""
        logger.info("Deduplicating Telegram data...")
        
        telegram_file = self.output_dir / "telegram_raw.json"
        if not telegram_file.exists():
            logger.warning("Telegram data file not found")
            return {"telegram_messages": [], "duplicates_removed": 0}
        
        try:
            with open(telegram_file, 'r') as f:
                messages = json.load(f)
            
            original_count = len(messages)
            seen_hashes = set()
            unique_messages = []
            duplicates = []
            
            for message in messages:
                content_hash = self.generate_content_hash(message)
                
                if content_hash not in seen_hashes:
                    seen_hashes.add(content_hash)
                    unique_messages.append(message)
                else:
                    duplicates.append(message)
            
            # Save deduplicated data
            deduplicated_file = self.deduplicated_dir / "telegram_deduplicated.json"
            with open(deduplicated_file, 'w') as f:
                json.dump(unique_messages, f, indent=2, default=str)
            
            duplicates_removed = original_count - len(unique_messages)
            logger.info(f"Telegram: {duplicates_removed} duplicates removed ({original_count} -> {len(unique_messages)})")
            
            return {
                "telegram_messages": unique_messages,
                "duplicates_removed": duplicates_removed,
                "original_count": original_count,
                "final_count": len(unique_messages)
            }
            
        except Exception as e:
            logger.error(f"Error deduplicating Telegram data: {e}")
            return {"telegram_messages": [], "duplicates_removed": 0}
    
    def deduplicate_news_data(self) -> Dict[str, Any]:
        """Deduplicate news data"""
        logger.info("Deduplicating news data...")
        
        news_file = self.output_dir / "newsapi_raw.json"
        if not news_file.exists():
            logger.warning("News data file not found")
            return {"news_articles": [], "duplicates_removed": 0}
        
        try:
            with open(news_file, 'r') as f:
                articles = json.load(f)
            
            original_count = len(articles)
            seen_hashes = set()
            unique_articles = []
            duplicates = []
            
            for article in articles:
                content_hash = self.generate_content_hash(article)
                
                if content_hash not in seen_hashes:
                    seen_hashes.add(content_hash)
                    unique_articles.append(article)
                else:
                    duplicates.append(article)
            
            # Save deduplicated data
            deduplicated_file = self.deduplicated_dir / "news_deduplicated.json"
            with open(deduplicated_file, 'w') as f:
                json.dump(unique_articles, f, indent=2, default=str)
            
            duplicates_removed = original_count - len(unique_articles)
            logger.info(f"News: {duplicates_removed} duplicates removed ({original_count} -> {len(unique_articles)})")
            
            return {
                "news_articles": unique_articles,
                "duplicates_removed": duplicates_removed,
                "original_count": original_count,
                "final_count": len(unique_articles)
            }
            
        except Exception as e:
            logger.error(f"Error deduplicating news data: {e}")
            return {"news_articles": [], "duplicates_removed": 0}
    
    def create_deduplicated_consolidated_data(self, results: Dict[str, Any]):
        """Create new consolidated data with deduplicated content"""
        logger.info("Creating deduplicated consolidated data...")
        
        consolidated_data = {
            'tweets': results.get('twitter', {}).get('tweets', []),
            'reddit_posts': results.get('reddit', {}).get('reddit_posts', []),
            'telegram_messages': results.get('telegram', {}).get('telegram_messages', []),
            'news_articles': results.get('news', {}).get('news_articles', []),
            'crypto_data': [],  # Keep original crypto data
            'metadata': {
                'last_updated': datetime.now().isoformat(),
                'deduplication_date': datetime.now().isoformat(),
                'sources': [],
                'total_items': 0,
                'duplicates_removed': 0
            }
        }
        
        # Add crypto data if exists
        crypto_file = self.output_dir / "coingecko_raw.json"
        if crypto_file.exists():
            try:
                with open(crypto_file, 'r') as f:
                    consolidated_data['crypto_data'] = json.load(f)
            except Exception as e:
                logger.error(f"Error loading crypto data: {e}")
        
        # Calculate totals
        total_items = 0
        total_duplicates = 0
        
        for source, data in results.items():
            if data.get('final_count', 0) > 0:
                consolidated_data['metadata']['sources'].append(source)
                total_items += data.get('final_count', 0)
                total_duplicates += data.get('duplicates_removed', 0)
        
        consolidated_data['metadata']['total_items'] = total_items
        consolidated_data['metadata']['duplicates_removed'] = total_duplicates
        
        # Save deduplicated consolidated data
        consolidated_file = self.deduplicated_dir / "consolidated_data_deduplicated.json"
        with open(consolidated_file, 'w') as f:
            json.dump(consolidated_data, f, indent=2, default=str)
        
        logger.info(f"Deduplicated consolidated data saved: {total_items} items, {total_duplicates} duplicates removed")
        
        return consolidated_data
    
    def generate_deduplication_report(self, results: Dict[str, Any]):
        """Generate a detailed deduplication report"""
        logger.info("Generating deduplication report...")
        
        report = {
            'deduplication_date': datetime.now().isoformat(),
            'summary': {
                'total_duplicates_removed': 0,
                'total_original_items': 0,
                'total_final_items': 0,
                'deduplication_rate': 0.0
            },
            'by_source': {},
            'recommendations': []
        }
        
        total_duplicates = 0
        total_original = 0
        total_final = 0
        
        for source, data in results.items():
            duplicates = data.get('duplicates_removed', 0)
            original = data.get('original_count', 0)
            final = data.get('final_count', 0)
            
            total_duplicates += duplicates
            total_original += original
            total_final += final
            
            report['by_source'][source] = {
                'original_count': original,
                'final_count': final,
                'duplicates_removed': duplicates,
                'deduplication_rate': (duplicates / original * 100) if original > 0 else 0
            }
        
        report['summary']['total_duplicates_removed'] = total_duplicates
        report['summary']['total_original_items'] = total_original
        report['summary']['total_final_items'] = total_final
        report['summary']['deduplication_rate'] = (total_duplicates / total_original * 100) if total_original > 0 else 0
        
        # Generate recommendations
        if total_duplicates > 0:
            report['recommendations'].append(f"Removed {total_duplicates} duplicate items ({report['summary']['deduplication_rate']:.1f}% reduction)")
        
        for source, data in report['by_source'].items():
            if data['deduplication_rate'] > 10:
                report['recommendations'].append(f"High duplication in {source}: {data['deduplication_rate']:.1f}% duplicates")
        
        # Save report
        report_file = self.deduplicated_dir / "deduplication_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Deduplication report saved to {report_file}")
        
        return report
    
    def run_deduplication(self):
        """Run complete deduplication process"""
        logger.info("Starting data deduplication process...")
        
        # Run deduplication for each source
        results = {
            'twitter': self.deduplicate_twitter_data(),
            'reddit': self.deduplicate_reddit_data(),
            'telegram': self.deduplicate_telegram_data(),
            'news': self.deduplicate_news_data()
        }
        
        # Create deduplicated consolidated data
        consolidated_data = self.create_deduplicated_consolidated_data(results)
        
        # Generate report
        report = self.generate_deduplication_report(results)
        
        # Print summary
        print("\n" + "="*60)
        print("DATA DEDUPLICATION SUMMARY")
        print("="*60)
        
        total_duplicates = report['summary']['total_duplicates_removed']
        total_original = report['summary']['total_original_items']
        total_final = report['summary']['total_final_items']
        
        print(f"Total Items: {total_original:,} → {total_final:,}")
        print(f"Duplicates Removed: {total_duplicates:,}")
        print(f"Deduplication Rate: {report['summary']['deduplication_rate']:.1f}%")
        
        print(f"\nBy Source:")
        for source, data in report['by_source'].items():
            print(f"  {source.title()}: {data['original_count']:,} → {data['final_count']:,} (-{data['duplicates_removed']:,})")
        
        print(f"\nFiles saved in: {self.deduplicated_dir}")
        print("="*60)
        
        return results, consolidated_data, report

def main():
    """Main function to run deduplication"""
    deduplicator = DataDeduplicator()
    results, consolidated_data, report = deduplicator.run_deduplication()
    
    print("\n🎉 Deduplication completed successfully!")
    print("You can now use the deduplicated data files.")

if __name__ == "__main__":
    main() 