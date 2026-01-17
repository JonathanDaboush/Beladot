
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class CartItem:
	cart_item_id: int
	cart_id: int
	product_id: int
	variant_id: Optional[int]
	quantity: int
