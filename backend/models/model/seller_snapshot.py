from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SellerSnapshot:
    store_name: str
    contact_email: str
    seller_type: str
    approved_by_name: str
 
