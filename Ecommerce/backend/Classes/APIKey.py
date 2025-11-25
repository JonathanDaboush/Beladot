from typing import Optional
from datetime import datetime, timezone

class APIKey:
    def __init__(self, id, user_id, key_hash, name, scopes, is_active, is_revoked, created_at, expires_at, last_used_at):
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