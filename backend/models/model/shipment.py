"""
shipment.py

Model for shipment entity.
Represents a shipment for an order, including status and identifiers.
"""


from sqlalchemy import Column, Integer, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from backend.model.base import Base
from backend.model.enums import ShipmentStatus

class Shipment(Base):
    __tablename__ = 'shipment'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('order.id', ondelete='CASCADE'), nullable=False, index=True)
    shipment_status = Column(Enum(ShipmentStatus), default=ShipmentStatus.CREATED, nullable=False)

    __table_args__ = (
        Index('ix_shipment_order_id', 'order_id'),
    )

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


