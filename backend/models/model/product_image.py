from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ProductImage:
    image_id: int
    product_id: int
    image_url: str
