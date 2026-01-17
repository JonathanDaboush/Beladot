from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ShipmentAddress:
    shipment_address_id: int
    shipment_id: int
    recipient_name: str
    address_line_1: str
    address_line_2: str
    city: str
    state_province: str
    postal_code: str
    country: str
    phone_number: str
 
