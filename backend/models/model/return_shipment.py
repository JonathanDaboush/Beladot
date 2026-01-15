"""
return_shipment.py

Model for return shipment entity.
Represents a shipment returned by a customer, including status and timestamps.
"""

class ReturnShipment:
    def __init__(self, return_shipment_id, original_shipment_id, return_status, shipped_at, received_at):
        """
        Initialize ReturnShipment.
        Args:
            return_shipment_id (int): Unique identifier for the return shipment.
            original_shipment_id (int): ID of the original shipment.
            return_status (str): Status of the return.
            shipped_at (datetime): Timestamp when shipped.
            received_at (datetime): Timestamp when received.
        """
        self.return_shipment_id = return_shipment_id
        self.original_shipment_id = original_shipment_id
        self.return_status = return_status
        self.shipped_at = shipped_at
        self.received_at = received_at
