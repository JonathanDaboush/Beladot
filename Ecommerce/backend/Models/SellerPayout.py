from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime, String, Table, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class SellerPayout(Base):
    __tablename__ = 'seller_payouts'
    id = Column(Integer, primary_key=True)
    seller_id = Column(Integer, ForeignKey('sellers.id'), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    payout_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String(32), nullable=False, default='pending')  # pending, completed, failed
    related_order_ids = Column(String, nullable=True)  # CSV of order IDs for simplicity
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    seller = relationship('Seller', back_populates='payouts')
