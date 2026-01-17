from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class SellerReviewResponse:
    response_id: int
    review_id: int
    seller_id: int
    response_text: str
    created_at: Optional[datetime]
