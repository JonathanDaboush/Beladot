from sqlalchemy import Column, Integer, ForeignKey, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from database import Base


class ShipmentItem(Base):
    """
    Line item linking a Shipment to specific OrderItems with quantity.
    
    Invariant: Sum of quantities across all shipment_items for a given order_item_id
    must not exceed the order_item.quantity (enforced at application level).
    
    Example: OrderItem has quantity=5
    - Shipment 1: ShipmentItem with quantity=3 ✓
    - Shipment 2: ShipmentItem with quantity=2 ✓
    - Shipment 3: ShipmentItem with quantity=1 ✗ (exceeds total)
    """
    __tablename__ = "shipment_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False, index=True)
    order_item_id = Column(Integer, ForeignKey("order_items.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)  # Quantity being shipped
    
    # Relationships
    shipment = relationship("Shipment", back_populates="items")
    order_item = relationship("OrderItem", back_populates="shipment_items")
    
    # Constraints
    __table_args__ = (
       
        CheckConstraint("quantity > 0", name="ck_shipment_item_quantity_positive"),
        UniqueConstraint("shipment_id", "order_item_id", name="uq_shipment_item_per_shipment"),       
        Index("ix_shipment_item_order_item", "order_item_id"),
    )
    
    def __repr__(self):
        return f"<ShipmentItem(id={self.id}, shipment_id={self.shipment_id}, quantity={self.quantity})>"
