"""
shipment_issue.py

Model for shipment issue entity.
Represents an issue related to a shipment, including type, description, and resolution.
"""

from backend.model.enums import ShipmentIssueResolution

class ShipmentIssue:
    def __init__(self, issue_id, shipment_id, shipment_employee_name, issue_type, description, created_at, appointted_to, resolution=ShipmentIssueResolution.UNRESOLVED):
        """
        Initialize ShipmentIssue.
        Args:
            issue_id (int): Unique identifier for the issue.
            shipment_id (int): Associated shipment ID.
            shipment_employee_name (str): Name of the shipment employee.
            issue_type (str): Type of the issue.
            description (str): Description of the issue.
            created_at (datetime): Creation timestamp.
            appointted_to (str): Person appointed to resolve the issue.
            resolution (ShipmentIssueResolution, optional): Resolution status.
        """
        self.issue_id = issue_id
        self.shipment_id = shipment_id
        self.shipment_employee_name = shipment_employee_name
        self.issue_type = issue_type
        self.description = description
        self.created_at = created_at
        self.appointted_to = appointted_to
        self.resolution = resolution