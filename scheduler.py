# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from main import MainApp
import logging
from datetime import datetime
import pytz

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='news_scheduler.log'
)
logger = logging.getLogger(__name__)

def process_news():
    """Process and upload news articles"""
    try:
        logger.info("Starting scheduled news processing")
        print(f"\n🕒 Starting news processing at {datetime.now(pytz.UTC)}")
        
        # Initialize the main processor
        processor = MainApp()
        
        # Process and upload articles
        processed_articles = processor.process_articles()
        
        # Log results
        logger.info(f"Processed {len(processed_articles)} articles")
        print(f"✨ Successfully processed {len(processed_articles)} articles")
        
    except Exception as e:
        logger.error(f"Error in scheduled job: {str(e)}")
        print(f"❌ Error during processing: {str(e)}")

def start_scheduler(interval_minutes=30):
    """Start the scheduler with specified interval"""
    try:
        scheduler = BackgroundScheduler()
        
        # Add the job
        scheduler.add_job(
            func=process_news,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id='news_processor',
            name='Process and upload news',
            replace_existing=True,
            max_instances=1,  # Prevent multiple instances
            coalesce=True     # Combine missed runs
        )
        
        # Start the scheduler
        scheduler.start()
        logger.info(f"Scheduler started - running every {interval_minutes} minutes")
        print(f"✅ Scheduler started - will check for news every {interval_minutes} minutes")
        
        return scheduler
        
    except Exception as e:
        logger.error(f"Failed to start scheduler: {str(e)}")
        print(f"❌ Failed to start scheduler: {str(e)}")
        return None

if __name__ == "__main__":
    try:
        # Run once immediately
        print("🚀 Running initial news processing...")
        process_news()
        
        # Start scheduler for subsequent runs
        scheduler = start_scheduler(interval_minutes=75)  # Check every 30 minutes
        
        print("\n⌛ Scheduler is running. Press Ctrl+C to stop.")
        
        # Keep the script running
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("\n🛑 Stopping scheduler...")
            scheduler.shutdown()
            print("✅ Scheduler stopped")
            
    except Exception as e:
        logger.error(f"Main process error: {str(e)}")
        print(f"❌ Error: {str(e)}")