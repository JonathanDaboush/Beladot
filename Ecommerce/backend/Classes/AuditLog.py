from typing import Any

class AuditLog:
    def __init__(self, id, actor_id, actor_type, actor_email, action, target_type, target_id, item_metadata, ip_address, user_agent, created_at):
        self.id = id
        self.actor_id = actor_id
        self.actor_type = actor_type
        self.actor_email = actor_email
        self.action = action
        self.target_type = target_type
        self.target_id = target_id
        self.item_metadata = item_metadata
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.created_at = created_at
    
    def to_dict(self, include_sensitive: bool = False) -> dict[str, Any]:
        result = {
            "id": self.id,
            "actor_id": self.actor_id,
            "actor_type": self.actor_type,
            "action": self.action,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
        
        if include_sensitive:
            result["actor_email"] = self.actor_email
            result["ip_address"] = self.ip_address
            result["user_agent"] = self.user_agent
            result["metadata"] = self.item_metadata
        else:
            if self.item_metadata:
                sanitized = {k: v for k, v in self.item_metadata.items() if k not in ['password', 'token', 'key', 'secret']}
                result["metadata"] = sanitized
        
        return result