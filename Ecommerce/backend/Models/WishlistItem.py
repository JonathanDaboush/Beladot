from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class WishlistItem(Base):
    """
    SQLAlchemy ORM model for wishlist_items table.
    
    Individual line items in a user's wishlist. Links wishlist to specific product
    variants with timestamp tracking for sorting and notifications. Minimal design
    for fast operations and easy cart conversion.
    
    Database Schema:
        - Primary Key: id (auto-increment)
        - Foreign Keys: wishlist_id -> wishlists.id (CASCADE),
                       variant_id -> product_variants.id (CASCADE)
        - Indexes: id (primary), wishlist_id, variant_id,
                   composite (wishlist_id, added_at)
        - Unique constraint: (wishlist_id, variant_id) - no duplicate variants per wishlist
        
    Data Integrity:
        - Unique constraint prevents duplicate variants in same wishlist
        - Cascading delete when wishlist deleted (removes all items)
        - Cascading delete when variant deleted (removes stale items)
        
    Relationships:
        - Many-to-one with Wishlist (wishlist contains many items)
        - Many-to-one with ProductVariant (links to specific variant)
        
    Design Philosophy:
        - Minimal: Only essential data (variant_id, timestamp)
        - No price snapshot: Always use current price (unlike cart)
        - No quantity: Wishlists are "interested in" lists, not purchase lists
        - No metadata: Keep simple for fast add/remove operations
        
    Variant vs Product:
        - Stores variant_id (not product_id) for specificity
        - Example: "Blue, Size Large" T-shirt variant
        - Enables: Specific item tracking (not just product interest)
        - Price alerts: Variant-specific pricing
        
    Timestamps:
        - added_at: When user added item to wishlist
        - Uses: Sort by recency, track trends, calculate dwell time
        
    Deduplication:
        - Unique constraint: (wishlist_id, variant_id)
        - Prevents: User accidentally adding same variant multiple times
        - UI behavior: "Already in wishlist" message + highlight
        - Application logic: Check existence before insert, update added_at if exists
        
    Lifecycle:
        1. User clicks "Add to wishlist" on product page
        2. Check if WishlistItem exists (wishlist_id + variant_id)
        3. If exists: Show "Already in wishlist" or update added_at
        4. If not: Create WishlistItem with added_at = NOW()
        5. Update Wishlist.updated_at
        6. Item persists until user removes or variant deleted
        
    Cart Conversion:
        ```python
        # Single item
        cart_item = CartItem(
            cart_id=user.cart.id,
            product_id=wishlist_item.variant.product_id,
            variant_id=wishlist_item.variant_id,
            quantity=1,
            unit_price_cents=wishlist_item.variant.price_cents
        )
        
        # Bulk "Add all to cart"
        for item in wishlist.items:
            if item.variant.stock_quantity > 0:
                create_cart_item(item.variant)
        ```
        
    Query Patterns:
        - User's wishlist items:
          SELECT * FROM wishlist_items WHERE wishlist_id = X ORDER BY added_at DESC
        - Check if wishlisted:
          SELECT 1 FROM wishlist_items WHERE wishlist_id = X AND variant_id = Y
        - Recently added:
          SELECT * WHERE added_at > NOW() - INTERVAL '7 days'
        - Popular variants:
          SELECT variant_id, COUNT(*) FROM wishlist_items GROUP BY variant_id ORDER BY COUNT DESC
        
    Display Logic:
        - Load variant details: JOIN with product_variants, products
        - Show: Product name, variant name, image, current price
        - Availability: "In stock" / "Out of stock" / "Low stock"
        - Price tracking: Compare current price with historical prices
        
    Notifications:
        - Price drop: variant.price_cents < previous_price
        - Back in stock: variant.stock_quantity > 0 (was 0)
        - Low stock alert: variant.stock_quantity < threshold
        - Sale: variant has active coupon/discount
        
    Failure Modes:
        - Variant deleted: CASCADE removes WishlistItem automatically
        - Product deleted: Variant cascade deletes WishlistItem
        - Out of stock: Show "Notify me" button, keep in wishlist
        - Price increased: Show old vs new price (fetch from price history)
        
    Analytics:
        - Wishlist add rate: COUNT(new items) / DAU
        - Conversion rate: COUNT(wishlisted then purchased) / COUNT(wishlisted)
        - Average dwell time: AVG(purchase_date - added_at)
        - Popular products: Top wishlisted variants
        
    Performance:
        - Composite index (wishlist_id, added_at): Fast sorted retrieval
        - Index on variant_id: Fast popularity queries
        - Pagination: LIMIT/OFFSET for large wishlists
        - Eager loading: Join variant + product + images in single query
        
    Business Value:
        - Intent signal: High wishlist adds = popular product
        - Remarketing: Target users with wishlisted items
        - Inventory planning: Stock up on highly wishlisted items
        - Pricing strategy: Test price points on wishlisted items
    """
    __tablename__ = "wishlist_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    wishlist_id = Column(Integer, ForeignKey("wishlists.id", ondelete="CASCADE"), nullable=False, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=False, index=True)
    added_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    wishlist = relationship("Wishlist", back_populates="items")
    variant = relationship("ProductVariant")
    
    # Constraints
    __table_args__ = (
        # Prevent duplicate variants in same wishlist
        UniqueConstraint("wishlist_id", "variant_id", name="uq_wishlist_item_variant_per_wishlist"),
        
        # Index for variant lookups (check if item already wishlisted)
        Index("ix_wishlist_item_variant", "variant_id"),
        
        # Composite index for efficient wishlist queries
        Index("ix_wishlist_item_wishlist_added", "wishlist_id", "added_at"),
    )
    
    def __repr__(self):
        return f"<WishlistItem(id={self.id}, wishlist_id={self.wishlist_id}, variant_id={self.variant_id})>"
