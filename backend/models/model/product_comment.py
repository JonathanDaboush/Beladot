"""
product_comment.py

Domain model for product comments (pure dataclass, no ORM).
Represents a user's comment on a product.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(slots=True)
class ProductComment:
    comment_id: int
    product_id: int
    user_id: int
    comment: str
    created_at: Optional[datetime] = None
