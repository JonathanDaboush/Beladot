from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class ReviewStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"


class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True, index=True)
    rating = Column(Integer, nullable=False)
    title = Column(String(255), nullable=True)
    comment = Column(Text, nullable=True)
    is_verified_purchase = Column(Boolean, default=False, nullable=False, index=True)
    status = Column(SQLEnum(ReviewStatus), default=ReviewStatus.PENDING, nullable=False, index=True)
    moderation_notes = Column(Text, nullable=True)
    toxicity_score = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    
    product = relationship("Product", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
    order = relationship("Order")
    
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name='check_rating_range'),
        CheckConstraint("toxicity_score IS NULL OR (toxicity_score >= 0 AND toxicity_score <= 100)", name='check_toxicity_score_range'),
        CheckConstraint("approved_at IS NULL OR approved_at >= created_at", name='check_approved_after_created'),
        CheckConstraint("rejected_at IS NULL OR rejected_at >= created_at", name='check_rejected_after_created'),
        CheckConstraint("updated_at >= created_at", name='check_updated_after_created'),
    )
    
    def __repr__(self):
        return f"<Review(id={self.id}, product_id={self.product_id}, rating={self.rating}, status={self.status})>"
