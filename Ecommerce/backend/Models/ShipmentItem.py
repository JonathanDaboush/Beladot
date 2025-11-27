from sqlalchemy import Column, Integer, ForeignKey, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from database import Base


class ShipmentItem(Base):
    """
    SQLAlchemy ORM model for shipment_items table.
    
    Junction table linking Shipments to OrderItems with per-shipment quantities.
    Enables partial fulfillment where orders ship in multiple packages over time.
    Tracks exactly which items and quantities are in each shipment.
    
    Database Schema:
        - Primary Key: id (auto-increment)
        - Foreign Keys: shipment_id -> shipments.id (CASCADE),
                       order_item_id -> order_items.id (CASCADE)
        - Indexes: id (primary), shipment_id, order_item_id
        - Unique constraint: (shipment_id, order_item_id) - one line per item per shipment
        
    Data Integrity:
        - Quantity must be positive (at least 1 unit)
        - Unique constraint prevents duplicate item entries per shipment
        - Cascading delete when shipment or order item deleted
        
    Relationships:
        - Many-to-one with Shipment (shipment contains many items)
        - Many-to-one with OrderItem (order item can be in multiple shipments)
        
    Critical Invariant:
        - Application-level validation required:
          SUM(shipment_items.quantity WHERE order_item_id = X) <= order_item.quantity
        - Prevents over-shipping (can't ship more than ordered)
        - Enforced before creating ShipmentItem records
        
    Partial Fulfillment Example:
        Order contains:
        - OrderItem 1: Product A, quantity = 10
        - OrderItem 2: Product B, quantity = 5
        
        Shipment 1 (initial partial shipment):
        - ShipmentItem 1: order_item_id=1, quantity=6 (ship 6 of Product A)
        - ShipmentItem 2: order_item_id=2, quantity=5 (ship all of Product B)
        
        Shipment 2 (backorder fulfillment):
        - ShipmentItem 3: order_item_id=1, quantity=4 (ship remaining 4 of Product A)
        
        Total shipped:
        - Product A: 6 + 4 = 10 ✓ (matches ordered quantity)
        - Product B: 5 = 5 ✓ (matches ordered quantity)
        
    Use Cases:
        - Split shipments: Large orders ship from multiple warehouses
        - Backorders: Out-of-stock items ship later when restocked
        - Drop shipping: Some items ship directly from supplier
        - Partial cancellation: Customer cancels some items, rest still ship
        
    Fulfillment Status Tracking:
        - Unfulfilled quantity per OrderItem:
          order_item.quantity - SUM(shipment_items.quantity)
        - Fully fulfilled: unfulfilled_quantity = 0
        - Partially fulfilled: unfulfilled_quantity > 0
        
    Design Notes:
        - quantity: Number of units in THIS shipment (not cumulative)
        - No price information: Prices stored in OrderItem (single source of truth)
        - No product details: Link to OrderItem for product info
        - Immutable: Don't update after shipment created (create new shipment instead)
        
    Validation Logic:
        ```python
        # Before creating ShipmentItem
        already_shipped = db.query(func.sum(ShipmentItem.quantity))
                           .filter(ShipmentItem.order_item_id == order_item.id)
                           .scalar() or 0
        
        remaining = order_item.quantity - already_shipped
        
        if new_shipment_quantity > remaining:
            raise ValueError(f"Cannot ship {new_shipment_quantity}, only {remaining} remaining")
        ```
        
    Query Patterns:
        - Shipment contents: SELECT * WHERE shipment_id = X
        - Item fulfillment status:
          SELECT order_item_id, SUM(quantity) as shipped
          FROM shipment_items
          WHERE order_item_id IN (...)
          GROUP BY order_item_id
        - Unfulfilled items:
          SELECT oi.*, oi.quantity - COALESCE(SUM(si.quantity), 0) as remaining
          FROM order_items oi
          LEFT JOIN shipment_items si ON oi.id = si.order_item_id
          GROUP BY oi.id
          HAVING remaining > 0
        
    Reporting:
        - Fulfillment rate: COUNT(fully_fulfilled) / COUNT(order_items)
        - Average fulfillment time: AVG(first_shipment_date - order_date)
        - Split shipment rate: COUNT(orders with multiple shipments) / COUNT(orders)
        
    Warehouse Management:
        - Pick list: Generate from ShipmentItem records
        - Packing slip: Print order items with quantities per shipment
        - Inventory allocation: Reserve stock when shipment created
        - Inventory deduction: Decrement stock when shipment status = SHIPPED
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
