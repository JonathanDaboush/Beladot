"""
incident.py

Model for incident entity.
Represents an incident involving an employee, including status and cost.
"""

from backend.model.enums import IncidentStatus

class Incident:
    def __init__(self, incident_id=None, employee_id=None, description=None, cost=None, date=None, status=IncidentStatus.OPEN, deleted=False):
        """
        Initialize Incident.
        Args:
            incident_id (int, optional): Unique identifier for the incident (auto-generated if None).
            employee_id (int): Employee ID involved in the incident.
            description (str): Description of the incident.
            cost (float): Cost associated with the incident.
            date (datetime, optional): Date of the incident.
            status (IncidentStatus, optional): Status of the incident.
            deleted (bool, optional): Whether the incident is deleted.
        """
        self.incident_id = incident_id
        self.employee_id = employee_id
        self.description = description
        self.cost = cost
        self.date = date
        self.status = status
        self.deleted = deleted
