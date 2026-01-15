"""
manager.py

Model for manager entity.
Represents a manager and their department association.
"""

class Manager:
    def __init__(self, manager_id, user_id, department_id, is_active, created_at, last_active_at):
        """
        Initialize Manager.
        Args:
            manager_id (int): Unique identifier for the manager.
            user_id (int): User ID of the manager.
            department_id (int): Department ID associated with the manager.
            is_active (bool): Whether the manager is active.
            created_at (datetime): Creation timestamp.
            last_active_at (datetime): Last active timestamp.
        """
        self.manager_id = manager_id
        self.user_id = user_id
        self.department_id = department_id
        self.is_active = is_active
        self.created_at = created_at
        self.last_active_at = last_active_at
