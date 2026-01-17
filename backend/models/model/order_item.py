"""
order_item.py

Expose the canonical OrderItem ORM model from the persistence layer to avoid
duplicate table declarations. Use backend.persistance.order_item.OrderItem as
the single source of truth for the 'order_item' table.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class OrderItem:
	order_item_id: int
	order_id: int
	product_id: int
	variant_id: Optional[int]
	quantity: int
	subtotal: float
