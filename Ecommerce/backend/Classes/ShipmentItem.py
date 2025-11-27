# Represents which OrderItems are included in a specific shipment and in what quantities.
# Needed because orders can ship in multiple boxes or some items may ship separately.

class ShipmentItem:
    """
    Domain model representing an order item included in a specific shipment.
    
    This class links order items to shipments, enabling split shipments where an order
    ships in multiple packages or items ship separately. It tracks which items and how
    many units are in each shipment box.
    
    Key Responsibilities:
        - Link order items to shipments
        - Track quantity in this specific shipment
        - Support partial shipments (quantity < ordered)
    
    Use Cases:
        - Split shipments: Large orders shipping in multiple boxes
        - Partial shipments: Some items ready before others
        - Separate shipments: Different warehouses or carriers
    
    Design Pattern:
        - Join entity between Shipment and OrderItem
        - Owned entity (lifecycle controlled by Shipment)
    
    Design Notes:
        - Sum of quantities across all shipments should equal order item quantity
        - This is a domain object; persistence handled by ShipmentItemRepository
    """
    def __init__(self, id, shipment_id, order_item_id, quantity):
        """
        Initialize a ShipmentItem domain object.
        
        Args:
            id: Unique identifier (None for new items before persistence)
            shipment_id: Foreign key to parent shipment
            order_item_id: Foreign key to order item being shipped
            quantity: Number of units in this shipment (may be less than ordered)
        """
        self.id = id  # Unique shipment item identifier
        self.shipment_id = shipment_id  # Links to parent Shipment
        self.order_item_id = order_item_id  # Links to OrderItem being shipped in this package
        self.quantity = quantity  # How many units of this item are in this shipment (may be less than ordered if partial shipment)
