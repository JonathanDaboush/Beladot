from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Seller(Base):
    __tablename__ = "sellers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    legal_business_name = Column(String(255), nullable=False)
    business_type = Column(String(100), nullable=False)
    phone_number = Column(String(50), nullable=False)
    business_address = Column(String(255), nullable=False)
    tax_id = Column(String(100), nullable=False)
    tax_country = Column(String(50), nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_submitted_at = Column(DateTime(timezone=True), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    user = relationship("User", back_populates="seller_profile")
    products = relationship("Product", back_populates="seller", cascade="all, delete-orphan")
    variant_categories = relationship("VariantCategory", back_populates="seller", cascade="all, delete-orphan")
    finance_info = relationship("SellerFinance", back_populates="seller", uselist=False, cascade="all, delete-orphan")
    payouts = relationship("SellerPayout", back_populates="seller", cascade="all, delete-orphan")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
