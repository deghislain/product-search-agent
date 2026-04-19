"""
Product model for storing scraped product information.

This model represents a product found during a search execution,
including details like title, price, URL, and match score.
"""

from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Product(Base):
    """
    Product model for storing scraped product information.
    
    A Product represents an item found during a SearchExecution.
    Products are scraped from various platforms (Craigslist, Facebook, eBay)
    and evaluated against the search criteria to determine if they're a match.
    
    Attributes:
        id (str): Unique identifier (UUID)
        search_execution_id (str): Foreign key to parent SearchExecution
        title (str): Product title/name
        description (str, optional): Product description
        price (float): Product price
        url (str): Link to the product listing
        image_url (str, optional): Link to product image
        platform (str): Platform where product was found (craigslist, facebook, ebay)
        location (str, optional): Geographic location of the product
        posted_date (datetime, optional): When the product was posted
        match_score (float, optional): Similarity score (0-100) to search criteria
        is_match (bool): Whether product meets match threshold
        created_at (datetime): When the product was scraped
        
    Relationships:
        search_execution: Parent SearchExecution that found this product
        notifications: List of Notification records for this product
    
    Example:
        ```python
        from app.models import Product
        from app.database import SessionLocal
        from datetime import datetime
        
        # Create a new product
        product = Product(
            search_execution_id=execution.id,
            title="iPhone 13 128GB Blue",
            description="Excellent condition, barely used",
            price=450.0,
            url="https://boston.craigslist.org/product/123",
            image_url="https://images.craigslist.org/123.jpg",
            platform="craigslist",
            location="Boston, MA",
            posted_date=datetime.utcnow(),
            match_score=85.5,
            is_match=True
        )
        
        # Save to database
        db = SessionLocal()
        db.add(product)
        db.commit()
        db.refresh(product)
        
        print(f"Product saved: {product.title}")
        print(f"Match score: {product.match_score}%")
        
        # Check if it's a good match
        if product.is_good_match(threshold=70.0):
            print("This is a good match!")
        
        # Check if price is within budget
        if product.is_within_budget(500.0):
            print("Within budget!")
        
        db.close()
        ```
    """
    
    __tablename__ = "products"
    
    # ========================================================================
    # Primary Key
    # ========================================================================
    
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="Unique identifier for the product"
    )
    
    # ========================================================================
    # Foreign Keys
    # ========================================================================
    
    search_execution_id = Column(
        String(36),
        ForeignKey('search_executions.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="ID of the search execution that found this product"
    )
    
    # ========================================================================
    # Product Information
    # ========================================================================
    
    title = Column(
        String(500),
        nullable=False,
        index=True,
        comment="Product title or name"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Detailed product description"
    )
    
    price = Column(
        Float,
        nullable=False,
        index=True,
        comment="Product price in dollars"
    )
    
    url = Column(
        String(1000),
        nullable=False,
        unique=True,
        comment="URL to the product listing"
    )
    
    image_url = Column(
        String(1000),
        nullable=True,
        comment="URL to the product image"
    )
    
    # ========================================================================
    # Platform and Location
    # ========================================================================
    
    platform = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Platform where product was found (craigslist, facebook, ebay)"
    )
    
    location = Column(
        String(255),
        nullable=True,
        index=True,
        comment="Geographic location of the product"
    )
    
    posted_date = Column(
        DateTime,
        nullable=True,
        index=True,
        comment="When the product was originally posted"
    )
    
    # ========================================================================
    # Matching Information
    # ========================================================================
    
    match_score = Column(
        Float,
        nullable=True,
        index=True,
        comment="Similarity score (0-100) compared to search criteria"
    )
    
    is_match = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Whether product meets the match threshold"
    )
    
    # ========================================================================
    # Timestamps
    # ========================================================================
    
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="When the product was scraped and saved"
    )
    
    # ========================================================================
    # Relationships
    # ========================================================================
    
    # Many-to-one: Multiple products belong to one search execution
    # NOTE: This will be uncommented after SearchExecution model is updated
    # search_execution = relationship(
    #     "SearchExecution",
    #     back_populates="products"
    # )
    
    # One-to-many: A product can have multiple notifications
    # NOTE: This will be uncommented after Notification model is created
    # notifications = relationship(
    #     "Notification",
    #     back_populates="product",
    #     cascade="all, delete-orphan",
    #     lazy="dynamic"
    # )
    
    # ========================================================================
    # Indexes for Performance
    # ========================================================================
    
    __table_args__ = (
        # Composite index for finding matches
        Index('idx_products_match', 'is_match', 'match_score'),
        # Composite index for price filtering
        Index('idx_products_price_platform', 'price', 'platform'),
        # Index for recent products
        Index('idx_products_created', 'created_at'),
    )
    
    # ========================================================================
    # Methods
    # ========================================================================
    
    def __repr__(self) -> str:
        """String representation of Product."""
        return (
            f"<Product(id={self.id}, "
            f"title={self.title[:30]}..., "
            f"price=${self.price:.2f}, "
            f"platform={self.platform}, "
            f"is_match={self.is_match})>"
        )
    
    def is_good_match(self, threshold: float = 70.0) -> bool:
        """
        Check if product meets the match threshold.
        
        Args:
            threshold: Minimum match score required (0-100)
        
        Returns:
            bool: True if match_score >= threshold, False otherwise
        
        Example:
            ```python
            if product.is_good_match(threshold=75.0):
                print("This product is a good match!")
            ```
        """
        return self.match_score is not None and self.match_score >= threshold
    
    def is_within_budget(self, budget: float) -> bool:
        """
        Check if product price is within budget.
        
        Args:
            budget: Maximum price allowed
        
        Returns:
            bool: True if price <= budget, False otherwise
        
        Example:
            ```python
            if product.is_within_budget(500.0):
                print("Product is within budget!")
            ```
        """
        return self.price <= budget
    
    def mark_as_match(self, score: float) -> None:
        """
        Mark the product as a match with the given score.
        
        Args:
            score: Match score (0-100)
        
        Example:
            ```python
            product.mark_as_match(85.5)
            db.commit()
            ```
        """
        self.match_score = score
        self.is_match = True
    
    def mark_as_non_match(self, score: float | None = None) -> None:
        """
        Mark the product as not a match.
        
        Args:
            score: Optional match score (0-100)
        
        Example:
            ```python
            product.mark_as_non_match(45.0)
            db.commit()
            ```
        """
        if score is not None:
            self.match_score = score
        self.is_match = False
    
    def get_short_title(self, max_length: int = 50) -> str:
        """
        Get a shortened version of the title.
        
        Args:
            max_length: Maximum length of the title
        
        Returns:
            str: Shortened title with ellipsis if needed
        
        Example:
            ```python
            short_title = product.get_short_title(30)
            print(short_title)  # "iPhone 13 128GB Blue Excell..."
            ```
        """
        if len(self.title) <= max_length:
            return self.title
        return self.title[:max_length - 3] + "..."
    
    def days_since_posted(self) -> int:
        """
        Calculate days since the product was posted.
        
        Returns:
            int: Number of days, or 0 if posted_date is None
        
        Example:
            ```python
            days = product.days_since_posted()
            print(f"Posted {days} days ago")
            ```
        """
        if self.posted_date is None:
            return 0
        delta = datetime.utcnow() - self.posted_date
        return delta.days
    
    def is_recent(self, days: int = 7) -> bool:
        """
        Check if product was posted recently.
        
        Args:
            days: Number of days to consider as recent
        
        Returns:
            bool: True if posted within the specified days
        
        Example:
            ```python
            if product.is_recent(days=3):
                print("This is a recent listing!")
            ```
        """
        if self.posted_date is None:
            return False
        return self.days_since_posted() <= days
    
    def to_dict(self) -> dict:
        """
        Convert the product to a dictionary.
        
        Returns:
            dict: Dictionary representation of the product
        
        Example:
            ```python
            product_dict = product.to_dict()
            print(product_dict['title'])
            print(product_dict['price'])
            ```
        """
        return {
            'id': self.id,
            'search_execution_id': self.search_execution_id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'url': self.url,
            'image_url': self.image_url,
            'platform': self.platform,
            'location': self.location,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'match_score': self.match_score,
            'is_match': self.is_match,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'days_since_posted': self.days_since_posted(),
        }

# Made with Bob