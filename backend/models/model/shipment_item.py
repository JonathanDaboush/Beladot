"""
shipment_item.py

Model for shipment item entity.
Represents an item within a shipment, including product, variant, and status.
"""

from backend.model.enums import ShipmentItemStatus

class ShipmentItem:
    def __init__(self, shipment_item_id, shipment_id, product_id, variant_id, quantity, status=ShipmentItemStatus.PENDING, shipment_event_id=None):
        """
        Initialize ShipmentItem.
        Args:
            shipment_item_id (int): Unique identifier for the shipment item.
            shipment_id (int): Associated shipment ID.
            product_id (int): Product ID.
            variant_id (int): Variant ID.
            quantity (int): Quantity of the item.
            status (ShipmentItemStatus, optional): Status of the item.
            shipment_event_id (int, optional): Associated shipment event ID.
        """
        self.shipment_item_id = shipment_item_id
        self.shipment_id = shipment_id
        self.product_id = product_id
        self.variant_id = variant_id
        self.quantity = quantity
        self.status = status
        self.shipment_event_id = shipment_event_id
