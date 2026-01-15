"""
refund_snapshot.py

Model for refund snapshot entity.
Represents a snapshot of a refund, including user, order, amount, and approval details.
"""


import hashlib
from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from backend.model.base import Base
import datetime

class RefundSnapshot(Base):
    __tablename__ = 'refund_snapshot'
    id = Column(Integer, primary_key=True)
    payment_user_name = Column(String(128), nullable=False)
    order_number = Column(String(64), nullable=False)
    amount = Column(Float, nullable=False)
    reason = Column(String(256), nullable=False)
    approved_by_name = Column(String(128), nullable=False)
    status = Column(String(32), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    checksum = Column(String(64), nullable=False, unique=True)

    __table_args__ = (
        Index('ix_refund_snapshot_order_number', 'order_number'),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.checksum = self.compute_checksum()

    def compute_checksum(self):
        data = f"{self.payment_user_name}{self.order_number}{self.amount}{self.reason}{self.approved_by_name}{self.status}{self.created_at}"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __setattr__(self, key, value):
        # Enforce immutability after creation except for checksum
        if hasattr(self, 'id') and self.id is not None and key not in {'checksum', '_sa_instance_state'}:
            raise AttributeError('Snapshots are immutable')
        super().__setattr__(key, value)
