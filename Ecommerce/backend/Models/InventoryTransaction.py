from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class TransactionType(str, enum.Enum):
    PURCHASE = "purchase"
    RESTOCK = "restock"
    RETURN = "return"
    ADJUSTMENT = "adjustment"
    DAMAGE = "damage"
    LOSS = "loss"


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    quantity_change = Column(Integer, nullable=False)
    quantity_after = Column(Integer, nullable=False)
    reference_id = Column(String(100), nullable=True, index=True)
    actor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    product = relationship("Product", back_populates="inventory_transactions")
    actor = relationship("User")
    
    __table_args__ = (
        CheckConstraint("quantity_change != 0", name='check_quantity_change_non_zero'),
        CheckConstraint("quantity_after >= 0", name='check_quantity_after_non_negative'),
    )
    
    def __repr__(self):
        return f"<InventoryTransaction(id={self.id}, product_id={self.product_id}, type={self.transaction_type})>"
