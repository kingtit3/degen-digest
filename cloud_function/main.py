import json
import logging
import os
from datetime import datetime

import functions_framework
from google.cloud import storage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
GCS_BUCKET = os.getenv("BUCKET_NAME", "degen-digest-data")
PROJECT_ID = os.getenv("PROJECT_ID")


@functions_framework.http
def migrate(request):
    """HTTP Cloud Function for migrating data from GCS to Cloud SQL."""
    try:
        logger.info("Starting migration check...")

        # GCS client
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(GCS_BUCKET)

        # Get all consolidated files
        blobs = list(bucket.list_blobs(prefix="consolidated/"))
        logger.info(f"Found {len(blobs)} consolidated files.")

        # Just return the file count for now - we'll implement the actual migration later
        file_count = len([b for b in blobs if b.name.endswith(".json")])

        logger.info(f"Migration check complete. Found {file_count} JSON files.")

        return (
            json.dumps(
                {
                    "status": "success",
                    "files_found": file_count,
                    "timestamp": datetime.now().isoformat(),
                    "message": "Migration check completed - actual migration will be implemented next",
                }
            ),
            200,
            {"Content-Type": "application/json"},
        )

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return (
            json.dumps(
                {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
            {"Content-Type": "application/json"},
        )
