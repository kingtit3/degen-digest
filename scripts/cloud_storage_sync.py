#!/usr/bin/env python3
"""
Google Cloud Storage Sync for Degen Digest
Syncs local data with Google Cloud Storage bucket.
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any, Optional

# Google Cloud Storage imports
try:
    from google.cloud import storage
    from google.cloud.exceptions import NotFound
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    print("Warning: Google Cloud Storage not available. Install with: pip install google-cloud-storage")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CloudStorageSync:
    def __init__(self, bucket_name: str = "degen-digest-data", local_root: str = ".", project_id: str = "lucky-union-463615-t3"):
        self.bucket_name = bucket_name
        self.local_root = Path(local_root)
        self.output_dir = self.local_root / "output"
        self.project_id = project_id
        
        if GCS_AVAILABLE:
            try:
                self.client = storage.Client(project=project_id)
                self.bucket = self.client.bucket(bucket_name)
                # Create bucket if it doesn't exist
                if not self.bucket.exists():
                    self.bucket.create(project=project_id)
                    logger.info(f"Created bucket: {bucket_name} in project: {project_id}")
                else:
                    logger.info(f"Using existing bucket: {bucket_name} in project: {project_id}")
            except Exception as e:
                logger.error(f"Error accessing bucket {bucket_name} in project {project_id}: {e}")
                self.bucket = None
        else:
            self.bucket = None
            logger.warning("Google Cloud Storage not available")
    
    def upload_file(self, local_path: Path, cloud_path: str) -> bool:
        """Upload a single file to cloud storage"""
        if not self.bucket or not GCS_AVAILABLE:
            logger.warning("Cloud storage not available, skipping upload")
            return False
        
        try:
            blob = self.bucket.blob(cloud_path)
            blob.upload_from_filename(str(local_path))
            logger.info(f"Uploaded: {local_path} -> {cloud_path}")
            return True
        except Exception as e:
            logger.error(f"Error uploading {local_path}: {e}")
            return False
    
    def download_file(self, cloud_path: str, local_path: Path) -> bool:
        """Download a single file from cloud storage"""
        if not self.bucket or not GCS_AVAILABLE:
            logger.warning("Cloud storage not available, skipping download")
            return False
        
        try:
            blob = self.bucket.blob(cloud_path)
            if not blob.exists():
                logger.warning(f"File not found in cloud: {cloud_path}")
                return False
            
            local_path.parent.mkdir(parents=True, exist_ok=True)
            blob.download_to_filename(str(local_path))
            logger.info(f"Downloaded: {cloud_path} -> {local_path}")
            return True
        except Exception as e:
            logger.error(f"Error downloading {cloud_path}: {e}")
            return False
    
    def upload_all_data(self):
        """Upload all important data files to cloud storage"""
        logger.info("Uploading all data to cloud storage...")
        
        # Files to upload
        files_to_upload = [
            ("twitter_raw.json", "data/twitter_raw.json"),
            ("reddit_raw.json", "data/reddit_raw.json"),
            ("telegram_raw.json", "data/telegram_raw.json"),
            ("newsapi_raw.json", "data/newsapi_raw.json"),
            ("coingecko_raw.json", "data/coingecko_raw.json"),
            ("enhanced_twitter_data.json", "data/enhanced_twitter_data.json"),
            ("health_metrics.json", "data/health_metrics.json"),
            ("health_alerts.json", "data/health_alerts.json"),
            ("consolidated_data.json", "data/consolidated_data.json"),
            ("degen_digest.db", "database/degen_digest.db"),
        ]
        
        # Enhanced pipeline files
        pipeline_files = [
            ("enhanced_pipeline/viral_predictions.json", "enhanced_pipeline/viral_predictions.json"),
            ("enhanced_pipeline/processed_data.json", "enhanced_pipeline/processed_data.json"),
            ("enhanced_pipeline/summary_report.json", "enhanced_pipeline/summary_report.json"),
            ("enhanced_pipeline/trends_analysis.json", "enhanced_pipeline/trends_analysis.json"),
            ("enhanced_pipeline/pipeline_stats.json", "enhanced_pipeline/pipeline_stats.json"),
        ]
        
        files_to_upload.extend(pipeline_files)
        
        uploaded_count = 0
        for local_filename, cloud_path in files_to_upload:
            local_path = self.output_dir / local_filename
            if local_path.exists():
                if self.upload_file(local_path, cloud_path):
                    uploaded_count += 1
            else:
                logger.warning(f"Local file not found: {local_filename}")
        
        logger.info(f"Uploaded {uploaded_count} files to cloud storage")
        return uploaded_count
    
    def download_all_data(self):
        """Download all data files from cloud storage"""
        logger.info("Downloading all data from cloud storage...")
        
        # Files to download
        files_to_download = [
            ("data/twitter_raw.json", "twitter_raw.json"),
            ("data/reddit_raw.json", "reddit_raw.json"),
            ("data/telegram_raw.json", "telegram_raw.json"),
            ("data/newsapi_raw.json", "newsapi_raw.json"),
            ("data/coingecko_raw.json", "coingecko_raw.json"),
            ("data/enhanced_twitter_data.json", "enhanced_twitter_data.json"),
            ("data/health_metrics.json", "health_metrics.json"),
            ("data/health_alerts.json", "health_alerts.json"),
            ("data/consolidated_data.json", "consolidated_data.json"),
            ("database/degen_digest.db", "degen_digest.db"),
        ]
        
        # Enhanced pipeline files
        pipeline_files = [
            ("enhanced_pipeline/viral_predictions.json", "enhanced_pipeline/viral_predictions.json"),
            ("enhanced_pipeline/processed_data.json", "enhanced_pipeline/processed_data.json"),
            ("enhanced_pipeline/summary_report.json", "enhanced_pipeline/summary_report.json"),
            ("enhanced_pipeline/trends_analysis.json", "enhanced_pipeline/trends_analysis.json"),
            ("enhanced_pipeline/pipeline_stats.json", "enhanced_pipeline/pipeline_stats.json"),
        ]
        
        files_to_download.extend(pipeline_files)
        
        downloaded_count = 0
        for cloud_path, local_filename in files_to_download:
            local_path = self.output_dir / local_filename
            if self.download_file(cloud_path, local_path):
                downloaded_count += 1
        
        logger.info(f"Downloaded {downloaded_count} files from cloud storage")
        return downloaded_count
    
    def sync_data(self, direction: str = "both"):
        """Sync data between local and cloud storage"""
        logger.info(f"Syncing data (direction: {direction})...")
        
        if direction == "upload" or direction == "both":
            self.upload_all_data()
        
        if direction == "download" or direction == "both":
            self.download_all_data()
    
    def list_cloud_files(self) -> List[str]:
        """List all files in cloud storage"""
        if not self.bucket or not GCS_AVAILABLE:
            logger.warning("Cloud storage not available")
            return []
        
        try:
            blobs = self.bucket.list_blobs()
            files = [blob.name for blob in blobs]
            logger.info(f"Found {len(files)} files in cloud storage")
            return files
        except Exception as e:
            logger.error(f"Error listing cloud files: {e}")
            return []
    
    def get_file_metadata(self, cloud_path: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a cloud file"""
        if not self.bucket or not GCS_AVAILABLE:
            return None
        
        try:
            blob = self.bucket.blob(cloud_path)
            if not blob.exists():
                return None
            
            return {
                'name': blob.name,
                'size': blob.size,
                'updated': blob.updated.isoformat(),
                'content_type': blob.content_type,
                'md5_hash': blob.md5_hash
            }
        except Exception as e:
            logger.error(f"Error getting metadata for {cloud_path}: {e}")
            return None
    
    def backup_database(self):
        """Create a timestamped backup of the database in cloud storage"""
        if not self.bucket or not GCS_AVAILABLE:
            logger.warning("Cloud storage not available")
            return False
        
        db_path = self.output_dir / "degen_digest.db"
        if not db_path.exists():
            logger.warning("Local database not found")
            return False
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        cloud_backup_path = f"backups/degen_digest_{timestamp}.db"
        
        return self.upload_file(db_path, cloud_backup_path)
    
    def restore_database(self, backup_timestamp: str):
        """Restore database from a cloud backup"""
        if not self.bucket or not GCS_AVAILABLE:
            logger.warning("Cloud storage not available")
            return False
        
        cloud_backup_path = f"backups/degen_digest_{backup_timestamp}.db"
        local_restore_path = self.output_dir / f"degen_digest_restored_{backup_timestamp}.db"
        
        return self.download_file(cloud_backup_path, local_restore_path)

def main():
    """Main function to run cloud storage sync"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sync Degen Digest data with Google Cloud Storage")
    parser.add_argument("--direction", choices=["upload", "download", "both"], default="both",
                       help="Direction of sync (default: both)")
    parser.add_argument("--bucket", default="degen-digest-data",
                       help="Cloud storage bucket name")
    parser.add_argument("--project", default="lucky-union-463615-t3",
                       help="Google Cloud project ID")
    parser.add_argument("--list", action="store_true",
                       help="List files in cloud storage")
    parser.add_argument("--backup", action="store_true",
                       help="Create database backup")
    parser.add_argument("--restore", type=str,
                       help="Restore database from backup timestamp (YYYYMMDD_HHMMSS)")
    
    args = parser.parse_args()
    
    sync = CloudStorageSync(bucket_name=args.bucket, project_id=args.project)
    
    if args.list:
        files = sync.list_cloud_files()
        print("\nCloud Storage Files:")
        for file in files:
            print(f"  {file}")
    
    elif args.backup:
        if sync.backup_database():
            print("Database backup created successfully")
        else:
            print("Failed to create database backup")
    
    elif args.restore:
        if sync.restore_database(args.restore):
            print(f"Database restored from backup: {args.restore}")
        else:
            print(f"Failed to restore database from backup: {args.restore}")
    
    else:
        sync.sync_data(direction=args.direction)
        print("Cloud storage sync completed!")

if __name__ == "__main__":
    main() 