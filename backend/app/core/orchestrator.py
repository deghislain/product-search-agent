"""
Search Orchestrator - Coordinates multi-platform product searches
"""
from app.models.product import Product
from this import d
from typing import Any, List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import asyncio
import logging

from app.models.search_request import SearchRequest
from app.models.product import Product
from app.models.search_execution import SearchExecution
from app.models.email_preference import EmailPreference
from app.scrapers.craigslist import CraigslistScraper
from app.scrapers.ebay_factory import get_ebay_scraper, EbayScraperType
from app.scrapers.facebook_marketplace import FacebookMarketplaceScraper
from app.core.matching import ProductMatcher
from app.core.personalized_scoring import PersonalizedScoreCalculator
from app.services.email_service import EmailService
from app.config import settings

from app.core.websocket_manager import manager
from app.schemas.notification import (
    WebSocketMatchFoundNotification,
    WebSocketSearchStatusNotification,
    WebSocketErrorNotification
)
from datetime import datetime

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



class SearchOrchestrator:
    """
    Orchestrates product searches across multiple platforms.
    
    Responsibilities:
    - Coordinate scraper execution
    - Integrate matching engine
    - Save results to database
    - Handle errors and retries
    """
    
    def __init__(self, db: Session):
        """Initialize orchestrator with database session."""
        self.db = db
        self.matching_engine = ProductMatcher(min_score_threshold = 85.0)
        self.personalized_scorer = PersonalizedScoreCalculator(db=db)
        self.email_service = EmailService(settings)
        
        # Initialize scrapers
        self.scrapers = {
            'craigslist': CraigslistScraper(),
            'ebay': get_ebay_scraper(scraper_type=EbayScraperType.AUTO),
            'facebook': FacebookMarketplaceScraper()
        }
    
    async def execute_search(
        self,
        search_request: SearchRequest,
        user_id: Optional[str] = None
    ) -> SearchExecution:
        """
        Execute a complete search across all enabled platforms.
        
        Args:
            search_request: The search request to execute
            user_id: Optional user ID for personalized scoring
            
        Returns:
            SearchExecution: Record of the search execution
            
        Workflow:
        1. Create execution record
        2. Search each platform
        3. Match products against criteria (with personalization if user_id provided)
        4. Save results to database
        5. Update execution status
        """
        logger.info(f"Starting search execution for request {search_request.id}")
        if user_id:
            logger.info(f"Using personalized scoring for user: {user_id}")
        
        # Step 1: Create execution record
        execution = SearchExecution(
            search_request_id=search_request.id,
            status='running',
            started_at=datetime.now(timezone.utc)
        )
        self.db.add(execution)
        self.db.commit()
        
        try:
            # Send search started notification
            await self._notify_search_started(search_request, execution)
            
            # Step 2: Get platforms to search
            platforms = self._get_active_platforms(search_request)
            
            # Step 3: Search all platforms concurrently
            all_products_dicts = await self._search_all_platforms(
                search_request,
                platforms
            )
            
            # Step 3.5: Convert dictionaries to Product objects (with image fetching)
            all_products = await self._convert_dicts_to_products(all_products_dicts)
            
            # Step 4: Match products against criteria (with personalization)
            matched_products = await self._match_products(
                search_request,
                all_products,
                user_id
            )
            
            # Step 5: Save results to database and send notifications
            await self._save_products(matched_products, execution.id, search_request.id)
            
            # Step 6: Update execution status
            execution.status = 'completed'
            execution.completed_at = datetime.now(timezone.utc)
            execution.products_found = len(all_products)  # Total products found
            execution.matches_found = len(matched_products)  # Products that passed threshold
            
            logger.info(
                f"Search execution {execution.id} completed. "
                f"Found {len(matched_products)} matching products"
            )
            
            # Send search completed notification
            await self._notify_search_completed(search_request, execution, len(matched_products))
            
        except Exception as e:
            logger.error(f"Search execution {execution.id} failed: {str(e)}")
            execution.status = 'failed'
            execution.error_message = str(e)
            execution.completed_at = datetime.now(timezone.utc)
            
            # Send error notification
            await self._notify_error(search_request, str(e))
            
        finally:
            self.db.commit()
            
        return execution
    async def execute_search_immediately(
        self,
        search_request_id: str,
        db: Session
    ) -> None:
        """
        Execute a search immediately (called as background task).
        
        This method is designed to be called as a FastAPI background task.
        It creates its own database session and handles all errors gracefully.
        
        Args:
            search_request_id: ID of the search request to execute
            db: Database session (will be used and closed by this method)
            
        Note:
            This method is async and can be run in the background without
            blocking the API response to the user.
        """
        try:
            logger.info(f"🚀 Starting immediate execution for search request {search_request_id}")
            
            # Get search request from database
            search_request = db.query(SearchRequest).filter(
                SearchRequest.id == search_request_id
            ).first()
            
            if not search_request:
                logger.error(f"❌ Search request {search_request_id} not found")
                return
            
            # Update orchestrator's db session to use the provided one
            original_db = self.db
            self.db = db
            
            try:
                # Execute the search using the main execute_search method
                execution = await self.execute_search(search_request)
                
                logger.info(
                    f"✅ Immediate execution completed for search request {search_request_id}. "
                    f"Status: {execution.status}, Products found: {execution.products_found}"
                )
            finally:
                # Restore original db session
                self.db = original_db
            
        except Exception as e:
            logger.error(f"❌ Error in immediate execution for {search_request_id}: {str(e)}", exc_info=True)
        finally:
            # Always close the database session
            try:
                db.close()
                logger.debug(f"Database session closed for search request {search_request_id}")
            except Exception as e:
                logger.error(f"Error closing database session: {str(e)}")


    def _get_active_platforms(self, search_request: SearchRequest) -> List[str]:
        """
        Get list of platforms to search based on search request settings.
        
        If no platforms are explicitly selected, searches ALL platforms by default.
        If any platform is selected, only searches the selected platforms.
        
        Args:
            search_request: The search request
            
        Returns:
            List of platform names to search
        """
        logger.info(f"Getting list of platforms to search for request {search_request.id}")
        platforms = []
        
        # Check which platforms are enabled
        if search_request.search_craigslist:
            platforms.append('craigslist')
        if search_request.search_ebay:
            platforms.append('ebay')
        if search_request.search_facebook:
            platforms.append('facebook')
        
        # If no platforms are selected, search ALL platforms by default
        if not platforms:
            platforms = ['craigslist', 'ebay', 'facebook']
            logger.info(f"No platforms selected, defaulting to ALL platforms for search {search_request.id}")
        else:
            logger.info(f"Selected platforms for search {search_request.id}: {platforms}")
            
        return platforms


    async def _search_all_platforms(
        self, 
        search_request: SearchRequest, 
        platforms: List[str]
    ) -> List[Product]:
        """
        Search all platforms concurrently.
        
        Args:
            search_request: The search request
            platforms: List of platform names to search
            
        Returns:
            List of all products found across platforms
        """
        # Create search tasks for each platform
        logger.info(f"Searching all platforms concurrently for request {search_request.id}")
        tasks = [
            self._search_platform(search_request, platform)
            for platform in platforms
        ]
        
        # Run all searches concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results and filter out errors
        all_products: list[Product] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(
                    f"Platform {platforms[i]} search failed: {str(result)}"
                )
            else:
                all_products.extend(result)
                
        logger.info(f"Total products found across all platforms: {len(all_products)}")
        return all_products


    def _normalize_location_for_platform(self, location: Optional[str], platform: str) -> str:
        """
        Normalize location string for specific platform requirements.
        
        Args:
            location: User-provided location (e.g., "USA", "Boston, US", "Halifax, Canada")
            platform: Platform name ('craigslist', 'ebay', 'facebook')
            
        Returns:
            Platform-specific location string
            
        Examples:
            >>> _normalize_location_for_platform("USA", "craigslist")
            'sfbay'  # Default to San Francisco Bay Area
            >>> _normalize_location_for_platform("Boston, US", "craigslist")
            'boston'
            >>> _normalize_location_for_platform("New York", "craigslist")
            'newyork'
        """
        if not location:
            # Default locations per platform
            defaults = {
                'craigslist': 'sfbay',
                'ebay': 'US',
                'facebook': 'US'
            }
            return defaults.get(platform, 'US')
        
        # Normalize location string
        location_lower = location.lower().strip()
        
        if platform == 'craigslist':
            # Map common locations to Craigslist subdomains
            location_map = {
                'usa': 'sfbay',
                'us': 'sfbay',
                'united states': 'sfbay',
                'san francisco': 'sfbay',
                'sf': 'sfbay',
                'bay area': 'sfbay',
                'new york': 'newyork',
                'nyc': 'newyork',
                'ny': 'newyork',
                'los angeles': 'losangeles',
                'la': 'losangeles',
                'chicago': 'chicago',
                'boston': 'boston',
                'seattle': 'seattle',
                'portland': 'portland',
                'denver': 'denver',
                'austin': 'austin',
                'miami': 'miami',
                'atlanta': 'atlanta',
                'philadelphia': 'philadelphia',
                'washington': 'washingtondc',
                'dc': 'washingtondc',
                'dallas': 'dallas',
                'houston': 'houston',
                'phoenix': 'phoenix',
                'san diego': 'sandiego',
                'detroit': 'detroit',
                'minneapolis': 'minneapolis',
                'tampa': 'tampa',
                'baltimore': 'baltimore',
                'st louis': 'stlouis',
                'las vegas': 'lasvegas',
                'sacramento': 'sacramento',
                'halifax': 'sfbay',  # No Halifax on Craigslist, default to sfbay
                'canada': 'sfbay',  # Default Canadian searches to sfbay
            }
            
            # Try exact match first
            if location_lower in location_map:
                return location_map[location_lower]
            
            # Try to extract city name from "City, State" or "City, Country" format
            if ',' in location_lower:
                city = location_lower.split(',')[0].strip()
                if city in location_map:
                    return location_map[city]
            
            # If no match found, default to sfbay
            logger.warning(f"Unknown Craigslist location '{location}', defaulting to 'sfbay'")
            return 'sfbay'
        
        # For other platforms, return as-is
        return location

    async def _search_platform(
        self,
        search_request: SearchRequest,
        platform: str
    ) -> List[Dict]:
        """
        Search a single platform with retry logic.
        
        Args:
            search_request: The search request
            platform: Platform name ('craigslist', 'ebay', 'facebook')
            
        Returns:
            List of products found on this platform
        """
        max_retries = 3
        retry_delay = 5  # seconds
        
        for attempt in range(max_retries):
            try:
                logger.info(
                    f"Searching {platform} (attempt {attempt + 1}/{max_retries})"
                )
                
                # Get the appropriate scraper
                scraper = self.scrapers[platform]
                
                # Normalize location for this platform
                normalized_location = self._normalize_location_for_platform(
                    search_request.location,
                    platform
                )
                logger.info(f"Using location '{normalized_location}' for {platform}")
                
                # Execute search
                products = await scraper.search(
                    query=search_request.product_name,
                    location=normalized_location,
                    max_price=search_request.budget,
                    #min_price=search_request.min_price
                )
                
                logger.info(f"Found {len(products)} products on {platform}")
                return products
                
            except Exception as e:
                logger.warning(
                    f"Attempt {attempt + 1} failed for {platform}: {str(e)}"
                )
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error(f"All retries exhausted for {platform}")
                    raise
                    
        return []

    async def _convert_dicts_to_products(self, product_dicts: List[Dict]) -> List[Product]:
        """
        Convert product dictionaries from scrapers to Product objects.
        Fetches images for Craigslist products if not available.
        
        Args:
            product_dicts: List of product dictionaries from scrapers
            
        Returns:
            List of Product objects
        """
        products = []
        for product_dict in product_dicts:
            try:
                # Get image URL - fetch from detail page for Craigslist if needed
                image_url = product_dict.get('image_url')
                
                # If no image and it's a Craigslist product, try to fetch it
                if not image_url and product_dict.get('platform') == 'craigslist':
                    try:
                        scraper = self.scrapers.get('craigslist')
                        if scraper and hasattr(scraper, 'get_first_image_url'):
                            image_url = await scraper.get_first_image_url(product_dict.get('url', ''))
                            if image_url:
                                logger.debug(f"Fetched image for Craigslist product: {product_dict.get('title', '')[:50]}")
                    except Exception as e:
                        logger.debug(f"Could not fetch image for Craigslist product: {e}")
                
                # Create Product object from dictionary
                # Note: listing_id is not a Product model field, so we skip it
                # Convert posted_date string to datetime object if present
                posted_date = product_dict.get('posted_date')
                if posted_date and isinstance(posted_date, str):
                    try:
                        posted_date = datetime.fromisoformat(posted_date).date()
                    except (ValueError, AttributeError):
                        posted_date = None
                
                product = Product(
                    title=product_dict.get('title', ''),
                    price=product_dict.get('price', 0.0),
                    url=product_dict.get('url', ''),
                    platform=product_dict.get('platform', ''),
                    location=product_dict.get('location'),
                    description=product_dict.get('description'),
                    image_url=image_url,
                    posted_date=posted_date
                )
                products.append(product)
            except Exception as e:
                logger.warning(f"Failed to convert product dict to Product object: {e}")
                continue
        
        logger.info(f"Converted {len(products)} product dictionaries to Product objects")
        return products

    async def _match_products(
        self,
        search_request: SearchRequest,
        products: List[Product],
        user_id: Optional[str] = None
    ) -> List[Product]:
        """
        Match products against search criteria using personalized scoring.
        
        Args:
            search_request: The search request with criteria
            products: List of products to match
            user_id: Optional user ID for personalized scoring
            
        Returns:
            List of products that match criteria (with personalized match scores)
        """
        logger.info(f"Matching {len(products)} products against criteria")
        
        if user_id:
            # Use personalized scoring
            logger.info(f"Using personalized scoring for user {user_id}")
            scored_products = await self.personalized_scorer.score_and_filter_products(
                products=products,
                search_request=search_request,
                user_id=user_id
            )
            # Convert tuples back to list of products with scores set
            matched_products = []
            for product, score in scored_products:
                product.match_score = score
                product.is_match = True
                matched_products.append(product)
        else:
            # Use standard matching engine
            logger.info("Using standard matching (no personalization)")
            matched_products: List[Product] = self.matching_engine.find_matches(
                products=products,
                search_request=search_request
            )
        
        logger.info(
            f"Found {len(matched_products)} products above match threshold"
        )
        
        return matched_products

    async def _save_products(
        self,
        products: List[Product],
        execution_id: int,
        search_request_id: str
    ) -> None:
        """
        Save matched products to database and send notifications.
        
        Args:
            products: List of matched Product objects
            execution_id: ID of the search execution
            search_request_id: ID of the search request (for notifications)
        """
        logger.info(f"Saving {len(products)} products to database")
        
        for product in products:
            # Check if product already exists (duplicate detection using URL)
            existing_product = self.db.query(Product).filter(
                Product.url == product.url
            ).first()
            
            if existing_product:
                # Update existing product
                existing_product.price = product.price
                existing_product.is_match = True
                existing_product.match_score = product.match_score
                # Update search_execution_id to associate with current search
                existing_product.search_execution_id = execution_id
                logger.debug(f"Updated existing product {existing_product.id}")
            else:
                # Set the search_execution_id for the new product
                product.search_execution_id = execution_id
                # Mark as match since it passed the threshold
                product.is_match = True
                
                # Add to database
                self.db.add(product)
                self.db.commit()  # Commit to get the product ID
                self.db.refresh(product)  # Refresh to get the generated ID
                
                logger.debug(f"Created new product: {product.title}")
                
                # Send real-time notification for new match
                await self._notify_match_found(
                    search_request_id=search_request_id,
                    product=product,
                    match_score=product.match_score if product.match_score else 0.0
                )
        
        self.db.commit()
        logger.info("All products saved successfully")
        

    async def _notify_match_found(
        self,
        search_request_id: str,
        product: Product,
        match_score: float
    ):
        """Send real-time notification for new match"""
        try:
            # Use to_dict() method if available, otherwise access attributes directly
            if hasattr(product, 'to_dict'):
                product_dict = product.to_dict()
                notification = WebSocketMatchFoundNotification(
                    message=f"New match found: {product_dict['title']}",
                    search_request_id=search_request_id,
                    product_id=product_dict['id'],
                    product_title=product_dict['title'],
                    product_price=product_dict['price'],
                    product_url=product_dict['url'],
                    match_score=match_score,
                    platform=product_dict['platform']
                )
            else:
                # Fallback: access attributes directly (works after commit/refresh)
                notification = WebSocketMatchFoundNotification(
                    message=f"New match found: {product.title}",
                    search_request_id=search_request_id,
                    product_id=product.id,
                    product_title=product.title,
                    product_price=product.price,
                    product_url=product.url,
                    match_score=match_score,
                    platform=product.platform
                )
            
            # Broadcast to all connected clients
            await manager.broadcast(notification.model_dump(mode='json'))
            logger.info(f"Sent WebSocket match notification for product: {product.title}")
            
            # Send email notification if enabled
            await self._send_match_email(search_request_id, product)
            
        except Exception as e:
            logger.error(f"Failed to send match notification: {str(e)}")
    
    async def _notify_search_started(
        self,
        search_request: SearchRequest,
        execution: SearchExecution
    ):
        """Send notification when search starts"""
        try:
            from app.schemas.notification import NotificationType
            
            notification = WebSocketSearchStatusNotification(
                message=f"Search started: {search_request.product_name}",
                type=NotificationType.SEARCH_STARTED,
                search_request_id=str(search_request.id),
                search_execution_id=str(execution.id) if execution.id else None,
                status="started",
                matches_found=None  # Not applicable for started status
            )
            
            await manager.broadcast(notification.model_dump(mode='json'))
            logger.info(f"Sent WebSocket search started notification for: {search_request.product_name}")
            
            # Send email notification if enabled
            await self._send_search_started_email(search_request)
            
        except Exception as e:
            logger.error(f"Failed to send search started notification: {str(e)}")
    
    async def _notify_search_completed(
        self,
        search_request: SearchRequest,
        execution: SearchExecution,
        matches_found: int
    ):
        """Send notification when search completes"""
        try:
            from app.schemas.notification import NotificationType
            
            notification = WebSocketSearchStatusNotification(
                message=f"Search completed: {search_request.product_name} - Found {matches_found} matches",
                type=NotificationType.SEARCH_COMPLETED,
                search_request_id=str(search_request.id),
                search_execution_id=str(execution.id) if execution.id else None,
                status="completed",
                matches_found=matches_found
            )
            
            await manager.broadcast(notification.model_dump(mode='json'))
            logger.info(f"Sent search completed notification: {matches_found} matches found")
        except Exception as e:
            logger.error(f"Failed to send search completed notification: {str(e)}")
    
    async def _notify_error(
        self,
        search_request: SearchRequest,
        error_message: str
    ):
        """Send notification when an error occurs"""
        try:
            notification = WebSocketErrorNotification(
                message=f"Error in search: {search_request.product_name}",
                search_request_id=str(search_request.id),
                error_details=error_message,
                error_code=None  # Optional field
            )
            
            await manager.broadcast(notification.model_dump(mode='json'))
            logger.error(f"Sent error notification: {error_message}")
        except Exception as e:
            logger.error(f"Failed to send error notification: {str(e)}")
    
    async def _send_match_email(
        self,
        search_request_id: str,
        product: Product
    ):
        """Send email notification for new match"""
        try:
            # Get email preferences for this search request
            email_pref = self.db.query(EmailPreference).filter(
                EmailPreference.search_request_id == search_request_id
            ).first()
            
            # Check if email notifications are enabled
            if not email_pref or not email_pref.notify_on_match:
                logger.debug(f"Email notifications disabled for search request {search_request_id}")
                return
            
            # Get the search request
            search_request = self.db.query(SearchRequest).filter(
                SearchRequest.id == search_request_id
            ).first()
            
            if not search_request:
                logger.warning(f"Search request {search_request_id} not found")
                return
            
            # Send email
            await self.email_service.send_match_notification(
                email=email_pref.email_address,
                product=product,
                search_request=search_request
            )
            
            logger.info(f"Sent match email notification to {email_pref.email_address}")
            
        except Exception as e:
            logger.error(f"Failed to send match email: {str(e)}")
    
    async def _send_search_started_email(
        self,
        search_request: SearchRequest
    ):
        """Send email notification when search starts"""
        try:
            # Get email preferences for this search request
            email_pref = self.db.query(EmailPreference).filter(
                EmailPreference.search_request_id == search_request.id
            ).first()
            
            # Check if email notifications are enabled
            if not email_pref or not email_pref.notify_on_start:
                logger.debug(f"Search started email notifications disabled for search request {search_request.id}")
                return
            
            # Send email
            await self.email_service.send_search_started(
                email=email_pref.email_address,
                search_request=search_request
            )
            
            logger.info(f"Sent search started email notification to {email_pref.email_address}")
            
        except Exception as e:
            logger.error(f"Failed to send search started email: {str(e)}")