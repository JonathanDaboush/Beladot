"""
address_snapshot.py

Model for address snapshot entity.
Represents a snapshot of an address for orders and shipments.
"""


import hashlib
from sqlalchemy import Column, Integer, String, DateTime, Index
from backend.model.base import Base
import datetime

class AddressSnapshot(Base):
    __tablename__ = 'address_snapshot'
    id = Column(Integer, primary_key=True)
    reference_type = Column(String(32), nullable=False)
    recipient_name = Column(String(128), nullable=False)
    street_line_1 = Column(String(128), nullable=False)
    street_line_2 = Column(String(128))
    city = Column(String(64), nullable=False)
    state_province = Column(String(64), nullable=False)
    postal_code = Column(String(32), nullable=False)
    country = Column(String(64), nullable=False)
    phone_number = Column(String(32), nullable=False)
    order_number = Column(String(64), nullable=False)
    shipment_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    checksum = Column(String(64), nullable=False, unique=True)

    __table_args__ = (
        Index('ix_address_snapshot_order_number', 'order_number'),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.checksum = self.compute_checksum()

    def compute_checksum(self):
        data = f"{self.reference_type}{self.recipient_name}{self.street_line_1}{self.street_line_2}{self.city}{self.state_province}{self.postal_code}{self.country}{self.phone_number}{self.order_number}{self.shipment_id}{self.created_at}"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __setattr__(self, key, value):
        # Enforce immutability after creation except for checksum
        if hasattr(self, 'id') and self.id is not None and key not in {'checksum', '_sa_instance_state'}:
            raise AttributeError('Snapshots are immutable')
        super().__setattr__(key, value)
