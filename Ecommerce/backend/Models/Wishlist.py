from sqlalchemy import Column, Integer, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Wishlist(Base):
    """
    SQLAlchemy ORM model for wishlists table.
    
    User's saved items collection for later purchase consideration. Enables
    price drop notifications, back-in-stock alerts, and easy conversion to cart.
    One wishlist per user (aggregate root).
    
    Database Schema:
        - Primary Key: id (auto-increment)
        - Foreign Key: user_id -> users.id (CASCADE)
        - Indexes: id (primary), user_id (unique)
        - Unique constraint: One wishlist per user
        
    Data Integrity:
        - User must be unique (one wishlist per user)
        - Timestamps: updated_at >= created_at
        - Cascading delete when user deleted
        
    Relationships:
        - One-to-one with User (user has one wishlist)
        - One-to-many with WishlistItem (wishlist contains many items)
        
    Design Philosophy:
        - Lightweight: Minimal metadata, fast operations
        - Simple: Basic add/remove, no complex rules
        - Long-term: Items persist indefinitely (unlike cart expiration)
        - Marketing: Enable targeted campaigns (price drops, restock alerts)
        
    Use Cases:
        - Save for later: Customer browses, saves interesting products
        - Gift lists: Share wishlist URL with friends/family
        - Price tracking: Monitor for sales/discounts
        - Out-of-stock: Save items that are currently unavailable
        - Research: Compare products over time before purchasing
        
    Wishlist vs Cart:
        - Wishlist: Long-term intent, no expiration, no checkout
        - Cart: Short-term intent, expires after 30 days, leads to checkout
        - Conversion: "Add all to cart" button moves wishlist items to cart
        
    Lifecycle:
        1. User registers/logs in
        2. Create empty wishlist (on first wishlist action)
        3. User adds items via "Add to wishlist" button
        4. Items persist across sessions
        5. User receives notifications (price drops, restocks)
        6. User converts to cart: "Add all to cart" or individual items
        7. Wishlist remains (items not removed after purchase)
        
    Timestamps:
        - created_at: When wishlist first created (typically at user registration)
        - updated_at: Last time item added/removed (activity tracking)
        
    Marketing Features:
        - Email campaigns: "Items in your wishlist are on sale!"
        - Push notifications: "Price dropped on Product X"
        - Restock alerts: "Product Y back in stock"
        - Abandoned wishlist: "Still interested? Complete your purchase"
        - Share wishlist: Social sharing, gift registry
        
    Privacy:
        - Default: Private (only user can see)
        - Optional: Public/shared wishlist URL
        - Gift registry: Special mode for weddings, birthdays
        
    Analytics:
        - Wishlist size: COUNT(wishlist_items) per user
        - Conversion rate: Wishlist adds that become purchases
        - Popular items: Products most frequently wishlisted
        - Abandonment: Wishlist items never converted to cart
        
    Cart Conversion:
        - "Add to cart" single item: Create CartItem from WishlistItem
        - "Add all to cart": Bulk create CartItems from all WishlistItems
        - Stock check: Validate availability before adding to cart
        - Price update: Use current price (not wishlisted price)
        - Keep in wishlist: Items remain after adding to cart (non-destructive)
        
    Failure Handling:
        - Deleted variant: Show as unavailable, offer similar products
        - Out of stock: Show "Notify me" button
        - Price increased: Show old vs new price
        - Product discontinued: Suggest alternatives
        
    Performance:
        - Lazy loading: Don't fetch items until needed
        - Caching: Cache wishlist item count (display in header)
        - Pagination: Load items in batches (if large wishlist)
        
    Business Value:
        - Re-engagement: Bring users back with targeted notifications
        - Conversion: Lower barrier to purchase (saved shopping list)
        - Data: Learn customer preferences and interests
        - Retention: Keep users engaged between purchases
    """
    __tablename__ = "wishlists"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="wishlist")
    items = relationship("WishlistItem", back_populates="wishlist", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        # Timestamps: updated_at >= created_at
        CheckConstraint("updated_at >= created_at", name="ck_wishlist_updated_after_created"),
        
        # Index for user lookups (one wishlist per user)
        Index("ix_wishlist_user_id", "user_id"),
    )
    
    def __repr__(self):
        return f"<Wishlist(id={self.id}, user_id={self.user_id})>"
