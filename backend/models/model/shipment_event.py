"""
shipment_event.py

Model for shipment event entity.
Represents an event in the shipment lifecycle, including status, location, and timestamps.
"""

from backend.model.enums import ShipmentEventStatus

class ShipmentEvent:
    def __init__(self, event_id, shipment_id, status=ShipmentEventStatus.CREATED, description=None, location=None, occurred_at=None, created_at=None, updated_at=None):
        """
        Initialize ShipmentEvent.
        Args:
            event_id (int): Unique identifier for the event.
            shipment_id (int): Associated shipment ID.
            status (ShipmentEventStatus, optional): Status of the event.
            description (str, optional): Description of the event.
            location (str, optional): Location of the event.
            occurred_at (datetime, optional): When the event occurred.
            created_at (datetime, optional): Creation timestamp.
            updated_at (datetime, optional): Last update timestamp.
        """
        self.event_id = event_id
        self.shipment_id = shipment_id
        self.status = status
        self.description = description
        self.location = location
        self.occurred_at = occurred_at
        self.created_at = created_at
        self.updated_at = updated_at
