"""
shipping_snapshot.py

Model for shipping snapshot entity.
Represents a snapshot of a shipment, including events, items, and total cost.
"""

from backend.model.enums import ShippingSnapshotStatus

class ShippingSnapshot:
    def __init__(self, snapshot_id, shipment_id, status=ShippingSnapshotStatus.COMPLETE, events=None, items=None, total_cost=0, created_at=None):
        """
        Initialize ShippingSnapshot.
        Args:
            snapshot_id (int): Unique identifier for the snapshot.
            shipment_id (int): Associated shipment ID.
            status (ShippingSnapshotStatus, optional): Status of the snapshot.
            events (list, optional): List of event dicts.
            items (list, optional): List of item dicts.
            total_cost (float, optional): Total cost of the shipment.
            created_at (datetime, optional): Creation timestamp.
        """
        self.snapshot_id = snapshot_id
        self.shipment_id = shipment_id
        self.status = status
        self.events = events or []  # List of dicts with event info
        self.items = items or []    # List of dicts with item info
        self.total_cost = total_cost
        self.created_at = created_at
