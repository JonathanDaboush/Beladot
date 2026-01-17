from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ProductVariant:
    variant_id: int
    product_id: int
    variant_name: str
    price: float
    quantity: int
    is_active: bool
