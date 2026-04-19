from typing import List, Set, Tuple
from datetime import datetime
from app.models.product import Product
from app.core.similarity import SimilarityCalculator


class DuplicateDetector:
    """
    Detects duplicate products across different platforms.
    
    Uses title similarity and price proximity to identify duplicates.
    """
    
    def __init__(
        self,
        title_threshold: float = 85.0,
        similarity_calculator: SimilarityCalculator | None = None,
        price_tolerance: float = 0.10  # 10% price difference
    ):
        """
            Initialize duplicate detector.
            
            Args:
                similarity_calculator: For comparing titles
                title_threshold: Minimum title similarity to consider duplicate
                price_tolerance: Max price difference ratio (0.10 = 10%)
        """
        self.title_threshold = title_threshold
        self.price_tolerance = price_tolerance
        self.similarity_calculator = similarity_calculator or SimilarityCalculator()
        
    def are_duplicates(self, product1: Product, product2: Product) -> bool:
        """
        Check if two products are duplicates.
        
        Criteria for duplicates:
        1. Titles are highly similar (>= threshold)
        2. Prices are close (within tolerance)
        3. Different platforms (same platform = different listings)
        
        Example:
            Product 1: "iPhone 13 Pro" $500 (Craigslist)
            Product 2: "iPhone 13 Pro" $510 (eBay)
            -> True (same item, 2% price diff)
        
        Returns:
            True if products are likely duplicates
        """
        # Check if same platform (not duplicates if same platform)
        if product1.platform != product2.platform:
            # Calculate title similarity
            title_similarity = self.similarity_calculator.calculate_similarity(
                product1.title,
                product2.title
            )
            
            # Check if titles are similar enough
            if title_similarity < self.title_threshold:
                return False
            
            # Calculate price difference ratio
            price_difference_ratio = self._calculate_price_difference_ratio(
                product1.price,
                product2.price
            )
            
            # Check if prices are close enough
            if price_difference_ratio > self.price_tolerance:
                return False
            
            # Both criteria met - they are duplicates
            return True
        
        # Same platform means different listings, not duplicates
        return False
        
    
    def _calculate_price_difference_ratio(
        self,
        price1: float,
        price2: float
    ) -> float:
        """
        Calculate relative price difference.
        
        Formula: |price1 - price2| / max(price1, price2)
        
        Example:
            $500 vs $550 -> 0.09 (9% difference)
            $100 vs $200 -> 0.50 (50% difference)
        
        Returns:
            Ratio between 0 and 1
        """
        if max(price1, price2) == 0:
            return 0.0
        return abs(price1 - price2) / max(price1, price2)

    
    
    def find_duplicates(
        self,
        products: List[Product]
    ) -> List[Tuple[Product, Product]]:
        """
        Find all duplicate pairs in a list of products.
        
        Returns list of tuples, each containing two duplicate products.
        
        Example:
            Input: [prod1, prod2, prod3, prod4]
            Output: [(prod1, prod3), (prod2, prod4)]
            (prod1 and prod3 are duplicates, prod2 and prod4 are duplicates)
        """
        duplicates = []
        
        # Compare each product with every other product
        # Use i+1 to avoid comparing a product with itself and avoid duplicate pairs
        for i in range(len(products)):
            for j in range(i + 1, len(products)):
                if self.are_duplicates(products[i], products[j]):
                    duplicates.append((products[i], products[j]))
        
        return duplicates
    
    def remove_duplicates(
        self,
        products: List[Product],
        keep_strategy: str = "highest_score"
    ) -> List[Product]:
        """
        Remove duplicate products, keeping the best one.
        
        Args:
            products: List of products to deduplicate
            keep_strategy: Which duplicate to keep
                - "highest_score": Keep product with highest match_score
                - "most_recent": Keep most recently scraped
                - "lowest_price": Keep cheapest option
        
        Returns:
            List with duplicates removed
        """
        if not products:
            return []
        
        # Step 1: Find all duplicate pairs
        duplicate_pairs = self.find_duplicates(products)
        
        if not duplicate_pairs:
            # No duplicates found, return original list
            return products
        
        # Step 2: Group duplicates together using Union-Find approach
        # Create a mapping of product to its duplicate group
        duplicate_groups = {}  # Maps product id to set of duplicate products
        product_to_group_id = {}  # Maps product to its group ID
        
        for prod1, prod2 in duplicate_pairs:
            # Get IDs for both products (use id() for object identity)
            id1, id2 = id(prod1), id(prod2)
            
            # Check if either product is already in a group
            group_id1 = product_to_group_id.get(id1)
            group_id2 = product_to_group_id.get(id2)
            
            if group_id1 is None and group_id2 is None:
                # Neither in a group, create new group
                new_group_id = id1
                duplicate_groups[new_group_id] = {prod1, prod2}
                product_to_group_id[id1] = new_group_id
                product_to_group_id[id2] = new_group_id
            elif group_id1 is not None and group_id2 is None:
                # prod1 in group, add prod2 to same group
                duplicate_groups[group_id1].add(prod2)
                product_to_group_id[id2] = group_id1
            elif group_id1 is None and group_id2 is not None:
                # prod2 in group, add prod1 to same group
                duplicate_groups[group_id2].add(prod1)
                product_to_group_id[id1] = group_id2
            else:
                # Both in groups, merge groups if different
                if group_id1 != group_id2:
                    # Merge group2 into group1
                    duplicate_groups[group_id1].update(duplicate_groups[group_id2])
                    # Update all products in group2 to point to group1
                    for prod in duplicate_groups[group_id2]:
                        product_to_group_id[id(prod)] = group_id1
                    # Remove group2
                    del duplicate_groups[group_id2]
        
        # Step 3: Apply keep_strategy to choose which product to keep from each group
        products_to_remove = set()
        
        for group_id, group_products in duplicate_groups.items():
            # Choose the best product based on strategy
            if keep_strategy == "highest_score":
                # Keep product with highest match_score
                best_product = max(group_products, key=lambda p: p.match_score if p.match_score else 0)
            elif keep_strategy == "most_recent":
                # Keep most recently scraped (highest created_at timestamp)
                best_product = max(group_products, key=lambda p: p.created_at if p.created_at else datetime.min)
            elif keep_strategy == "lowest_price":
                # Keep cheapest option
                best_product = min(group_products, key=lambda p: p.price if p.price else float('inf'))
            else:
                # Default to highest_score if invalid strategy
                best_product = max(group_products, key=lambda p: p.match_score if p.match_score else 0)
            
            # Mark all others in the group for removal
            for product in group_products:
                if product is not best_product:
                    products_to_remove.add(id(product))
        
        # Step 4: Return deduplicated list (products not marked for removal)
        deduplicated = [p for p in products if id(p) not in products_to_remove]
        
        return deduplicated