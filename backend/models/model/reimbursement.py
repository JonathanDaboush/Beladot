"""
reimbursement.py

Model for reimbursement entity.
Represents a reimbursement record, including incident, approval, and status details.
"""

from backend.model.enums import ReimbursementStatus

class Reimbursement:
    def __init__(self, reimbursement_id, incident_id, description, response=None, amount_approved=None, status=ReimbursementStatus.PENDING, deleted=False):
        """
        Initialize Reimbursement.
        Args:
            reimbursement_id (int): Unique identifier for the reimbursement.
            incident_id (int): Associated incident ID.
            description (str): Description of the reimbursement.
            response (str, optional): Response to the reimbursement.
            amount_approved (float, optional): Approved amount.
            status (ReimbursementStatus, optional): Status of the reimbursement.
            deleted (bool, optional): Whether the reimbursement is deleted.
        """
        self.reimbursement_id = reimbursement_id
        self.incident_id = incident_id
        self.description = description
        self.response = response
        self.amount_approved = amount_approved
        self.status = status
        self.deleted = deleted
