from sqlalchemy import Column, Integer, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Wishlist(Base):
    """
    Lightweight user-owned collection of variant IDs for long-term intent.
    
    Responsibilities:
    - Enable saved items list for marketing and conversions
    - Support simple operations (add/remove)
    - Easy conversion to Cart
    
    Design: Minimal metadata — only IDs and timestamps.
    No heavy business logic; keep it fast and simple.
    
    Failure modes:
    - Stale variants (deleted/out-of-stock) handled at cart migration
    - WishlistService provides clear UI messaging
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
