from hashing import bcrypt, check_password_hash
import json
import os

class User:
    """
    Domain model representing a user account with authentication and authorization capabilities.
    
    This class encapsulates user identity, credentials, and permissions. It handles password
    hashing/verification using bcrypt and integrates with a role-based permission system.
    
    Key Responsibilities:
        - Secure password management (hashing, verification)
        - Role-based permission checking via external config
        - User profile data management
        - Account security tracking (login attempts, locks)
        - Password reset token management
    
    Security Features:
        - Bcrypt password hashing with automatic salt generation
        - Failed login attempt tracking
        - Account locking mechanism
        - Single-use password reset tokens with expiration
    
    Design Notes:
        - Permissions are loaded once from JSON and cached at class level
        - Email addresses are expected to be normalized (lowercase)
        - This is the domain object; persistence handled by UserRepository
    """
    
    # Class-level cache for permission configuration
    _permissions = None
    
    @classmethod
    def _load_permissions(cls):
        """
        Load role permissions from JSON configuration file.
        
        Permissions are loaded once and cached at the class level for performance.
        The configuration file defines which actions each role can perform on each resource.
        
        Returns:
            dict: The complete permissions configuration structure
        """
        if cls._permissions is None:
            json_path = os.path.join(os.path.dirname(__file__), '..', 'Utilities', 'role_permissions.json')
            with open(json_path, 'r') as f:
                cls._permissions = json.load(f)
        return cls._permissions
    
    def __init__(self, id, email, first_name, last_name, hashed_password, role, is_active, email_verified, last_login_at, failed_login_attempts, locked_until, created_at, updated_at, password_reset_token=None, password_reset_expires=None):
        """
        Initialize a User domain object.
        
        Args:
            id: Unique identifier (None for new users before persistence)
            email: User's email address (should be lowercase)
            first_name: User's first name
            last_name: User's last name
            hashed_password: Bcrypt hashed password (None initially, set via set_password)
            role: User's role (admin, customer, support)
            is_active: Whether the account is active
            email_verified: Whether email has been verified
            last_login_at: Timestamp of last successful login
            failed_login_attempts: Count of consecutive failed login attempts
            locked_until: Timestamp until which account is locked (None if not locked)
            created_at: Account creation timestamp
            updated_at: Last update timestamp
            password_reset_token: Single-use token for password reset (optional)
            password_reset_expires: Expiration time for reset token (optional)
        """
        self.id = id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.hashed_password = hashed_password
        self.role = role
        self.is_active = is_active
        self.email_verified = email_verified
        self.last_login_at = last_login_at
        self.failed_login_attempts = failed_login_attempts
        self.locked_until = locked_until
        self.created_at = created_at
        self.updated_at = updated_at
        self.password_reset_token = password_reset_token
        self.password_reset_expires = password_reset_expires

    def set_password(self, password: str):
        """
        Hash and store a new password securely using bcrypt.
        
        This method generates a new salt and hashes the plaintext password.
        The resulting hash is stored in hashed_password field.
        
        Args:
            password: Plaintext password to hash and store
            
        Security:
            - Uses bcrypt with automatic salt generation
            - Salt is embedded in the hash (no separate storage needed)
            - Computationally expensive to slow down brute-force attacks
        """
        self.hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """
        Verify a plaintext password against the stored hash.
        
        Args:
            password: Plaintext password to verify
            
        Returns:
            bool: True if password matches, False otherwise
            
        Security:
            - Timing-safe comparison via bcrypt
            - Does not reveal information about password validity through timing
        """
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))
    
    def full_name(self) -> str:
        """
        Get the user's full name for display purposes.
        
        Returns:
            str: Full name in "FirstName LastName" format
        """
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self) -> dict:
        """
        Serialize user data to a dictionary for API responses.
        
        Returns:
            dict: User data excluding sensitive fields like hashed_password
            
        Note:
            This method intentionally excludes sensitive data like password hash,
            reset tokens, and detailed security tracking information.
        """
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    def can(self, action: str, resource: str) -> bool:
        """
        Check if this user's role has permission to perform an action on a resource.
        
        This method implements role-based access control by consulting the
        permissions configuration loaded from role_permissions.json.
        
        Args:
            action: The action to check (e.g., "read", "write", "delete")
            resource: The resource type (e.g., "product", "order", "user")
            
        Returns:
            bool: True if user's role permits the action, False otherwise
            
        Example:
            >>> user.can("write", "product")
            True  # if user is admin
            False # if user is customer
            
        Design:
            - Permissions are defined in JSON config, not hardcoded
            - Actions may have modifiers (e.g., "read:own" vs "read:all")
            - Returns False for unknown roles or resources (fail-safe)
        """
        perms = self._load_permissions()
        
        # Check if role exists in configuration
        if self.role in perms.get('user_roles', {}):
            role_perms = perms['user_roles'][self.role].get('permissions', {})
        else:
            return False
        
        # Check if resource exists in role permissions
        if resource not in role_perms:
            return False
        
        allowed_actions = role_perms[resource]
        
        # Check if action matches any allowed action (base action comparison)
        for allowed_action in allowed_actions:
            base_action = allowed_action.split(':')[0]
            if base_action == action:
                return True
        
        return False
    
    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate all user fields against business rules and constraints.
        
        This method performs comprehensive validation to ensure data integrity
        before persistence. It checks format, length, logical consistency, and
        business rules.
        
        Returns:
            tuple: (is_valid: bool, errors: list[str])
                - is_valid: True if all validations pass
                - errors: List of validation error messages (empty if valid)
                
        Validation Rules:
            Email:
                - Required, must contain @
                - Maximum 255 characters
                - Must be lowercase
            Name fields:
                - Required, non-empty after trimming
                - Maximum 100 characters each
            Password:
                - Hashed password required and non-empty
                - Maximum 255 characters
            Security fields:
                - Failed attempts cannot be negative
                - Last login must be after creation
            Timestamps:
                - updated_at must be >= created_at
                
        Design:
            Returns all validation errors at once rather than failing fast,
            providing complete feedback for correction.
        """
        validation_errors = []
        
        # Email validation
        if not self.email or '@' not in self.email:
            validation_errors.append("email is required and must contain @")
        elif len(self.email) > 255:
            validation_errors.append("email cannot exceed 255 characters")
        elif self.email != self.email.lower():
            validation_errors.append("email must be lowercase")
        
        # First name validation
        if not self.first_name or len(self.first_name.strip()) == 0:
            validation_errors.append("first_name is required and cannot be empty")
        elif len(self.first_name) > 100:
            validation_errors.append("first_name cannot exceed 100 characters")
        
        # Last name validation
        if not self.last_name or len(self.last_name.strip()) == 0:
            validation_errors.append("last_name is required and cannot be empty")
        elif len(self.last_name) > 100:
            validation_errors.append("last_name cannot exceed 100 characters")
        
        # Password validation (hash must exist)
        if not self.hashed_password or len(self.hashed_password) == 0:
            validation_errors.append("hashed_password is required and cannot be empty")
        elif len(self.hashed_password) > 255:
            validation_errors.append("hashed_password cannot exceed 255 characters")
        
        # Security field validation
        if self.failed_login_attempts < 0:
            validation_errors.append("failed_login_attempts cannot be negative")
        
        # Timestamp logical consistency
        if self.last_login_at and self.created_at:
            if self.last_login_at < self.created_at:
                validation_errors.append("last_login_at cannot be before created_at")
        
        if self.updated_at and self.created_at:
            if self.updated_at < self.created_at:
                validation_errors.append("updated_at cannot be before created_at")
        
        return len(validation_errors) == 0, validation_errors
    
    def is_locked(self) -> bool:
        """
        Check if the user account is currently locked due to failed login attempts.
        
        Returns:
            bool: True if account is locked and lock hasn't expired, False otherwise
            
        Design:
            - Accounts lock after too many failed login attempts
            - Locks are temporary with an expiration timestamp
            - Returns False if no lock is set (locked_until is None)
        """
        if self.locked_until is None:
            return False
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) < self.locked_until
        