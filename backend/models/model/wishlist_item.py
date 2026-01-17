from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class WishlistItem:
	wishlist_item_id: int
	wishlist_id: int
	product_id: int
	variant_id: int
	quantity: int
