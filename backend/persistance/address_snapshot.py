
# ------------------------------------------------------------------------------
# address_snapshot.py
# ------------------------------------------------------------------------------
# SQLAlchemy ORM model for the address_snapshot table.
# This module defines the AddressSnapshot class, which represents a snapshot of
# an address at a specific point in time. Used for historical or reference
# purposes, such as storing the address associated with an order or shipment.
# ------------------------------------------------------------------------------

from sqlalchemy import Column, String, Integer
from backend.db.base import Base

class AddressSnapshot(Base):
    """
    ORM model for the 'address_snapshot' table.
    Represents a snapshot of an address for historical or reference purposes.

    Attributes:
        reference_type (String): Type of reference (e.g., 'order', 'shipment').
        recipient_name (String): Name of the recipient at this address.
        street_line_1 (String): First line of the street address.
        street_line_2 (String): Second line of the street address (optional).
        city (String): City of the address.
        state_province (String): State or province of the address.
        postal_code (String): Postal or ZIP code.
        country (String): Country of the address.
        phone_number (String): Contact phone number for the address.
        order_number (String): Order number associated with this address (if any).
        shipment_id (String): Shipment ID associated with this address (if any).
    """
    __tablename__ = 'address_snapshot'
    id = Column(Integer, primary_key=True, index=True)
    reference_type = Column(String(50))
    recipient_name = Column(String(255))
    street_line_1 = Column(String(255))
    street_line_2 = Column(String(255))
    city = Column(String(100))
    state_province = Column(String(50))
    postal_code = Column(String(20))
    country = Column(String(50))
    phone_number = Column(String(20))
    order_number = Column(String(50))  # Order reference (if applicable)
    shipment_id = Column(String(50))   # Shipment reference (if applicable)
