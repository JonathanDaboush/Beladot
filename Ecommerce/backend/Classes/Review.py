from typing import Any
from datetime import datetime, timezone

class Review:
    """
    Domain model representing a product review with moderation and verification features.
    
    This class manages customer reviews, including content moderation, verified purchase
    badges, and cache invalidation for performance. It supports admin approval workflows
    and toxicity detection.
    
    Key Responsibilities:
        - Store review content (rating, title, comment)
        - Track review status (pending, approved, rejected)
        - Verify purchases (is_verified_purchase badge)
        - Support moderation workflow with notes
        - Detect potentially toxic content (toxicity_score)
        - Invalidate product review caches on approval
    
    Review States:
        - pending: Awaiting moderation
        - approved: Published and visible
        - rejected: Rejected by moderator
    
    Moderation Features:
        - Manual approval by admins
        - Toxicity scoring (ML-based or keyword-based)
        - Moderation notes for audit trail
        - Verified purchase badge builds trust
    
    Design Notes:
        - Reviews linked to products, users, and optionally orders
        - order_id enables verified purchase detection
        - toxicity_score guides moderation priority
        - This is a domain object; persistence handled by ReviewRepository
    """
    def __init__(self, id, product_id, user_id, order_id, rating, title, comment, is_verified_purchase, status, moderation_notes, toxicity_score, created_at, updated_at, approved_at, rejected_at):
        """
        Initialize a Review domain object.
        
        Args:
            id: Unique identifier (None for new reviews before persistence)
            product_id: Foreign key to the product being reviewed
            user_id: Foreign key to the reviewing user
            order_id: Foreign key to purchase order (None if not verified)
            rating: Star rating (typically 1-5)
            title: Review title/headline
            comment: Review text content
            is_verified_purchase: Whether user purchased this product
            status: Review status (pending, approved, rejected)
            moderation_notes: Admin notes about moderation decision
            toxicity_score: ML-generated toxicity score (0-1, higher = more toxic)
            created_at: Review creation timestamp
            updated_at: Last modification timestamp
            approved_at: When review was approved
            rejected_at: When review was rejected
        """
        self.id = id
        self.product_id = product_id
        self.user_id = user_id
        self.order_id = order_id
        self.rating = rating
        self.title = title
        self.comment = comment
        self.is_verified_purchase = is_verified_purchase
        self.status = status
        self.moderation_notes = moderation_notes
        self.toxicity_score = toxicity_score
        self.created_at = created_at
        self.updated_at = updated_at
        self.approved_at = approved_at
        self.rejected_at = rejected_at
    
    def approve(self, actor_id: str, repository=None, cache_service=None) -> None:
        """
        Approve the review and invalidate product review cache.
        
        Args:
            actor_id: ID of user approving the review
            repository: Repository for persisting changes and audit log (optional)
            cache_service: Service for cache invalidation (optional)
            
        Side Effects:
            - Changes status to 'approved'
            - Sets approved_at to current time
            - Updates updated_at timestamp
            - Appends approval note to moderation_notes
            - Creates audit log entry
            - Invalidates product review cache
            - Persists review via repository
            
        Design Notes:
            - Idempotent (returns early if already approved)
            - Cache invalidation failures silently ignored
            - Moderation notes accumulate with timestamps
        """
        if self.status == "approved":
            return
        
        self.status = "approved"
        self.approved_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        self.moderation_notes = f"{self.moderation_notes or ''}\n[{datetime.now(timezone.utc).isoformat()}] Approved by {actor_id}"
        
        if repository:
            repository.update(self)
            repository.create_audit_log({
                "actor_id": actor_id,
                "action": "review.approved",
                "target_type": "review",
                "target_id": self.id,
                "metadata": {"product_id": self.product_id}
            })
        
        if cache_service:
            try:
                cache_service.invalidate(f"product:{self.product_id}:reviews")
            except:
                pass
    
    def to_dict(self, include_moderation: bool = False) -> dict[str, Any]:
        """
        Convert review to dictionary for API responses.
        
        Args:
            include_moderation: If True, include moderation data (default False)
            
        Returns:
            dict: Review data with optional moderation fields
            
        Design Notes:
            - Moderation data (notes, toxicity, dates) requires admin access
            - Public API should never include moderation details
            - Verified purchase badge included for trust
        """
        result = {
            "id": self.id,
            "product_id": self.product_id,
            "user_id": self.user_id,
            "rating": self.rating,
            "title": self.title,
            "comment": self.comment,
            "is_verified_purchase": self.is_verified_purchase,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_moderation:
            result["moderation_notes"] = self.moderation_notes
            result["toxicity_score"] = self.toxicity_score
            result["approved_at"] = self.approved_at.isoformat() if self.approved_at else None
            result["rejected_at"] = self.rejected_at.isoformat() if self.rejected_at else None
        
        return result