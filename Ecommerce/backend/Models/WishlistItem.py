from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class WishlistItem(Base):
    """
    Lightweight line item in a Wishlist.
    
    Design: Stores only variant_id and timestamp — no heavy metadata.
    Supports simple add/remove operations and easy Cart conversion.
    
    Failure modes:
    - Stale variants (deleted/out-of-stock) detected during cart migration
    - Foreign key CASCADE handles deleted variants automatically
    - WishlistService provides clear UI messaging for unavailable items
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
