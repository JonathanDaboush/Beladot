
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Product:
	product_id: int
	seller_id: int
	category_id: int
	subcategory_id: int
	title: str
	description: Optional[str]
	price: float
	currency: str
	is_active: bool
	created_at: Optional[datetime]
	updated_at: Optional[datetime]
