from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ProductVariantImage:
    image_id: int
    variant_id: int
    image_url: str
