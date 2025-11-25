from typing import Any
from datetime import datetime, timezone

class Review:
    def __init__(self, id, product_id, user_id, order_id, rating, title, comment, is_verified_purchase, status, moderation_notes, toxicity_score, created_at, updated_at, approved_at, rejected_at):
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