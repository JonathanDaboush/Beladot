from typing import Optional
from datetime import datetime, timezone

class APIKey:
    """
    Domain model representing an API authentication key with scope-based authorization.
    
    This class manages API keys for programmatic access to the platform, providing
    fine-grained permission control through scopes. It supports expiration, revocation,
    and hierarchical permission checking.
    
    Key Responsibilities:
        - Store hashed API key credentials (never plaintext)
        - Manage key lifecycle (active, revoked, expired)
        - Enforce scope-based permissions (resource:action format)
        - Track key usage (last_used_at)
        - Support named keys for user organization
    
    Security Features:
        - Keys stored as hashes (one-way, like passwords)
        - Scope-based authorization (principle of least privilege)
        - Time-based expiration support
        - Revocation mechanism with audit trail
        - Wildcard scopes for convenience (use carefully)
    
    Scope Format:
        - Simple: 'products' (access to all product actions)
        - Action-specific: 'products:read' (read-only access)
        - Wildcards: 'products:*' (all actions), '*' (all resources)
    
    Design Notes:
        - Scopes stored as list of strings for flexibility
        - Hierarchical scope checking (resource:action)
        - This is a domain object; persistence handled by APIKeyRepository
    """
    def __init__(self, id, user_id, key_hash, name, scopes, is_active, is_revoked, created_at, expires_at, last_used_at):
        """
        Initialize an APIKey domain object.
        
        Args:
            id: Unique identifier (None for new keys before persistence)
            user_id: Foreign key to the owning user
            key_hash: Hashed API key (never store plaintext)
            name: User-friendly name for the key (e.g., "Production Server")
            scopes: List of permission scopes (e.g., ['products:read', 'orders:*'])
            is_active: Whether the key is currently active
            is_revoked: Whether the key has been permanently revoked
            created_at: Key creation timestamp
            expires_at: Expiration timestamp (None for no expiration)
            last_used_at: Last successful authentication timestamp
        """
        self.id = id
        self.user_id = user_id
        self.key_hash = key_hash
        self.name = name
        self.scopes = scopes
        self.is_active = is_active
        self.is_revoked = is_revoked
        self.created_at = created_at
        self.expires_at = expires_at
        self.last_used_at = last_used_at
    
    def check_scope(self, scope: str) -> bool:
        """
        Check if the API key has permission for a specific scope.
        
        Performs comprehensive authorization check including key status (active, revoked,
        expired) and hierarchical scope matching with wildcard support.
        
        Args:
            scope: Permission scope to check (e.g., 'products:read', 'orders:create')
            
        Returns:
            bool: True if key has permission and is valid, False otherwise
            
        Authorization Rules:
            - Key must be active and not revoked
            - Key must not be expired
            - Exact scope match: 'products:read' matches 'products:read'
            - Wildcard scopes: '*' or 'all' grant all permissions
            - Resource wildcards: 'products:*' grants all product actions
            - Resource-only: 'products' grants all product actions
            
        Design Notes:
            - Fails closed (returns False on any invalid condition)
            - Checks expiration before scope matching (security first)
            - Supports hierarchical scope parsing (resource:action)
        """
        if not self.is_active or self.is_revoked:
            return False
        
        if self.expires_at and datetime.now(timezone.utc) > self.expires_at:
            return False
        
        if not self.scopes:
            return False
        
        if "*" in self.scopes or "all" in self.scopes:
            return True
        
        if scope in self.scopes:
            return True
        
        resource, action = scope.split(":") if ":" in scope else (scope, None)
        
        for granted_scope in self.scopes:
            if ":" in granted_scope:
                granted_resource, granted_action = granted_scope.split(":")
                if granted_resource == resource and (granted_action == "*" or granted_action == action):
                    return True
            elif granted_scope == resource:
                return True
        
        return False
    
    def revoke(self, actor_id: str, repository=None) -> None:
        """
        Permanently revoke the API key and create audit trail.
        
        Args:
            actor_id: ID of the user/system performing the revocation
            repository: Repository for persisting changes and audit log (optional)
            
        Side Effects:
            - Sets is_revoked to True
            - Sets is_active to False
            - Persists key via repository if provided
            - Creates audit log entry via repository if provided
            
        Design Notes:
            - Revocation is permanent (cannot be undone)
            - Both flags set for defense in depth
            - Audit trail critical for security compliance
        """
        self.is_revoked = True
        self.is_active = False
        
        if repository:
            repository.update(self)
            repository.create_audit_log({
                "actor_id": actor_id,
                "action": "api_key.revoked",
                "target_type": "api_key",
                "target_id": self.id,
                "metadata": {"key_name": self.name, "user_id": self.user_id}
            })