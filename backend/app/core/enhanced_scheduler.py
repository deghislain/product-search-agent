from app.models.search_request import SearchRequest


from app.core.scheduler import SearchScheduler
from app.core.adaptive_scheduler import get_adaptive_scheduler
from app.database import SessionLocal
from app.models import SearchRequest, SearchStatus
from app.core.orchestrator import SearchOrchestrator
from typing import List, Optional
from apscheduler.triggers.cron import CronTrigger

import logging
import asyncio
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedSearchScheduler(SearchScheduler):
    def __init__(self):
        super().__init__()
        self.adaptive_scheduler = get_adaptive_scheduler()
    
    def get_active_searches(self) -> List[SearchRequest] | None:
        """Get all active search requests from the database."""  
            # Create database session
        db = SessionLocal()
        active_searches = None
        try:
            active_searches = db.query(SearchRequest).filter(
                    SearchRequest.status == SearchStatus.ACTIVE.value
                ).all()
                
            logger.info(f"📊 Found {len(active_searches)} active search requests")
                
            if not active_searches:
                logger.info("ℹ️  No active searches to run")
                return active_searches

        except Exception as e:
            logger.error(f"❌ Critical error in scheduled execution: {str(e)}")
            import traceback
            traceback.print_exc()
            
        finally:
            # Always close the database session
            db.close()
        return active_searches


       
    async def _run_search(self, search_request_id):
        db = SessionLocal()
        try:
            search_request = db.query(SearchRequest).filter(
                SearchRequest.id == search_request_id
            ).one()
            
            if search_request:
                logger.info(f"\n🔎 Running search: {search_request.product_name}")
                logger.info(f"   ID: {search_request.id}")
                logger.info(f"   Location: {search_request.location}")
                
                # Run the search
                orchestrator = SearchOrchestrator(db)
                execution = await orchestrator.execute_search(search_request)
                
                # Log results
                if execution.status == 'completed':
                    logger.info(f"✅ Search completed successfully")
                    logger.info(f"   Products found: {execution.products_found}")
                    logger.info(f"   Matches: {execution.matches_found}")
                else:
                    logger.warning(f"⚠️  Search failed: {execution.error_message}")
                
                # IMPORTANT: Reschedule next search adaptively
                await self.schedule_search(search_request)
                
        except Exception as e:
            logger.error(f"❌ Error running search {search_request_id}: {str(e)}")
        finally:
            db.close()
    
    async def schedule_search(self, search_request):
        # Use adaptive scheduling instead of fixed interval
        next_time = await self.adaptive_scheduler.get_next_search_time(
            search_request
        )
        
        # Schedule the search
        self.scheduler.add_job(
            func=self._run_search,
            trigger='date',
            run_date=next_time,
            args=[search_request.id]
        )
    async def _analyze_patterns(self):
        """Analyze patterns for all platforms."""
        logger.info("Starting pattern analysis for all platforms...")
        await self.adaptive_scheduler.analyze_all_patterns()

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
            '''
            self.scheduler.add_job(
                func=self._run_all_searches,  # The function to call
                trigger=IntervalTrigger(hours=2),  # Run every 2 hours
                id='search_job',  # Unique identifier
                name='Run All Product Searches',  # Human-readable name
                replace_existing=True  # Replace if job already exists
            )
            '''
            active_searches: List[SearchRequest] | None = self.get_active_searches()
            for search_request in active_searches:
                self.schedule_search(search_request)


            # Add the daily digest job to run at 9 AM
            self.scheduler.add_job(
                func=self._send_daily_digest,  # The function to call
                trigger=CronTrigger(hour=9, minute=0),  # Run at 9:00 AM daily
                id='daily_digest_job',  # Unique identifier
                name='Send Daily Digest Emails',  # Human-readable name
                replace_existing=True  # Replace if job already exists
            )

           
            # Add pattern analysis job to run at 3 AM daily
            self.scheduler.add_job(
                func=self._analyze_patterns,
                trigger=CronTrigger(hour=3, minute=0),
                id='pattern_analysis_job',
                name='Analyze Listing Patterns',
                replace_existing=True
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