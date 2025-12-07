from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class StoredPaymentMethod(Base):
    """
    SQLAlchemy ORM model for stored_payment_methods table.
    
    Securely stores customer payment methods (tokenized via payment gateway) for
    recurring charges, subscriptions, and one-click checkout.
    
    Database Schema:
        - Primary Key: id (auto-increment)
        - Foreign Key: user_id -> users.id (CASCADE delete)
        - Indexes: id (primary), user_id, gateway_token, is_default
        
    Data Integrity:
        - Gateway token required (never store raw card numbers)
        - Last 4 digits for display purposes only
        - One default per user (enforced in application logic)
        - Cascading delete when user deleted
        
    Relationships:
        - Many-to-one with User (user has multiple payment methods)
        
    Security:
        - gateway_token: Payment provider's token (e.g., Stripe pm_xxx)
        - NEVER stores CVV, full card number, or expiration date
        - PCI compliance via tokenization
        - Tokens invalidated when card expires or is reported stolen
        
    Design Notes:
        - card_brand: visa, mastercard, amex, etc.
        - card_last_four: Display for user to identify card
        - expiry_month/year: For expiration warnings
        - billing_zip: For AVS verification
        - is_default: Quick checkout default selection
        
    Usage:
        - Checkout: Customer selects from stored methods
        - Subscriptions: Auto-charge default method
        - One-click: Charge default without re-entering card
        
    Gateway Integration:
        - Stripe: gateway_token = pm_xxx (Payment Method ID)
        - PayPal: gateway_token = billing agreement ID
        - Must be validated with gateway before storage
    """
    __tablename__ = "stored_payment_methods"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    gateway_token = Column(String(255), nullable=False, index=True, unique=True)  # e.g., Stripe Payment Method ID
    card_brand = Column(String(50), nullable=True)  # visa, mastercard, amex, etc.
    card_last_four = Column(String(4), nullable=True)  # Last 4 digits for display
    expiry_month = Column(Integer, nullable=True)  # 1-12
    expiry_year = Column(Integer, nullable=True)  # 4-digit year
    billing_zip = Column(String(20), nullable=True)  # For AVS verification
    is_default = Column(Boolean, default=False, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)  # Can be disabled without deletion
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    user = relationship("User", back_populates="stored_payment_methods")
    
    def __repr__(self):
        return f"<StoredPaymentMethod(id={self.id}, user_id={self.user_id}, brand={self.card_brand}, last_four={self.card_last_four})>"
