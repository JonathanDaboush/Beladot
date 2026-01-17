from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class ProductRating:
    rating_id: int
    product_id: int
    user_id: int
    rating: int
    created_at: Optional[datetime]
