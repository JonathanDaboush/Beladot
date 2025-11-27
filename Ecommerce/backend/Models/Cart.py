from sqlalchemy import Column, Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Cart(Base):
    """
    SQLAlchemy ORM model for carts table.
    
    Shopping cart associated with user or guest session. Stores cart items
    and timestamps for cart activity tracking.
    
    Database Schema:
        - Primary Key: id (auto-increment)
        - Foreign Key: user_id -> users.id (CASCADE delete, nullable)
        - Indexes: id (primary), user_id
        
    Data Integrity:
        - updated_at >= created_at
        - Cascading delete when user deleted
        - Cart items cascade deleted when cart deleted
        
    Relationships:
        - One-to-one with User (user can have one cart)
        - One-to-many with CartItem (cascade delete)
        
    Design Notes:
        - user_id nullable supports guest carts (session-based)
        - Timestamps track cart creation and last modification
        - Cart persistence enables "save for later" and cross-device sync
    """
    __tablename__ = "carts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    user = relationship("User", back_populates="cart")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("updated_at >= created_at", name='check_updated_after_created'),
    )
    
    def __repr__(self):
        return f"<Cart(id={self.id}, user_id={self.user_id})>"
