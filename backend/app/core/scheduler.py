"""
Background Scheduler Service

This module provides automatic scheduling of product searches.
Searches run every 2 hours for all active search requests.
Daily digest emails are sent at 9 AM.

"""
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timezone
import logging
from typing import Optional

from app.database import SessionLocal
from app.models import SearchRequest, SearchStatus
from app.core.orchestrator import SearchOrchestrator
from app.services.email_service import EmailService
from app.config import settings

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)




class SearchScheduler:
    """
    Manages automatic execution of product searches.
    
    The scheduler runs as a background service and executes
    searches for all active search requests every 2 hours.
    
    Example:
        ```python
        scheduler = SearchScheduler()
        scheduler.start()  # Starts the scheduler
        # ... app runs ...
        scheduler.shutdown()  # Stops the scheduler
        ```
    """
    
    def __init__(self):
        """Initialize the scheduler."""
        # Create an async scheduler (works with FastAPI)
        self.scheduler = AsyncIOScheduler()
        self._is_running = False
        self.email_service = EmailService(settings)
        logger.info("SearchScheduler initialized")
    
    def start(self):
        """
        Start the scheduler.
        
        This method:
        1. Configures the scheduler to run every 2 hours
        2. Configures daily digest to run at 9 AM
        3. Starts the background scheduler
        4. Optionally runs an immediate search on startup
        """
        if self._is_running:
            logger.warning("Scheduler is already running")
            return
        
        try:
            # Add the search job to run every 2 hours
            self.scheduler.add_job(
                func=self._run_all_searches,  # The function to call
                trigger=IntervalTrigger(hours=2),  # Run every 2 hours
                id='search_job',  # Unique identifier
                name='Run All Product Searches',  # Human-readable name
                replace_existing=True  # Replace if job already exists
            )
            
            # Add the daily digest job to run at 9 AM
            self.scheduler.add_job(
                func=self._send_daily_digest,  # The function to call
                trigger=CronTrigger(hour=9, minute=0),  # Run at 9:00 AM daily
                id='daily_digest_job',  # Unique identifier
                name='Send Daily Digest Emails',  # Human-readable name
                replace_existing=True  # Replace if job already exists
            )
            
            # Start the scheduler
            self.scheduler.start()
            self._is_running = True
            
            logger.info("✅ Scheduler started successfully")
            logger.info("📅 Searches will run every 2 hours")
            logger.info("📧 Daily digest will be sent at 9:00 AM")
            
            # Optional: Run searches immediately on startup
            # Only if there's a running event loop (e.g., in FastAPI context)
            try:
                loop = asyncio.get_running_loop()
                asyncio.create_task(self._run_all_searches())
                logger.info("🚀 Triggered immediate search execution")
            except RuntimeError:
                # No event loop running (e.g., in tests or standalone mode)
                logger.debug("No event loop running, skipping immediate search execution")
            
        except Exception as e:
            logger.error(f"❌ Failed to start scheduler: {str(e)}")
            raise
    async def _send_daily_digest(self):
        """
        Send daily digest emails to all users with digest enabled.
        
        This method:
        1. Queries products from the last 24 hours
        2. Gets email preferences with digest enabled
        3. Groups matches by email address
        4. Sends digest email to each user
        5. Logs comprehensive statistics
        """
        start_time = datetime.now()
        logger.info("=" * 80)
        logger.info("📧 DAILY DIGEST EMAIL JOB STARTED")
        logger.info(f"⏰ Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)
        
        db = None
        success_count = 0
        failure_count = 0
        total_matches = 0
        
        try:
            # Create database session
            db = SessionLocal()
            
            # Prepare digest data
            logger.info("📊 Preparing daily digest data...")
            digest_data = await self.email_service.prepare_daily_digest_data(db)
            
            if not digest_data:
                logger.info("ℹ️  No digest data to send (no matches in last 24 hours or no users with digest enabled)")
                return
            
            logger.info(f"📬 Found digest data for {len(digest_data)} email address(es)")
            
            # Send digest to each email address
            for email, matches in digest_data.items():
                try:
                    match_count = len(matches)
                    total_matches += match_count
                    
                    logger.info(f"📤 Sending digest to {email} ({match_count} match(es))...")
                    
                    # Send the digest email
                    await self.email_service.send_daily_digest(
                        email=email,
                        matches=matches
                    )
                    
                    success_count += 1
                    logger.info(f"✅ Successfully sent digest to {email}")
                    
                except Exception as e:
                    failure_count += 1
                    logger.error(f"❌ Failed to send digest to {email}: {str(e)}")
                    logger.exception(e)
            
            # Log summary statistics
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info("=" * 80)
            logger.info("📧 DAILY DIGEST EMAIL JOB COMPLETED")
            logger.info(f"⏰ End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"⏱️  Duration: {duration:.2f} seconds")
            logger.info(f"✅ Successful: {success_count}")
            logger.info(f"❌ Failed: {failure_count}")
            logger.info(f"📦 Total Matches: {total_matches}")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error("=" * 80)
            logger.error("❌ DAILY DIGEST EMAIL JOB FAILED")
            logger.error(f"Error: {str(e)}")
            logger.exception(e)
            logger.error("=" * 80)
            raise
        
        finally:
            # Always close the database session
            if db:
                db.close()
                logger.debug("Database session closed")
    
    def get_digest_job_info(self) -> dict:
        """
        Get information about the daily digest job.
        
        Returns:
            dict: Job information including next run time and status
        """
        try:
            job = self.scheduler.get_job('daily_digest_job')
            
            if job is None:
                return {
                    'status': 'not_scheduled',
                    'message': 'Daily digest job is not scheduled',
                    'next_run_time': None
                }
            
            next_run = job.next_run_time
            
            return {
                'status': 'scheduled',
                'job_id': job.id,
                'job_name': job.name,
                'next_run_time': next_run.isoformat() if next_run else None,
                'trigger': str(job.trigger),
                'message': f'Next digest will be sent at {next_run.strftime("%Y-%m-%d %H:%M:%S")}' if next_run else 'No next run time'
            }
            
        except Exception as e:
            logger.error(f"Error getting digest job info: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error: {str(e)}',
                'next_run_time': None
            }
    
    def get_all_jobs_info(self) -> dict:
        """
        Get information about all scheduled jobs.
        
        Returns:
            dict: Information about all jobs including search and digest
        """
        try:
            jobs = self.scheduler.get_jobs()
            
            jobs_info = {
                'scheduler_running': self._is_running,
                'total_jobs': len(jobs),
                'jobs': []
            }
            
            for job in jobs:
                next_run = job.next_run_time
                jobs_info['jobs'].append({
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': next_run.isoformat() if next_run else None,
                    'trigger': str(job.trigger)
                })
            
            return jobs_info
            
        except Exception as e:
            logger.error(f"Error getting all jobs info: {str(e)}")
            return {
                'scheduler_running': self._is_running,
                'error': str(e)
            }

    

    def shutdown(self):
        """
        Shutdown the scheduler gracefully.
        
        This method:
        1. Stops accepting new jobs
        2. Waits for running jobs to complete
        3. Shuts down the scheduler
        """
        if not self._is_running:
            logger.warning("Scheduler is not running")
            return
        
        try:
            logger.info("🛑 Shutting down scheduler...")
            
            # Shutdown the scheduler
            # wait=True means wait for running jobs to finish
            self.scheduler.shutdown(wait=True)
            
            self._is_running = False
            logger.info("✅ Scheduler shut down successfully")
            
        except Exception as e:
            logger.error(f"❌ Error shutting down scheduler: {str(e)}")
            raise

    async def _run_all_searches(self):
        """
        Run searches for all active search requests.
        
        This method:
        1. Gets all active search requests from database
        2. Runs each search using the orchestrator
        3. Logs results and errors
        
        This is the method that gets called every 2 hours.
        """
        logger.info("=" * 70)
        logger.info("🔍 Starting scheduled search execution")
        logger.info(f"⏰ Time: {datetime.now(timezone.utc)}")
        logger.info("=" * 70)
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Step 1: Get all active search requests
            active_searches = db.query(SearchRequest).filter(
                SearchRequest.status == SearchStatus.ACTIVE.value
            ).all()
            
            logger.info(f"📊 Found {len(active_searches)} active search requests")
            
            if not active_searches:
                logger.info("ℹ️  No active searches to run")
                return
            
            # Step 2: Run each search
            for search_request in active_searches:
                try:
                    logger.info(f"\n🔎 Running search: {search_request.product_name}")
                    logger.info(f"   ID: {search_request.id}")
                    logger.info(f"   Location: {search_request.location}")
                    
                    # Create orchestrator and run search
                    orchestrator = SearchOrchestrator(db)
                    execution = await orchestrator.execute_search(search_request)
                    
                    # Log results
                    if execution.status == 'completed':
                        logger.info(f"✅ Search completed successfully")
                        logger.info(f"   Products found: {execution.products_found}")
                        logger.info(f"   Matches: {execution.matches_found}")
                    else:
                        logger.warning(f"⚠️  Search failed: {execution.error_message}")
                    
                except Exception as e:
                    logger.error(
                        f"❌ Error running search {search_request.id}: {str(e)}"
                    )
                    # Continue with next search even if this one fails
                    continue
            
            logger.info("\n" + "=" * 70)
            logger.info("✅ Scheduled search execution completed")
            logger.info("=" * 70 + "\n")
            
        except Exception as e:
            logger.error(f"❌ Critical error in scheduled execution: {str(e)}")
            import traceback
            traceback.print_exc()
            
        finally:
            # Always close the database session
            db.close()

    def is_running(self) -> bool:
        """
        Check if the scheduler is currently running.
        
        Returns:
            bool: True if scheduler is running, False otherwise
        """
        return self._is_running

    def get_next_run_time(self) -> Optional[datetime]:
        """
        Get the next scheduled run time.
        
        Returns:
            datetime: Next run time, or None if scheduler not running
            
        Example:
            ```python
            next_run = scheduler.get_next_run_time()
            print(f"Next search at: {next_run}")
            ```
        """
        if not self._is_running:
            return None
        
        try:
            job = self.scheduler.get_job('search_job')
            if job:
                return job.next_run_time
            return None
        except Exception as e:
            logger.error(f"Error getting next run time: {str(e)}")
            return None

    def get_job_info(self) -> dict:
        """
        Get information about the scheduled job.
        
        Returns:
            dict: Job information including next run time, interval, etc.
            
        Example:
            ```python
            info = scheduler.get_job_info()
            print(f"Job: {info['name']}")
            print(f"Next run: {info['next_run']}")
            ```
        """
        if not self._is_running:
            return {
                'status': 'stopped',
                'message': 'Scheduler is not running'
            }
        
        try:
            job = self.scheduler.get_job('search_job')
            if job:
                return {
                    'status': 'running',
                    'job_id': job.id,
                    'name': job.name,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger)
                }
            return {
                'status': 'running',
                'message': 'No job found'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }