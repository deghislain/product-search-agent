"""
Adaptive Search Scheduler - Learns optimal search times.

This module implements intelligent scheduling that learns when to search
based on listing patterns for each platform. Instead of fixed 2-hour intervals,
it predicts the best times to find new listings.

Key Features:
- Analyzes when new listings appear on each platform
- Learns platform-specific patterns (e.g., Craigslist weekends, eBay Sunday evenings)
- Adjusts search frequency based on activity
- Reduces unnecessary searches during low-activity periods
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import statistics

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import SessionLocal
from app.models import SearchRequest, Product, SearchExecution
from app.core.llm_client import get_groq_client

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



class ListingPattern:
    """Represents learned patterns for a platform."""
    
    def __init__(self, platform: str):
        self.platform = platform
        self.hourly_activity = defaultdict(int)  # Hour of day -> listing count
        self.daily_activity = defaultdict(int)   # Day of week -> listing count
        self.peak_hours = []  # List of peak hours
        self.peak_days = []   # List of peak days
        self.avg_new_listings_per_hour = 0.0
        self.last_updated = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "platform": self.platform,
            "hourly_activity": dict(self.hourly_activity),
            "daily_activity": dict(self.daily_activity),
            "peak_hours": self.peak_hours,
            "peak_days": self.peak_days,
            "avg_new_listings_per_hour": self.avg_new_listings_per_hour,
            "last_updated": self.last_updated.isoformat()
        }


class AdaptiveScheduler:
    """
    Learns optimal search times for each platform/category.
    
    Instead of searching every 2 hours regardless of activity,
    this scheduler learns when new listings typically appear and
    adjusts the search schedule accordingly.
    
    Example insights:
    - Craigslist: Most new listings on weekends 8-10 AM
    - eBay: Auctions end Sunday evenings 6-9 PM
    - Facebook: Peak activity weekday evenings 5-8 PM
    
    Usage:
        ```python
        scheduler = AdaptiveScheduler()
        
        # Analyze patterns (run periodically)
        await scheduler.analyze_all_patterns()
        
        # Get next optimal search time
        next_time = await scheduler.get_next_search_time(search_request)
        
        # Get scheduling recommendation
        recommendation = await scheduler.get_schedule_recommendation(search_request)
        ```
    """
    
    def __init__(self):
        """Initialize the adaptive scheduler."""
        self.listing_patterns: Dict[str, ListingPattern] = {}
        self.llm = get_groq_client()
        logger.info("AdaptiveScheduler initialized")
    
    async def analyze_listing_patterns(
        self,
        platform: str,
        db: Optional[Session] = None
    ) -> ListingPattern:
        """
        Analyze when new listings appear on a platform.
        
        This method:
        1. Queries all products from the platform
        2. Analyzes their created_at timestamps
        3. Identifies peak hours and days
        4. Calculates average listing frequency
        
        Args:
            platform: Platform name (craigslist, ebay, facebook)
            db: Database session (optional, creates new if not provided)
            
        Returns:
            ListingPattern: Learned patterns for the platform
        """
        should_close_db = False
        if db is None:
            db = SessionLocal()
            should_close_db = True
        
        try:
            logger.info(f"Analyzing listing patterns for {platform}...")
            
            # Create pattern object
            pattern = ListingPattern(platform)
            
            # Get all products from this platform (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            products = db.query(Product).filter(
                Product.platform == platform,
                Product.created_at >= thirty_days_ago
            ).all()
            
            if not products:
                logger.warning(f"No products found for {platform} in last 30 days")
                return pattern
            
            logger.info(f"Analyzing {len(products)} products from {platform}")
            
            # Analyze hourly patterns
            for product in products:
                if product.created_at:
                    hour = product.created_at.hour
                    day = product.created_at.weekday()  # 0=Monday, 6=Sunday
                    
                    pattern.hourly_activity[hour] += 1
                    pattern.daily_activity[day] += 1
            
            # Calculate average listings per hour
            total_hours = (datetime.utcnow() - thirty_days_ago).total_seconds() / 3600
            pattern.avg_new_listings_per_hour = len(products) / total_hours
            
            # Identify peak hours (top 25% of activity)
            if pattern.hourly_activity:
                hourly_values = list(pattern.hourly_activity.values())
                threshold = statistics.quantiles(hourly_values, n=4)[2]  # 75th percentile
                pattern.peak_hours = [
                    hour for hour, count in pattern.hourly_activity.items()
                    if count >= threshold
                ]
                pattern.peak_hours.sort()
            
            # Identify peak days (top 3 days)
            if pattern.daily_activity:
                sorted_days = sorted(
                    pattern.daily_activity.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                pattern.peak_days = [day for day, _ in sorted_days[:3]]
            
            # Store pattern
            self.listing_patterns[platform] = pattern
            pattern.last_updated = datetime.utcnow()
            
            logger.info(f"✅ Pattern analysis complete for {platform}")
            logger.info(f"   Peak hours: {pattern.peak_hours}")
            logger.info(f"   Peak days: {self._format_days(pattern.peak_days)}")
            logger.info(f"   Avg listings/hour: {pattern.avg_new_listings_per_hour:.2f}")
            
            return pattern
            
        finally:
            if should_close_db:
                db.close()
    
    async def analyze_all_patterns(self, db: Optional[Session] = None):
        """
        Analyze patterns for all platforms.
        
        Should be run periodically (e.g., daily) to keep patterns up-to-date.
        
        Args:
            db: Database session (optional)
        """
        platforms = ["craigslist", "ebay", "facebook"]
        
        for platform in platforms:
            try:
                await self.analyze_listing_patterns(platform, db)
            except Exception as e:
                logger.error(f"Failed to analyze {platform}: {e}")
    
    async def get_next_search_time(
        self,
        search_request: SearchRequest,
        current_time: Optional[datetime] = None
    ) -> datetime:
        """
        Calculate the optimal next search time for a search request.
        
        Instead of fixed 2-hour intervals, this considers:
        - Platform-specific listing patterns
        - Time of day and day of week
        - Recent search activity
        - Search urgency (based on budget and match quality)
        
        Args:
            search_request: The search request to schedule
            current_time: Current time (defaults to now)
            
        Returns:
            datetime: Optimal time for next search
        """
        if current_time is None:
            current_time = datetime.utcnow()
        
        # Determine which platforms to search
        platforms = []
        if search_request.search_craigslist:
            platforms.append("craigslist")
        if search_request.search_ebay:
            platforms.append("ebay")
        if search_request.search_facebook:
            platforms.append("facebook")
        
        if not platforms:
            # Default to 2 hours if no platforms selected
            return current_time + timedelta(hours=2)
        
        # Get patterns for selected platforms
        relevant_patterns = [
            self.listing_patterns.get(p)
            for p in platforms
            if p in self.listing_patterns
        ]
        
        if not relevant_patterns:
            # No patterns learned yet, use default
            logger.info("No patterns learned yet, using default 2-hour interval")
            return current_time + timedelta(hours=2)
        
        # Find next peak hour across all platforms
        next_peak = self._find_next_peak_time(current_time, relevant_patterns)
        
        # Adjust based on activity level
        avg_activity = statistics.mean([
            p.avg_new_listings_per_hour
            for p in relevant_patterns
        ])
        
        if avg_activity > 5.0:
            # High activity: search more frequently
            max_wait = timedelta(hours=1)
        elif avg_activity > 2.0:
            # Medium activity: normal frequency
            max_wait = timedelta(hours=2)
        else:
            # Low activity: search less frequently
            max_wait = timedelta(hours=4)
        
        # Don't wait longer than max_wait, even if peak is far away
        if next_peak > current_time + max_wait:
            next_peak = current_time + max_wait
        
        logger.info(f"Next search scheduled for {next_peak} "
                   f"(in {(next_peak - current_time).total_seconds() / 3600:.1f} hours)")
        
        return next_peak
    
    def _find_next_peak_time(
        self,
        current_time: datetime,
        patterns: List[ListingPattern]
    ) -> datetime:
        """
        Find the next peak time across multiple platform patterns.
        
        Args:
            current_time: Current time
            patterns: List of platform patterns
            
        Returns:
            datetime: Next peak time
        """
        current_hour = current_time.hour
        current_day = current_time.weekday()
        
        # Collect all peak hours from all patterns
        all_peak_hours = set()
        for pattern in patterns:
            all_peak_hours.update(pattern.peak_hours)
        
        if not all_peak_hours:
            # No peaks identified, default to next hour
            return current_time + timedelta(hours=1)
        
        # Find next peak hour today
        future_peaks_today = [h for h in all_peak_hours if h > current_hour]
        
        if future_peaks_today:
            # Next peak is today
            next_hour = min(future_peaks_today)
            next_time = current_time.replace(
                hour=next_hour,
                minute=0,
                second=0,
                microsecond=0
            )
            return next_time
        else:
            # Next peak is tomorrow
            next_hour = min(all_peak_hours)
            next_time = (current_time + timedelta(days=1)).replace(
                hour=next_hour,
                minute=0,
                second=0,
                microsecond=0
            )
            return next_time
    
    async def get_schedule_recommendation(
        self,
        search_request: SearchRequest,
        db: Optional[Session] = None
    ) -> Dict:
        """
        Get AI-powered scheduling recommendation for a search request.
        
        Uses LLM to analyze patterns and provide human-readable recommendations.
        
        Args:
            search_request: The search request
            db: Database session (optional)
            
        Returns:
            dict: Scheduling recommendation with reasoning
        """
        should_close_db = False
        if db is None:
            db = SessionLocal()
            should_close_db = True
        
        try:
            # Get platforms
            platforms = []
            if search_request.search_craigslist:
                platforms.append("craigslist")
            if search_request.search_ebay:
                platforms.append("ebay")
            if search_request.search_facebook:
                platforms.append("facebook")
            
            # Get patterns
            patterns_info = []
            for platform in platforms:
                if platform in self.listing_patterns:
                    pattern = self.listing_patterns[platform]
                    patterns_info.append(
                        f"{platform.title()}: Peak hours {pattern.peak_hours}, "
                        f"Peak days {self._format_days(pattern.peak_days)}, "
                        f"Avg {pattern.avg_new_listings_per_hour:.1f} listings/hour"
                    )
            
            # Get recent search history
            recent_executions = db.query(SearchExecution).filter(
                SearchExecution.search_request_id == search_request.id
            ).order_by(SearchExecution.started_at.desc()).limit(5).all()
            
            execution_summary = []
            for exe in recent_executions:
                execution_summary.append(
                    f"{exe.started_at.strftime('%a %H:%M')}: "
                    f"{exe.products_found} products, {exe.matches_found} matches"
                )
            
            # Generate recommendation using LLM
            prompt = f"""
Analyze this search schedule and provide recommendations:

SEARCH REQUEST:
- Product: {search_request.product_name}
- Budget: ${search_request.budget}
- Platforms: {', '.join(platforms)}

PLATFORM PATTERNS:
{chr(10).join(patterns_info) if patterns_info else "No patterns learned yet"}

RECENT SEARCH HISTORY:
{chr(10).join(execution_summary) if execution_summary else "No recent searches"}

Provide a scheduling recommendation:
1. Best times to search (specific hours/days)
2. Recommended frequency (how often)
3. Reasoning (why these times are optimal)

Keep it concise and actionable (under 150 words).

Recommendation:"""

            try:
                recommendation = await self.llm.generate(
                    prompt,
                    temperature=0.7,
                    max_tokens=200
                )
            except Exception as e:
                logger.error(f"LLM recommendation failed: {e}")
                recommendation = self._generate_fallback_recommendation(
                    platforms,
                    patterns_info
                )
            
            # Calculate next search time
            next_search = await self.get_next_search_time(search_request)
            
            return {
                "search_request_id": search_request.id,
                "platforms": platforms,
                "next_search_time": next_search.isoformat(),
                "hours_until_next": (next_search - datetime.utcnow()).total_seconds() / 3600,
                "recommendation": recommendation.strip(),
                "patterns_analyzed": len(patterns_info) > 0
            }
            
        finally:
            if should_close_db:
                db.close()
    
    def _format_days(self, days: List[int]) -> str:
        """Convert day numbers to names."""
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        return ", ".join([day_names[d] for d in sorted(days)])
    
    def _generate_fallback_recommendation(
        self,
        platforms: List[str],
        patterns_info: List[str]
    ) -> str:
        """Generate a simple recommendation when LLM fails."""
        if patterns_info:
            return (
                f"Based on learned patterns for {', '.join(platforms)}, "
                f"I recommend searching during peak activity times. "
                f"This will maximize your chances of finding new listings."
            )
        else:
            return (
                f"No patterns learned yet for {', '.join(platforms)}. "
                f"I'll search every 2 hours initially and learn optimal times "
                f"as we collect more data."
            )
    
    def get_pattern_summary(self) -> Dict:
        """
        Get a summary of all learned patterns.
        
        Returns:
            dict: Summary of patterns for all platforms
        """
        summary = {}
        for platform, pattern in self.listing_patterns.items():
            summary[platform] = {
                "peak_hours": pattern.peak_hours,
                "peak_days": self._format_days(pattern.peak_days),
                "avg_listings_per_hour": round(pattern.avg_new_listings_per_hour, 2),
                "last_updated": pattern.last_updated.isoformat(),
                "total_hourly_data_points": sum(pattern.hourly_activity.values())
            }
        return summary


# Singleton instance
_adaptive_scheduler = None

def  get_adaptive_scheduler() -> AdaptiveScheduler:
    """Get or create the adaptive scheduler singleton."""
    global _adaptive_scheduler
    if _adaptive_scheduler is None:
        _adaptive_scheduler = AdaptiveScheduler()
    return _adaptive_scheduler

# Made with Bob
