"""
employee_snapshot.py

Model for employee snapshot records, including name, department, role, and approval details.
Represents a snapshot of an employee's record for auditing and historical tracking.
"""


import hashlib
from sqlalchemy import Column, Integer, String, DateTime, Index
from backend.model.base import Base
import datetime

class EmployeeSnapshot(Base):
    __tablename__ = 'employee_snapshot'
    id = Column(Integer, primary_key=True)
    full_name = Column(String(128), nullable=False)
    department_name = Column(String(128), nullable=False)
    role = Column(String(64), nullable=False)
    approved_by_name = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    checksum = Column(String(64), nullable=False, unique=True)

    __table_args__ = (
        Index('ix_employee_snapshot_full_name', 'full_name'),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.checksum = self.compute_checksum()

    def compute_checksum(self):
        data = f"{self.full_name}{self.department_name}{self.role}{self.approved_by_name}{self.created_at}"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __setattr__(self, key, value):
        # Enforce immutability after creation except for checksum
        if hasattr(self, 'id') and self.id is not None and key not in {'checksum', '_sa_instance_state'}:
            raise AttributeError('Snapshots are immutable')
        super().__setattr__(key, value)
