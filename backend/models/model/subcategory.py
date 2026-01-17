from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Subcategory:
    subcategory_id: int
    category_id: int
    name: str
    image_url: Optional[str]
