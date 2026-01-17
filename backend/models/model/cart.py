
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Cart:
	cart_id: int
	user_id: int
	created_at: Optional[datetime]
	updated_at: Optional[datetime]
