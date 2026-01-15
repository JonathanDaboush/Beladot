"""
paystub_snapshot.py

Model for paystub snapshot entity.
Represents a snapshot of an employee's paystub, including hours, pay, and deductions.
"""


import hashlib
from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from backend.model.base import Base
import datetime

class PaystubSnapshot(Base):
    __tablename__ = 'paystub_snapshot'
    id = Column(Integer, primary_key=True)
    employee_name = Column(String(128), nullable=False)
    hours_worked = Column(Float, nullable=False)
    sick_days = Column(Integer, nullable=False)
    pto_days = Column(Integer, nullable=False)
    hourly_rate = Column(Float, nullable=False)
    gross_pay = Column(Float, nullable=False)
    deductions = Column(Float, nullable=False)
    net_pay = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    checksum = Column(String(64), nullable=False, unique=True)

    __table_args__ = (
        Index('ix_paystub_snapshot_employee_name', 'employee_name'),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.checksum = self.compute_checksum()

    def compute_checksum(self):
        data = f"{self.employee_name}{self.hours_worked}{self.sick_days}{self.pto_days}{self.hourly_rate}{self.gross_pay}{self.deductions}{self.net_pay}{self.created_at}"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __setattr__(self, key, value):
        # Enforce immutability after creation except for checksum
        if hasattr(self, 'id') and self.id is not None and key not in {'checksum', '_sa_instance_state'}:
            raise AttributeError('Snapshots are immutable')
        super().__setattr__(key, value)
