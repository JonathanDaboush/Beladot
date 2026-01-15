"""
shift_request.py

Model for shift request entity.
Represents a request for a work shift, including approval and status.
"""

from backend.model.enums import ShiftRequestStatus

class ShiftRequest:
    def __init__(self, shift_request_id, shift_id, requesting_emp_id, approved_by_manager_id, status=ShiftRequestStatus.REQUESTED):
        """
        Initialize ShiftRequest.
        Args:
            shift_request_id (int): Unique identifier for the shift request.
            shift_id (int): Associated shift ID.
            requesting_emp_id (int): Employee ID requesting the shift.
            approved_by_manager_id (int): Manager ID who approved the request.
            status (ShiftRequestStatus, optional): Status of the request.
        """
        self.shift_request_id = shift_request_id
        self.shift_id = shift_id
        self.requesting_emp_id = requesting_emp_id
        self.approved_by_manager_id = approved_by_manager_id
        self.status = status
