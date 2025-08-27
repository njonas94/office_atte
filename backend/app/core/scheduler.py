import schedule
import time
import redis
import logging
from datetime import datetime
from app.db.database_manager import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataRefreshScheduler:
    def __init__(self):
        self.redis_client = redis.Redis(host='redis', port=6379, db=0)
        self.db_manager = DatabaseManager()
    
    async def refresh_data_cache(self):
        """Refresh cached data"""
        try:
            logger.info("Starting data cache refresh...")
            
            # Connect to database
            await self.db_manager.connect()
            
            # Clear relevant cache keys
            keys_to_clear = [
                "employees*",
                "attendance*", 
                "monthly_all*",
                "employee_info*"
            ]
            
            for pattern in keys_to_clear:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                    logger.info(f"Cleared {len(keys)} cache keys matching {pattern}")
            
            # Pre-warm cache with frequently accessed data
            await self._prewarm_cache()
            
            # Disconnect from database
            await self.db_manager.disconnect()
            
            logger.info("Data cache refresh completed successfully")
            
        except Exception as e:
            logger.error(f"Error during cache refresh: {e}")
    
    async def _prewarm_cache(self):
        """Pre-warm cache with frequently accessed data"""
        try:
            # Get current month data
            current_date = datetime.now()
            
            # Pre-warm employees list
            await self.db_manager.get_all_employees()
            logger.info("Pre-warmed employees cache")
            
            # Pre-warm current month attendance data
            await self.db_manager.get_monthly_attendance_all_employees(
                current_date.year, 
                current_date.month
            )
            logger.info("Pre-warmed current month attendance cache")
            
            # Pre-warm previous month data if we're early in the month
            if current_date.day <= 5:
                prev_month = current_date.month - 1 if current_date.month > 1 else 12
                prev_year = current_date.year if current_date.month > 1 else current_date.year - 1
                
                await self.db_manager.get_monthly_attendance_all_employees(
                    prev_year, 
                    prev_month
                )
                logger.info("Pre-warmed previous month attendance cache")
            
        except Exception as e:
            logger.error(f"Error pre-warming cache: {e}")
    
    def run_refresh_job(self):
        """Wrapper to run async refresh job"""
        import asyncio
        asyncio.run(self.refresh_data_cache())
    
    def start_scheduler(self):
        """Start the scheduler"""
        logger.info("Starting data refresh scheduler...")
        
        # Schedule refresh every 12 hours
        schedule.every(12).hours.do(self.run_refresh_job)
        
        # Run initial refresh
        self.run_refresh_job()
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

if __name__ == "__main__":
    scheduler = DataRefreshScheduler()
    scheduler.start_scheduler()