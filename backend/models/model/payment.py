
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from backend.model.base import Base

class Payment(Base):
    __tablename__ = 'payment'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('order.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(8), nullable=False)
    status = Column(String(32), nullable=False)

    __table_args__ = (
        Index('ix_payment_order_id', 'order_id'),
        Index('ix_payment_user_id', 'user_id'),
    )

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
