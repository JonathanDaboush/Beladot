from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class ProductReview:
    review_id: int
    product_id: int
    user_id: int
    rating_id: int
    review_text: str
    created_at: Optional[datetime]
