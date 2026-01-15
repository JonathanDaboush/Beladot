class UserSnapshot:
    def __init__(self, full_name, email, phone_number, account_type, bank, approved_by_name):
"""
user_snapshot.py

Model for user snapshot entity.
Represents a snapshot of a user's account, including credentials and contact info.
"""

class UserSnapshot:
    def __init__(self, us_id, user_id, username, password, email, phone, dob, user_type):
        """
        Initialize UserSnapshot.
        Args:
            us_id (int): Unique identifier for the user snapshot.
            user_id (int): Associated user ID.
            username (str): Username.
            password (str): Password hash.
            email (str): Email address.
            phone (str): Phone number.
            dob (str): Date of birth.
            user_type (str): Type of user (e.g., admin, customer).
        """
        self.us_id = us_id
        self.user_id = user_id
        self.username = username
        self.password = password
        self.email = email
        self.phone = phone
        self.dob = dob
        self.user_type = user_type
