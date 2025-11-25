from hashing import bcrypt, check_password_hash
import json
import os

class User:
    _permissions = None
    
    @classmethod
    def _load_permissions(cls):
        if cls._permissions is None:
            json_path = os.path.join(os.path.dirname(__file__), '..', 'Utilities', 'role_permissions.json')
            with open(json_path, 'r') as f:
                cls._permissions = json.load(f)
        return cls._permissions
    
    def __init__(self, id, email, first_name, last_name, hashed_password, role, is_active, email_verified, last_login_at, failed_login_attempts, locked_until, created_at, updated_at):
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

    def set_password(self, password: str):
        self.hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))
    
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self) -> dict:
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
        perms = self._load_permissions()
        
        if self.role in perms.get('user_roles', {}):
            role_perms = perms['user_roles'][self.role].get('permissions', {})
        else:
            return False
        
        if resource not in role_perms:
            return False
        
        allowed_actions = role_perms[resource]
        
        for allowed_action in allowed_actions:
            base_action = allowed_action.split(':')[0]
            if base_action == action:
                return True
        
        return False
    
    def validate(self) -> tuple[bool, list[str]]:
        validation_errors = []
        
        if not self.email or '@' not in self.email:
            validation_errors.append("email is required and must contain @")
        elif len(self.email) > 255:
            validation_errors.append("email cannot exceed 255 characters")
        elif self.email != self.email.lower():
            validation_errors.append("email must be lowercase")
        
        if not self.first_name or len(self.first_name.strip()) == 0:
            validation_errors.append("first_name is required and cannot be empty")
        elif len(self.first_name) > 100:
            validation_errors.append("first_name cannot exceed 100 characters")
        
        if not self.last_name or len(self.last_name.strip()) == 0:
            validation_errors.append("last_name is required and cannot be empty")
        elif len(self.last_name) > 100:
            validation_errors.append("last_name cannot exceed 100 characters")
        
        if not self.hashed_password or len(self.hashed_password) == 0:
            validation_errors.append("hashed_password is required and cannot be empty")
        elif len(self.hashed_password) > 255:
            validation_errors.append("hashed_password cannot exceed 255 characters")
        
        if self.failed_login_attempts < 0:
            validation_errors.append("failed_login_attempts cannot be negative")
        
        if self.last_login_at and self.created_at:
            if self.last_login_at < self.created_at:
                validation_errors.append("last_login_at cannot be before created_at")
        
        if self.updated_at and self.created_at:
            if self.updated_at < self.created_at:
                validation_errors.append("updated_at cannot be before created_at")
        
        return len(validation_errors) == 0, validation_errors
    
    def is_locked(self) -> bool:
        if self.locked_until is None:
            return False
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) < self.locked_until
        