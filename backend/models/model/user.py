from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(slots=True)
class User:
	user_id: int
	full_name: str
	dob: Optional[date]
	password: str
	phone_number: Optional[str]
	email: str
	created_at: Optional[date]
	img_location: Optional[str]
	account_status: str
