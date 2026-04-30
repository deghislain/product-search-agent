"""
API routes for search request management.

This module provides REST API endpoints for managing search requests:
- List all search requests (with pagination)
- Get a single search request by ID
- Create new search requests (Part 2)
- Update search requests (Part 3)
- Delete search requests (Part 3)
- Pause/Resume search requests (Part 4)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.api.dependencies import get_db
from app.models import SearchRequest, SearchStatus
from app.schemas import (
    SearchRequestResponse,
    SearchRequestListResponse,
)
from app.schemas import SearchRequestCreate
from app.schemas import SearchRequestUpdate
from app.core.orchestrator import SearchOrchestrator
from app.database import SessionLocal
from app.core.query_optimizer import QueryOptimizer
from app.core.reasoning_engine import ReasoningEngine


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Create router with prefix and tags
router = APIRouter(
    prefix="/api/search-requests",
    tags=["search-requests"]
)


# ============================================================================
# GET Endpoints
# ============================================================================

@router.get("/", response_model=SearchRequestListResponse)
def list_search_requests(
    skip: int = Query(default=0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(default=50, ge=1, le=100, description="Maximum number of records to return"),
    status: Optional[str] = Query(default=None, description="Filter by status (active, paused, completed, cancelled)"),
    db: Session = Depends(get_db)
):
    """
    List all search requests with pagination and optional filtering.
    
    This endpoint retrieves a paginated list of search requests from the database.
    You can filter by status and control pagination with skip/limit parameters.
    
    Args:
        skip: Number of records to skip (for pagination). Default: 0
        limit: Maximum number of records to return (1-100). Default: 50
        status: Optional status filter (active, paused, completed, cancelled)
        db: Database session (injected by FastAPI)
        
    Returns:
        SearchRequestListResponse: Paginated list of search requests with metadata
        
    Example:
        ```
        GET /api/search-requests?skip=0&limit=10
        GET /api/search-requests?status=active
        GET /api/search-requests?skip=10&limit=20&status=paused
        ```
        
    Response:
        ```json
        {
            "items": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "product_name": "iPhone 13",
                    "product_description": "Looking for iPhone 13",
                    "budget": 600.0,
                    "location": "Boston, MA",
                    "match_threshold": 75.0,
                    "status": "active",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00"
                }
            ],
            "total": 1,
            "page": 1,
            "page_size": 50
        }
        ```
    """
    # Build query
    query = db.query(SearchRequest)
    
    # Apply status filter if provided
    if status:
        query = query.filter(SearchRequest.status == status)
    else:
        # By default, exclude cancelled searches (soft-deleted)
        query = query.filter(SearchRequest.status != SearchStatus.CANCELLED)
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination
    search_requests = query.offset(skip).limit(limit).all()
    
    # Calculate page number
    page = (skip // limit) + 1 if limit > 0 else 1
    
    # Return paginated response
    return SearchRequestListResponse(
        items=search_requests,
        total=total,
        page=page,
        page_size=limit
    )


@router.get("/{search_request_id}", response_model=SearchRequestResponse)
def get_search_request(
    search_request_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a single search request by ID.
    
    This endpoint retrieves detailed information about a specific search request.
    
    Args:
        search_request_id: Unique identifier (UUID) of the search request
        db: Database session (injected by FastAPI)
        
    Returns:
        SearchRequestResponse: Detailed search request information
        
    Raises:
        HTTPException: 404 if search request not found
        
    Example:
        ```
        GET /api/search-requests/123e4567-e89b-12d3-a456-426614174000
        ```
        
    Response (200 OK):
        ```json
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "product_name": "iPhone 13",
            "product_description": "Looking for iPhone 13 in good condition",
            "budget": 600.0,
            "location": "Boston, MA",
            "match_threshold": 75.0,
            "status": "active",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }
        ```
        
    Response (404 Not Found):
        ```json
        {
            "detail": "Search request with id 123... not found"
        }
        ```
    """
    # Query database for the search request
    search_request = db.query(SearchRequest).filter(
        SearchRequest.id == search_request_id
    ).first()
    
    # Check if found
    if not search_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Search request with id {search_request_id} not found"
        )
    
    # Return the search request
    return search_request


# ============================================================================
# Additional GET endpoints for statistics (optional but useful)
# ============================================================================

@router.get("/{search_request_id}/stats", response_model=dict)
def get_search_request_stats(
    search_request_id: str,
    db: Session = Depends(get_db)
):
    """
    Get statistics for a specific search request.
    
    This endpoint provides summary statistics about a search request,
    including execution count, total products found, and matches.
    
    Args:
        search_request_id: Unique identifier of the search request
        db: Database session (injected by FastAPI)
        
    Returns:
        dict: Statistics about the search request
        
    Raises:
        HTTPException: 404 if search request not found
        
    Example:
        ```
        GET /api/search-requests/123e4567-e89b-12d3-a456-426614174000/stats
        ```
        
    Response:
        ```json
        {
            "search_request_id": "123e4567-e89b-12d3-a456-426614174000",
            "product_name": "iPhone 13",
            "status": "active",
            "total_executions": 5,
            "total_products_found": 125,
            "total_matches_found": 8,
            "average_match_rate": 6.4,
            "last_execution": "2024-01-01T12:00:00"
        }
        ```
    """
    from app.models import SearchExecution
    
    # Verify search request exists
    search_request = db.query(SearchRequest).filter(
        SearchRequest.id == search_request_id
    ).first()
    
    if not search_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Search request with id {search_request_id} not found"
        )
    
    # Get execution statistics
    executions = db.query(SearchExecution).filter(
        SearchExecution.search_request_id == search_request_id
    ).all()
    
    total_executions = len(executions)
    total_products = sum(e.products_found for e in executions)
    total_matches = sum(e.matches_found for e in executions)
    
    # Calculate average match rate
    if total_products > 0:
        avg_match_rate = (total_matches / total_products) * 100
    else:
        avg_match_rate = 0.0
    
    # Get last execution time
    last_execution = None
    if executions:
        last_execution = max(e.started_at for e in executions)
    
    return {
        "search_request_id": search_request_id,
        "product_name": search_request.product_name,
        "status": search_request.status.value,
        "total_executions": total_executions,
        "total_products_found": total_products,
        "total_matches_found": total_matches,
        "average_match_rate": round(avg_match_rate, 2),
        "last_execution": last_execution.isoformat() if last_execution else None
    }


# ============================================================================
# POST, PUT, DELETE endpoints will be added in subsequent subtasks
# ============================================================================

# Subtask 3.4 will add:
# - POST /api/search-requests (create new search)

@router.post("/", response_model=SearchRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_search_request(
    search_request: SearchRequestCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a new search request and execute it immediately.
    
    The search will:
    1. Execute immediately (in background)
    2. Continue executing every 2 hours via scheduler
    3. Stop when deleted
    
    Args:
        search_request: Search request data from request body
        background_tasks: FastAPI background tasks manager
        db: Database session
        
    Returns:
        SearchRequestResponse: Created search request
    """
    # Create database model from schema
    # If no platforms are selected, default to ALL platforms
    search_craigslist = search_request.search_craigslist
    search_ebay = search_request.search_ebay
    search_facebook = search_request.search_facebook
    
    # If all platforms are False, enable all of them
    if not (search_craigslist or search_ebay or search_facebook):
        logger.info("No platforms selected, defaulting to ALL platforms")
        search_craigslist = True
        search_ebay = True
        search_facebook = True
    
    db_search_request = SearchRequest(
        product_name=search_request.product_name,
        product_description=search_request.product_description,
        budget=search_request.budget,
        location=search_request.location,
        match_threshold=search_request.match_threshold,
        search_craigslist=search_craigslist,
        search_ebay=search_ebay,
        search_facebook=search_facebook
    )
    
    # Add to database
    db.add(db_search_request)
    db.commit()
    db.refresh(db_search_request)
    
    # Trigger immediate execution in background
    # Create a new database session for the background task
    background_db = SessionLocal()
    orchestrator = SearchOrchestrator(background_db)
    
    background_tasks.add_task(
        orchestrator.execute_search_immediately,
        search_request_id=db_search_request.id,
        db=background_db
    )
    
    logger.info(f"✅ Search request {db_search_request.id} created and queued for immediate execution")
    
    return db_search_request

# Subtask 3.5 will add:
# - PUT /api/search-requests/{id} (update search)

@router.put("/{search_request_id}", response_model=SearchRequestResponse)
def update_search_request(
    search_request_id: str,
    search_request_update: SearchRequestUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing search request.
    
    Args:
        search_request_id: ID of search request to update
        search_request_update: Updated data (only provided fields will be updated)
        db: Database session
        
    Returns:
        SearchRequestResponse: Updated search request
        
    Raises:
        HTTPException: 404 if search request not found
    """
    # Find existing record
    db_search_request = db.query(SearchRequest).filter(
        SearchRequest.id == search_request_id
    ).first()
    
    if not db_search_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Search request with id {search_request_id} not found"
        )
    
    # Update fields (only if provided)
    update_data = search_request_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_search_request, field, value)
    
    # Save changes
    db.commit()
    db.refresh(db_search_request)
    
    return db_search_request

# - DELETE /api/search-requests/{id} (delete search)
@router.delete("/{search_request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_search_request(
    search_request_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a search request.
    
    This sets the status to 'cancelled' instead of hard-deleting the record.
    This ensures the scheduler won't pick it up again, and preserves history.
    
    Args:
        search_request_id: ID of search request to delete
        db: Database session
        
    Returns:
        None (204 No Content)
        
    Raises:
        HTTPException: 404 if search request not found
    """
    # Find existing record
    db_search_request = db.query(SearchRequest).filter(
        SearchRequest.id == search_request_id
    ).first()
    
    if not db_search_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Search request with id {search_request_id} not found"
        )
    
    # Set status to cancelled instead of hard delete
    # This prevents the scheduler from picking it up again
    db_search_request.status = SearchStatus.CANCELLED
    db.commit()
    
    logger.info(f"Search request {search_request_id} cancelled (soft delete)")
    
    return None
# Subtask 3.6 will add:
# - POST /api/search-requests/{id}/pause (pause search)
@router.post("/{search_request_id}/pause", response_model=SearchRequestResponse)
def pause_search_request(
    search_request_id: str,
    db: Session = Depends(get_db)
):
    """
    Pause an active search request.
    
    Args:
        search_request_id: ID of search request to pause
        db: Database session
        
    Returns:
        SearchRequestResponse: Updated search request
        
    Raises:
        HTTPException: 404 if search request not found
    """
    # Find existing record
    db_search_request = db.query(SearchRequest).filter(
        SearchRequest.id == search_request_id
    ).first()
    
    if not db_search_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Search request with id {search_request_id} not found"
        )
    
    # Pause the search
    db_search_request.pause()
    db.commit()
    db.refresh(db_search_request)
    
    return db_search_request

# - POST /api/search-requests/{id}/resume (resume search)
@router.post("/{search_request_id}/resume", response_model=SearchRequestResponse)
def resume_search_request(
    search_request_id: str,
    db: Session = Depends(get_db)
):
    """
    Resume a paused search request.
    
    Args:
        search_request_id: ID of search request to resume
        db: Database session
        
    Returns:
        SearchRequestResponse: Updated search request
        
    Raises:
        HTTPException: 404 if search request not found
    """
    # Find existing record
    db_search_request = db.query(SearchRequest).filter(
        SearchRequest.id == search_request_id
    ).first()
    
    if not db_search_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Search request with id {search_request_id} not found"
        )
    
    # Resume the search
    db_search_request.resume()
    db.commit()
    db.refresh(db_search_request)
    
    return db_search_request



# ============================================================================
# Agentic Features - Query Optimization & Adaptive Scheduling
# ============================================================================

query_optimizer = QueryOptimizer()
reasoning_engine = ReasoningEngine()

from app.core.adaptive_scheduler import get_adaptive_scheduler
adaptive_scheduler = get_adaptive_scheduler()

@router.post("/{search_request_id}/optimize", response_model=dict)
async def optimize_search_query(
    search_request_id: str,
    db: Session = Depends(get_db)
):
    """
    Optimize the search query using AI based on past results and user feedback.
    
    This endpoint uses the QueryOptimizer to analyze previous search results
    and generate an improved query. The optimization history is tracked in
    the database for learning and transparency.
    
    Args:
        search_request_id: ID of the search request to optimize
        db: Database session
        
    Returns:
        dict: Optimization results including original query, optimized query,
              reasoning, and updated query version
              
    Raises:
        HTTPException: 404 if search request not found
        HTTPException: 400 if optimization is disabled for this search
        HTTPException: 400 if no previous results to analyze
        
    Example:
        ```
        POST /api/search-requests/123e4567-e89b-12d3-a456-426614174000/optimize
        ```
        
    Response:
        ```json
        {
            "search_request_id": "123e4567-e89b-12d3-a456-426614174000",
            "original_query": "Toyota Camry",
            "optimized_query": "Toyota Camry 2015-2018 LE SE XLE under 100k miles",
            "query_version": 1,
            "reasoning": "Based on 15 high-scoring matches, added year range 2015-2018 and popular trim levels (LE, SE, XLE). Added mileage constraint based on budget.",
            "optimization_metrics": {
                "previous_results_count": 150,
                "high_score_products": 15,
                "avg_previous_score": 65.5,
                "optimization_timestamp": "2026-04-26T15:55:00Z"
            }
        }
        ```
    """
    from app.models import Product
    from datetime import datetime
    
    # Get search request
    search_request = db.query(SearchRequest).filter(
        SearchRequest.id == search_request_id
    ).first()
    
    if not search_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Search request with id {search_request_id} not found"
        )
    
    # Check if optimization is enabled
    if not search_request.optimization_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query optimization is disabled for this search request"
        )
    
    # Get previous results
    previous_results = db.query(Product).filter(
        Product.search_request_id == search_request_id
    ).all()
    
    if not previous_results:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No previous results to analyze. Run a search first."
        )
    
    # Analyze products by match score
    # High-scoring products indicate what the user wants
    clicked_products = [p for p in previous_results if p.match_score >= 80]
    ignored_products = [p for p in previous_results if p.match_score < 60]
    
    logger.info(f"Optimizing query for search {search_request_id}: "
                f"{len(previous_results)} results, "
                f"{len(clicked_products)} high-score, "
                f"{len(ignored_products)} low-score")
    
    # Store current query in history before optimization
    current_history = search_request.query_history or []
    avg_score = sum(p.match_score for p in previous_results) / len(previous_results)
    
    current_history.append({
        "version": search_request.query_version,
        "query": search_request.product_name,
        "timestamp": datetime.utcnow().isoformat(),
        "results_count": len(previous_results),
        "high_score_count": len(clicked_products),
        "avg_match_score": round(avg_score, 2)
    })
    
    # Optimize query using AI
    try:
        optimized_query = await query_optimizer.optimize_query(
            original_query=search_request.product_name,
            budget=search_request.budget,
            previous_results=previous_results,
            clicked_products=clicked_products,
            ignored_products=ignored_products
        )
    except Exception as e:
        logger.error(f"Query optimization failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query optimization failed: {str(e)}"
        )
    
    # Generate reasoning explanation
    reasoning = await reasoning_engine.explain_optimization(
        original_query=search_request.product_name,
        optimized_query=optimized_query,
        clicked_products=clicked_products,
        ignored_products=ignored_products
    )
    
    # Update search request with optimized query
    search_request.product_name = optimized_query
    search_request.query_version += 1
    search_request.query_history = current_history
    search_request.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(search_request)
    
    logger.info(f"Query optimized: v{search_request.query_version - 1} -> v{search_request.query_version}")
    
    return {
        "search_request_id": search_request_id,
        "original_query": current_history[-1]["query"],
        "optimized_query": optimized_query,
        "query_version": search_request.query_version,
        "reasoning": reasoning,
        "optimization_metrics": {
            "previous_results_count": len(previous_results),
            "high_score_products": len(clicked_products),
            "low_score_products": len(ignored_products),
            "avg_previous_score": round(avg_score, 2),
            "optimization_timestamp": datetime.utcnow().isoformat()
        }
    }


@router.get("/{search_request_id}/products/{product_id}/explanation")
async def get_match_explanation(
    id: int,
    db: Session = Depends(get_db)
):
    """
    Get AI explanation for why a product matched.
    
    Example:
        GET /api/products/123/explanation
        
        Returns:
        {
            "product_id": 123,
            "match_score": 87.5,
            "explanation": "This product scored 87% because..."
        }
    """
    # Get product
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get search request
    search_request = db.query(SearchRequest).filter(
        SearchRequest.id == product.search_request_id
    ).first()
    
    # Generate explanation
    explanation = await reasoning_engine.explain_match_score(
        product=product,
        search_request=search_request
    )
    
    return {
        "product_id": product.id,
        "match_score": product.match_score,
        "explanation": explanation
    }


# ============================================================================
# Agentic Features - Adaptive Scheduling
# ============================================================================

@router.get("/{search_request_id}/schedule-recommendation", response_model=dict)
async def get_schedule_recommendation(
    search_request_id: str,
    db: Session = Depends(get_db)
):
    """
    Get AI-powered scheduling recommendation for a search request.
    
    This endpoint analyzes platform-specific listing patterns and provides
    intelligent recommendations on when to search for optimal results.
    
    Args:
        search_request_id: ID of the search request
        db: Database session
        
    Returns:
        dict: Scheduling recommendation with next search time and reasoning
        
    Raises:
        HTTPException: 404 if search request not found
        
    Example:
        ```
        GET /api/search-requests/123e4567-e89b-12d3-a456-426614174000/schedule-recommendation
        ```
        
    Response:
        ```json
        {
            "search_request_id": "123e4567-e89b-12d3-a456-426614174000",
            "platforms": ["craigslist", "ebay"],
            "next_search_time": "2026-04-26T20:00:00Z",
            "hours_until_next": 1.5,
            "recommendation": "Based on learned patterns, Craigslist has peak activity on weekends 8-10 AM with an average of 12 new listings per hour. eBay auctions typically end Sunday evenings 6-9 PM. I recommend searching at 8 PM tonight to catch both platforms' peak times.",
            "patterns_analyzed": true
        }
        ```
    """
    # Get search request
    search_request = db.query(SearchRequest).filter(
        SearchRequest.id == search_request_id
    ).first()
    
    if not search_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Search request with id {search_request_id} not found"
        )
    
    # Get recommendation from adaptive scheduler
    try:
        recommendation = await adaptive_scheduler.get_schedule_recommendation(
            search_request,
            db
        )
        return recommendation
    except Exception as e:
        logger.error(f"Failed to get schedule recommendation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate schedule recommendation: {str(e)}"
        )


@router.post("/analyze-patterns", response_model=dict)
async def analyze_listing_patterns(
    platform: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Analyze listing patterns for platforms.
    
    This endpoint triggers pattern analysis for one or all platforms.
    Should be run periodically (e.g., daily) to keep patterns up-to-date.
    
    Args:
        platform: Specific platform to analyze (optional, analyzes all if not provided)
        db: Database session
        
    Returns:
        dict: Analysis results
        
    Example:
        ```
        POST /api/search-requests/analyze-patterns?platform=craigslist
        ```
        
    Response:
        ```json
        {
            "status": "success",
            "platforms_analyzed": ["craigslist"],
            "patterns": {
                "craigslist": {
                    "peak_hours": [8, 9, 10, 18, 19, 20],
                    "peak_days": "Sat, Sun",
                    "avg_listings_per_hour": 12.5,
                    "last_updated": "2026-04-26T18:00:00Z"
                }
            }
        }
        ```
    """
    try:
        if platform:
            # Analyze specific platform
            logger.info(f"Analyzing patterns for {platform}")
            await adaptive_scheduler.analyze_listing_patterns(platform, db)
            platforms_analyzed = [platform]
        else:
            # Analyze all platforms
            logger.info("Analyzing patterns for all platforms")
            await adaptive_scheduler.analyze_all_patterns(db)
            platforms_analyzed = ["craigslist", "ebay", "facebook"]
        
        # Get pattern summary
        patterns = adaptive_scheduler.get_pattern_summary()
        
        return {
            "status": "success",
            "platforms_analyzed": platforms_analyzed,
            "patterns": patterns,
            "message": f"Successfully analyzed patterns for {', '.join(platforms_analyzed)}"
        }
    except Exception as e:
        logger.error(f"Pattern analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pattern analysis failed: {str(e)}"
        )


@router.get("/patterns/summary", response_model=dict)
async def get_patterns_summary():
    """
    Get summary of all learned listing patterns.
    
    Returns:
        dict: Summary of patterns for all platforms
        
    Example:
        ```
        GET /api/search-requests/patterns/summary
        ```
        
    Response:
        ```json
        {
            "craigslist": {
                "peak_hours": [8, 9, 10, 18, 19, 20],
                "peak_days": "Sat, Sun",
                "avg_listings_per_hour": 12.5,
                "last_updated": "2026-04-26T18:00:00Z",
                "total_hourly_data_points": 1250
            },
            "ebay": {
                "peak_hours": [18, 19, 20, 21],
                "peak_days": "Sun",
                "avg_listings_per_hour": 8.3,
                "last_updated": "2026-04-26T18:00:00Z",
                "total_hourly_data_points": 890
            }
        }
        ```
    """
    patterns = adaptive_scheduler.get_pattern_summary()
    
    if not patterns:
        return {
            "message": "No patterns learned yet. Run pattern analysis first.",
            "patterns": {}
        }
    
    return patterns


# Made with Bob
