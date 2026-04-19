"""
API routes for product management.
This module provides REST API endpoints for retrieving products and matches:
List all products
List only matching products
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.api.dependencies import get_db
from app.models import Product
from app.schemas import ProductResponse, ProductListResponse

# Create router
router = APIRouter(
    prefix="/api/products",
    tags=["products"]
)


@router.get("/", response_model=ProductListResponse)
def list_products(
    skip: int = 0,
    limit: int = 50,
    platform: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    List all products with optional filtering.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        platform: Filter by platform (craigslist, facebook, ebay)
        min_price: Minimum price filter
        max_price: Maximum price filter
        db: Database session
        
    Returns:
        ProductListResponse: Paginated list of products
    """
    # Build query
    query = db.query(Product)
    
    # Apply filters
    if platform:
        query = query.filter(Product.platform == platform)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    # Get results
    products = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return ProductListResponse(
        items=products,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/matches", response_model=ProductListResponse)
def list_matching_products(
    skip: int = 0,
    limit: int = 200,
    min_score: float = Query(default=0.0, ge=0, le=100),
    search_request_id: Optional[str] = Query(default=None, description="Filter by search request ID"),
    db: Session = Depends(get_db)
):
    """
    List only products that are matches.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        min_score: Minimum match score filter
        search_request_id: Optional filter by specific search request
        db: Database session
        
    Returns:
        ProductListResponse: Paginated list of matching products
    """
    # Query for matches only
    query = db.query(Product).filter(
        Product.is_match == True,
        Product.match_score >= min_score
    )
    
    # Filter by search_request_id if provided
    if search_request_id:
        # Join with SearchExecution to filter by search_request_id
        from app.models.search_execution import SearchExecution
        query = query.join(
            SearchExecution,
            Product.search_execution_id == SearchExecution.id
        ).filter(
            SearchExecution.search_request_id == search_request_id
        )
    
    query = query.order_by(Product.match_score.desc())
    
    # Get results
    products = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return ProductListResponse(
        items=products,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )