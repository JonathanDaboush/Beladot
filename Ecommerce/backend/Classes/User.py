# Represents a registered user account (customer, admin, or staff member).
# Central to authentication, order history, and personalized shopping experience.
class User:
    def __init__(self, id, email, first_name, last_name, hashed_password, role, is_active, created_at, updated_at):
        self.id = id  # Unique user identifier
        self.email = email  # User's email address for login and communication (must be unique)
        self.first_name = first_name  # User's first name for personalization and shipping
        self.last_name = last_name  # User's last name for personalization and shipping
        self.hashed_password = hashed_password  # Securely hashed password (never store plain text passwords)
        self.role = role  # User permission level: "customer", "admin", "staff", "super_admin"
        self.is_active = is_active  # Whether account is enabled (false = suspended/banned but not deleted)
        self.created_at = created_at  # When user registered/account was created
        self.updated_at = updated_at  # When user profile was last modified
