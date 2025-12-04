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
    """
    SQLAlchemy ORM model for inventory_transactions table.
    
    Immutable audit log for all inventory movements. Implements double-entry
    ledger pattern where every stock change is recorded with before/after snapshots.
    
    Database Schema:
        - Primary Key: id (auto-increment)
        - Foreign Keys: product_id -> products.id (CASCADE), actor_id -> users.id (SET NULL)
        - Indexes: id (primary), product_id, reference_id, created_at
        
    Data Integrity:
        - quantity_change cannot be zero (must be positive or negative)
        - quantity_after must be non-negative (no negative stock)
        - Immutable records (no updates, only inserts)
        
    Relationships:
        - Many-to-one with Product (product has many transactions)
        - Many-to-one with User (actor who initiated the transaction)
        
    Transaction Types:
        - PURCHASE: Customer order decreases stock (negative change)
        - RESTOCK: Supplier delivery increases stock (positive change)
        - RETURN: Customer return increases stock (positive change)
        - ADJUSTMENT: Manual correction (positive or negative)
        - DAMAGE: Damaged goods removed (negative change)
        - LOSS: Lost/stolen inventory (negative change)
        
    Ledger Pattern:
        - Every transaction records:
          * quantity_change: Delta applied (e.g., -5 for purchase of 5 units)
          * quantity_after: Snapshot of stock level after transaction
        - Enable auditing: Reconstruct inventory at any point in time
        - Detect discrepancies: Compare physical count vs. ledger
        
    Design Notes:
        - reference_id: Links to source record (order_id, shipment_id, etc.)
        - actor_id: User who initiated (admin, system, customer)
        - notes: Free-text explanation for adjustments/corrections
        - created_at: Immutable timestamp (transaction time)
        - No updates allowed: Corrections use ADJUSTMENT transactions
        
    Query Patterns:
        - Current stock: Latest quantity_after for product_id
        - Stock history: SELECT * WHERE product_id = X ORDER BY created_at
        - Variance report: SUM(quantity_change) GROUP BY transaction_type
        - Audit trail: Filter by reference_id to see order impact
        
    Reconciliation:
        - Physical count != quantity_after → Create ADJUSTMENT transaction
        - Example: Expected 100, counted 95 → ADJUSTMENT of -5
    """
    __tablename__ = "inventory_transactions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_type = Column(SQLEnum(TransactionType, values_callable=lambda x: [e.value for e in x]), nullable=False)
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
