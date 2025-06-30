import functions_framework
import subprocess
import sys
import os
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@functions_framework.http
def refresh_data(request):
    """Cloud Function to refresh all data sources and regenerate PDFs"""
    
    try:
        logger.info("Starting automated data refresh...")
        
        # Change to the app directory
        os.chdir('/workspace')
        
        # Run all scrapers
        scrapers = [
            "python -m scrapers.twitter_apify",
            "python -m scrapers.telegram_telethon", 
            "python -m scrapers.reddit_rss",
            "python -m scrapers.newsapi_headlines",
            "python -m scrapers.coingecko_gainers"
        ]
        
        for scraper in scrapers:
            logger.info(f"Running {scraper}")
            result = subprocess.run(scraper.split(), capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Scraper failed: {scraper}")
                logger.error(f"Error: {result.stderr}")
            else:
                logger.info(f"Scraper completed: {scraper}")
        
        # Run main processing pipeline
        logger.info("Running main processing pipeline...")
        result = subprocess.run(["python", "main.py"], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Main pipeline failed: {result.stderr}")
        else:
            logger.info("Main pipeline completed")
        
        # Generate review PDF
        logger.info("Generating review PDF...")
        result = subprocess.run(["python", "generate_review.py"], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Review generation failed: {result.stderr}")
        else:
            logger.info("Review PDF generated")
        
        logger.info("Data refresh completed successfully!")
        
        return {
            'status': 'success',
            'message': 'Data refresh completed successfully',
            'timestamp': str(subprocess.run(['date'], capture_output=True, text=True).stdout.strip())
        }
        
    except Exception as e:
        logger.error(f"Data refresh failed: {str(e)}")
        return {
            'status': 'error',
            'message': f'Data refresh failed: {str(e)}',
            'timestamp': str(subprocess.run(['date'], capture_output=True, text=True).stdout.strip())
        }, 500 