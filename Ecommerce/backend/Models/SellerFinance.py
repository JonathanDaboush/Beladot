from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class SellerFinance(Base):
    __tablename__ = "seller_finance"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False, unique=True)
    bank_account_number = Column(String(255), nullable=False)
    bank_routing_number = Column(String(255), nullable=False)
    account_holder_name = Column(String(255), nullable=False)
    bank_country = Column(String(100), nullable=False)
    payout_frequency = Column(String(50), default="weekly", nullable=False)
    document_type = Column(String(50), nullable=True)
    document_url = Column(String(500), nullable=True)
    document_verified = Column(Boolean, default=False)
    seller = relationship("Seller", back_populates="finance_info")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
