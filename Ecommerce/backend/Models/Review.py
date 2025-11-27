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
    """
    SQLAlchemy ORM model for reviews table.
    
    User-generated product reviews with moderation workflow, verified purchase badges,
    and automated toxicity detection. Supports star ratings, titles, and detailed comments.
    
    Database Schema:
        - Primary Key: id (auto-increment)
        - Foreign Keys: product_id -> products.id (CASCADE), user_id -> users.id (CASCADE),
                       order_id -> orders.id (SET NULL)
        - Indexes: id (primary), product_id, user_id, order_id, is_verified_purchase,
                   status, created_at
        
    Data Integrity:
        - Rating must be 1-5 stars (inclusive)
        - Toxicity score (if present) must be 0-100
        - Approval timestamp must be after creation
        - Rejection timestamp must be after creation
        - Updated timestamp must be after creation
        
    Relationships:
        - Many-to-one with Product (product has many reviews)
        - Many-to-one with User (user can write many reviews)
        - Many-to-one with Order (optional, for verified purchases)
        
    Moderation Workflow:
        1. PENDING: Review submitted, awaiting moderation
        2. APPROVED: Passes moderation, displayed publicly
        3. REJECTED: Violates guidelines, not displayed
        4. FLAGGED: Reported by users, needs admin review
        
    Verified Purchase:
        - is_verified_purchase: True if order_id exists and user purchased product
        - Adds credibility badge to review
        - Prevents fake reviews from non-customers
        
    Content Safety:
        - toxicity_score: 0-100 from ML toxicity detection API
        - High scores auto-flag for moderation
        - Thresholds: <30 (clean), 30-70 (review), >70 (auto-reject)
        
    Design Notes:
        - title: Optional short headline (e.g., "Great product!")
        - comment: Detailed review text
        - moderation_notes: Internal notes from moderation team
        - Rating required, title/comment optional
        - Order link enables purchase verification
        
    Display Logic:
        - Public: status = APPROVED
        - Verified badge: is_verified_purchase = true
        - Average rating: AVG(rating) WHERE status = APPROVED
        - Sort by: created_at DESC (newest first)
        
    Anti-Spam:
        - One review per user per product (application-level enforcement)
        - Verified purchases prioritized in sorting
        - Toxicity detection prevents abuse
        
    Analytics:
        - Average rating per product
        - Review count per product
        - Verification rate: COUNT(is_verified_purchase=true) / COUNT(*)
        - Moderation metrics: Approval/rejection rates
    """
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
